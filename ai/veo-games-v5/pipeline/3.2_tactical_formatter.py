#!/usr/bin/env python3
"""
3.11 Tactical Formatter
Convert plain text tactical analysis into rich JSON format for webapp
"""

import sys
import os
import json
import time
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

def load_env_multisource() -> None:
    """Load environment variables from multiple likely locations"""
    load_dotenv()  # Keep shell environment
    
    candidates = [
        Path(__file__).resolve().parent.parent / '.env',   # ai/footy2/.env
        Path(__file__).resolve().parents[2] / '.env',      # ai/.env
        Path(__file__).resolve().parents[3] / '.env',      # repo root .env
    ]
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            pass

load_env_multisource()

class TacticalFormatter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for tactical analysis conversion"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def convert_tactical_to_json(self, tactical_text: str, summary_text: str, team_config: dict, match_id: str) -> dict:
        """Use Gemini to convert plain text tactical analysis to rich JSON format"""
        
        prompt = f"""Convert this plain text tactical analysis into a rich, structured JSON format for webapp display.

**TEAM MAPPING:**
- Team A: {team_config['team_a']['name']} ({team_config['team_a']['colors']})
- Team B: {team_config['team_b']['name']} ({team_config['team_b']['colors']})

**TACTICAL TEXT:**
{tactical_text}

**SUMMARY TEXT:**
{summary_text}

**REQUIRED JSON FORMAT:**
```json
{{
  "tactical_analysis": {{
    "red_team": {{
      "team_name": "{team_config['team_a']['name']}",
      "strengths": [
        "Detailed strength 1 with specific examples",
        "Detailed strength 2 with tactical context"
      ],
      "weaknesses": [
        "Detailed weakness 1 with specific examples",
        "Detailed weakness 2 with tactical context"
      ],
      "key_players": [
        "Player description with role and impact",
        "Another key player with tactical contribution"
      ],
      "tactical_setup": "Detailed description of team's tactical approach and formation",
      "performance_summary": "Overall assessment of team's performance in this match"
    }},
    "blue_team": {{
      "team_name": "{team_config['team_b']['name']}",
      "strengths": [
        "Detailed strength 1 with specific examples",
        "Detailed strength 2 with tactical context"
      ],
      "weaknesses": [
        "Detailed weakness 1 with specific examples", 
        "Detailed weakness 2 with tactical context"
      ],
      "key_players": [
        "Player description with role and impact",
        "Another key player with tactical contribution"
      ],
      "tactical_setup": "Detailed description of team's tactical approach and formation",
      "performance_summary": "Overall assessment of team's performance in this match"
    }},
    "match_summary": {{
      "final_score": "Extract final score from summary text",
      "match_story": "Compelling narrative of how the match unfolded tactically",
      "key_moments": [
        "Critical tactical moment 1",
        "Critical tactical moment 2",
        "Critical tactical moment 3"
      ],
      "tactical_themes": [
        "Main tactical battle 1",
        "Main tactical battle 2", 
        "Main tactical battle 3"
      ]
    }},
    "recommendations": {{
      "{team_config['team_a']['name'].lower()}": [
        "Specific tactical improvement 1",
        "Specific tactical improvement 2"
      ],
      "{team_config['team_b']['name'].lower()}": [
        "Specific tactical improvement 1", 
        "Specific tactical improvement 2"
      ]
    }}
  }}
}}
```

**CONVERSION RULES:**
- Extract detailed tactical insights from the text
- Provide specific examples and context for each point
- Use team names from config, not jersey colors
- Create compelling narratives that coaches would find valuable
- Focus on tactical patterns, not just individual events
- Make recommendations actionable and specific
- Extract final score from summary text accurately

Convert the tactical analysis to rich JSON format:"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed: {e}")
                return {
                    "tactical_analysis": {
                        "error": "JSON parsing failed",
                        "raw_response": response_text
                    }
                }
                
        except Exception as e:
            print(f"⚠️  Gemini conversion failed: {e}")
            return {
                "tactical_analysis": {
                    "error": f"Conversion failed: {str(e)}"
                }
            }

def main():
    if len(sys.argv) != 2:
        print("Usage: python 3.2_tactical_formatter.py <match-id>")
        print("Example: python 3.2_tactical_formatter.py 20250427-match-apr-27-2025-9bd1cf29")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    # Load required files
    team_config_file = outputs_dir / '1_team_config.json'
    tactical_file = outputs_dir / '2.6_focused_tactical.txt'
    summary_file = outputs_dir / '2.6_focused_summary.txt'
    
    if not team_config_file.exists():
        print(f"❌ Error: Team configuration not found: {team_config_file}")
        sys.exit(1)
    
    if not tactical_file.exists():
        print(f"❌ Error: Focused tactical analysis not found: {tactical_file}")
        print("Run step 2.6 first: python 2.6_focused_events.py <match-id>")
        sys.exit(1)
    
    if not summary_file.exists():
        print(f"❌ Error: Focused summary data not found: {summary_file}")
        print("Run step 2.6 first: python 2.6_focused_events.py <match-id>")
        sys.exit(1)
    
    # Load data
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    with open(tactical_file, 'r') as f:
        tactical_text = f.read()
    
    with open(summary_file, 'r') as f:
        summary_text = f.read()
    
    print(f"🎯 Converting tactical analysis to JSON: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print("=" * 50)
    print("🧠 Using Gemini to convert tactical text to rich JSON...")
    
    # Initialize formatter and convert
    formatter = TacticalFormatter()
    tactical_json = formatter.convert_tactical_to_json(tactical_text, summary_text, team_config, match_id)
    
    # Save tactical JSON file
    tactical_json_file = outputs_dir / '3.2_tactical_analysis.json'
    
    with open(tactical_json_file, 'w') as f:
        json.dump(tactical_json, f, indent=2)
    
    print(f"✅ Tactical JSON formatting complete!")
    print(f"📄 Tactical analysis: {tactical_json_file}")
    
    # Show summary
    if 'tactical_analysis' in tactical_json and 'match_summary' in tactical_json['tactical_analysis']:
        match_summary = tactical_json['tactical_analysis']['match_summary']
        print(f"\n📊 Summary:")
        print(f"   Final score: {match_summary.get('final_score', 'Unknown')}")
        print(f"   Match story: {match_summary.get('match_story', 'N/A')[:100]}...")
        
        if 'tactical_themes' in match_summary:
            print(f"   Tactical themes: {len(match_summary['tactical_themes'])} identified")
    
    print(f"\n🎉 Rich tactical analysis complete!")
    print(f"📁 File saved in: {outputs_dir}")

if __name__ == "__main__":
    main()
