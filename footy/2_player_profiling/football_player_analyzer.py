#!/usr/bin/env python3
"""
Football Player Analyzer
Analyzes 30-second football clips for player identification
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent / "0_utils"))
from config import API_SETTINGS, FOOTBALL_SETTINGS, PATHS, get_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballPlayerAnalyzer:
    """
    Analyzes football video clips for player identification
    Identifies: jersey numbers, team colors, positions, player roles
    """
    
    def __init__(self):
        """Initialize the analyzer with API configuration"""
        self.api_key = get_api_key()
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(API_SETTINGS["model"])
        
        # Output directory
        self.output_dir = PATHS["player_output"]
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            "clips_processed": 0,
            "players_identified": 0,
            "api_calls": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def get_player_analysis_prompt(self, clip_path: str, clip_number: int) -> str:
        """Generate prompt for football player analysis"""
        return f"""
👥 FOOTBALL PLAYER ANALYSIS
===========================

You are a professional football scout. Analyze this 30-second football clip and identify ALL players visible.

**PLAYER IDENTIFICATION REQUIREMENTS:**
- 🎽 JERSEY NUMBERS: Identify all visible jersey numbers
- 🎨 TEAM COLORS: Note team colors (Blue, Red, White, etc.)
- ⚽ POSITIONS: Identify player positions (GK, DEF, MID, FWD)
- 🏃 PLAYER ROLES: Note player roles and responsibilities
- 📍 POSITIONING: Describe where players are positioned on the field

**ANALYSIS REQUIREMENTS:**
1. Watch the entire 30-second clip carefully
2. Identify ALL players visible in the clip
3. Note jersey numbers and team colors
4. Classify player positions (Goalkeeper, Defender, Midfielder, Forward)
5. Describe player roles and responsibilities
6. Note any key players or standout performances

**OUTPUT FORMAT:**
```
FOOTBALL PLAYER ANALYSIS - CLIP_{clip_number:03d}
==================================================

ESTIMATED TOTALS:
- Active Players: ~X people
- Total Individuals: ~X people

DETAILED ANALYSIS:
Player_10: Blue jersey #10, midfielder, central playmaker, involved in build-up play, ACTIVE
Player_7: Red jersey #7, defender, right-back, making overlapping runs, ACTIVE
Player_1: Blue jersey #1, goalkeeper, making saves and distribution, ACTIVE
Bystander_Coach: Standing on sideline, observing play, no active involvement, BYSTANDER
...
```

**PLAYER CLASSIFICATION:**
- **ACTIVE**: Players actively involved in the game
- **BYSTANDER**: Coaches, substitutes, spectators not in play

**POSITION CLASSIFICATION:**
- **GK**: Goalkeeper
- **DEF**: Defender (Center-back, Full-back, Wing-back)
- **MID**: Midfielder (Defensive, Central, Attacking)
- **FWD**: Forward (Striker, Winger, Second Striker)

**IMPORTANT:**
- Be precise with jersey numbers and team colors
- Classify positions accurately
- Note any key players or standout performances
- Distinguish between active players and bystanders
- Focus on football-specific player roles and positioning

