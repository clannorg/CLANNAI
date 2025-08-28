#!/usr/bin/env python3
"""
5. Format for Webapp
Use Gemini to convert plain text highlights into webapp-compatible JSON format
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

class WebappFormatter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for text-to-JSON conversion"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def convert_text_to_json(self, highlights_text: str, summary_text: str, team_config: dict, match_id: str) -> dict:
        """Use Gemini to convert plain text highlights to webapp JSON format"""
        
        prompt = f"""Convert this plain text match analysis into webapp-compatible JSON format.

**TEAM MAPPING:**
- Team A: {team_config['team_a']['name']} ({team_config['team_a']['colors']})
- Team B: {team_config['team_b']['name']} ({team_config['team_b']['colors']})

**EVENTS TEXT:**
{highlights_text}

**SUMMARY TEXT:**
{summary_text}

**REQUIRED JSON FORMAT:**
```json
{{
  "timeline_events": [
    {{
      "timestamp": 2205,
      "type": "goal",
      "team": "{team_config['team_b']['name']}",
      "description": "Corduff celebrates a goal, Dalkey kicks off to restart", 
      "excitement_level": 10,
      "original_team_name": "{team_config['team_b']['colors']}",
      "veo_verified": true,
      "ai_detected": false
    }},
    {{
      "timestamp": 810,
      "type": "penalty",
      "team": "{team_config['team_a']['name']}",
      "description": "Penalty kick results in a goal", 
      "excitement_level": 6,
      "original_team_name": "{team_config['team_a']['colors']}",
      "veo_verified": false,
      "ai_detected": true
    }}
  ],
  "match_summary": "Match summary from text",
  "final_score": "Final score from text"
}}
```

**CRITICAL CONVERSION RULES:**
- Convert timestamps MM:SS to seconds (e.g., "36:45" → 2205)
- Map team visual identifiers to exact team NAMES from config (team field = team name, original_team_name = jersey colors)
- Include ALL event types: GOAL, SHOT, PENALTY, FOUL, CORNER, THROW-IN, KICK-OFF, etc.
- VEO VERIFICATION FLAGS:
  * veo_verified: true + ai_detected: false → for "GOAL:", "SHOT:" (VEO ground truth)
  * veo_verified: false + ai_detected: true → for anything with "(AI-reported, not VEO verified)"
  * veo_verified: true + ai_detected: false → for standard events like "FOUL:", "CORNER:", etc.
- EXCITEMENT LEVELS:
  * 10: VEO verified goals
  * 8: VEO verified shots
  * 6: AI-detected penalties/goals
  * 4: Fouls, corners, throw-ins
  * 2: Kick-offs, goal kicks
- Extract match summary and final score from the mega_summary.txt content if available

Convert ALL events from the text to JSON format:"""

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
                    "timeline_events": [],
                    "match_summary": "JSON parsing failed",
                    "final_score": "Unknown",
                    "raw_response": response_text
                }
                
        except Exception as e:
            print(f"⚠️  Gemini conversion failed: {e}")
            return {
                "timeline_events": [],
                "match_summary": "Conversion failed",
                "final_score": "Unknown",
                "error": str(e)
            }

def create_match_metadata(webapp_data: dict, match_id: str, team_config: dict) -> dict:
    """Create metadata file for the match in v3 format (East London style)"""
    
    # Count events by type
    event_counts = {}
    for event in webapp_data['timeline_events']:
        event_type = event['type']
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    # Create v3 format metadata matching East London structure
    metadata = {
        'match_id': match_id,
        'teams': {
            'red_team': {
                'name': team_config['team_a']['name'],
                'jersey_color': team_config['team_a']['colors']
            },
            'blue_team': {
                'name': team_config['team_b']['name'], 
                'jersey_color': team_config['team_b']['colors']
            }
        },
        'counts': {
            'goals': event_counts.get('goal', 0),
            'shots': event_counts.get('shot', 0)
        },
        'files': {
            'video_mp4': f"https://end-nov-webapp-clann.s3.amazonaws.com/analysis-videos/{match_id}-video-mp4.mp4",
            'web_events_array_json': f"https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/{match_id}-web_events_array-json.json",
            'web_events_json': None,
            'timeline_txt': None,
            'ground_truth_json': None,
            'other_events_txt': None,
            'tactical_json': None
        },
        'final_score': webapp_data['final_score'],
        'match_summary': webapp_data['match_summary']
    }
    
    return metadata

def main():
    if len(sys.argv) != 2:
        print("Usage: python 5_format_webapp.py <match-id>")
        print("Example: python 5_format_webapp.py sunday-league-game-1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    # Load required files
    team_config_file = outputs_dir / '1_team_config.json'
    # Use focused events from 2.6 analyzer
    highlights_file = outputs_dir / '2.6_focused_events.txt'
    # Also load summary for final score and match summary
    summary_file = outputs_dir / '2.6_focused_summary.txt'
    
    if not team_config_file.exists():
        print(f"❌ Error: Team configuration not found: {team_config_file}")
        sys.exit(1)
    
    if not highlights_file.exists():
        print(f"❌ Error: Focused events data not found: {highlights_file}")
        print("Run step 2.6 first: python 2.6_focused_events.py <match-id>")
        sys.exit(1)
    
    if not summary_file.exists():
        print(f"❌ Error: Focused summary data not found: {summary_file}")
        print("Run step 2.6 first: python 2.6_focused_events.py <match-id>")
        sys.exit(1)
    
    # Load data
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    with open(highlights_file, 'r') as f:
        highlights_text = f.read()
    
    with open(summary_file, 'r') as f:
        summary_text = f.read()
    
    print(f"🌐 Formatting for webapp: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print("=" * 50)
    print("🧠 Using Gemini to convert text to JSON...")
    
    # Initialize formatter and convert
    formatter = WebappFormatter()
    webapp_data = formatter.convert_text_to_json(highlights_text, summary_text, team_config, match_id)
    match_metadata = create_match_metadata(webapp_data, match_id, team_config)
    
    # Save webapp files
    webapp_file = outputs_dir / '3.1_web_events_array.json'
    metadata_file = outputs_dir / '3.1_match_metadata.json'
    
    with open(webapp_file, 'w') as f:
        json.dump(webapp_data.get('timeline_events', []), f, indent=2)
    
    with open(metadata_file, 'w') as f:
        json.dump(match_metadata, f, indent=2)
    
    # Also save complete webapp data
    complete_file = outputs_dir / '3.1_webapp_complete.json'
    with open(complete_file, 'w') as f:
        json.dump(webapp_data, f, indent=2)
    
    print(f"✅ Webapp formatting complete!")
    print(f"📄 Timeline events: {webapp_file}")
    print(f"📄 Match metadata: {metadata_file}")
    print(f"📄 Complete data: {complete_file}")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   Total events: {len(webapp_data['timeline_events'])}")
    print(f"   Goals: {match_metadata['counts'].get('goals', 0)}")
    print(f"   Shots: {match_metadata['counts'].get('shots', 0)}")
    print(f"   Final score: {webapp_data['final_score']}")
    
    if webapp_data['timeline_events']:
        print(f"\n🎯 Sample events:")
        for event in webapp_data['timeline_events'][:3]:
            mins = event['timestamp'] // 60
            secs = event['timestamp'] % 60
            print(f"   {mins:02d}:{secs:02d} - {event['type'].upper()}: {event['description'][:60]}...")
    
    print(f"\n🎉 Analysis complete! Ready for webapp integration.")
    print(f"📁 All files saved in: {outputs_dir}")

if __name__ == "__main__":
    main()