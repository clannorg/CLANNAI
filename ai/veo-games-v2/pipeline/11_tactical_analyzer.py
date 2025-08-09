#!/usr/bin/env python3
"""
11. Tactical Analysis Generator for v2 Pipeline
Generates tactical analysis in webapp-compatible JSON format
"""

import sys
import os
import json
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from multiple locations
env_paths = [
    Path('.env'),
    Path('../.env'), 
    Path('../../.env'),
    Path('/home/ubuntu/CLANNAI/.env'),
    Path('/home/ubuntu/CLANNAI/ai/.env')
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔑 Loaded environment from: {env_path}")
        break

class TacticalAnalyzer:
    def __init__(self):
        """Initialize the tactical analyzer with Gemini"""
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        print("🧠 Tactical Analyzer initialized with Gemini 2.5 Pro")

    def get_tactical_prompt(self, team_color: str, team_type: str = "team") -> str:
        """Generate tactical analysis prompt"""
        # Map Red team to Black/White for analysis
        actual_team = "Black/White" if team_color == "Red" else team_color
        return f"""You are an elite football tactical analyst providing coaching insights for the {actual_team} {team_type}.

Analyze the match timeline and provide comprehensive tactical insights in this EXACT JSON format:

{{
  "tactical_analysis": {{
    "{team_color.lower()}_team": {{
      "strengths": [
        {{
          "title": "Strength Name",
          "description": "Detailed explanation with timeline evidence",
          "evidence": ["Timestamp quotes from timeline"],
          "coaching_tip": "Specific instruction to maintain this"
        }}
      ],
      "weaknesses": [
        {{
          "title": "Weakness Name", 
          "description": "Detailed explanation with timeline evidence",
          "evidence": ["Timestamp quotes from timeline"],
          "improvement": "Specific coaching fix"
        }}
      ],
      "key_players": [
        {{
          "impact": "Player role/contribution",
          "evidence": "Timeline evidence"
        }}
      ],
      "formation_analysis": {{
        "observed_formation": "Best guess formation",
        "effectiveness": "How well it worked",
        "adjustments": "Suggested changes"
      }},
      "set_pieces": {{
        "attacking": "Corners, free kicks effectiveness",
        "defending": "Defensive set piece analysis"
      }},
      "transitions": {{
        "attack_to_defense": "How they defend after losing ball",
        "defense_to_attack": "How they counter-attack"
      }}
    }}
  }},
  "match_overview": {{
    "final_score": "X-X (best guess from timeline)",
    "match_summary": "Brief 2-3 sentence match summary",
    "key_moments": [
      {{
        "timestamp": "Time in match",
        "event": "What happened",
        "significance": "Why it mattered"
      }}
    ],
    "tempo_analysis": "Overall pace and style of play"
  }},
  "manager_recommendations": {{
    "immediate_fixes": [
      "Specific tactical adjustment for next game"
    ],
    "training_focus": [
      "Key areas to work on in training"
    ],
    "player_development": [
      "Individual player improvements needed"
    ]
  }}
}}

CRITICAL REQUIREMENTS:
1. Base ALL analysis on actual timeline evidence - quote specific events
2. Use {team_color} team perspective throughout
3. Be specific and actionable for coaches
4. Include timestamps where possible
5. Focus on tactical patterns, not just individual events
6. Provide concrete coaching recommendations

Return ONLY the JSON - no other text."""

    def analyze_team_tactics(self, match_id: str, timeline_content: str, team_color: str) -> dict:
        """Generate tactical analysis for a specific team"""
        print(f"🔍 Analyzing {team_color} team tactics...")
        
        # Truncate timeline if too long (keep first 50k chars)
        if len(timeline_content) > 50000:
            timeline_sample = timeline_content[:50000] + "\n...(timeline truncated for analysis)"
            print(f"📝 Using timeline sample: {len(timeline_sample)} characters")
        else:
            timeline_sample = timeline_content
        
        prompt = self.get_tactical_prompt(team_color)
        full_prompt = f"{prompt}\n\nMATCH TIMELINE:\n{timeline_sample}"
        
        try:
            response = self.model.generate_content(full_prompt)
            
            if not response.text or response.text.strip() == "":
                print(f"❌ Empty response for {team_color} team")
                return {}
            
            # Clean up response text
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            result = json.loads(response_text)
            print(f"✅ {team_color} team analysis complete")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse {team_color} team JSON: {e}")
            print(f"🔍 Response text: {response.text[:200]}...")
            return {}
        except Exception as e:
            print(f"❌ Error analyzing {team_color} team: {e}")
            return {}

    def generate_tactical_analysis(self, match_id: str) -> bool:
        """Generate complete tactical analysis for the match"""
        print(f"🎯 Starting tactical analysis for {match_id}")
        
        data_dir = Path("../outputs") / match_id
        
        # Read timeline
        timeline_path = data_dir / "5_complete_timeline.txt"
        if not timeline_path.exists():
            print(f"❌ Timeline not found: {timeline_path}")
            return False
            
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline_content = f.read()
        
        print(f"📖 Loaded timeline: {len(timeline_content)} characters")
        
        # Analyze both teams (Blue vs Red for webapp compatibility)
        blue_analysis = self.analyze_team_tactics(match_id, timeline_content, "Blue")
        red_analysis = self.analyze_team_tactics(match_id, timeline_content, "Red")
        
        # Combine analyses into webapp format
        combined_analysis = {
            "tactical_analysis": {},
            "match_overview": {},
            "manager_recommendations": {}
        }
        
        # Add team analyses
        if blue_analysis.get("tactical_analysis"):
            combined_analysis["tactical_analysis"].update(blue_analysis["tactical_analysis"])
        if red_analysis.get("tactical_analysis"):
            combined_analysis["tactical_analysis"].update(red_analysis["tactical_analysis"])
            
        # Use the Red team analysis as primary (Black/White team renamed to Red for webapp)
        if red_analysis.get("match_overview"):
            combined_analysis["match_overview"] = red_analysis["match_overview"]
        elif blue_analysis.get("match_overview"):
            combined_analysis["match_overview"] = blue_analysis["match_overview"]
            
        # Combine recommendations (Red team = Black/White team)
        blue_recs = blue_analysis.get("manager_recommendations", {})
        red_recs = red_analysis.get("manager_recommendations", {})
        
        combined_analysis["manager_recommendations"] = {
            "blue_team": blue_recs,
            "red_team": red_recs,
            "general": {
                "match_summary": "Tactical analysis for Blue vs Red teams (Red = Black/White)",
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # Save tactical analysis
        output_path = data_dir / "11_tactical_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_analysis, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Tactical analysis saved: {output_path}")
        print(f"📊 Teams analyzed: {list(combined_analysis['tactical_analysis'].keys())}")
        print(f"🔄 Note: Red team = Black/White team for webapp compatibility")
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 11_tactical_analyzer.py <match_id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        analyzer = TacticalAnalyzer()
        success = analyzer.generate_tactical_analysis(match_id)
        
        if success:
            print("🎉 Tactical analysis generation completed!")
        else:
            print("❌ Tactical analysis generation failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()