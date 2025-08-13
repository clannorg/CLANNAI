#!/usr/bin/env python3
"""
13. Format for Webapp

Takes the rich mega_analysis.json and converts it into webapp-compatible formats:
- web_events_array.json (timeline events)
- 11_tactical_analysis.json (insights tab)

Uses Gemini to convert the narrative analysis into structured JSON.

Usage:
  python 13_format_for_webapp.py <match-id>

Example:
  python 13_format_for_webapp.py 20250523-match-23-may-2025-3fc1de88
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class WebappFormatter:
    def __init__(self):
        """Initialize Gemini client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print(f"🔄 Webapp Formatter initialized with Gemini 2.0 Flash")

    def load_mega_analysis(self, match_id: str) -> dict:
        """Load the mega analysis text files"""
        outputs_dir = Path("../outputs") / match_id
        
        # Load the three text files
        events_path = outputs_dir / "mega_events.txt"
        tactical_path = outputs_dir / "mega_tactical.txt"
        summary_path = outputs_dir / "mega_summary.txt"
        
        if not events_path.exists():
            raise Exception(f"mega_events.txt not found: {events_path}")
        if not tactical_path.exists():
            raise Exception(f"mega_tactical.txt not found: {tactical_path}")
        if not summary_path.exists():
            raise Exception(f"mega_summary.txt not found: {summary_path}")
        
        # Read all text files
        with open(events_path, 'r') as f:
            events_text = f.read()
        with open(tactical_path, 'r') as f:
            tactical_text = f.read()
        with open(summary_path, 'r') as f:
            summary_text = f.read()
        
        return {
            'events_text': events_text,
            'tactical_text': tactical_text,
            'summary_text': summary_text
        }

    def format_events(self, mega_analysis: dict) -> list:
        """Convert mega events text to web events array"""
        
        events_text = mega_analysis['events_text']
        
        prompt = f"""
Convert this football match events list into a JSON array for a webapp timeline.

EVENTS TEXT:
{events_text}

OUTPUT FORMAT - Return a JSON array where each event has:
{{
  "type": "goal" | "shot" | "foul" | "corner" | "substitution" | "yellow_card" | "red_card" | "kick_off",
  "timestamp": <seconds from match start>,
  "team": "red" | "blue",
  "description": "<brief description max 100 chars>"
}}

RULES:
1. Parse each line in format: "MM:SS - TYPE: Team - Description"
2. Convert timestamps like "32:48" to seconds (32*60 + 48 = 1968)
3. Map teams: Yellow team -> "red", Blue team -> "blue"
4. Map event types: GOAL->goal, SHOT->shot, FOUL->foul, KICK-OFF->kick_off, etc.
5. Keep descriptions concise and clear
6. Sort by timestamp ascending
7. Only include events with clear timestamps

Return ONLY the JSON array, no other text.
"""

        try:
            response = self.model.generate_content(prompt)
            events_text = response.text.strip()
            
            # Clean up response
            if events_text.startswith('```json'):
                events_text = events_text[7:]
            if events_text.endswith('```'):
                events_text = events_text[:-3]
            
            events = json.loads(events_text)
            print(f"✅ Generated {len(events)} events for webapp")
            return events
            
        except Exception as e:
            print(f"❌ Failed to format events: {e}")
            return []

    def format_tactical(self, mega_analysis: dict) -> dict:
        """Convert mega tactical text to tactical insights"""
        
        tactical_text = mega_analysis['tactical_text']
        summary_text = mega_analysis['summary_text']
        
        prompt = f"""
Convert this football match tactical analysis into structured insights for a webapp.

TACTICAL ANALYSIS:
{tactical_text}

MATCH SUMMARY:
{summary_text}

OUTPUT FORMAT - Return JSON with this exact structure:
{{
  "red_team": {{
    "team_name": "Yellow Team",
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "key_players": ["player1", "player2"],
    "tactical_setup": "Formation and style description",
    "performance_summary": "Overall performance paragraph"
  }},
  "blue_team": {{
    "team_name": "Blue Team", 
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2", "weakness3"],
    "key_players": ["player1", "player2"],
    "tactical_setup": "Formation and style description",
    "performance_summary": "Overall performance paragraph"
  }},
  "match_summary": {{
    "final_score": "X-Y",
    "key_moments": ["moment1", "moment2", "moment3"],
    "turning_points": ["point1", "point2"],
    "overall_narrative": "Match story paragraph"
  }}
}}

RULES:
1. Map Yellow Team to red_team, Blue Team to blue_team
2. Extract insights from the tactical analysis sections
3. Keep arrays to 2-4 items each
4. Make descriptions coach-friendly and actionable
5. Extract final score and key moments from summary
6. If specific players aren't mentioned, use generic descriptions

Return ONLY the JSON object, no other text.
"""

        try:
            response = self.model.generate_content(prompt)
            tactical_text = response.text.strip()
            
            # Clean up response
            if tactical_text.startswith('```json'):
                tactical_text = tactical_text[7:]
            if tactical_text.endswith('```'):
                tactical_text = tactical_text[:-3]
            
            tactical = json.loads(tactical_text)
            print(f"✅ Generated tactical analysis for webapp")
            return tactical
            
        except Exception as e:
            print(f"❌ Failed to format tactical analysis: {e}")
            return {}

    def save_outputs(self, match_id: str, events: list, tactical: dict):
        """Save formatted outputs"""
        outputs_dir = Path("../outputs") / match_id
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save web events array
        events_path = outputs_dir / "web_events_array.json"
        with open(events_path, 'w') as f:
            json.dump(events, f, indent=2)
        print(f"✅ Saved: {events_path}")
        
        # Save web events (legacy format)
        events_legacy_path = outputs_dir / "web_events.json"
        with open(events_legacy_path, 'w') as f:
            json.dump({"events": events}, f, indent=2)
        print(f"✅ Saved: {events_legacy_path}")
        
        # Save tactical analysis
        tactical_path = outputs_dir / "11_tactical_analysis.json"
        with open(tactical_path, 'w') as f:
            json.dump(tactical, f, indent=2)
        print(f"✅ Saved: {tactical_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python 13_format_for_webapp.py <match-id>")
        print("Example: python 13_format_for_webapp.py 20250523-match-23-may-2025-3fc1de88")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        formatter = WebappFormatter()
        
        print(f"🎯 Formatting webapp outputs for: {match_id}")
        
        # Load mega analysis
        print("📖 Loading mega analysis...")
        mega_analysis = formatter.load_mega_analysis(match_id)
        
        # Format events
        print("🎮 Formatting events for timeline...")
        events = formatter.format_events(mega_analysis)
        
        # Format tactical analysis
        print("🧠 Formatting tactical insights...")
        tactical = formatter.format_tactical(mega_analysis)
        
        # Save outputs
        print("💾 Saving webapp outputs...")
        formatter.save_outputs(match_id, events, tactical)
        
        print(f"\n🎉 WEBAPP FORMATTING COMPLETE!")
        print(f"📊 Events generated: {len(events)}")
        print(f"🧠 Tactical teams: {len(tactical.get('red_team', {}))} red, {len(tactical.get('blue_team', {}))} blue")
        print(f"💾 Files ready for S3 upload")
        
    except Exception as e:
        print(f"❌ Webapp formatting failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()