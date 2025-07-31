#!/usr/bin/env python3
"""
5.0 Goals and Shots Synthesis  
Uses Gemini 2.5 Pro to extract precise timing for goals and shots from detailed clip analyses
Parses exact timestamps from enhanced AI analysis (e.g. "10s: goal", "6s: shot saved")
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GoalsAndShotsSynthesizer:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for precise goals and shots extraction"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use 2.5 Pro for intelligent synthesis
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def get_goals_and_shots_prompt(self, clip_analyses: list) -> str:
        """Generate prompt for precise goals and shots extraction"""
        
        # Combine all clip analyses into one context with precise timing
        all_clips_text = ""
        for i, analysis in enumerate(clip_analyses):
            clip_time = analysis['start_seconds']
            minutes = clip_time // 60
            seconds = clip_time % 60
            timestamp = f"{minutes:02.0f}:{seconds:02.0f}"
            
            all_clips_text += f"\n--- CLIP {i+1} (starts at {timestamp}, ends at {minutes:02.0f}:{(seconds+15)%60:02.0f}) ---\n"
            all_clips_text += analysis['events_analysis']
            all_clips_text += "\n"
        
        return f"""
⚽🎯 PRECISE GOALS AND SHOTS EXTRACTION
=====================================

You are analyzing detailed football clip analyses to extract PRECISE timing for goals and shots.

Each clip shows 15 seconds of footage. The AI analysis includes detailed timing like:
- "10s: The shot beats the goalkeeper and goes into the net for a goal"
- "6s: Shot saved by goalkeeper"  
- "8s: Ball sails over goalkeeper into the net"

🎯 YOUR MISSION: Extract ALL shooting events with PRECISE timestamps

📊 EXTRACT THESE EVENTS:

1. **GOALS** - Ball crosses goal line successfully
   - Look for: "goal", "scores", "ball crosses line", "into the net", "finds the net"
   - Parse timing: "10s: goal" = 10 seconds into that clip

2. **SHOTS SAVED** - Goalkeeper stops the shot
   - Look for: "save", "saved by goalkeeper", "keeper stops", "parried"
   - Parse timing: "6s: shot saved" = 6 seconds into that clip

3. **SHOTS MISSED** - Shot goes wide, over, or hits post
   - Look for: "wide", "over", "misses", "hits post", "off target"
   - Parse timing: "8s: shot goes wide" = 8 seconds into that clip

4. **SHOTS BLOCKED** - Defender blocks the shot
   - Look for: "blocked", "deflected", "defender blocks"
   - Parse timing: "5s: shot blocked" = 5 seconds into that clip

🔢 PRECISE TIMESTAMP CALCULATION:
- Clip starts at X seconds
- Event happens at Y seconds into clip  
- Precise timestamp = X + Y seconds
- Convert to MM:SS format

Example:
- Clip starts at 780s (13:00)
- "8s: ball sails into the net for a goal"
- Precise timestamp = 780 + 8 = 788 seconds = 13:08

🔍 CLIP ANALYSES TO PARSE:
{all_clips_text}

📤 OUTPUT FORMAT (JSON):
{{
  "goals": [
    {{
      "precise_timestamp": "13:08",
      "precise_seconds": 788,
      "team": "Red Team",
      "description": "Long-range shot beats goalkeeper into top corner",
      "clip_start_time": "13:00", 
      "event_timing_in_clip": "8s",
      "evidence": "8s: ball sails over goalkeeper into the net",
      "source_clip": "clip_13m00s.mp4",
      "confidence": "HIGH"
    }}
  ],
  "shots_saved": [
    {{
      "precise_timestamp": "07:22",
      "precise_seconds": 442,
      "team": "Black Team",
      "description": "Close-range shot saved by goalkeeper",
      "clip_start_time": "07:15",
      "event_timing_in_clip": "7s", 
      "evidence": "7s: goalkeeper makes save",
      "source_clip": "clip_07m15s.mp4",
      "confidence": "HIGH"
    }}
  ],
  "shots_missed": [
    {{
      "precise_timestamp": "03:45",
      "precise_seconds": 225,
      "team": "Red Team", 
      "description": "Shot from penalty area goes wide",
      "clip_start_time": "03:30",
      "event_timing_in_clip": "15s",
      "evidence": "15s: shot goes wide of goal",
      "source_clip": "clip_03m30s.mp4",
      "confidence": "MEDIUM"
    }}
  ],
  "shots_blocked": [
    {{
      "precise_timestamp": "09:33",
      "precise_seconds": 573,
      "team": "Black Team",
      "description": "Shot blocked by defender",
      "clip_start_time": "09:30",
      "event_timing_in_clip": "3s",
      "evidence": "3s: defender blocks shot",
      "source_clip": "clip_09m30s.mp4", 
      "confidence": "HIGH"
    }}
  ],
  "summary": {{
    "total_goals": 2,
    "total_shots": 8,
    "goals_breakdown": {{"Red Team": 1, "Black Team": 1}},
    "shots_breakdown": {{"saved": 3, "missed": 2, "blocked": 1, "goals": 2}},
    "analysis_method": "Precise timing extraction from enhanced AI clips",
    "time_period_analyzed": "First 15 minutes (0:00-15:00)"
  }}
}}

