#!/usr/bin/env python3
"""
Basketball Event Detector - High Confidence Events
Analyzes video clips to detect basketball events with precise timestamps
"""

import json
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from dotenv import load_dotenv
import os
import math

# Load environment variables
load_dotenv()

class BasketballEventDetector:
    def __init__(self):
        """Initialize the event detector with Gemini 2.5"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def encode_video_base64(self, video_path: str) -> str:
        """Convert video to base64 for Gemini API"""
        try:
            result = subprocess.run([
                'ffmpeg', '-i', str(video_path),
                '-vf', 'scale=640:480',  # Resize for API
                '-r', '2',  # 2 fps for better event detection
                '-f', 'image2pipe', '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264', '-preset', 'ultrafast',
                '-t', '15',  # 15 seconds max
                '-y', '-'
            ], capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Error encoding video: {e}")
            return None

    def get_event_analysis_prompt(self, timestamp: str, camera_side: str) -> str:
        """Generate prompt for high-confidence event detection with basket identification"""
        return f"""
🏀 BASKETBALL EVENT DETECTION
==============================

Analyze this 15-second basketball video clip and describe, in plain text, any high-confidence basketball events you see. Include:
- The exact time in the clip (in seconds) for each event
- Who was involved (active player or bystander, with description)
- What happened (shot, rebound, turnover, foul, etc.)
- The outcome (made/missed, etc.)
- Which basket the event occurred at (LEFT BASKET or RIGHT BASKET)

IMPORTANT: For each event, identify which basket it occurred at:
- LEFT BASKET: Events happening at the left side basket
- RIGHT BASKET: Events happening at the right side basket

If a bystander takes a shot, say so. If no high-confidence events occur, say: "No high-confidence events detected in this clip."

RESPONSE FORMAT (PLAIN TEXT ONLY, NO JSON):

