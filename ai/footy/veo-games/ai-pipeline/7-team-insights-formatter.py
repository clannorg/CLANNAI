#!/usr/bin/env python3
"""
7. Team Insights Formatter - Digestible Intelligence
Creates clean team summary cards that flex AI intelligence for web display
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

class TeamInsightsFormatter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for intelligent team summaries"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def create_team_insights(self, match_id: str) -> bool:
        """Create digestible team insights that flex AI intelligence"""
        print(f"🏆 Creating team insights summary for {match_id}")
        
        data_dir = Path("../data") / match_id
        
        # Load tactical insights
        tactical_path = data_dir / "tactical_coaching_insights.json"
        timeline_path = data_dir / "intelligent_match_timeline.json"
        
        if not tactical_path.exists():
            print(f"❌ Tactical insights not found: {tactical_path}")
            return False
        
        # Load data
        with open(tactical_path, 'r') as f:
            tactical_data = json.load(f)
        
        timeline_data = {}
        if timeline_path.exists():
            with open(timeline_path, 'r') as f:
                timeline_data = json.load(f)
        
        # Create insights prompt
        prompt = self.create_insights_prompt(tactical_data, timeline_data)
        
        try:
            print("🧠 Generating digestible team insights with Gemini 2.5 Pro...")
            start_time = time.time()
            
            response = self.model.generate_content(prompt)
            processing_time = time.time() - start_time
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                team_insights = json.loads(json_text)
            except json.JSONDecodeError:
                print("⚠️  Response wasn't valid JSON, saving as text")
                team_insights = {
                    "error": "Could not parse JSON",
                    "raw_response": response_text
                }
            
            # Save team insights
            output_path = data_dir / "team_insights_summary.json"
            with open(output_path, 'w') as f:
                json.dump(team_insights, f, indent=2)
            
            print(f"✅ Team insights created successfully!")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            print(f"💾 Saved to: {output_path}")
            
            # Preview the insights
            if "red_team" in team_insights and "black_team" in team_insights:
                print(f"\n🔴 RED TEAM PREVIEW:")
                red = team_insights["red_team"]
                print(f"   💪 Strength: {red.get('top_strength', 'N/A')}")
                print(f"   ⚠️  Weakness: {red.get('top_weakness', 'N/A')}")
                print(f"   🎯 Style: {red.get('play_style', 'N/A')}")
                
                print(f"\n⚫ BLACK TEAM PREVIEW:")
                black = team_insights["black_team"]
                print(f"   💪 Strength: {black.get('top_strength', 'N/A')}")
                print(f"   ⚠️  Weakness: {black.get('top_weakness', 'N/A')}")
                print(f"   🎯 Style: {black.get('play_style', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating team insights: {e}")
            return False

    def create_insights_prompt(self, tactical_data: dict, timeline_data: dict) -> str:
        """Create prompt for digestible team insights"""
        
        return f"""
🏆 CREATE DIGESTIBLE TEAM INSIGHTS FOR WEB DISPLAY

You are creating clean, professional team summary cards that showcase AI intelligence for coaches.

TACTICAL DATA:
{json.dumps(tactical_data, indent=2)}

TIMELINE DATA:
{json.dumps(timeline_data.get('match_summary', {}), indent=2)[:1000]}...

🎯 OUTPUT FORMAT - CLEAN TEAM CARDS:

```json
{
  "match_summary": {
    "time_analyzed": "First 15 minutes", 
    "ai_intelligence": "Advanced tactical effectiveness analysis",
    "key_insight": "One sentence about the game flow"
  },
  "red_team": {
    "team_name": "Red Team",
    "overall_rating": "Strong/Good/Needs Work",
    "top_strength": "One clear strength with data",
    "top_weakness": "One clear weakness with data", 
    "play_style": "Their preferred approach",
    "key_stat": "Most impressive statistic",
    "suggestion": "One specific coaching tip",
    "highlight_moment": "Best moment for this team",
    "areas_to_improve": ["Specific area 1", "Specific area 2"],
    "what_works": "What they should keep doing"
  },
  "black_team": {
    "team_name": "Black Team",
    "overall_rating": "Strong/Good/Needs Work",
    "top_strength": "One clear strength with data",
    "top_weakness": "One clear weakness with data",
    "play_style": "Their preferred approach", 
    "key_stat": "Most impressive statistic",
    "suggestion": "One specific coaching tip",
    "highlight_moment": "Best moment for this team",
    "areas_to_improve": ["Specific area 1", "Specific area 2"],
    "what_works": "What they should keep doing"
  },
  "tactical_comparison": {
    "attacking_effectiveness": "Which team creates better chances",
    "defensive_solidity": "Which team defends better",
    "possession_style": "How teams differ in approach",
    "key_battle": "Main tactical battle in the game"
  },
  "coaching_insights": [
    "AI-powered insight 1 that shows intelligence",
    "AI-powered insight 2 that coaches love",
    "AI-powered insight 3 that beats VEO"
  ]
}
```

📋 REQUIREMENTS:

1. **Be Specific with Data**: "31 successful attacks" not "good attacking"
2. **Actionable Advice**: "Work on ball retention in midfield" not "improve possession" 
3. **Show AI Intelligence**: Reference specific moments, patterns, ratios
4. **Coach-Friendly Language**: Professional but accessible
5. **Flex Over VEO**: Show depth VEO can't provide

📊 KEY METRICS TO HIGHLIGHT:
- Turnover ratios (1.75 vs 0.57)
- Attack effectiveness (31 vs 40 instances)
- Play style frequency (Direct play 19 times)
- Specific weaknesses (10 turnover patterns)

🎯 TONE: Professional analyst who has watched the game closely and provides insights a coach would pay for.

Create the team insights summary now:
"""

def main():
    """Create team insights summary for a match"""
    if len(sys.argv) != 2:
        print("Usage: python 7-team-insights-formatter.py <match-id>")
        print("Example: python 7-team-insights-formatter.py ballyclare-20250111")
        return
    
    match_id = sys.argv[1]
    formatter = TeamInsightsFormatter()
    success = formatter.create_team_insights(match_id)
    
    if success:
        print(f"🎯 Team insights ready for web display!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()