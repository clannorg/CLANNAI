#!/usr/bin/env python3
"""
Model Timeline Synthesis with ULTRA-STRICT Goal Detection
Uses proper kickoff validation logic from original pipeline
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

class ModelTimelineSynthesis:
    def __init__(self, model_name):
        """Initialize with specified Gemini model for synthesis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        # Use 2.5-pro for synthesis (best at validation logic)
        self.synthesis_model = genai.GenerativeModel('gemini-2.5-pro')
        
    def load_clip_analyses(self, match_id):
        """Load all clip analyses for this model"""
        results_dir = Path("../results") / match_id / self.model_name
        analyses_dir = results_dir / "clip_analyses"
        
        if not analyses_dir.exists():
            raise FileNotFoundError(f"Clip analyses not found: {analyses_dir}")
        
        analyses = []
        analysis_files = sorted(analyses_dir.glob("*.json"))
        
        for file_path in analysis_files:
            with open(file_path, 'r') as f:
                analysis = json.load(f)
                if analysis['status'] == 'success':
                    analyses.append(analysis)
        
        # Sort by start time
        analyses.sort(key=lambda x: x['start_seconds'])
        return analyses

    def get_synthesis_prompt(self, analyses):
        """Create synthesis prompt with ULTRA-STRICT validation rules"""
        clips_text = ""
        for i, analysis in enumerate(analyses, 1):
            clips_text += f"\n{i:2d}. {analysis['timestamp']:>6} - {analysis['events_analysis']}"
        
        num_clips = len(analyses)
        time_duration = num_clips * 15 // 60  # Convert to minutes
        
        return f"""
🧠 INTELLIGENT FOOTBALL MATCH SYNTHESIS
=========================================

You are an expert football analyst reviewing {num_clips} clips ({time_duration} minutes) from a match.
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

RULE 4: TEMPORAL VALIDATION
- Cannot have 2 kickoffs within 60 seconds by same team
- Cannot have 2 goals within 30 seconds (extremely rare)
- Check for impossible sequences

📊 YOUR TASKS:

1. **CONSERVATIVE GOAL DETECTION**:
   - Find clips that explicitly state "GOAL" 
   - Check next clip for CENTER CIRCLE kickoff by OPPOSING team
   - REJECT if scoring team takes kickoff (breaks football rules)

2. **EVENT TIMELINE**:
   - Create chronological list of significant events
   - Include: goals, shots, key passes, fouls, cards, corners
   - Filter out routine passes and minor events

3. **CONFIDENCE ASSESSMENT**:
   - HIGH: Explicit "GOAL" statement + opposing team kickoff validation
   - MEDIUM: Clear goal but kickoff issues (flag as suspicious)
   - REJECT: No goal statement OR same team kickoff OR no kickoff found

🔍 CLIP ANALYSES TO SYNTHESIZE:
{clips_text}

📤 OUTPUT FORMAT (JSON):
{{
  "goals_detected": [
    {{
      "timestamp": "2:45",
      "scoring_team": "team in blue jerseys", 
      "description": "Shot from penalty area crosses goal line",
      "confidence": "HIGH",
      "evidence": "Explicit GOAL statement + opposing team kickoff at 2:50",
      "source_clips": ["clip_00m45s.mp4"]
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
      "team": "red team"
    }}
  ],
  "match_summary": "Brief description of match flow and key patterns",
  "data_quality": {{
    "clips_processed": {num_clips},
    "clips_with_issues": 0,
    "overall_confidence": "HIGH/MEDIUM/LOW"
  }}
}}

🎯 BE EXTREMELY CONSERVATIVE WITH GOALS - Better to miss a real goal than accept a false positive!
"""

    def synthesize_timeline(self, match_id):
        """Synthesize clip analyses using proper validation logic"""
        print(f"🧠 ULTRA-STRICT Timeline Synthesis: {self.model_name}")
        print(f"📊 Match: {match_id}")
        print("=" * 60)
        
        # Load clip analyses
        try:
            analyses = self.load_clip_analyses(match_id)
            print(f"📋 Loaded {len(analyses)} successful clip analyses")
        except Exception as e:
            print(f"❌ Error loading analyses: {e}")
            return False
        
        if not analyses:
            print("❌ No successful analyses found")
            return False
        
        # Create synthesis prompt with validation rules
        prompt = self.get_synthesis_prompt(analyses)
        
        try:
            print("🧠 Applying ULTRA-STRICT validation with gemini-2.5-pro...")
            start_time = time.time()
            
            response = self.synthesis_model.generate_content(prompt)
            synthesis_time = time.time() - start_time
            
            print(f"✅ Validation complete in {synthesis_time:.1f} seconds")
            
            # Parse JSON response
            try:
                # Clean up response text
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "")
                
                timeline_data = json.loads(response_text)
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}")
                # Create fallback structure
                timeline_data = {
                    "goals_detected": [],
                    "rejected_false_positives": [],
                    "key_events": [],
                    "match_summary": "Synthesis completed but JSON parsing failed",
                    "raw_response": response.text.strip(),
                    "data_quality": {
                        "clips_processed": len(analyses),
                        "clips_with_issues": 0,
                        "overall_confidence": "UNKNOWN"
                    }
                }
            
            # Add metadata
            timeline_data["metadata"] = {
                "model_used_for_clips": self.model_name,
                "synthesis_model": "gemini-2.5-pro",
                "validation_rules": "ULTRA-STRICT with kickoff validation",
                "clips_analyzed": len(analyses),
                "time_range": f"{analyses[0]['timestamp']} - {analyses[-1]['timestamp']}",
                "synthesis_timestamp": datetime.now().isoformat(),
                "synthesis_time_seconds": synthesis_time
            }
            
            # Save timeline
            results_dir = Path("../results") / match_id / self.model_name
            timeline_path = results_dir / "validated_timeline.json"
            
            with open(timeline_path, 'w') as f:
                json.dump(timeline_data, f, indent=2)
            
            print(f"💾 Validated timeline saved: {timeline_path}")
            
            # Print results summary
            print("\n🎯 VALIDATION RESULTS:")
            print("=" * 50)
            
            goals = timeline_data.get("goals_detected", [])
            rejected = timeline_data.get("rejected_false_positives", [])
            events = timeline_data.get("key_events", [])
            
            print(f"✅ Goals Detected: {len(goals)}")
            for goal in goals:
                confidence = goal.get('confidence', 'UNKNOWN')
                timestamp = goal.get('timestamp', 'N/A')
                team = goal.get('scoring_team', 'Unknown team')
                print(f"  {timestamp} - {team} ({confidence} confidence)")
            
            if rejected:
                print(f"\n❌ Rejected False Positives: {len(rejected)}")
                for reject in rejected[:3]:  # Show first 3
                    timestamp = reject.get('timestamp', 'N/A')
                    reason = reject.get('reason', 'No reason given')
                    print(f"  {timestamp} - {reason}")
            
            print(f"\n📋 Key Events: {len(events)}")
            for event in events[:5]:  # Show first 5
                timestamp = event.get('timestamp', 'N/A')
                event_type = event.get('type', 'event')
                description = event.get('description', 'No description')
                print(f"  {timestamp} - {event_type}: {description[:50]}...")
            
            data_quality = timeline_data.get("data_quality", {})
            confidence = data_quality.get("overall_confidence", "UNKNOWN")
            print(f"\n🔍 Overall Confidence: {confidence}")
            
            return True
            
        except Exception as e:
            print(f"❌ Synthesis failed: {e}")
            return False

def run_synthesis(model_name, match_id):
    """Run validated timeline synthesis for specified model"""
    synthesizer = ModelTimelineSynthesis(model_name)
    
    try:
        success = synthesizer.synthesize_timeline(match_id)
        if success:
            print(f"\n🎯 ULTRA-STRICT timeline synthesis complete for {model_name}!")
            print(f"📁 Results: ../results/{match_id}/{model_name}/validated_timeline.json")
        return success
    except Exception as e:
        print(f"❌ Synthesis failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python synthesis.py <model-name> <match-id>")
        print("Example: python synthesis.py gemini-2.5-flash ballyclare-20250111")
        print("\nAvailable models:")
        print("  - gemini-2.5-flash")
        print("  - gemini-2.5-pro") 
        print("  - gemini-2.0-flash")
        print("  - gemini-1.5-pro")
        print("  - gemini-1.5-flash")
        sys.exit(1)
    
    model_name = sys.argv[1]
    match_id = sys.argv[2]
    
    success = run_synthesis(model_name, match_id)
    
    if not success:
        sys.exit(1) 