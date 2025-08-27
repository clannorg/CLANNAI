#!/usr/bin/env python3
"""
4.6. Convert Tactical Analysis to JSON
Convert our amazing plain text tactical analysis to webapp-compatible JSON format
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
        Path(__file__).resolve().parent.parent / '.env',  # ai/footy2/.env
        Path(__file__).resolve().parents[2] / '.env',     # ai/.env
        Path(__file__).resolve().parents[3] / '.env',     # repo root .env
    ]
    
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            pass

load_env_multisource()

class TacticalJSONConverter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for JSON conversion"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def get_conversion_prompt(self, team_config: dict) -> str:
        """Generate prompt to convert tactical analysis to webapp JSON format"""
        team_a_name = team_config['team_a']['name']
        team_b_name = team_config['team_b']['name']
        
        return f"""Convert this detailed tactical analysis into the exact JSON format required by the ClannAI webapp.

**TEAM MAPPING:**
- Team A: {team_a_name} → "red_team" in JSON
- Team B: {team_b_name} → "blue_team" in JSON

**REQUIRED JSON STRUCTURE:**
```json
{{
  "tactical_analysis": {{
    "red_team": {{
      "team_name": "{team_a_name}",
      "strengths": [
        "Strength 1 extracted from analysis",
        "Strength 2 extracted from analysis"
      ],
      "weaknesses": [
        "Weakness 1 extracted from analysis", 
        "Weakness 2 extracted from analysis"
      ],
      "key_players": [
        "Player description: Role and impact",
        "Player description: Role and impact"
      ],
      "tactical_setup": "Formation and tactical approach summary",
      "performance_summary": "Overall performance paragraph"
    }},
    "blue_team": {{
      "team_name": "{team_b_name}",
      "strengths": ["Extracted strengths"],
      "weaknesses": ["Extracted weaknesses"],
      "key_players": ["Player descriptions"],
      "tactical_setup": "Formation and approach",
      "performance_summary": "Performance summary"
    }}
  }},
  "match_overview": {{
    "final_score": "Team A X - Y Team B",
    "key_tactical_story": "Main tactical narrative from analysis"
  }},
  "key_moments": [
    "Turning point 1 with timestamp",
    "Turning point 2 with timestamp"
  ],
  "manager_recommendations": {{
    "red_team": [
      "Recommendation 1 for {team_a_name}",
      "Recommendation 2 for {team_a_name}"
    ],
    "blue_team": [
      "Recommendation 1 for {team_b_name}",
      "Recommendation 2 for {team_b_name}"
    ]
  }}
}}
```

**EXTRACTION RULES:**
1. **Strengths/Weaknesses**: Extract from the tactical analysis sections
2. **Key Players**: Use player descriptions from analysis (e.g., "Tall player: Central role, high impact")
3. **Tactical Setup**: Summarize formation and approach from analysis
4. **Performance Summary**: Condense team performance into 1-2 sentences
5. **Key Moments**: Extract turning points with timestamps from analysis
6. **Manager Recommendations**: Extract coaching insights from analysis

**IMPORTANT:**
- Keep the exact JSON structure shown above
- Extract real insights from the analysis, don't make up content
- Use player descriptions from the analysis (physical appearance, role)
- Include timestamps in key moments where available
- Make recommendations actionable and specific

Convert the following tactical analysis to JSON:"""

    def convert_to_json(self, tactical_text: str, team_config: dict) -> dict:
        """Convert tactical analysis text to webapp-compatible JSON"""
        try:
            prompt = self.get_conversion_prompt(team_config)
            
            conversion_input = f"""
{prompt}

**TACTICAL ANALYSIS TO CONVERT:**
{tactical_text}

Convert this to the exact JSON format specified above:"""
            
            print("🔄 Converting tactical analysis to JSON format...")
            
            response = self.model.generate_content(conversion_input)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Find JSON in the response (sometimes wrapped in markdown)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            
            # Parse and validate JSON
            tactical_json = json.loads(json_text)
            
            return tactical_json
            
        except Exception as e:
            return {"error": f"Failed to convert tactical analysis: {str(e)}"}

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4.6_convert_tactical_to_json.py <match-id>")
        print("Example: python 4.6_convert_tactical_to_json.py leo1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    # Check required files exist
    tactical_text_file = outputs_dir / 'tactical_analysis.txt'
    team_config_file = outputs_dir / 'team_config.json'
    
    if not tactical_text_file.exists():
        print(f"❌ Error: Tactical analysis text file not found: {tactical_text_file}")
        print("Run step 4.5 first: python 4.5_tactical_analysis.py <match-id>")
        sys.exit(1)
    
    if not team_config_file.exists():
        print(f"❌ Error: Team config not found: {team_config_file}")
        sys.exit(1)
    
    # Load data
    print(f"🔄 Converting tactical analysis to JSON for: {match_id}")
    print("=" * 50)
    
    with open(tactical_text_file, 'r') as f:
        tactical_text = f.read()
    
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    print(f"📊 Input text: {len(tactical_text):,} characters")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    
    # Initialize converter
    converter = TacticalJSONConverter()
    
    # Convert to JSON
    print("\n🔄 Converting to webapp-compatible JSON...")
    print("⏳ This may take 30-60 seconds...")
    
    tactical_json = converter.convert_to_json(tactical_text, team_config)
    
    if "error" in tactical_json:
        print(f"❌ Conversion failed: {tactical_json['error']}")
        sys.exit(1)
    
    # Save JSON
    json_file = outputs_dir / 'tactical_analysis.json'
    with open(json_file, 'w') as f:
        json.dump(tactical_json, f, indent=2)
    
    print(f"\n✅ JSON conversion complete!")
    print(f"📁 JSON saved to: {json_file}")
    print(f"📊 JSON structure: {list(tactical_json.keys())}")
    
    # Show preview
    if 'tactical_analysis' in tactical_json:
        teams = list(tactical_json['tactical_analysis'].keys())
        print(f"🔍 Teams in JSON: {teams}")
        
        if 'red_team' in tactical_json['tactical_analysis']:
            red_team = tactical_json['tactical_analysis']['red_team']
            print(f"🔴 Red team strengths: {len(red_team.get('strengths', []))}")
            print(f"🔴 Red team weaknesses: {len(red_team.get('weaknesses', []))}")
    
    print(f"\n🎯 Ready for S3 upload: python 6_s3_uploader.py {match_id}")

if __name__ == "__main__":
    main()