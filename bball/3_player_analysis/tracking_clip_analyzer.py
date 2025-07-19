#!/usr/bin/env python3
"""
Individual Player Tracking - Basketball Performance Analysis
Analyzes video clips to track a specific player's performance throughout the game
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

# =============================================================================
# 🎯 PLAYER CONFIGURATION - EDIT THIS SECTION
# =============================================================================
# Change these values to analyze a different player
TARGET_PLAYER = "Player_31"                    # Player identifier (e.g., "Player_31", "Player_86")
PLAYER_JERSEY = "Blue jersey #31"              # Jersey description for analysis
PLAYER_DESCRIPTION = "Blue jersey #31, athletic build, high-volume scorer, versatile shooter from 3-point to inside paint, active on both baskets, strong finisher, appears in 12 game segments throughout the 10-minute game with 6/12 shots made (50% shooting), excellent 3-point shooter (1/1), struggled with free throws (0/1), made 3 consecutive shots in final minutes showing clutch performance"
# =============================================================================

# Load environment variables
load_dotenv()

class PlayerTrackingAnalyzer:
    def __init__(self, target_player: str = TARGET_PLAYER):
        """Initialize the player tracking analyzer with Gemini 2.0 Flash"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Change from Pro to Flash (like events analyzer)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.target_player = target_player
        
    def encode_video_base64(self, video_path: str) -> str:
        """Convert video to base64 for Gemini API"""
        try:
            result = subprocess.run([
                'ffmpeg', '-i', str(video_path),
                '-vf', 'scale=640:480',  # Resize for API
                '-r', '2',  # 2 fps for better tracking
                '-f', 'image2pipe', '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264', '-preset', 'ultrafast',
                '-t', '15',  # 15 seconds max
                '-y', '-'
            ], capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Error encoding video: {e}")
            return None

    def get_player_tracking_prompt(self, timestamp: str, target_player: str) -> str:
        return f"""
🏀 PLAYER EVENT TRACKING - DUAL CAMERA ANALYSIS
===============================================

MISSION: Track ALL basketball events involving {target_player} in this 15-second dual-camera video clip.

CONTEXT: You have synchronized left and right camera views of the same 15-second basketball session. Use BOTH camera angles to get a complete picture of {target_player}'s actions throughout the clip.

TRACKING REQUIREMENTS:
- Shots (made/missed) - specify which basket if possible
- Passes (completed/intercepted) 
- Rebounds (secured/missed)
- Dribbling (initiated/continued/completed)
- Defensive actions (guarding, blocking, positioning)
- Movement patterns (court positioning, cuts, screens)
- Ball possession changes

FORMAT: [time]s: {target_player} [action] - [outcome]

EXAMPLES:
2.1s: {target_player} takes jump shot - MADE
4.3s: {target_player} passes to teammate - COMPLETED
7.8s: {target_player} grabs rebound - SECURED
10.2s: {target_player} dribbles ball - INITIATED
12.5s: {target_player} defends shot - BLOCKED

IMPORTANT:
- Use BOTH left and right camera angles for complete tracking
- If {target_player} is not visible, say: "{target_player} not visible"
- Be specific about shot outcomes (MADE/MISSED)
- Note defensive actions and court positioning
- Track ball possession and movement patterns

TIMESTAMP: {timestamp}
TARGET PLAYER: {target_player}
"""

    def analyze_player_in_clip(self, left_clip_path: str, right_clip_path: str, timestamp: str) -> dict:
        """Analyze a clip for specific player tracking"""
        print(f"🎯 Tracking {self.target_player} in {timestamp}")
        
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
        prompt = self.get_player_tracking_prompt(timestamp, self.target_player)
        
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
            print(f"\n===== {self.target_player} TRACKING for {timestamp} =====\n{response_text}\n========================================\n")
            return {
                "timestamp": timestamp,
                "player": self.target_player,
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
            print(f"❌ Error tracking {self.target_player} in {timestamp}: {e}")
            return {
                "timestamp": timestamp,
                "player": self.target_player,
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

    def analyze_player_parallel(self, max_workers: int = 4, batch_size: int = 8, delay: int = 60) -> list:
        """Analyze clips in parallel for player tracking with batching"""
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
        
        print(f"🎯 Found {len(clip_pairs)} clip pairs for {self.target_player} tracking")
        print("🚀 Using batch processing for player tracking\n")
        
        results = []
        total_batches = math.ceil(len(clip_pairs) / batch_size)

        for batch_num in range(total_batches):
            start = batch_num * batch_size
            end = min(start + batch_size, len(clip_pairs))
            batch = clip_pairs[start:end]
            print(f"🚩 Processing batch {batch_num+1}/{total_batches} ({len(batch)} clips)")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_clip = {
                    executor.submit(self.analyze_player_in_clip, left_clip, right_clip, timestamp): (left_clip, right_clip, timestamp)
                    for left_clip, right_clip, timestamp in batch
                }
                for future in as_completed(future_to_clip):
                    left_clip, right_clip, timestamp = future_to_clip[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                            print(f"✅ Completed {self.target_player} tracking for {timestamp}")
                        else:
                            print(f"❌ Failed to track {self.target_player} in {timestamp}")
                    except Exception as e:
                        print(f"❌ Exception for {timestamp}: {e}")

            if batch_num < total_batches - 1:
                print(f"⏳ Waiting {delay} seconds to avoid rate limits...")
                time.sleep(delay)

        return results

    def save_results(self, results: list):
        """Save player tracking results to output directory"""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save individual clip analyses
        for result in results:
            timestamp = result.get('timestamp', 'unknown')
            safe_timestamp = timestamp.replace(':', '_')
            text_filename = f"player_tracking_{safe_timestamp}.txt"
            text_file = output_dir / text_filename
            with open(text_file, 'w') as f:
                f.write(f"PLAYER TRACKING ANALYSIS - {self.target_player} - {timestamp}\n")
                f.write("=" * 60 + "\n\n")
                f.write(result.get('summary', 'No summary available'))
                f.write("\n")
        
        print(f"\n📁 Results saved to: {output_dir}")
        print(f"   📝 Text files: player_tracking_*.txt")

def main():
    """Run individual player tracking analysis"""
    print("🎯 INDIVIDUAL PLAYER TRACKING")
    print("=" * 50)
    print("📊 Tracking specific player performance throughout the game")
    print(f"🎯 Target player: {TARGET_PLAYER} ({PLAYER_JERSEY})")
    print()
    
    try:
        # Initialize analyzer
        analyzer = PlayerTrackingAnalyzer(target_player=TARGET_PLAYER)
        
        # Analyze clips
        results = analyzer.analyze_player_parallel()
        
        if results:
            # Save results
            analyzer.save_results(results)
            print(f"\n✅ Player tracking complete!")
            print(f"   📊 Processed {len(results)} clips")
            print(f"   🎯 Tracked {analyzer.target_player} throughout the game")
        else:
            print("\n❌ No results generated")
            
    except Exception as e:
        print(f"❌ Error in player tracking: {e}")

if __name__ == "__main__":
    main() 