#!/usr/bin/env python3
"""
Correct Insights Generator
Generates AI insights based on VEO-enhanced events (correct data)
"""

import sys
import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class CorrectInsightsGenerator:
    def __init__(self):
        """Initialize with Gemini AI"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("🧠 Correct Insights Generator initialized")
        print("✅ Using VEO-enhanced events (correct data)")

    def load_enhanced_events(self, data_dir):
        """Load the correct enhanced events"""
        events_path = data_dir / "enhanced_events.json"
        if not events_path.exists():
            print(f"❌ Enhanced events not found: {events_path}")
            return None
            
        with open(events_path, 'r') as f:
            events = json.load(f)
        
        print(f"📊 Enhanced Events Loaded: {len(events)} total events")
        
        # Count event types
        event_counts = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print("📋 Event Breakdown:")
        for event_type, count in sorted(event_counts.items()):
            print(f"   {event_type}: {count}")
        
        return events

    def generate_correct_insights(self, events):
        """Generate tactical insights based on correct events"""
        
        # Count goals
        goals = [e for e in events if e.get('type') == 'goal']
        shots = [e for e in events if e.get('type') == 'shot']
        
        print(f"🎯 Match Facts: {len(goals)} goals, {len(shots)} shots")
        
        prompt = f"""You are generating tactical insights for a football match based on VERIFIED event data.

VERIFIED MATCH EVENTS:
{json.dumps(events, indent=2)}

CONFIRMED MATCH FACTS:
- Total Goals: {len(goals)}
- Total Shots: {len(shots)}
- Total Events: {len(events)}

TASK: Generate comprehensive tactical insights based on this VERIFIED data only.

ANALYSIS GUIDELINES:
1. Use ONLY the events provided - do not infer additional events
2. The goal count is DEFINITIVE - if only 1 goal, then final score is 1-0
3. Base all analysis on actual shot attempts, fouls, cards shown
4. Focus on tactical patterns visible in the event data
5. Identify team strengths and weaknesses from actual events

OUTPUT FORMAT:
{{
  "match_overview": {{
    "final_score": "1-0 or 0-0 based on goal count",
    "total_goals": {len(goals)},
    "total_shots": {len(shots)},
    "key_tactical_story": "Main tactical narrative",
    "winning_team": "team that scored or 'draw' if 0-0"
  }},
  "tactical_analysis": {{
    "red_team": {{
      "strengths": ["strength1", "strength2"],
      "weaknesses": ["weakness1", "weakness2"],
      "shot_accuracy": "analysis based on actual shots"
    }},
    "blue_team": {{
      "strengths": ["strength1", "strength2"], 
      "weaknesses": ["weakness1", "weakness2"],
      "shot_accuracy": "analysis based on actual shots"
    }}
  }},
  "key_moments": [
    {{
      "timestamp": 5548,
      "description": "Goal description",
      "tactical_significance": "Why this moment mattered"
    }}
  ],
  "manager_recommendations": {{
    "red_team": ["rec1", "rec2"],
    "blue_team": ["rec1", "rec2"]
  }}
}}

Be precise and factual. Only analyze what actually happened based on the verified events.
"""

        try:
            response = self.model.generate_content(prompt)
            insights_text = response.text.strip()
            
            # Clean JSON
            if insights_text.startswith('```json'):
                insights_text = insights_text[7:]
            if insights_text.endswith('```'):
                insights_text = insights_text[:-3]
            
            insights = json.loads(insights_text)
            
            print(f"✅ Generated correct tactical insights")
            return insights
            
        except Exception as e:
            print(f"❌ Insights generation failed: {e}")
            return None

    def generate_insights(self, match_id):
        """Main function to generate correct insights"""
        print(f"🎯 Generating correct insights for {match_id}")
        print("=" * 60)
        
        data_dir = Path("../data") / match_id
        if not data_dir.exists():
            print(f"❌ Match data not found: {data_dir}")
            return False
        
        # Load enhanced events
        events = self.load_enhanced_events(data_dir)
        if not events:
            return False
        
        print("\n🔄 Generating correct tactical insights...")
        
        # Generate insights
        insights = self.generate_correct_insights(events)
        if not insights:
            return False
        
        # Save insights
        output_path = data_dir / "correct_insights.json"
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ CORRECT INSIGHTS GENERATED!")
        print("=" * 60)
        
        match_overview = insights.get('match_overview', {})
        print(f"🏆 Final Score: {match_overview.get('final_score', 'Unknown')}")
        print(f"⚽ Goals: {match_overview.get('total_goals', 0)}")
        print(f"🎯 Shots: {match_overview.get('total_shots', 0)}")
        print(f"🎪 Key Story: {match_overview.get('key_tactical_story', 'N/A')[:100]}...")
        
        print(f"\n📁 Correct insights saved to: {output_path}")
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python correct_insights_generator.py <match-id>")
        print("Example: python correct_insights_generator.py 19-20250419")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        generator = CorrectInsightsGenerator()
        success = generator.generate_insights(match_id)
        
        if success:
            print("\n🎉 Correct insights generation completed!")
        else:
            print("\n❌ Insights generation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()