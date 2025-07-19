#!/usr/bin/env python3
"""
Game298_0601 Analyzer
Self-contained AI analysis system for Game298_0601 clips
"""

import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Gemini
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Game298Analyzer:
    """
    Analyzes Game298_0601 video clips for events using Gemini AI
    Detects: goals, shots, passes, tackles, fouls, cards, set pieces
    """
    
    def __init__(self):
        """Initialize the analyzer with API configuration"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Output directory
        self.output_dir = Path("analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            "clips_processed": 0,
            "errors": 0
        }
    
    def encode_video_base64(self, video_path: str) -> bytes:
        """Convert video to base64 for Gemini API"""
        try:
            result = subprocess.run([
                'ffmpeg', '-i', str(video_path),
                '-vf', 'scale=640:480',  # Resize for API
                '-r', '2',  # 2 fps for better event detection
                '-f', 'image2pipe', '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264', '-preset', 'ultrafast',
                '-t', '30',  # 30 seconds max for football clips
                '-y', '-'
            ], capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error encoding video: {e}")
            return None
    
    def get_events_prompt(self, clip_path: str, clip_number: int, clip_start_time: str) -> str:
        """Generate prompt for football event analysis"""
        duration = 30  # 30 seconds per clip
        prompt = f"""
You are analyzing a {duration}-second football video clip that starts at {clip_start_time} into the match. 

**FOCUS ON CRITICAL FOOTBALL EVENTS ONLY:**
- GOALS (listen for referee whistle - whistle indicates goal scored)
- SHOTS ON TARGET (saved/blocked/missed - no whistle means not a goal)
- TURNOVERS (possession changes, interceptions, clear possession switches)
- PENALTIES awarded or taken
- RED/YELLOW CARDS shown
- MAJOR FOULS (that result in free kicks/penalties)
- CORNER KICKS awarded
- SUBSTITUTIONS
- MAJOR TACTICAL CHANGES (formation shifts, pressing)

**IGNORE:**
- Routine passes
- Basic dribbling
- Minor movements
- Unclear/uncertain events

**ANALYSIS FORMAT:**
```
FOOTBALL EVENTS ANALYSIS - CLIP_{clip_number:03d} (Starts at {clip_start_time})
==================================================

[Absolute match time]s: [Event Description] - [EVENT TYPE]
[Absolute match time]s: [Event Description] - [EVENT TYPE]
...

**KEY MOMENTS:**
- [Summary of major events]

**MATCH FLOW:**
- [Brief tactical overview]
```

**TIMESTAMP FORMAT:**
- This clip starts at {clip_start_time} into the match
- Use absolute match time: "0m48s:" (minutes and seconds from match start)
- Calculate: clip start time + seconds into clip = absolute match time
- Example: If clip starts at 0m30s and event is 9 seconds into clip = "0m39s:"
- Example: If clip starts at 1m00s and event is 15 seconds into clip = "1m15s:"

**IMPORTANT:**
- Only report events you are confident about
- If unsure about a foul/card/penalty, don't call it
- Focus on clear, significant moments
- Be slightly less conservative with goals - if it looks like a goal, call it a goal
- Pay attention to referee whistle for goal confirmation
- Distinguish between shots and saves (no whistle = save, whistle = goal)
- For goals: Look for ball crossing goal line, referee whistle, or clear goal celebration
- ALWAYS use absolute match time, never clip-relative time

