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
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FootballClipAnalyzer:
    def __init__(self):
        """Initialize the clip analyzer with Gemini 2.5 Pro for maximum accuracy"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        


    def get_football_analysis_prompt(self) -> str:
        """Enhanced prompt with precise timing estimation - WINNING APPROACH + TIMING!"""
        return """🏟️ FOOTBALL MATCH CLIP ANALYSIS (15 seconds)

Analyze this 15-second football clip and provide:
1. **Main action description** (1-2 sentences)
2. **Key timing estimates** within the 15-second window

🎯 FOCUS ON RED vs BLACK TEAMS:
- Ball possession and which team controls it
- Key ball connections (passes, shots, tackles, saves)
- Player movements and team formations
- Precise timing of major events

⏱️ TIMING FORMAT:
Estimate when key events happen within the 15-second clip:
- "2s: Red player receives pass in midfield"
- "7s: Black defender tackles, ball goes out"
- "12s: Red team shoots, goalkeeper saves"

🏟️ EXAMPLE OUTPUT:
"Red team attacks down the left wing, black team defends deep.
2s: Red winger receives ball on left touchline
6s: Cross delivered into penalty area  
9s: Black defender heads clear to midfield
13s: Both teams compete for loose ball"

Focus on the most significant ball connections and team actions with timing estimates."""

    def analyze_football_clip(self, compressed_clip_path: str, clip_info: dict) -> dict:
        """Analyze a single compressed football clip using WINNING FILE UPLOAD approach"""
        clip_filename = clip_info['filename']
        start_seconds = clip_info['start_seconds']
        
        print(f"⚽ Analyzing {clip_filename} (starts at {start_seconds//60:.0f}:{start_seconds%60:02.0f})")
        
        start_time = time.time()
        
        # Generate timestamp for context (needed for error handling too)
        minutes = start_seconds // 60
        seconds = start_seconds % 60
        timestamp = f"{minutes:02d}:{seconds:02d}"
        
        try:
            # WINNING APPROACH: Use file upload instead of base64
            video_file = genai.upload_file(path=str(compressed_clip_path))
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(0.5)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise Exception(f"Video processing failed for {clip_filename}")
            
            # WINNING APPROACH: Simple prompt
            prompt = self.get_football_analysis_prompt()
            
            # API call with file upload
            api_start = time.time()
            response = self.model.generate_content([video_file, prompt])
            api_time = time.time() - api_start
            
            # Clean up uploaded file
            genai.delete_file(video_file.name)
            
            # Get plain text response
            response_text = response.text.strip()
            
            processing_time = time.time() - start_time
            
            print(f"✅ Analysis complete for {clip_filename}")
            print(f"   📊 Processing: {processing_time:.1f}s | API: {api_time:.1f}s")
            
            return {
                "clip_filename": clip_filename,
                "start_seconds": start_seconds,
                "end_seconds": clip_info['end_seconds'],
                "duration": clip_info['duration'],
                "timestamp": timestamp,
                "analysis_timestamp": datetime.now().isoformat(),
                "gemini_model": "gemini-2.5-pro",
                "events_analysis": response_text,
                "processing_time_seconds": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {clip_filename}: {e}")
            return {
                "clip_filename": clip_filename,
                "start_seconds": start_seconds,
                "timestamp": timestamp,
                "analysis_timestamp": datetime.now().isoformat(),
                "gemini_model": "gemini-2.5-pro",
                "events_analysis": f"Error: {str(e)}",
                "processing_time_seconds": 0,
                "status": "failed"
            }

def analyze_clips(match_id):
    """Analyze clips with optimized batch processing and rate limiting"""
    print(f"🧠 Step 4: Gemini football analysis for {match_id}")
    
    # Data directories
    data_dir = Path("../data") / match_id
    clips_dir = data_dir / "clips"  # Use original clips instead of compressed
    analyses_dir = data_dir / "clip_analyses"
    
    if not clips_dir.exists():
        print(f"❌ Clips directory not found: {clips_dir}")
        print(f"   Run 3_generate_clips.py first")
        return False
    
    # Create analyses directory
    analyses_dir.mkdir(exist_ok=True)
    
    # Scan original clips directory (high quality clips)
    clip_pairs = []
    original_clips = sorted(list(clips_dir.glob("clip_*.mp4")))
    
    # FULL MATCH ANALYSIS (all clips)
    print(f"🎯 FULL MATCH ANALYSIS: Processing all clips")
    print(f"📊 Total clips available: {len(original_clips)}")
    print(f"🚀 Ready to process COMPLETE MATCH")
    
    for original_clip in original_clips:
        # Extract timing from filename: clip_00m00s.mp4 -> 00m00s
        filename_base = original_clip.stem  # clip_00m00s
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
            clip_pairs.append((original_clip, clip_info))
        except (ValueError, IndexError):
            print(f"⚠️  Could not parse timing from: {original_clip.name}")
    
    if not clip_pairs:
        print("❌ No original clips found for analysis")
        return False
    
    print(f"⚽ Found {len(clip_pairs)} clips for FIRST 15 MINUTES analysis")
    print("🎯 Using MATURE RATE-LIMITED APPROACH")
    print("⏱️  Processing in small batches to respect API limits")
    print()
    
    # Initialize analyzer
    try:
        analyzer = FootballClipAnalyzer()
    except ValueError as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    results = []
    
    # SMART RATE LIMITING ARCHITECTURE  
    GEMINI_LIMIT_PER_MINUTE = 150
    clip_count = len(clip_pairs)
    
    if clip_count <= GEMINI_LIMIT_PER_MINUTE:
        # FAST PATH: All clips in one batch (under limit)
        batch_size = clip_count
        max_workers = min(clip_count, 25)  # Reasonable worker limit
        delay_between_batches = 0
        total_batches = 1
        print(f"🚀 FAST PATH: All {clip_count} clips in one batch (under 150/min limit)")
        print(f"⚡ Max workers: {max_workers}")
        print(f"⏱️  Estimated time: ~2-3 minutes")
    else:
        # LIMIT PATH: Hit the limit, then wait
        batch_size = GEMINI_LIMIT_PER_MINUTE - 10  # 140 to be safe
        max_workers = 30
        delay_between_batches = 65  # Wait just over a minute
        total_batches = math.ceil(clip_count / batch_size)
        print(f"⚡ LIMIT PATH: {total_batches} batches of ~{batch_size} clips")
        print(f"🚦 Hit limit, wait 65s, repeat")
        print(f"⏱️  Estimated time: ~{total_batches * 3} minutes")
    print()
    
    # Process clips in small, manageable batches
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(clip_pairs))
        batch_clips = clip_pairs[start_idx:end_idx]
        
        print(f"📦 Batch {batch_num + 1}/{total_batches}: Processing {len(batch_clips)} clips")
        batch_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_clip = {
                executor.submit(analyzer.analyze_football_clip, original_clip, clip_info): (original_clip, clip_info)
                for original_clip, clip_info in batch_clips
            }
            
            batch_successful = 0
            batch_failed = 0
            
            for future in as_completed(future_to_clip):
                original_clip, clip_info = future_to_clip[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        
                        # Save individual analysis
                        analysis_filename = clip_info['filename'].replace('.mp4', '_analysis.json')
                        analysis_path = analyses_dir / analysis_filename
                        with open(analysis_path, 'w') as f:
                            json.dump(result, f, indent=2)
                        
                        batch_successful += 1
                        print(f"✅ {clip_info['filename']} complete ({len(results)}/{len(clip_pairs)} total)")
                        
                        # No artificial delays - let API handle the flow
                    else:
                        batch_failed += 1
                        print(f"❌ Failed to analyze {clip_info['filename']}")
                except Exception as e:
                    batch_failed += 1
                    print(f"❌ Exception analyzing {clip_info['filename']}: {e}")
        
        batch_time = time.time() - batch_start_time
        print(f"📦 Batch {batch_num + 1}/{total_batches} complete: ✅{batch_successful} ❌{batch_failed} in {batch_time:.1f}s")
        
        # Only wait if we have more batches AND we're hitting the rate limit
        if batch_num < total_batches - 1 and delay_between_batches > 0:
            print(f"⏳ Rate limit cooldown: {delay_between_batches}s...")
            time.sleep(delay_between_batches)
        print()
    
    total_successful = len(results)
    total_failed = len(clip_pairs) - total_successful
    
    print(f"\n⚽ SMART ANALYSIS COMPLETE!")
    print("=" * 50)
    print(f"🚀 Processed with intelligent rate limiting")
    print(f"✅ Successful: {total_successful}/{len(clip_pairs)} clips")
    print(f"❌ Failed: {total_failed} clips")
    print(f"📁 Individual analyses saved to: {analyses_dir}")
    print(f"⚡ Architecture: {'FAST PATH' if len(clip_pairs) <= GEMINI_LIMIT_PER_MINUTE else 'LIMIT PATH'}")
    
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