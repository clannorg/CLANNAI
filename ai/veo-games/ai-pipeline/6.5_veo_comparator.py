#!/usr/bin/env python3
"""
6.5 VEO Comparator
Takes kickoff-validated goals/shots and compares them against VEO ground truth
Creates goals_and_shots_timeline.json with only VEO-confirmed events
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

class VEOComparator:
    def __init__(self):
        """Initialize with Gemini for intelligent VEO comparison"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🎯 VEO Comparator initialized with Gemini AI")

    def get_comparison_prompt(self, validated_timeline: str, veo_events: list) -> str:
        """Create prompt for comparing validated timeline with VEO ground truth"""
        veo_events_str = "\n".join([
            f"- {event['event_type']} at {event['timestamp']} ({event.get('duration', 'unknown')}s duration)"
            for event in veo_events
        ])
        
        return f"""You are a football analyst comparing AI-validated events with official VEO ground truth data.

TASK: Compare the kickoff-validated AI timeline with VEO official events and output only VEO-confirmed events in JSON format.

KICKOFF-VALIDATED AI TIMELINE:
{validated_timeline}

VEO GROUND TRUTH EVENTS:
{veo_events_str}

COMPARISON RULES:
1. For each VEO event, find the closest AI description within ±30 seconds
2. VEO "Goal" events must match AI descriptions (goals, celebrations, restarts)
3. VEO "Shot on goal" events must match AI shot descriptions (saves, blocks, misses)
4. Keep the AI timestamp and description (more detailed than VEO)
5. Only include events that have BOTH VEO confirmation AND AI description

OUTPUT FORMAT (JSON only):
{{
  "goals": [
    {{
      "timestamp": "MM:SS",
      "timestamp_seconds": 0000,
      "team": "red/blue/etc",
      "description": "AI description of how goal occurred",
      "veo_match": "Goal at MM:SS",
      "confidence": "high/medium/low"
    }}
  ],
  "shots": [
    {{
      "timestamp": "MM:SS", 
      "timestamp_seconds": 0000,
      "team": "red/blue/etc",
      "description": "AI description of shot",
      "outcome": "saved/missed/blocked",
      "veo_match": "Shot on goal at MM:SS",
      "confidence": "high/medium/low"
    }}
  ],
  "summary": {{
    "total_events": 0,
    "goals_confirmed": 0,
    "shots_confirmed": 0,
    "veo_goals_total": 0,
    "veo_shots_total": 0
  }}
}}

IMPORTANT: 
- Output ONLY valid JSON
- Use AI timestamps (more accurate than VEO)
- Match within ±30 second tolerance
- Include confidence level for each match"""

    def compare_with_veo(self, match_id: str) -> bool:
        """Compare validated timeline with VEO ground truth"""
        print(f"🎯 Comparing validated timeline with VEO for {match_id}")
        
        data_dir = Path("../data") / match_id
        validated_timeline_path = data_dir / "6_validated_timeline.txt"
        veo_ground_truth_path = data_dir / "1_veo_ground_truth.json"
        output_path = data_dir / "goals_and_shots_timeline.json"
        
        # Check input files exist
        if not validated_timeline_path.exists():
            print(f"❌ Validated timeline not found: {validated_timeline_path}")
            return False
            
        if not veo_ground_truth_path.exists():
            print(f"❌ VEO ground truth not found: {veo_ground_truth_path}")
            return False
        
        # Read input files
        print("📥 Reading validated timeline and VEO ground truth...")
        with open(validated_timeline_path, 'r') as f:
            validated_timeline = f.read()
            
        with open(veo_ground_truth_path, 'r') as f:
            veo_data = json.load(f)
        
        # Extract VEO events
        veo_events = veo_data.get('events', [])
        if not veo_events:
            print("⚠️ No VEO events found")
            return False
            
        print(f"📊 Found {len(veo_events)} VEO events to compare")
        
        # Generate comparison analysis
        print("🧠 Comparing validated timeline with VEO events...")
        comparison_prompt = self.get_comparison_prompt(validated_timeline, veo_events)
        
        try:
            response = self.model.generate_content(comparison_prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            goals_shots_data = json.loads(response_text)
            
            # Save the goals and shots timeline
            print(f"💾 Saving VEO-confirmed timeline to: {output_path}")
            with open(output_path, 'w') as f:
                json.dump(goals_shots_data, f, indent=2)
            
            # Print summary
            summary = goals_shots_data.get('summary', {})
            print(f"\n📊 VEO COMPARISON RESULTS:")
            print(f"   🎯 Goals confirmed: {summary.get('goals_confirmed', 0)}/{summary.get('veo_goals_total', 0)}")
            print(f"   🎯 Shots confirmed: {summary.get('shots_confirmed', 0)}/{summary.get('veo_shots_total', 0)}")
            print(f"   📊 Total events: {summary.get('total_events', 0)}")
            
            print("✅ VEO comparison completed successfully!")
            print(f"📊 Output: {output_path}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Response was: {response_text[:200]}...")
            return False
        except Exception as e:
            print(f"❌ Error during VEO comparison: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 6.5_veo_comparator.py <match_id>")
        print("Example: python 6.5_veo_comparator.py 19-20250419")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    comparator = VEOComparator()
    success = comparator.compare_with_veo(match_id)
    
    if success:
        print(f"\n🎯 VEO comparison completed for {match_id}!")
        print("📝 goals_and_shots_timeline.json contains only VEO-confirmed events")
        print("🔄 Next: Run 9_convert_to_web_format.py for final web JSON")
    else:
        print(f"\n❌ VEO comparison failed for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()