Analyze this {duration}-second football clip and identify ONLY the major football events that occurred.
"""
        return prompt
    
    def analyze_clip(self, clip_path: str, clip_number: int, clip_start_time: str) -> Dict[str, Any]:
        """Analyze a single football clip for events"""
        try:
            logger.info(f"Analyzing clip {clip_number:03d}: {Path(clip_path).name} (starts at {clip_start_time})")
            
            # Generate prompt
            prompt = self.get_events_prompt(clip_path, clip_number, clip_start_time)
            
            # Encode video
            video_data = self.encode_video_base64(clip_path)
            if not video_data:
                raise Exception("Failed to encode video")
            
            # Call Gemini API
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "video/mp4",
                    "data": video_data
                }
            ])
            
            # Parse response
            analysis_text = response.text
            
            # Save individual clip analysis
            output_filename = f"events_analysis_{clip_number:03d}.txt"
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w') as f:
                f.write(f"FOOTBALL EVENTS ANALYSIS - CLIP_{clip_number:03d}\n")
                f.write("=" * 50 + "\n\n")
                f.write(analysis_text)
                f.write("\n")
            
            logger.info(f"✅ Clip {clip_number:03d} analyzed successfully")
            
            return {
                "success": True,
                "clip_number": clip_number,
                "analysis": analysis_text,
                "output_path": str(output_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing clip {clip_number:03d}: {e}")
            self.stats["errors"] += 1
            
            return {
                "success": False,
                "clip_number": clip_number,
                "error": str(e)
            }
    
    def analyze_all_clips(self) -> List[Dict[str, Any]]:
        """Analyze Game298_0601 clips up to 4 minutes (240 seconds)"""
        clips_dir = Path("clips")
        
        if not clips_dir.exists():
            logger.error(f"Clips directory not found: {clips_dir}")
            return []
        
        # Find all clips with time-based naming
        clip_files = sorted([
            f for f in clips_dir.glob("clip_*.mp4")
        ])
        
        if not clip_files:
            logger.error(f"No clips found in: {clips_dir}")
            return []
        
        # Filter clips up to 4 minutes (240 seconds)
        # We want clips: clip_0m00s.mp4, clip_0m30s.mp4, ..., clip_3m30s.mp4
        max_minutes = 3  # Up to 3 minutes 30 seconds
        filtered_clips = []
        
        for clip_path in clip_files:
            # Extract start time from filename (e.g., clip_0m30s.mp4 -> 0m30s)
            time_str = clip_path.stem.split('_')[-1]
            minutes = int(time_str.split('m')[0])
            seconds = int(time_str.split('m')[1].split('s')[0])
            start_time_seconds = minutes * 60 + seconds
            
            if start_time_seconds <= 210:  # 3m30s = 210 seconds
                filtered_clips.append(clip_path)
        
        logger.info(f"Found {len(filtered_clips)} clips to analyze (first 4 minutes)")
        
        results = []
        
        for clip_path in filtered_clips:
            # Extract start time from filename (e.g., clip_0m30s.mp4 -> 0m30s)
            time_str = clip_path.stem.split('_')[-1]
            minutes = int(time_str.split('m')[0])
            seconds = int(time_str.split('m')[1].split('s')[0])
            start_time_seconds = minutes * 60 + seconds
            
            # Calculate clip number based on start time (0, 30, 60, 90, 120, 150, 180, 210)
            clip_number = (start_time_seconds // 30) + 1
            
            # Calculate clip start time string
            clip_start_minutes = start_time_seconds // 60
            clip_start_seconds = start_time_seconds % 60
            clip_start_time = f"{clip_start_minutes}m{clip_start_seconds:02d}s"
            
            # Analyze clip
            result = self.analyze_clip(str(clip_path), clip_number, clip_start_time)
            results.append(result)
            
            # Rate limiting
            time.sleep(1.0)  # 1 second delay between API calls
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print analysis summary"""
        successful = len([r for r in results if r["success"]])
        total = len(results)
        
        print("\n" + "=" * 60)
        print("GAME298_0601 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total clips: {total}")
        print(f"Successful analyses: {successful}")
        print(f"Failed analyses: {total - successful}")
        print(f"Success rate: {(successful/total)*100:.1f}%" if total > 0 else "0%")
        print(f"Output directory: {self.output_dir}")
        print("=" * 60)

def main():
    """Main analysis process"""
    logger.info("🎬 Starting Game298_0601 analysis")
    
    try:
        # Initialize analyzer
        analyzer = Game298Analyzer()
        
        # Run analysis
        results = analyzer.analyze_all_clips()
        
        # Print summary
        analyzer.print_summary(results)
        
        if results:
            successful = len([r for r in results if r["success"]])
            if successful > 0:
                logger.info("✅ Analysis completed successfully!")
                print(f"\n📁 Analysis files saved in: {analyzer.output_dir}")
                print("Next step: Run synthesis to create timeline")
            else:
                logger.error("❌ No clips were analyzed successfully!")
        else:
            logger.error("❌ No clips found to analyze!")
            
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 