Analyze the video clip and provide a complete player identification analysis.
"""
    
    def analyze_clip(self, clip_path: str, clip_number: int) -> Dict[str, Any]:
        """Analyze a single football clip for players"""
        try:
            logger.info(f"Analyzing players in clip {clip_number:03d}: {Path(clip_path).name}")
            
            # Generate prompt
            prompt = self.get_player_analysis_prompt(clip_path, clip_number)
            
            # Read video file
            with open(clip_path, 'rb') as video_file:
                video_data = video_file.read()
            
            # Call Gemini API
            response = self.model.generate_content([prompt, video_data])
            
            # Parse response
            analysis_text = response.text
            
            # Save individual clip analysis
            output_filename = f"player_analysis_{clip_number:03d}.txt"
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w') as f:
                f.write(analysis_text)
            
            # Save JSON version
            json_filename = f"player_analysis_{clip_number:03d}.json"
            json_path = self.output_dir / json_filename
            
            analysis_data = {
                "clip_number": clip_number,
                "clip_path": str(clip_path),
                "analysis": analysis_text,
                "timestamp": datetime.now().isoformat(),
                "api_model": API_SETTINGS["model"]
            }
            
            with open(json_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            # Update statistics
            self.stats["clips_processed"] += 1
            self.stats["api_calls"] += 1
            
            logger.info(f"✅ Clip {clip_number:03d} player analysis complete")
            
            return {
                "success": True,
                "clip_number": clip_number,
                "analysis": analysis_text,
                "output_path": str(output_path),
                "json_path": str(json_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing players in clip {clip_number:03d}: {e}")
            self.stats["errors"] += 1
            
            return {
                "success": False,
                "clip_number": clip_number,
                "error": str(e)
            }
    
    def analyze_all_clips(self, clips_dir: str) -> List[Dict[str, Any]]:
        """Analyze all football clips for players"""
        clips_path = Path(clips_dir)
        
        if not clips_path.exists():
            logger.error(f"Clips directory not found: {clips_dir}")
            return []
        
        # Find all football clips
        clip_files = sorted([
            f for f in clips_path.glob("football_clip_*.mp4")
        ])
        
        if not clip_files:
            logger.error(f"No football clips found in: {clips_dir}")
            return []
        
        logger.info(f"Found {len(clip_files)} clips for player analysis")
        
        # Start timing
        self.stats["start_time"] = datetime.now()
        
        results = []
        
        for i, clip_path in enumerate(clip_files):
            # Extract clip number from filename
            clip_number = int(clip_path.stem.split('_')[-1])
            
            # Analyze clip
            result = self.analyze_clip(str(clip_path), clip_number)
            results.append(result)
            
            # Rate limiting
            if i < len(clip_files) - 1:  # Don't delay after last clip
                time.sleep(API_SETTINGS["rate_limit_delay"])
        
        # End timing
        self.stats["end_time"] = datetime.now()
        
        # Save analysis statistics
        self.save_analysis_stats(results)
        
        return results
    
    def save_analysis_stats(self, results: List[Dict[str, Any]]):
        """Save analysis statistics"""
        successful_results = [r for r in results if r["success"]]
        
        stats_data = {
            "analysis_date": datetime.now().isoformat(),
            "total_clips": len(results),
            "successful_clips": len(successful_results),
            "failed_clips": len(results) - len(successful_results),
            "api_calls": self.stats["api_calls"],
            "errors": self.stats["errors"],
            "processing_time": str(self.stats["end_time"] - self.stats["start_time"]) if self.stats["start_time"] and self.stats["end_time"] else None,
            "api_model": API_SETTINGS["model"],
            "football_positions": FOOTBALL_SETTINGS["positions"]
        }
        
        stats_path = self.output_dir / "player_analysis_statistics.json"
        with open(stats_path, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        logger.info(f"📊 Player analysis complete: {len(successful_results)}/{len(results)} clips successful")
        logger.info(f"📈 Statistics saved: {stats_path}")

def main():
    """Main function for football player analysis"""
    analyzer = FootballPlayerAnalyzer()
    
    # Analyze clips from the processed directory
    clips_dir = PATHS["processed_clips"]
    
    print("👥 Football Player Analysis")
    print("=" * 30)
    print(f"Analyzing clips from: {clips_dir}")
    print(f"Output directory: {PATHS['player_output']}")
    print()
    
    # Run analysis
    results = analyzer.analyze_all_clips(str(clips_dir))
    
    if results:
        successful = len([r for r in results if r["success"]])
        print(f"\n✅ Player analysis complete: {successful}/{len(results)} clips successful")
        print(f"📁 Results saved in: {PATHS['player_output']}")
    else:
        print("\n❌ No clips were analyzed successfully")

if __name__ == "__main__":
    main() 