Example:
8.5s: Player_31 (Blue jersey #31) takes a jump shot from three point line – MISSED [LEFT BASKET]
12.3s: Bystander (Gray shirt) takes a practice shot from sideline – MADE [RIGHT BASKET]
15.1s: Player_35 (Purple jersey #35) grabs the rebound [LEFT BASKET]
"""

    def analyze_dual_view_clip(self, left_clip_path: str, right_clip_path: str, timestamp: str) -> dict:
        """Analyze a synchronized dual-view clip for events (plain text only)"""
        print(f"🎬 Analyzing events for {timestamp}")
        
        start_time = time.time()
        
        # Encode both videos
        encode_start = time.time()
        left_video_base64 = self.encode_video_base64(left_clip_path)
        right_video_base64 = self.encode_video_base64(right_clip_path)
        
        if not left_video_base64 or not right_video_base64:
            print(f"❌ Failed to encode videos for {timestamp}")
            return None
            
        encode_time = time.time() - encode_start
        
        # Generate prompt
        prompt = self.get_event_analysis_prompt(timestamp, "dual")
        
        try:
            # API call with both videos
            api_start = time.time()
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "video/mp4",
                    "data": left_video_base64
                },
                {
                    "mime_type": "video/mp4", 
                    "data": right_video_base64
                }
            ])
            api_time = time.time() - api_start
            
            # Get plain text response
            response_text = response.text.strip()
            print(f"\n===== EVENTS SUMMARY for {timestamp} =====\n{response_text}\n========================================\n")
            return {
                "timestamp": timestamp,
                "summary": response_text,
                "processing_info": {
                    'encode_time': encode_time,
                    'api_time': api_time,
                    'total_time': time.time() - start_time,
                    'left_clip_path': str(left_clip_path),
                    'right_clip_path': str(right_clip_path)
                }
            }
        except Exception as e:
            print(f"❌ Error analyzing events for {timestamp}: {e}")
            return {
                "timestamp": timestamp,
                "summary": f"Error: {e}",
                "processing_info": {
                    'encode_time': encode_time,
                    'total_time': time.time() - start_time,
                    'error': str(e)
                }
            }

    def get_clip_pairs(self, clips_dir: Path, sample_size: int | None = None) -> list:
        """Get synchronized left/right clip pairs for analysis"""
        clip_pairs = []
        
        # If no sample_size specified, find all available clips
        if sample_size is None:
            # Find all left clips and determine the range
            left_clips = list(clips_dir.glob("compressed_left_*.mp4"))
            if not left_clips:
                return []
            
            # Extract timestamps and find the maximum
            timestamps = []
            for clip in left_clips:
                timestamp = clip.stem.replace('compressed_left_', '')
                timestamps.append(timestamp)
            
            # Sort timestamps and find the highest
            timestamps.sort()
            max_timestamp = timestamps[-1]
            minutes, seconds = map(int, max_timestamp.split('_'))
            sample_size = minutes * 4 + (seconds // 15) + 1
        
        # Get all clips up to sample_size
        for i in range(sample_size):
            minutes = i // 4
            seconds = (i % 4) * 15
            timestamp = f"{minutes}_{seconds:02d}"
            
            # Use compressed clips for API processing
            left_clip = clips_dir / f"compressed_left_{timestamp}.mp4"
            right_clip = clips_dir / f"compressed_right_{timestamp}.mp4"
            
            if left_clip.exists() and right_clip.exists():
                clip_pairs.append((left_clip, right_clip, timestamp))
            else:
                print(f"⚠️  Missing compressed clip pair for {timestamp}")
        
        return clip_pairs

    def analyze_clips_parallel(self, max_workers: int = 4, batch_size: int = 8, delay: int = 60) -> list:
        """Analyze clips in parallel for event detection"""
        # Get script directory and set up paths
        script_dir = Path(__file__).parent
        utils_output_dir = script_dir.parent / "0_utils" / "output"
        clips_dir = utils_output_dir / "compressed_clips"
        
        # Check if clips exist
        if not clips_dir.exists():
            print(f"❌ Clips directory not found: {clips_dir}")
            print("   Run split_videos.py and compress_videos.py first!")
            return []
        
        # Get clip pairs for analysis
        clip_pairs = self.get_clip_pairs(clips_dir, sample_size=None)  # All available clips
        
        if not clip_pairs:
            print("❌ No clip pairs found for analysis")
            return []

        print(f"🎬 Found {len(clip_pairs)} clip pairs for event analysis")
        print("🚀 Using batch processing for event detection\n")

        results = []
        total_batches = math.ceil(len(clip_pairs) / batch_size)

        for batch_num in range(total_batches):
            start = batch_num * batch_size
            end = min(start + batch_size, len(clip_pairs))
            batch = clip_pairs[start:end]
            print(f"🚩 Processing batch {batch_num+1}/{total_batches} ({len(batch)} clips)")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_clip = {
                    executor.submit(self.analyze_dual_view_clip, left_clip, right_clip, timestamp): (left_clip, right_clip, timestamp)
                    for left_clip, right_clip, timestamp in batch
                }
                for future in as_completed(future_to_clip):
                    left_clip, right_clip, timestamp = future_to_clip[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                            print(f"✅ Completed event analysis for {timestamp}")
                        else:
                            print(f"❌ Failed to analyze events for {timestamp}")
                    except Exception as e:
                        print(f"❌ Exception for {timestamp}: {e}")

            if batch_num < total_batches - 1:
                print(f"⏳ Waiting {delay} seconds to avoid rate limits...")
                time.sleep(delay)

        return results

    def save_results(self, results: list):
        """Save event analysis results to output directory (plain text only)"""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save individual clip analyses (plain text only)
        for result in results:
            timestamp = result.get('timestamp', 'unknown')
            safe_timestamp = timestamp.replace(':', '_')
            text_filename = f"events_analysis_{safe_timestamp}.txt"
            text_file = output_dir / text_filename
            with open(text_file, 'w') as f:
                f.write(f"BASKETBALL EVENTS ANALYSIS - {timestamp}\n")
                f.write("=" * 50 + "\n\n")
                f.write(result.get('summary', 'No summary available'))
                f.write("\n")
        
        print(f"\n📁 Results saved to: {output_dir}")
        print(f"   📝 Text files: events_analysis_*.txt")

# Main function remains the same, but remove JSON event counting and combined output

def main():
    """Run basketball event detection analysis (plain text only)"""
    print("🏀 BASKETBALL EVENT DETECTOR")
    print("=" * 50)
    print("🎯 High-confidence event detection with precise timestamps")
    print("📊 Detecting shots, rebounds, turnovers, fouls, bystander activity")
    print()
    
    try:
        # Initialize detector
        detector = BasketballEventDetector()
        
        # Analyze clips
        results = detector.analyze_clips_parallel()
        
        if results:
            # Save results
            detector.save_results(results)
            print(f"\n✅ Event detection complete!")
            print(f"   📊 Processed {len(results)} clips")
        else:
            print("\n❌ No results generated")
            
    except Exception as e:
        print(f"❌ Error in event detection: {e}")

if __name__ == "__main__":
    main() 