#!/usr/bin/env python3
"""
4. Gemini Clip Analyzer
AI analyzes each 15s clip individually using optimized batch processing
"""

import sys
import os
import json
import time
import math
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from dotenv import load_dotenv
import math

# Load environment variables
load_dotenv()

class FootballClipAnalyzer:
    def __init__(self):
        """Initialize the clip analyzer with Gemini 2.0"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def encode_video_base64(self, video_path: str) -> bytes:
        """Convert video to base64 for Gemini API"""
        try:
            result = subprocess.run([
                'ffmpeg', '-i', str(video_path),
                '-vf', 'scale=640:480',  # Already compressed, just ensure format
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

    def get_football_analysis_prompt(self, timestamp: str) -> str:
        """Generate concise, factual football event detection"""
        return f"""
⚽ CONCISE FOOTBALL EVENT DETECTION
===================================

Analyze this 15-second clip. Report ONLY what you clearly see. Be factual and brief.

PRIORITY EVENTS (report if seen):
- GOALS: "Goal scored by [team/player]"
- SHOTS: "Shot by [team/player] - saved/missed"  
- KICKOFFS: "KICKOFF by [RED/BLACK] team from CENTER CIRCLE"
- GOAL KICKS: "GOAL KICK by [RED/BLACK] goalkeeper from penalty area"
- CELEBRATIONS: "Players celebrating"
- SAVES: "Goalkeeper save"

🚨 ULTRA-CRITICAL DISTINCTION:
- KICKOFF = Specific team lines up at CENTER CIRCLE, both teams on opposite sides, happens AFTER GOALS
- GOAL KICK = Specific goalkeeper kicks from PENALTY AREA, happens when ball goes out over goal line

ALWAYS specify which team/goalkeeper and which type of restart!

RESPONSE FORMAT - BRIEF FACTS ONLY:
State timestamp + what happened. No coaching advice. No invented details.

Example:
2.1s: Shot by BLACK team - saved by goalkeeper
8.3s: KICKOFF by RED team from CENTER CIRCLE
12.0s: Players celebrating near penalty area

WRONG examples (do NOT write like this):
❌ "Kickoff" (too vague - which team? which type?)
❌ "Restart from goal" (unclear - kickoff or goal kick?)

CORRECT examples (write like this):
✅ "KICKOFF by BLACK team from CENTER CIRCLE"
✅ "GOAL KICK by RED goalkeeper from penalty area"

Current clip time: {timestamp}

🚨 FINAL REMINDER: 
- If you see teams at center circle → "KICKOFF by [TEAM] from CENTER CIRCLE"  
- If you see goalkeeper in penalty area kicking → "GOAL KICK by [TEAM] goalkeeper"
- NEVER just say "kickoff" or "restart" - always specify type and team!

