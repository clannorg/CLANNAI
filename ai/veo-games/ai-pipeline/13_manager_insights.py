#!/usr/bin/env python3
"""
Manager Insights Generator
Reads AI descriptions, validated goals, and Veo ground truth to provide coaching insights.
"""

import json
import os
import sys
from pathlib import Path
import google.generativeai as genai
from datetime import datetime

class ManagerInsights:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def get_manager_insights_prompt(self) -> str:
        return """You are an elite football manager's tactical analyst. 

Read the match data and provide actionable coaching insights.

## OUTPUT FORMAT:

```json
{
  "match_summary": {
    "key_tactical_story": "What happened tactically in 2-3 sentences",
    "result_factors": ["Factor 1", "Factor 2", "Factor 3"]
  },
  "your_team_analysis": {
    "strengths_to_keep": [
      {
        "area": "Set pieces",
        "evidence": "Scored 2 penalties at 44:04 and 116:35",
        "keep_doing": "Practice penalty routines, maintain composure"
      }
    ],
    "weaknesses_to_fix": [
      {
        "area": "Defensive walls", 
        "evidence": "Conceded free kick goal at 132:13",
        "training_focus": "Wall positioning drills, 30 mins daily"
      }
    ]
  },
  "opposition_analysis": {
    "their_threats": [
      {
        "pattern": "Left wing crosses",
        "evidence": "Goals at 86:39, 129:08 from left side",
        "how_to_defend": "Double up on left winger, cut crossing angles"
      }
    ],
    "their_weaknesses": [
      {
        "vulnerability": "Set piece defending",
        "evidence": "Conceded penalty at 44:04", 
        "how_to_exploit": "Win free kicks in wide areas"
      }
    ]
  },
  "training_priorities": [
    {
      "priority": 1,
      "focus": "Defensive set pieces",
      "drill": "Wall positioning vs free kicks",
      "duration": "20 minutes",
      "measure": "Reduce free kick goals"
    }
  ],
  "next_match_tactics": [
    {
      "if_facing_similar_opponent": "Double mark their left winger",
      "set_piece_focus": "Practice defensive walls daily",
      "attacking_plan": "Target their weak defensive areas"
    }
  ]
}
```

## GUIDELINES:
- Focus on ACTIONABLE insights managers can use
- Use specific timestamps as evidence
- Identify clear patterns from the data
- Give practical training recommendations
- Think about next match preparation
- Be specific about what to do, not just what happened"""

    def generate_insights(self, match_id: str):
        """Generate manager insights from match data"""
        print(f"🎯 Generating manager insights for {match_id}")
        
        # Get base directory
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / match_id
        
        # Read source files
        validated_timeline_path = data_dir / "6_validated_timeline.txt"
        complete_timeline_path = data_dir / "5_complete_timeline.txt"
        veo_ground_truth_path = data_dir / "1_veo_ground_truth.json"
        
        if not all([p.exists() for p in [validated_timeline_path, complete_timeline_path, veo_ground_truth_path]]):
            raise FileNotFoundError("Required files not found")
        
        # Load data
        with open(validated_timeline_path, 'r') as f:
            validated_timeline = f.read()
        
        with open(complete_timeline_path, 'r') as f:
            complete_timeline = f.read()[:8000]  # Limit for tokens
        
        with open(veo_ground_truth_path, 'r') as f:
            veo_data = json.load(f)
        
        # Format Veo ground truth nicely
        veo_events = []
        for event in veo_data.get('events', []):
            timestamp = event.get('timestamp', 'Unknown')
            event_type = event.get('type', 'Unknown')
            team = event.get('team', 'Unknown')
            veo_events.append(f"{timestamp} - {event_type} ({team})")
        
        veo_summary = "\n".join(veo_events[:20])  # First 20 events
        
        # Create analysis prompt
        analysis_prompt = f"""
MANAGER INSIGHTS REQUEST

## MATCH DATA FOR ANALYSIS:

### AI VALIDATED GOALS & SHOTS:
{validated_timeline}

### DETAILED MATCH TIMELINE (8k chars):
{complete_timeline}

### VEO GROUND TRUTH EVENTS:
{veo_summary}

### MATCH CONTEXT:
- Total Veo Events: {len(veo_data.get('events', []))}
- Match Duration: {veo_data.get('duration', 'Unknown')}

---

{self.get_manager_insights_prompt()}
"""
        
        print("🧠 Processing tactical insights...")
        response = self.model.generate_content(analysis_prompt)
        
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Find JSON block
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            insights = json.loads(json_text)
            
            # Add metadata
            insights['match_id'] = match_id
            insights['generated_at'] = datetime.now().isoformat()
            
            return insights
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"🔍 Raw response: {response.text[:500]}...")
            
            # Return error info
            return {
                "match_id": match_id,
                "generated_at": datetime.now().isoformat(),
                "error": f"Failed to parse AI response: {e}",
                "raw_response": response.text[:1000]
            }

    def save_insights(self, match_id: str):
        """Generate and save manager insights"""
        insights = self.generate_insights(match_id)
        
        # Save to file
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / match_id
        output_path = data_dir / "13_manager_insights.json"
        
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Manager insights saved: {output_path}")
        
        # Print summary
        if 'error' not in insights:
            print(f"\n📋 MANAGER INSIGHTS SUMMARY:")
            print(f"🎯 Key Story: {insights.get('match_summary', {}).get('key_tactical_story', 'N/A')}")
            
            strengths = insights.get('your_team_analysis', {}).get('strengths_to_keep', [])
            print(f"💪 Team Strengths: {len(strengths)} identified")
            
            weaknesses = insights.get('your_team_analysis', {}).get('weaknesses_to_fix', [])
            print(f"⚠️  Areas to Fix: {len(weaknesses)} identified")
            
            priorities = insights.get('training_priorities', [])
            print(f"🏃 Training Priorities: {len(priorities)} recommended")
        else:
            print(f"❌ Error in insights: {insights.get('error', 'Unknown error')}")
        
        return output_path

def main():
    if len(sys.argv) != 2:
        print("Usage: python 13_manager_insights.py <match_id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        generator = ManagerInsights()
        generator.save_insights(match_id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()