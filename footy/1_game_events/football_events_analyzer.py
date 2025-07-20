#!/usr/bin/env python3
"""
Football Events Analyzer
Analyzes football video clips for events using Gemini AI
"""

import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "0_utils"))
from config import API_SETTINGS, FOOTBALL_SETTINGS, PATHS, get_api_key

# Import Gemini
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballEventsAnalyzer:
    """
    Analyzes football video clips for events using Gemini AI
    Detects: goals, shots, passes, tackles, fouls, cards, set pieces
    """
    
    def __init__(self):
        """Initialize the analyzer with API configuration"""
        self.api_key = get_api_key()
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model (use same as basketball)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Output directory
        self.output_dir = PATHS["events_output"]
        self.output_dir.mkdir(exist_ok=True)
        
        # Simple statistics tracking
        self.stats = {
            "clips_processed": 0,
            "errors": 0
        }
    
    def encode_video_base64(self, video_path: str) -> bytes:
        """Convert video to base64 for Gemini API (same as basketball)"""
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
    
    def get_events_prompt(self, clip_path: str, clip_number: int) -> str:
        """Generate prompt for football event analysis"""
        duration = 30 # Assuming a default duration for the prompt
        prompt = f"""
You are analyzing a {duration}-second football video clip. 

**FOCUS ON CRITICAL FOOTBALL EVENTS ONLY:**
- GOALS (with team and player if visible)
- TURNOVERS (possession changes, interceptions, clear possession switches)
- SHOTS ON TARGET (saved/blocked/missed)
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
FOOTBALL EVENTS ANALYSIS - CLIP_{clip_number:03d}
==================================================

[Seconds]s: [Event Description] - [EVENT TYPE]
[Seconds]s: [Event Description] - [EVENT TYPE]
...

**KEY MOMENTS:**
- [Summary of major events]

**MATCH FLOW:**
- [Brief tactical overview]
```

**TIMESTAMP FORMAT:**
- Use format: "27s:" (not "00:27s:" or "27.5s:")
- Just the number of seconds from clip start
- Example: "15s: Goal scored by team A - GOAL"

**IMPORTANT:**
- Only report events you are confident about
- If unsure about a foul/card/penalty, don't call it
- Focus on clear, significant moments
- Be conservative - quality over quantity

Analyze this {duration}-second football clip and identify ONLY the major football events that occurred.
"""
        return prompt
    
    def analyze_clip(self, clip_path: str, clip_number: int) -> Dict[str, Any]:
        """Analyze a single football clip for events"""
        try:
            logger.info(f"Analyzing clip {clip_number:03d}: {Path(clip_path).name}")
            
            # Generate prompt
            prompt = self.get_events_prompt(clip_path, clip_number)
            
            # Encode video properly (like basketball script)
            video_data = self.encode_video_base64(clip_path)
            if not video_data:
                raise Exception("Failed to encode video")
            
            # Call Gemini API with proper format
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "video/mp4",
                    "data": video_data
                }
            ])
            
            # Parse response
            analysis_text = response.text
            
            # Save individual clip analysis (plain text only)
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
    
    def analyze_all_clips(self, clips_dir: str) -> List[Dict[str, Any]]:
        """Analyze all football clips in directory"""
        clips_path = Path(clips_dir)
        
        if not clips_path.exists():
            logger.error(f"Clips directory not found: {clips_dir}")
            return []
        
        # Find all football clips (support both naming patterns)
        clip_files = sorted([
            f for f in clips_path.glob("*.mp4") 
            if f.name.startswith(("football_clip_", "match_"))
        ])
        
        if not clip_files:
            logger.error(f"No football clips found in: {clips_dir}")
            return []
        
        logger.info(f"Found {len(clip_files)} clips to analyze")
        
        results = []
        
        for i, clip_path in enumerate(clip_files):
            # Extract clip number from filename (handle both naming patterns)
            if clip_path.name.startswith("football_clip_"):
                clip_number = int(clip_path.stem.split('_')[-1])
            elif clip_path.name.startswith("match_"):
                # Extract actual match time from match_18m00s.mp4 -> 18:00
                time_str = clip_path.stem.replace("match_", "").replace("m", ":").replace("s", "")
                # Convert to seconds for absolute time calculation
                minutes, seconds = map(int, time_str.split(":"))
                clip_start_time = minutes * 60 + seconds
                clip_number = clip_start_time  # Use actual match time in seconds
            else:
                clip_number = i
            
            # Analyze clip
            result = self.analyze_clip(str(clip_path), clip_number)
            results.append(result)
            
            # Rate limiting
            if i < len(clip_files) - 1:  # Don't delay after last clip
                time.sleep(API_SETTINGS["rate_limit_delay"])
        
        return results
    
def main():
    """Main function for football events analysis"""
    analyzer = FootballEventsAnalyzer()
    
    # Analyze clips from the processed directory
    clips_dir = PATHS["processed_clips"]
    
    print("⚽ Football Events Analysis")
    print("=" * 30)
    print(f"Analyzing clips from: {clips_dir}")
    print(f"Output directory: {PATHS['events_output']}")
    print()
    
    # Run analysis
    results = analyzer.analyze_all_clips(str(clips_dir))
    
    if results:
        successful = len([r for r in results if r["success"]])
        print(f"\n✅ Analysis complete: {successful}/{len(results)} clips successful")
        print(f"📁 Results saved in: {PATHS['events_output']}")
    else:
        print("\n❌ No clips were analyzed successfully")

if __name__ == "__main__":
    main() 