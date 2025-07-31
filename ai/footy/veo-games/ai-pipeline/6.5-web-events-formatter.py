#!/usr/bin/env python3
"""
6.5 Web Events Formatter - Simple & Clean
Reads AI analysis files and outputs clean web JSON events using Gemini 2.5 Pro
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

class WebEventsFormatter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for clean web formatting"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def create_web_events(self, match_id: str) -> bool:
        """Convert AI analysis to clean web events format"""
        print(f"🎮 Creating clean web events for {match_id}")
        
        data_dir = Path("../data") / match_id
        
        # Load all AI analysis files
        files_to_load = {
            'tactical': data_dir / "tactical_coaching_insights.json",
            'timeline': data_dir / "intelligent_match_timeline.json", 
            'shots': data_dir / "goals_and_shots_timeline.json"
        }
        
        analysis_data = {}
        for key, file_path in files_to_load.items():
            if file_path.exists():
                with open(file_path, 'r') as f:
                    analysis_data[key] = json.load(f)
                print(f"✅ Loaded {key} analysis")
            else:
                print(f"⚠️  {key} analysis not found: {file_path}")
        
        if not analysis_data:
            print("❌ No analysis files found!")
            return False
        
        # Create Gemini prompt for web events
        prompt = self.create_web_events_prompt(analysis_data)
        
        try:
            print("🧠 Calling Gemini 2.5 Pro for web events formatting...")
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
            elif response_text.startswith('['):
                json_text = response_text
            else:
                # Try to find JSON array in response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != 0:
                    json_text = response_text[start_idx:end_idx]
                else:
                    raise ValueError("No valid JSON array found in response")
            
            # Parse and validate JSON
            try:
                web_events = json.loads(json_text)
                if not isinstance(web_events, list):
                    raise ValueError("Response is not a JSON array")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Response: {response_text}")
                return False
            
            # Save web events
            output_path = data_dir / "web_events.json"
            with open(output_path, 'w') as f:
                json.dump(web_events, f, indent=2)
            
            print(f"✅ Web events created successfully!")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            print(f"📊 Events created: {len(web_events)}")
            print(f"💾 Saved to: {output_path}")
            
            # Show sample events
            print(f"\n📋 Sample Events:")
            for i, event in enumerate(web_events[:3]):
                event_time = f"{event['timestamp']//60}:{event['timestamp']%60:02d}"
                print(f"   {i+1}. {event['type']} at {event_time} - {event['description']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating web events: {e}")
            return False

    def create_web_events_prompt(self, analysis_data: dict) -> str:
        """Create prompt for Gemini to generate clean web events"""
        
        # Combine all analysis data into context
        context = "AI ANALYSIS DATA:\n"
        for key, data in analysis_data.items():
            context += f"\n--- {key.upper()} DATA ---\n"
            context += json.dumps(data, indent=2)[:2000] + "...\n"  # Truncate for prompt size
        
        return f"""
🎮 CREATE CLEAN WEB EVENTS FOR VIDEO PLAYER

You are converting detailed AI football analysis into a simple, clean event format for a web video player.

{context}

🎯 OUTPUT FORMAT (EXACTLY THIS STRUCTURE):
[
  {{
    "type": "shot",
    "timestamp": 15,
    "description": "Early shot attempt",
    "player": "Bunny #1"
  }},
  {{
    "type": "goal",
    "timestamp": 17, 
    "description": "Opening goal",
    "player": "Bunny #1"
  }}
]

📋 EVENT TYPES TO USE:
- "goal" - Ball crosses goal line
- "shot" - Shot attempt (saved, missed, blocked)
- "save" - Goalkeeper save
- "foul" - Foul, tackle, penalty awarded
- "corner" - Corner kick
- "card" - Yellow/red card

⏱️ TIMESTAMP RULES:
- Use integer seconds only: 37, 780, 1245
- Convert from "MM:SS" format: "0:37" → 37, "13:00" → 780

👕 TEAM/PLAYER RULES:  
- Extract player info if available: "#7", "Goalkeeper", "Smith"
- If no player info, use: "Red Team" or "Black Team"
- Keep consistent with red/black team naming

✍️ DESCRIPTION RULES:
- Maximum 30 characters
- Action-focused: "Shot saved", "Header goal", "Long-range strike"
- Include key context: "Penalty area shot", "Free kick goal"

🎯 REQUIREMENTS:
1. Include ALL significant events (goals, shots, saves, major fouls)
2. Sort by timestamp (ascending order)
3. Output ONLY the JSON array - no explanation
4. Ensure valid JSON format
5. Extract precise timing from the AI analysis

Convert the AI analysis data into clean web events now:
"""

def main():
    """Create web events for a match"""
    if len(sys.argv) != 2:
        print("Usage: python 6.5-web-events-formatter.py <match-id>")
        print("Example: python 6.5-web-events-formatter.py ballyclare-20250111")
        return
    
    match_id = sys.argv[1]
    formatter = WebEventsFormatter()
    success = formatter.create_web_events(match_id)
    
    if success:
        print(f"🎯 Web events ready for website integration!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()