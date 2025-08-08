#!/usr/bin/env python3
"""
VEO-AI Event Enhancer
Smart script that respects VEO ground truth and enhances with AI descriptions
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class VEOAIEnhancer:
    def __init__(self):
        """Initialize with Gemini AI for smart description matching"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("🎯 VEO-AI Event Enhancer initialized")
        print("✅ VEO ground truth = SOURCE OF TRUTH")
        print("🧠 AI descriptions = ENHANCEMENT LAYER")

    def load_veo_ground_truth(self, data_dir):
        """Load VEO professional event data"""
        veo_path = data_dir / "1_veo_ground_truth.json"
        if not veo_path.exists():
            print(f"❌ VEO ground truth not found: {veo_path}")
            return None
            
        with open(veo_path, 'r') as f:
            veo_data = json.load(f)
        
        # Get summary data
        summary = veo_data.get('summary', {})
        print(f"📊 VEO Ground Truth Loaded:")
        print(f"   🥅 Goals: {summary.get('goals', 0)}")
        print(f"   ⚽ Shots: {summary.get('shots_on_goal', 0)}")
        print(f"   📅 Total Events: {veo_data.get('total_events', 0)}")
        
        return veo_data

    def load_ai_timeline(self, data_dir):
        """Load AI-generated match timeline"""
        timeline_path = data_dir / "5_complete_timeline.txt"
        if not timeline_path.exists():
            print(f"❌ AI timeline not found: {timeline_path}")
            return None
            
        with open(timeline_path, 'r') as f:
            timeline_content = f.read()
        
        print(f"🧠 AI Timeline Loaded: {len(timeline_content)} characters")
        return timeline_content

    def enhance_veo_events(self, veo_data, ai_timeline):
        """Use AI to enhance VEO events with rich descriptions"""
        
        if not veo_data.get('events'):
            print("❌ No VEO events found")
            return []
            
        prompt = f"""You are enhancing professional VEO event data with AI-generated match descriptions.

VEO GROUND TRUTH EVENTS (THESE ARE FACTS):
{json.dumps(veo_data.get('events', []), indent=2)}

AI MATCH TIMELINE (USE FOR DESCRIPTIONS):
{ai_timeline}

TASK: For each VEO event, find the best matching AI description and create enhanced events.

RULES:
1. VEO timestamps are GROUND TRUTH - use exact timestamp from VEO
2. VEO timing may be ±10-30 seconds off, so look for AI descriptions in that window
3. Match VEO event type exactly (Goal → goal, Shot on goal → shot)
4. Add rich AI description that matches the VEO timestamp context
5. If no good AI match found, use generic description
6. DO NOT create new events - only enhance existing VEO events
7. Include team information from AI descriptions when possible

OUTPUT FORMAT (JSON array):
[
  {{
    "type": "goal",
    "timestamp": 5548,
    "description": "Rich AI description of how goal occurred",
    "team": "red|blue|yellow|claret|light_blue",
    "veo_event_id": "abc123",
    "confidence": "high|medium|low"
  }}
]

SUPPORTED TYPES:
- "goal" (for VEO "Goal" events)
- "shot" (for VEO "Shot on goal" events) 
- "save" (if AI describes goalkeeper save)
- "foul" (if AI describes foul/free kick)
- "corner" (if AI describes corner kick)
- "yellow_card" (if AI describes yellow card)
- "red_card" (if AI describes red card)

Be strict - only high-confidence matches. Output ONLY the JSON array.
"""

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            
            # Clean up response
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            enhanced_events = json.loads(json_text)
            
            print(f"✅ Enhanced {len(enhanced_events)} VEO events with AI descriptions")
            return enhanced_events
            
        except Exception as e:
            print(f"❌ AI enhancement failed: {e}")
            return []

    def find_obvious_extras(self, ai_timeline, veo_events):
        """Find obvious additional events AI spotted that VEO missed"""
        
        # Extract VEO timestamps to avoid duplicates
        veo_timestamps = {event.get('timestamp_seconds', 0) for event in veo_events}
        
        prompt = f"""You are finding OBVIOUS additional football events that VEO missed.

AI MATCH TIMELINE:
{ai_timeline}

VEO ALREADY HAS EVENTS AT THESE TIMES (DO NOT DUPLICATE):
{sorted(veo_timestamps)}

TASK: Find clear, obvious events VEO missed. Be VERY strict - only include events you're 100% confident about.

TARGET EVENTS (only if very obvious):
1. Clear fouls with free kicks awarded
2. Obvious corner kicks  
3. Clear yellow/red cards shown
4. Obvious substitutions
5. Clear penalty awards (not goals)

RULES:
1. Must be clearly described in AI timeline
2. Must not overlap with VEO timestamps (±30 seconds)
3. Must be significant match events, not routine play
4. Include referee decisions, set pieces, disciplinary actions
5. DO NOT include: headers, passes, general attacks, saves (unless very obvious)

OUTPUT FORMAT (JSON array):
[
  {{
    "type": "foul|corner|yellow_card|red_card|substitution",
    "timestamp": 1234,
    "description": "Clear description of what happened",
    "team": "team_name",
    "confidence": "high",
    "source": "ai_detected"
  }}
]

Be extremely conservative. Quality over quantity. Output ONLY the JSON array.
"""

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip()
            
            # Clean up response
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
                
            if json_text.strip() == '[]':
                print("🔍 No obvious extras found (good - being strict)")
                return []
            
            extra_events = json.loads(json_text)
            print(f"🔍 Found {len(extra_events)} obvious additional events")
            return extra_events
            
        except Exception as e:
            print(f"⚠️  Could not extract extras: {e}")
            return []

    def enhance_match(self, match_id):
        """Main function to enhance match with VEO truth + AI intelligence"""
        print(f"🎯 Enhancing match {match_id}")
        print("=" * 60)
        
        data_dir = Path("../data") / match_id
        if not data_dir.exists():
            print(f"❌ Match data not found: {data_dir}")
            return False
        
        # Load VEO ground truth
        veo_data = self.load_veo_ground_truth(data_dir)
        if not veo_data:
            return False
        
        # Load AI timeline
        ai_timeline = self.load_ai_timeline(data_dir)
        if not ai_timeline:
            return False
        
        print("\n🔄 Processing...")
        
        # Enhance VEO events with AI descriptions
        enhanced_events = self.enhance_veo_events(veo_data, ai_timeline)
        
        # Find obvious extras VEO missed
        extra_events = self.find_obvious_extras(ai_timeline, veo_data.get('events', []))
        
        # Combine all events
        all_events = enhanced_events + extra_events
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.get('timestamp', 0))
        
        # Save enhanced events
        output_path = data_dir / "enhanced_events.json"
        with open(output_path, 'w') as f:
            json.dump(all_events, f, indent=2)
        
        # Save for web format converter
        web_array_path = data_dir / "web_events_array.json"
        with open(web_array_path, 'w') as f:
            json.dump(all_events, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ ENHANCEMENT COMPLETE!")
        print("=" * 60)
        
        event_types = {}
        for event in all_events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print(f"📊 Final Event Summary:")
        for event_type, count in sorted(event_types.items()):
            print(f"   {event_type}: {count}")
        
        print(f"\n📁 Enhanced events saved to: {output_path}")
        print(f"🌐 Web-ready events: {web_array_path}")
        
        # Show sample events
        print(f"\n🎮 Sample Enhanced Events:")
        for i, event in enumerate(all_events[:5]):
            timestamp_min = event.get('timestamp', 0) // 60
            timestamp_sec = event.get('timestamp', 0) % 60
            print(f"   {i+1}. {timestamp_min:02d}:{timestamp_sec:02d} - {event.get('type', '').upper()} - {event.get('description', '')[:50]}")
        
        if len(all_events) > 5:
            print(f"   ... and {len(all_events) - 5} more events")
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python veo_ai_enhancer.py <match-id>")
        print("Example: python veo_ai_enhancer.py 19-20250419")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        enhancer = VEOAIEnhancer()
        success = enhancer.enhance_match(match_id)
        
        if success:
            print("\n🎉 VEO-AI enhancement completed successfully!")
            print("🎯 Ready for web format conversion")
        else:
            print("\n❌ Enhancement failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()