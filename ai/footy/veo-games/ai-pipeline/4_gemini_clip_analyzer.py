#!/usr/bin/env python3
"""
4. Gemini Clip Analyzer
AI analyzes each 15s clip individually using optimized batch processing
"""

import sys
import os
import json
import time
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
        """Generate prompt for football event detection"""
        return f"""
⚽ FOOTBALL EVENT DETECTION
==============================

Analyze this 15-second football match clip and describe, in plain text, any football events you see. Include:
- The exact time in the clip (in seconds) for each event
- Who was involved (player description, jersey color/number if visible)
- What happened (goal, shot, pass, tackle, foul, corner kick, throw-in, etc.)
- The outcome (successful/unsuccessful)
- Field position (penalty area, center circle, attacking third, etc.)

IMPORTANT FOOTBALL EVENTS TO DETECT:
- ⚽ GOALS and shots (on target, off target, saved)
- 🥅 GOALKEEPING actions (saves, catches, clearances)
- ⚽ PASSING and crosses (successful, intercepted)
- 🏃 TACKLES and challenges (won, lost)
- 🔄 POSSESSION changes and turnovers
- 🟨 FOULS and disciplinary actions
- 📐 SET PIECES (corners, free kicks, throw-ins)
- 🏃 OFFSIDES and defensive plays

If no significant football events occur, say: "No significant football events detected in this clip."

RESPONSE FORMAT (PLAIN TEXT ONLY, NO JSON):

Example:
3.2s: Player in blue jersey (#10) takes a shot from edge of penalty area – SAVED by goalkeeper
7.8s: Goalkeeper distributes ball with throw to defender
12.1s: Red team player wins tackle in midfield, starts counter-attack
14.5s: Cross from right wing into penalty area – CLEARED by defender

Time reference: {timestamp}
"""

    def analyze_football_clip(self, compressed_clip_path: str, clip_info: dict) -> dict:
        """Analyze a single compressed football clip"""
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
    
    # Load clips metadata
    clips_dir = data_dir / "clips"
    segments_file = clips_dir / "segments.json"
    if not segments_file.exists():
        print(f"❌ Segments metadata not found: {segments_file}")
        return False
    
    with open(segments_file, 'r') as f:
        segments_data = json.load(f)
    
    # Create analyses directory
    analyses_dir.mkdir(exist_ok=True)
    
    # Get compressed clips with metadata
    clip_pairs = []
    for clip_info in segments_data['clips']:
        compressed_clip = compressed_dir / f"compressed_{clip_info['filename']}"
        if compressed_clip.exists():
            clip_pairs.append((compressed_clip, clip_info))
        else:
            print(f"⚠️  Missing compressed clip: {clip_info['filename']}")
    
    if not clip_pairs:
        print("❌ No compressed clips found for analysis")
        return False
    
    print(f"⚽ Found {len(clip_pairs)} compressed clips for analysis")
    print("🚀 Using batch processing with rate limiting")
    print("⏱️  Processing in batches of 8 with 60s delays")
    print()
    
    # Initialize analyzer
    try:
        analyzer = FootballClipAnalyzer()
    except ValueError as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    results = []
    batch_size = 8
    max_workers = 4
    delay_between_batches = 60
    
    total_batches = math.ceil(len(clip_pairs) / batch_size)
    
    for batch_num in range(total_batches):
        start = batch_num * batch_size
        end = min(start + batch_size, len(clip_pairs))
        batch = clip_pairs[start:end]
        
        print(f"🏈 Processing batch {batch_num+1}/{total_batches} ({len(batch)} clips)")
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
                        
                    else:
                        print(f"❌ Failed to analyze {clip_info['filename']}")
                except Exception as e:
                    print(f"❌ Exception analyzing {clip_info['filename']}: {e}")
        
        batch_time = time.time() - batch_start_time
        print(f"✅ Batch {batch_num+1} complete in {batch_time:.1f}s")
        
        # Rate limiting delay between batches
        if batch_num < total_batches - 1:
            print(f"⏳ Waiting {delay_between_batches}s to avoid rate limits...")
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