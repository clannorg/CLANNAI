#!/usr/bin/env python3
"""
5. Intelligent Gemini Synthesis
Uses Gemini 2.5 Pro to intelligently synthesize all clip analyses into match timeline
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

class IntelligentMatchSynthesizer:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for intelligent synthesis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use 2.5 Pro for intelligent synthesis
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def get_intelligent_synthesis_prompt(self, clip_analyses: list) -> str:
        """Generate prompt for intelligent match synthesis"""
        
        # Combine all clip analyses into one context
        all_clips_text = ""
        for i, analysis in enumerate(clip_analyses):
            clip_time = analysis['start_seconds']
            minutes = clip_time // 60
            seconds = clip_time % 60
            timestamp = f"{minutes:02.0f}:{seconds:02.0f}"
            
            all_clips_text += f"\n--- CLIP {i+1} ({timestamp} - {timestamp}) ---\n"
            all_clips_text += analysis['events_analysis']
            all_clips_text += "\n"
        
        return f"""
🧠 INTELLIGENT FOOTBALL MATCH SYNTHESIS
=========================================

You are an expert football analyst reviewing 52 clips (13 minutes) from a match.
Each clip below shows 15 seconds of footage with AI analysis.

🚨 ULTRA-STRICT GOAL DETECTION (NO FALSE POSITIVES):

RULE 1: ONLY count as goal if clip explicitly says "GOAL", "SCORES", "BALL CROSSES LINE"
- NOT: "shot", "save", "celebration", "close attempt"
- Must be CLEAR goal statement

RULE 2: KICKOFF VALIDATION REQUIRED
- Real goal MUST be followed by kickoff at CENTER CIRCLE
- Opposing team takes kickoff (NOT the scoring team)
- No kickoff = NO GOAL (was probably saved/missed)

RULE 3: LOGICAL VALIDATION
- If RED scores → BLACK takes kickoff
- If BLACK scores → RED takes kickoff  
- Same team kickoff = CONTRADICTION = NOT A GOAL

RULE 4: TEMPORAL VALIDATION (NEW!)
- Cannot have 2 kickoffs within 60 seconds by same team
- Cannot have 2 goals within 30 seconds (extremely rare)
- Check for impossible sequences (kickoff at 5:45 + goal at 6:00 = suspicious)

📊 YOUR TASKS:

1. **CONSERVATIVE GOAL DETECTION**:
   - Find clips that explicitly state "GOAL" 
   - Check next clip for CENTER CIRCLE kickoff by OPPOSING team
   - REJECT if scoring team takes kickoff (breaks football rules)

2. **EVENT TIMELINE** (Priority #2):
   - Create chronological list of significant events
   - Include: goals, shots, key passes, fouls, cards, corners
   - Filter out routine passes and minor events

3. **TEAM ANALYSIS** (Priority #3):
   - Identify which team scored (jersey colors, field position)
   - Track possession changes and attacking patterns

4. **CONFIDENCE ASSESSMENT**:
   - HIGH: Explicit "GOAL" statement + opposing team kickoff validation
   - MEDIUM: Clear goal but kickoff issues (flag as suspicious)
   - REJECT: No goal statement OR same team kickoff OR no kickoff found

🔍 CLIP ANALYSES TO SYNTHESIZE:
{all_clips_text}

📤 OUTPUT FORMAT (JSON):
{{
  "goals_detected": [
    {{
      "timestamp": "2:45",
      "scoring_team": "team in blue jerseys", 
      "description": "Shot from penalty area crosses goal line",
      "confidence": "HIGH",
      "evidence": "Explicit GOAL statement + opposing team kickoff at 2:50",
      "source_clips": ["clip_0011", "clip_0012"]
    }}
  ],
  "rejected_false_positives": [
    {{
      "timestamp": "4:45",
      "reason": "Scoring team took kickoff - violates football rules",
      "original_description": "Shot from free kick"
    }}
  ],
  "key_events": [
    {{
      "timestamp": "1:23", 
      "type": "shot",
      "description": "Long range shot saved by goalkeeper",
      "confidence": "HIGH"
    }}
  ],
  "match_summary": {{
    "total_real_goals": 2,
    "total_false_positives_rejected": 6,
    "validation_method": "Ultra-strict detection with kickoff validation",
    "key_moments": ["Only kickoff-validated goals included"],
    "possession_flow": "Even possession with dangerous attacks from both teams"
  }},
  "kickoff_analysis": [
    {{
      "kickoff_time": "2:50",
      "inferred_goal_time": "2:45", 
      "evidence": "Teams lined up after celebration"
    }}
  ]
}}

🚨 CRITICAL REMINDER: 
- REJECT if no explicit "GOAL" statement  
- REJECT if same team takes kickoff (rule violation)
- REJECT if kickoffs too close together (impossible timing)
- REJECT if multiple goals within 30 seconds (extremely rare)
- BETTER TO MISS than create FALSE POSITIVES
- Conservative detection = accurate results!
"""

    def synthesize_intelligently(self, match_id: str) -> dict:
        """Use Gemini 2.5 Pro to intelligently synthesize match timeline"""
        print(f"🧠 Step 5: Intelligent synthesis using Gemini 2.5 Pro for {match_id}")
        
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
        
        print(f"🚀 Sending to Gemini 2.5 Pro for intelligent synthesis...")
        
        # Generate intelligent synthesis prompt
        prompt = self.get_intelligent_synthesis_prompt(clip_analyses)
        
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
                intelligent_analysis = json.loads(json_text)
            except json.JSONDecodeError:
                print("⚠️  Response wasn't valid JSON, saving as text")
                intelligent_analysis = {
                    "raw_analysis": response_text,
                    "processing_note": "Response was text, not JSON"
                }
            
            # Create comprehensive timeline
            match_timeline = {
                "match_id": match_id,
                "synthesis_timestamp": datetime.now().isoformat(),
                "synthesis_method": "intelligent_gemini_2.5_pro",
                "clips_analyzed": len(clip_analyses),
                "processing_time_seconds": processing_time,
                "intelligent_analysis": intelligent_analysis,
                "source_clips": [f"clip_{i+4:04d}" for i in range(len(clip_analyses))]  # Starting from 0004
            }
            
            # Save match timeline
            timeline_path = data_dir / "intelligent_match_timeline.json"
            with open(timeline_path, 'w') as f:
                json.dump(match_timeline, f, indent=2)
            
            print(f"✅ Intelligent synthesis complete!")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            
            # Print summary
            if "goals_detected" in intelligent_analysis:
                goals = intelligent_analysis["goals_detected"]
                print(f"⚽ Goals detected: {len(goals)}")
                for goal in goals:
                    print(f"   🥅 {goal.get('timestamp', 'Unknown')} - {goal.get('description', 'Goal')}")
            
            if "key_events" in intelligent_analysis:
                events = intelligent_analysis["key_events"]
                print(f"📊 Key events: {len(events)}")
                
            print(f"💾 Saved to: {timeline_path}")
            
            return match_timeline
            
        except Exception as e:
            print(f"❌ Error in intelligent synthesis: {e}")
            return None

def synthesize_match(match_id):
    """Main synthesis function using intelligent analysis"""
    try:
        synthesizer = IntelligentMatchSynthesizer()
        result = synthesizer.synthesize_intelligently(match_id)
        return result is not None
    except ValueError as e:
        print(f"❌ Failed to initialize synthesizer: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 5_gemini_synthesis.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = synthesize_match(match_id)
    
    if success:
        print(f"🎯 Ready for Step 6: Web formatting")
    else:
        sys.exit(1) 