Be concise. Report facts only. No speculation.
"""

    def analyze_football_clip(self, compressed_clip_path: str, clip_info: dict) -> dict:
        """Analyze a single compressed football clip (better accuracy than raw)"""
        clip_filename = clip_info['filename']
        start_seconds = clip_info['start_seconds']
        
        print(f"⚽ Analyzing {clip_filename} (starts at {start_seconds//60:.0f}:{start_seconds%60:02.0f})")
        
        start_time = time.time()
        
        # Encode video
        encode_start = time.time()
        video_data = self.encode_video_base64(compressed_clip_path)
        
        if not video_data:
            print(f"❌ Failed to encode {clip_filename}")
            return None
            
        encode_time = time.time() - encode_start
        
        # Generate timestamp for context
        minutes = start_seconds // 60
        seconds = start_seconds % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        
        # Generate prompt
        prompt = self.get_football_analysis_prompt(timestamp)
        
        try:
            # API call
            api_start = time.time()
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "video/mp4",
                    "data": video_data
                }
            ])
            api_time = time.time() - api_start
            
            # Get plain text response
            response_text = response.text.strip()
            
            print(f"✅ Analysis complete for {clip_filename}")
            print(f"   📊 Encode: {encode_time:.1f}s | API: {api_time:.1f}s")
            
            return {
                "clip_filename": clip_filename,
                "start_seconds": start_seconds,
                "end_seconds": clip_info['end_seconds'],
                "duration": clip_info['duration'],
                "timestamp": timestamp,
                "analysis_timestamp": datetime.now().isoformat(),
                "gemini_model": "gemini-2.0-flash-exp",
                "events_analysis": response_text,
                "processing_info": {
                    'encode_time': encode_time,
                    'api_time': api_time,
                    'total_time': time.time() - start_time
                }
            }
        except Exception as e:
            print(f"❌ Error analyzing {clip_filename}: {e}")
            return {
                "clip_filename": clip_filename,
                "start_seconds": start_seconds,
                "timestamp": timestamp,
                "analysis_timestamp": datetime.now().isoformat(),
                "events_analysis": f"Error: {e}",
                "processing_info": {
                    'encode_time': encode_time,
                    'total_time': time.time() - start_time,
                    'error': str(e)
                }
            }

def analyze_clips(match_id):
    """Analyze clips with optimized batch processing and rate limiting"""
    print(f"🧠 Step 4: Gemini football analysis for {match_id}")
    
    data_dir = Path("../data") / match_id
    compressed_dir = data_dir / "compressed_clips"
    analyses_dir = data_dir / "clip_analyses"
    
    if not compressed_dir.exists():
        print(f"❌ Compressed clips directory not found: {compressed_dir}")
        print("Run Step 3.5 first: python 3.5_compress_clips.py")
        return False
    
    # Create analyses directory
    analyses_dir.mkdir(exist_ok=True)
    
    # Scan compressed clips directory directly (better accuracy than raw)
    clip_pairs = []
    compressed_clips = sorted(list(compressed_dir.glob("compressed_clip_*.mp4")))
    
    for compressed_clip in compressed_clips:
        # Extract timing from filename: compressed_clip_00m00s.mp4 -> 00m00s
        filename_base = compressed_clip.stem.replace("compressed_", "")  # clip_00m00s
        original_filename = f"{filename_base}.mp4"  # clip_00m00s.mp4
        
        # Parse time from filename: 00m00s -> 0 seconds
        time_part = filename_base.replace("clip_", "")  # 00m00s
        try:
            minutes = int(time_part.split('m')[0])
            seconds = int(time_part.split('m')[1].replace('s', ''))
            start_seconds = minutes * 60 + seconds
            
            clip_info = {
                'filename': original_filename,
                'start_seconds': start_seconds,
                'end_seconds': start_seconds + 15,  # 15-second clips
                'duration': 15,
                'timestamp': f"{minutes:02d}:{seconds:02d}"
            }
            clip_pairs.append((compressed_clip, clip_info))
        except (ValueError, IndexError):
            print(f"⚠️  Could not parse timing from: {compressed_clip.name}")
    
    if not clip_pairs:
        print("❌ No compressed clips found for analysis")
        return False
    
    print(f"⚽ Found {len(clip_pairs)} compressed clips for analysis (better accuracy)")
    print("⚡ Using OPTIMAL batching to max out 10 RPM experimental model limits")
    print("⏱️  Processing 10 clips in parallel every 60 seconds")
    print()
    
    # Initialize analyzer
    try:
        analyzer = FootballClipAnalyzer()
    except ValueError as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    results = []
    batch_size = 10  # Max out the 10 RPM limit
    max_workers = 10  # Full parallel processing
    delay_between_batches = 60  # Full minute between batches
    
    total_batches = math.ceil(len(clip_pairs) / batch_size)
    print(f"🎯 Processing {len(clip_pairs)} clips in {total_batches} batches of {batch_size}")
    print(f"⏱️  Estimated total time: {total_batches * delay_between_batches / 60:.1f} minutes")
    print()
    
    for batch_num in range(total_batches):
        start = batch_num * batch_size
        end = min(start + batch_size, len(clip_pairs))
        batch = clip_pairs[start:end]
        
        print(f"⚡ Processing batch {batch_num+1}/{total_batches} ({len(batch)} clips in parallel)")
        batch_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_clip = {
                executor.submit(analyzer.analyze_football_clip, compressed_clip, clip_info): (compressed_clip, clip_info)
                for compressed_clip, clip_info in batch
            }
            
            for future in as_completed(future_to_clip):
                compressed_clip, clip_info = future_to_clip[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        
                        # Save individual analysis
                        analysis_filename = clip_info['filename'].replace('.mp4', '_analysis.json')
                        analysis_path = analyses_dir / analysis_filename
                        with open(analysis_path, 'w') as f:
                            json.dump(result, f, indent=2)
                        
                        print(f"✅ Analysis complete for {clip_info['filename']}")
                    else:
                        print(f"❌ Failed to analyze {clip_info['filename']}")
                except Exception as e:
                    print(f"❌ Exception analyzing {clip_info['filename']}: {e}")
        
        batch_time = time.time() - batch_start_time
        print(f"✅ Batch {batch_num+1} complete in {batch_time:.1f}s")
        
        # Wait between batches (except for last batch)
        if batch_num < total_batches - 1:
            print(f"⏳ Waiting {delay_between_batches}s before next batch...")
            time.sleep(delay_between_batches)
            print()
    
    print(f"\n⚽ FOOTBALL ANALYSIS COMPLETE!")
    print("=" * 50)
    print(f"✅ Analyzed {len(results)}/{len(clip_pairs)} clips")
    print(f"📁 Individual analyses saved to: {analyses_dir}")
    
    return len(results) > 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 4_gemini_clip_analyzer.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = analyze_clips(match_id)
    
    if success:
        print(f"🎯 Ready for Step 5: Gemini synthesis")
    else:
        sys.exit(1) 