🚨 CRITICAL INSTRUCTIONS:
- ONLY extract events with clear timing statements (e.g. "8s: goal")
- Calculate precise timestamps accurately (clip_start + event_timing)
- Include team identification (Red/Black based on description)
- HIGH confidence for explicit statements, MEDIUM for inferred
- Better to MISS ambiguous events than create false positives
"""

    def extract_goals_and_shots(self, match_id: str) -> dict:
        """Use Gemini 2.5 Pro to extract precise goals and shots timing"""
        print(f"⚽ Step 5.0: Goals and Shots extraction using Gemini 2.5 Pro for {match_id}")
        
        data_dir = Path("../data") / match_id
        analyses_dir = data_dir / "clip_analyses"
        
        if not analyses_dir.exists():
            print(f"❌ Clip analyses not found: {analyses_dir}")
            return None
        
        # Load all clip analyses
        analysis_files = sorted(list(analyses_dir.glob("*_analysis.json")))
        if not analysis_files:
            print(f"❌ No analysis files found in {analyses_dir}")
            return None
            
        print(f"📊 Loading {len(analysis_files)} clip analyses...")
        
        clip_analyses = []
        for analysis_file in analysis_files:
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
                clip_analyses.append(analysis)
        
        print(f"🎯 Sending to Gemini 2.5 Pro for precise goals and shots extraction...")
        
        # Generate goals and shots extraction prompt
        prompt = self.get_goals_and_shots_prompt(clip_analyses)
        
        try:
            start_time = time.time()
            
            # Call Gemini 2.5 Pro for intelligent analysis
            response = self.model.generate_content(prompt)
            
            processing_time = time.time() - start_time
            
            # Parse the response (should be JSON)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                goals_and_shots_data = json.loads(json_text)
            except json.JSONDecodeError:
                print("⚠️  Response wasn't valid JSON, saving as text")
                goals_and_shots_data = {
                    "raw_analysis": response_text,
                    "processing_note": "Response was text, not JSON"
                }
            
            # Create comprehensive goals and shots analysis
            goals_and_shots_timeline = {
                "match_id": match_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "precise_goals_and_shots_gemini_2.5_pro",
                "clips_analyzed": len(clip_analyses),
                "time_period": "First 15 minutes (0:00-15:00)",
                "processing_time_seconds": processing_time,
                "goals_and_shots_analysis": goals_and_shots_data,
                "source_clips": [analysis['clip_filename'] for analysis in clip_analyses]
            }
            
            # Save goals and shots timeline
            timeline_path = data_dir / "goals_and_shots_timeline.json"
            with open(timeline_path, 'w') as f:
                json.dump(goals_and_shots_timeline, f, indent=2)
            
            print(f"✅ Goals and shots extraction complete!")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            
            # Print summary
            if "goals" in goals_and_shots_data:
                goals = goals_and_shots_data["goals"]
                print(f"⚽ Goals found: {len(goals)}")
                for goal in goals:
                    print(f"   🥅 {goal.get('precise_timestamp', 'Unknown')} - {goal.get('team', 'Unknown team')} - {goal.get('description', 'Goal')}")
            
            if "shots_saved" in goals_and_shots_data:
                saves = goals_and_shots_data["shots_saved"]
                print(f"🧤 Shots saved: {len(saves)}")
                
            if "shots_missed" in goals_and_shots_data:
                misses = goals_and_shots_data["shots_missed"]
                print(f"📤 Shots missed: {len(misses)}")
                
            if "shots_blocked" in goals_and_shots_data:
                blocks = goals_and_shots_data["shots_blocked"]
                print(f"🚫 Shots blocked: {len(blocks)}")
                
            print(f"💾 Saved to: {timeline_path}")
            
            return goals_and_shots_timeline
            
        except Exception as e:
            print(f"❌ Error in goals and shots extraction: {e}")
            return None

def extract_goals_and_shots_from_match(match_id):
    """Main extraction function using precise goals and shots analysis"""
    try:
        synthesizer = GoalsAndShotsSynthesizer()
        result = synthesizer.extract_goals_and_shots(match_id)
        return result is not None
    except ValueError as e:
        print(f"❌ Failed to initialize goals and shots synthesizer: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 5.0-gemini-goals-shots.py <match-id>")
        print("Example: python 5.0-gemini-goals-shots.py ballyclare-20250111")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = extract_goals_and_shots_from_match(match_id)
    
    if success:
        print(f"🎯 Goals and shots analysis complete! Ready for next step.")
    else:
        sys.exit(1) 