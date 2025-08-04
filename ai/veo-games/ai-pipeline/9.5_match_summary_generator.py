#!/usr/bin/env python3
"""
9.5 Match Summary Generator
Creates a comprehensive match summary for website display
Includes team mapping, score, key events, and display metadata
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
load_dotenv(Path(__file__).parent.parent / '.env')

class MatchSummaryGenerator:
    def __init__(self):
        """Initialize with Gemini for intelligent match summarization"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("📋 Match Summary Generator initialized with Gemini AI")

    def get_summary_prompt(self, web_events_json: str, source_json: str, definite_events: str) -> str:
        """Create prompt for generating comprehensive match summary"""
        return f"""You are a football match analyst creating a comprehensive summary for website display.

WEB EVENTS DATA:
{web_events_json}

SOURCE DATA:
{source_json}

DEFINITE EVENTS ANALYSIS:
{definite_events}

TASK: Create a comprehensive match summary that helps display the game information effectively.

OUTPUT JSON FORMAT:
{{
  "match_info": {{
    "match_id": "newmills-20250222",
    "title": "Newmills vs St Marys",
    "date": "2025-02-22",
    "venue": "Newmills",
    "duration_minutes": 90,
    "status": "completed"
  }},
  "team_mapping": {{
    "red": {{
      "display_name": "Newmills FC",
      "color": "#FF0000",
      "is_home": true
    }},
    "yellow": {{
      "display_name": "St Marys",
      "color": "#FFFF00", 
      "is_home": false
    }}
  }},
  "score_line": {{
    "red": 3,
    "yellow": 2,
    "final_score": "3-2",
    "result": "red_win"
  }},
  "event_statistics": {{
    "total_events": 106,
    "goals": 5,
    "shots": 25,
    "fouls": 18,
    "cards": 3,
    "corners": 8,
    "substitutions": 4
  }},
  "key_moments": [
    {{
      "timestamp": 5200,
      "time_display": "86:39",
      "type": "goal",
      "description": "Goal from left wing cross",
      "team": "red",
      "importance": "high"
    }}
  ],
  "match_narrative": {{
    "opening_phase": "First 30 minutes summary",
    "key_turning_point": "Moment that changed the game",
    "closing_phase": "Final 30 minutes summary",
    "match_summary": "Overall match story in 2-3 sentences"
  }},
  "tactical_overview": {{
    "dominant_team": "red",
    "game_style": "attacking",
    "key_patterns": ["Left wing attacks", "Set piece threat"],
    "momentum_shifts": ["After red goal at 86:39", "Late pressure from yellow"]
  }},
  "display_metadata": {{
    "primary_color": "#FF0000",
    "secondary_color": "#FFFF00",
    "highlight_events": [5200, 7748, 7933],
    "recommended_clips": [
      {{"start": 5180, "end": 5220, "title": "Opening Goal"}},
      {{"start": 7728, "end": 7768, "title": "Equalizer"}}
    ]
  }}
}}

INSTRUCTIONS:
1. Identify team colors and map to actual team names if available
2. Calculate accurate score from goal events
3. Count events by type for statistics
4. Extract 3-5 most important moments
5. Create narrative that explains match flow
6. Provide tactical overview of playing styles
7. Generate display metadata for frontend styling
8. Use exact timestamps from events data
9. Make descriptions engaging but accurate
10. Focus on information useful for website display

TEAM IDENTIFICATION RULES:
- Use source data for official team names
- Map colors (red/yellow/black/blue) to actual teams
- Determine home/away based on venue
- Assign appropriate display colors
- Default to color names if team names unavailable

Be comprehensive but focused on display-relevant information."""

    def generate_match_summary(self, match_id: str) -> bool:
        """Generate comprehensive match summary"""
        print(f"📋 Generating match summary for {match_id}")
        
        data_dir = Path("../data") / match_id
        web_events_path = data_dir / "web_events.json"
        source_path = data_dir / "1_source.json"
        definite_events_path = data_dir / "7.5_definite_events.txt"
        output_path = data_dir / "9.5_match_summary.json"
        
        # Check required files exist
        required_files = [web_events_path, source_path]
        for file_path in required_files:
            if not file_path.exists():
                print(f"❌ Required file not found: {file_path}")
                return False
        
        # Read input files
        print("📥 Reading match data files...")
        
        with open(web_events_path, 'r') as f:
            web_events_json = f.read()
            
        with open(source_path, 'r') as f:
            source_json = f.read()
            
        definite_events = ""
        if definite_events_path.exists():
            with open(definite_events_path, 'r') as f:
                definite_events = f.read()
        
        # Generate match summary
        print("🧠 Analyzing match for comprehensive summary...")
        summary_prompt = self.get_summary_prompt(web_events_json, source_json, definite_events)
        
        try:
            response = self.model.generate_content(summary_prompt)
            summary_content = response.text
            
            # Parse JSON response
            if '```json' in summary_content:
                json_start = summary_content.find('```json') + 7
                json_end = summary_content.find('```', json_start)
                summary_content = summary_content[json_start:json_end]
            elif '```' in summary_content:
                json_start = summary_content.find('```') + 3
                json_end = summary_content.find('```', json_start)
                summary_content = summary_content[json_start:json_end]
            
            # Validate JSON
            summary_data = json.loads(summary_content.strip())
            
            # Add generation metadata
            summary_data["generation_info"] = {
                "generated_at": datetime.now().isoformat(),
                "generator": "clann_ai_match_summary",
                "version": "1.0",
                "source_events": summary_data.get("event_statistics", {}).get("total_events", 0)
            }
            
            # Save match summary
            print(f"💾 Saving match summary to: {output_path}")
            with open(output_path, 'w') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            print("✅ Match summary generated successfully!")
            print(f"📊 Output: {output_path}")
            
            # Print summary preview
            print(f"\n📋 MATCH SUMMARY PREVIEW:")
            if "match_info" in summary_data:
                match_info = summary_data["match_info"]
                print(f"   🏆 Match: {match_info.get('title', match_id)}")
                print(f"   📅 Date: {match_info.get('date', 'Unknown')}")
                print(f"   🏟️  Venue: {match_info.get('venue', 'Unknown')}")
            
            if "score_line" in summary_data:
                score = summary_data["score_line"]
                print(f"   ⚽ Score: {score.get('final_score', 'Unknown')}")
            
            if "event_statistics" in summary_data:
                stats = summary_data["event_statistics"]
                print(f"   📊 Events: {stats.get('total_events', 0)} total")
                print(f"   🎯 Goals: {stats.get('goals', 0)}, Shots: {stats.get('shots', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating match summary: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 9.5_match_summary_generator.py <match_id>")
        print("Example: python 9.5_match_summary_generator.py newmills-20250222")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    generator = MatchSummaryGenerator()
    success = generator.generate_match_summary(match_id)
    
    if success:
        print(f"\n📋 Match summary ready for {match_id}!")
        print("🌐 Contains team mapping, score, statistics, and display metadata")
        print("🎯 Perfect for website match display and navigation")
    else:
        print(f"\n❌ Failed to generate match summary for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()