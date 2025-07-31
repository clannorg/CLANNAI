#!/usr/bin/env python3
"""
6. ClannAI Video Player Formatter
Uses Gemini 2.5 Pro to convert match timeline into ClannAI video player format
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

class ClannAIFormatter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for intelligent formatting"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def get_clannai_format_prompt(self, timeline_data: dict) -> str:
        """Generate prompt for ClannAI video player formatting"""
        
        return f"""
🎯 CONVERT MATCH TIMELINE TO CLANNAI VIDEO PLAYER FORMAT

You are converting AI football analysis into the exact format needed for ClannAI's video player.

INPUT DATA:
{json.dumps(timeline_data, indent=2)}

🎮 CLANNAI VIDEO PLAYER REQUIREMENTS:

OUTPUT FORMAT (exactly this structure):
```json
[
  {{
    "type": "EVENT_TYPE",
    "timestamp": SECONDS_NUMBER,
    "description": "Concise description",
    "player": "Player info",
    "team": "red|black"
  }}
]
```

📋 EVENT TYPE MAPPING:
- Goals → "goal" 
- Shots/Shot attempts → "shot"
- Saves/Goalkeeper saves → "save"
- Fouls/Tackles → "foul"
- Yellow cards → "yellow_card"
- Red cards → "red_card"
- Corners → "corner"
- Free kicks → "foul" (or "corner" if corner kick)
- Penalties → "foul"
- Substitutions → "substitution"
- Clearances → "foul" (defensive action)
- Offside → "offside"

⏱️ TIMESTAMP CONVERSION:
- Convert "MM:SS" to total seconds: "01:00" → 60, "13:00" → 780
- Use integers only: 120 not "120" or "2:00"

👕 TEAM MAPPING:
- "Black Team" / "team in black" / "blue team" → "black"
- "Red Team" / "team in red" → "red"  
- If unclear, use "black" or "red" based on context

✍️ DESCRIPTION RULES:
- Keep descriptions under 50 characters
- Be specific: "Header from corner" not "Goal scored"
- Include location: "Shot from penalty area"
- Action-focused: "Diving save" not "Goalkeeper saves"

👤 PLAYER EXTRACTION:
- Extract player info if mentioned: "Smith #9", "#11", "Goalkeeper"
- If no specific player, use team role: "Black Team", "Red Team"

🎯 EXAMPLE OUTPUT:
```json
[
  {{"type": "shot", "timestamp": 30, "description": "Shot from penalty area saved", "player": "Black Team", "team": "black"}},
  {{"type": "goal", "timestamp": 60, "description": "Direct free kick into top corner", "player": "Black Team", "team": "black"}},
  {{"type": "foul", "timestamp": 165, "description": "Penalty awarded after foul", "player": "Red Team", "team": "red"}},
  {{"type": "save", "timestamp": 735, "description": "Double save prevents goal", "player": "Goalkeeper", "team": "black"}},
  {{"type": "goal", "timestamp": 780, "description": "Long-range shot over keeper", "player": "Black Team", "team": "black"}}
]
```

CRITICAL: 
- Output ONLY the JSON array, no explanation
- Ensure valid JSON format
- Sort by timestamp (ascending)
- Include ALL significant events from the timeline
- Use exact event types from the mapping above

Convert the match timeline now:"""

    def format_for_clannai(self, match_id: str) -> bool:
        """Convert intelligent match timeline to ClannAI format using Gemini"""
        print(f"🎮 Step 6: ClannAI Video Player formatting for {match_id}")
        
        data_dir = Path("../data") / match_id
        timeline_path = data_dir / "intelligent_match_timeline.json"
        
        if not timeline_path.exists():
            print(f"❌ Intelligent match timeline not found: {timeline_path}")
            print("Run Step 5 first: python 5_gemini_synthesis.py")
            return False
        
        # Load match timeline
        with open(timeline_path, 'r') as f:
            timeline_data = json.load(f)
        
        print("🧠 Using Gemini 2.5 Pro to format for ClannAI video player...")
        
        try:
            start_time = time.time()
            
            # Get formatting prompt
            prompt = self.get_clannai_format_prompt(timeline_data)
            
            # Generate ClannAI format
            response = self.model.generate_content(prompt)
            processing_time = time.time() - start_time
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Clean up response (remove markdown formatting if present)
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            try:
                clannai_events = json.loads(response_text)
                
                # Validate format
                if not isinstance(clannai_events, list):
                    raise ValueError("Output is not an array")
                
                for event in clannai_events:
                    if not isinstance(event.get('timestamp'), (int, float)):
                        raise ValueError(f"Invalid timestamp in event: {event}")
                    if 'type' not in event:
                        raise ValueError(f"Missing type in event: {event}")
                
                print(f"✅ Generated {len(clannai_events)} events for video player")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse Gemini JSON response: {e}")
                print(f"Raw response: {response_text[:200]}...")
                return False
            except ValueError as e:
                print(f"❌ Invalid event format: {e}")
                return False
            
            # Save ClannAI format
            clannai_path = data_dir / "clannai_events.json" 
            with open(clannai_path, 'w') as f:
                json.dump(clannai_events, f, indent=2)
            
            # Also save in legacy web format for backwards compatibility
            web_data = {
                "match_id": match_id,
                "generated_at": datetime.now().isoformat(),
                "model_used": "gemini-2.5-pro",
                "processing_time_seconds": processing_time,
                "events": clannai_events,
                "event_count": len(clannai_events)
            }
            
            web_path = data_dir / "web_format.json"
            with open(web_path, 'w') as f:
                json.dump(web_data, f, indent=2)
            
            print(f"✅ Step 6 complete!")
            print(f"📁 ClannAI events: {clannai_path}")
            print(f"📁 Web format: {web_path}")
            print(f"🎯 {len(clannai_events)} events ready for video player")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            
            # Show sample events
            if clannai_events:
                print("\n📋 Sample events:")
                for event in clannai_events[:3]:
                    print(f"  {event['timestamp']}s - {event['type']}: {event['description']}")
                if len(clannai_events) > 3:
                    print(f"  ... and {len(clannai_events) - 3} more events")
            
            return True
            
        except Exception as e:
            print(f"❌ Gemini formatting failed: {e}")
            return False

def format_for_web(match_id):
    """Main function to format match timeline for ClannAI video player"""
    try:
        formatter = ClannAIFormatter()
        return formatter.format_for_clannai(match_id)
    except ValueError as e:
        print(f"❌ Failed to initialize formatter: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 6_web_formatter.py <match-id>")
        print()
        print("Converts intelligent match timeline to ClannAI video player format")
        print("Output: clannai_events.json (for video player)")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = format_for_web(match_id)
    
    if success:
        print(f"🎯 Ready for Step 7: Accuracy evaluation")
    else:
        sys.exit(1) 