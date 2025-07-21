#!/usr/bin/env python3
"""
Football Formation Analyzer
Analyzes football clips for team formations and tactical patterns
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from datetime import datetime

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent / "0_utils"))
from config import API_SETTINGS, FOOTBALL_SETTINGS, PATHS, get_api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballFormationAnalyzer:
    """
    Analyzes football video clips for tactical formations and patterns
    Detects: team formations, player positioning, tactical strategies
    """
    
    def __init__(self):
        """Initialize the analyzer with API configuration"""
        self.api_key = get_api_key()
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model for tactical analysis
        self.model = genai.GenerativeModel(API_SETTINGS["tactical_model"])
        
        # Output directory
        self.output_dir = PATHS["tactical_output"]
        self.output_dir.mkdir(exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            "clips_processed": 0,
            "formations_detected": 0,
            "api_calls": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def get_formation_analysis_prompt(self, clip_path: str, clip_number: int) -> str:
        """Generate prompt for football formation analysis"""
        return f"""
🏟️ FOOTBALL FORMATION ANALYSIS
==============================

You are a professional football tactician. Analyze this 30-second football clip and identify team formations and tactical patterns.

**FORMATION DETECTION REQUIREMENTS:**
- 📐 TEAM FORMATIONS: Identify formations (4-3-3, 4-4-2, 3-5-2, etc.)
- 🎯 PLAYER POSITIONING: Note how players are positioned on the field
- ⚽ TACTICAL PATTERNS: Identify pressing, possession, and attacking strategies
- 🏃 PLAYER MOVEMENT: Note player runs, positioning, and tactical roles
- 📊 TEAM SHAPE: Analyze defensive and attacking shapes

**ANALYSIS REQUIREMENTS:**
1. Watch the entire 30-second clip carefully
2. Identify team formations for both teams
3. Note player positioning and tactical roles
4. Analyze pressing strategies and defensive organization
5. Identify attacking patterns and build-up play
6. Note any tactical changes or key moments

**OUTPUT FORMAT:**
```
FOOTBALL FORMATION ANALYSIS - CLIP_{clip_number:03d}
====================================================

TEAM FORMATIONS:
Blue Team: 4-3-3 formation
- GK: Player_1 (Blue #1) - Sweeper-keeper role
- DEF: Players 2,3,4,5 - High defensive line
- MID: Players 6,8,10 - Central midfield control
- FWD: Players 7,9,11 - Attacking trio

Red Team: 4-4-2 formation  
- GK: Player_12 (Red #12) - Traditional goalkeeper
- DEF: Players 13,14,15,16 - Compact defensive block
- MID: Players 17,18,19,20 - Wide midfield support
- FWD: Players 21,22 - Striker partnership

TACTICAL PATTERNS:
- Blue team using high pressing and possession-based play
- Red team employing counter-attacking strategy
- Key battle in midfield between Player_8 (Blue) and Player_19 (Red)
- Blue team dominating possession with 65% ball control
```

**FORMATION TYPES TO DETECT:**
- **4-3-3**: Attacking formation with wingers
- **4-4-2**: Balanced formation with two strikers
- **3-5-2**: Wing-back system with three center-backs
- **4-2-3-1**: Modern attacking formation
- **3-4-3**: Attacking wing-back system
- **5-3-2**: Defensive formation with wing-backs

**TACTICAL PATTERNS:**
- **High Pressing**: Aggressive pressure on opponents
- **Possession Play**: Ball retention and build-up
- **Counter-Attacking**: Quick transitions to attack
- **Defensive Block**: Compact defensive organization
- **Wing Play**: Attacking down the flanks
- **Central Control**: Midfield dominance

**IMPORTANT:**
- Be precise with formation identification
- Note tactical patterns and strategies
- Identify key players and their roles
- Analyze team shapes and positioning
- Focus on football-specific tactical concepts

Analyze the video clip and provide a complete tactical formation analysis.
"""
    
    def analyze_clip(self, clip_path: str, clip_number: int) -> Dict[str, Any]:
        """Analyze a single football clip for formations"""
        try:
            logger.info(f"Analyzing formations in clip {clip_number:03d}: {Path(clip_path).name}")
            
            # Generate prompt
            prompt = self.get_formation_analysis_prompt(clip_path, clip_number)
            
            # Read video file
            with open(clip_path, 'rb') as video_file:
                video_data = video_file.read()
            
            # Call Gemini API
            response = self.model.generate_content([prompt, video_data])
            
            # Parse response
            analysis_text = response.text
            
            # Save individual clip analysis
            output_filename = f"formation_analysis_{clip_number:03d}.txt"
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w') as f:
                f.write(analysis_text)
            
            # Save JSON version
            json_filename = f"formation_analysis_{clip_number:03d}.json"
            json_path = self.output_dir / json_filename
            
            analysis_data = {
                "clip_number": clip_number,
                "clip_path": str(clip_path),
                "analysis": analysis_text,
                "timestamp": datetime.now().isoformat(),
                "api_model": API_SETTINGS["tactical_model"]
            }
            
            with open(json_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            # Update statistics
            self.stats["clips_processed"] += 1
            self.stats["api_calls"] += 1
            
            logger.info(f"✅ Clip {clip_number:03d} formation analysis complete")
            
            return {
                "success": True,
                "clip_number": clip_number,
                "analysis": analysis_text,
                "output_path": str(output_path),
                "json_path": str(json_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing formations in clip {clip_number:03d}: {e}")
            self.stats["errors"] += 1
            
            return {
                "success": False,
                "clip_number": clip_number,
                "error": str(e)
            }
    
    def analyze_all_clips(self, clips_dir: str) -> List[Dict[str, Any]]:
        """Analyze all football clips for formations"""
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
        
        logger.info(f"Found {len(clip_files)} clips for formation analysis")
        
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
            "api_model": API_SETTINGS["tactical_model"],
            "football_formations": FOOTBALL_SETTINGS["formations"]
        }
        
        stats_path = self.output_dir / "formation_analysis_statistics.json"
        with open(stats_path, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        logger.info(f"📊 Formation analysis complete: {len(successful_results)}/{len(results)} clips successful")
        logger.info(f"📈 Statistics saved: {stats_path}")

def main():
    """Main function for football formation analysis"""
    analyzer = FootballFormationAnalyzer()
    
    # Analyze clips from the processed directory
    clips_dir = PATHS["processed_clips"]
    
    print("🏟️ Football Formation Analysis")
    print("=" * 30)
    print(f"Analyzing clips from: {clips_dir}")
    print(f"Output directory: {PATHS['tactical_output']}")
    print()
    
    # Run analysis
    results = analyzer.analyze_all_clips(str(clips_dir))
    
    if results:
        successful = len([r for r in results if r["success"]])
        print(f"\n✅ Formation analysis complete: {successful}/{len(results)} clips successful")
        print(f"📁 Results saved in: {PATHS['tactical_output']}")
    else:
        print("\n❌ No clips were analyzed successfully")

if __name__ == "__main__":
    main() 