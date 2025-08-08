#!/usr/bin/env python3
"""
7.5 Definite Events Builder
Cross-references VEO ground truth with AI descriptions to create validated events
Only includes events that match VEO timestamps ±30 seconds with rich AI descriptions
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

class DefiniteEventsBuilder:
    def __init__(self):
        """Initialize with Gemini for intelligent cross-referencing"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🎯 Definite Events Builder initialized with Gemini AI")

    def get_cross_reference_prompt(self, veo_events: list, ai_timeline: str) -> str:
        """Create prompt for intelligent timestamp-based cross-referencing"""
        veo_events_str = "\n".join([f"- {event['type'].upper()} at {event['timestamp']} ({event.get('team', 'unknown')} team)" for event in veo_events])
        
        return f"""You are an expert football analyst tasked with finding AI descriptions that match VEO ground truth events using timestamp analysis.

TASK: For each VEO event, find the matching AI description within ±30 seconds of the VEO timestamp.

VEO GROUND TRUTH EVENTS:
{veo_events_str}

AI COMPLETE TIMELINE:
{ai_timeline}

INSTRUCTIONS:
1. For each VEO event, search the AI timeline within ±30 seconds of that timestamp
2. Look for ANY AI description that could match (shots, saves, celebrations, restarts, etc.)
3. A VEO "goal" might be described as a "shot" in AI timeline - that's OK, connect them!
4. A VEO "shot" should match AI descriptions of shots, saves, blocks, etc.
5. Extract the most relevant AI description even if it's not perfectly classified
6. Include rich context and details from the AI timeline

MATCHING RULES:
- VEO goal at 92:28 → Look for AI events 92:00-92:58 (shots, celebrations, restarts)
- VEO shot at 08:08 → Look for AI events 07:38-08:38 (shots, saves, blocks)
- Use ±30 second tolerance for all matches
- Prioritize detailed AI descriptions over perfect classification

OUTPUT FORMAT:
=== DEFINITE GOALS ===
Timestamp: [AI timestamp] ([seconds])
Team: [team from AI description]
Description: [Full AI description with context]
VEO Match: Confirmed goal at [VEO timestamp] - [confidence level]

=== DEFINITE SHOTS ===  
Timestamp: [AI timestamp] ([seconds])
Team: [team from AI description]
Description: [Full AI description with context]
Outcome: [saved/missed/blocked from AI]
VEO Match: Confirmed shot at [VEO timestamp] - [confidence level]

QUALITY FOCUS:
- Timestamp-based matching (±30 seconds)
- Rich AI descriptions for engagement
- Clear confidence indicators
- Connect events intelligently, not just by classification"""

    def parse_veo_events(self, veo_data: dict) -> list:
        """Extract VEO events with timestamps"""
        events = []
        
        # Extract all events from VEO data
        for event in veo_data.get('events', []):
            event_type = event.get('event_type', '').lower()
            timestamp = event.get('timestamp', '').strip()
            
            if timestamp and event_type:
                if event_type == 'goal':
                    events.append({
                        'type': 'goal',
                        'timestamp': timestamp,
                        'team': 'unknown'  # VEO doesn't specify team in this data
                    })
                elif event_type == 'shot on goal':
                    events.append({
                        'type': 'shot',
                        'timestamp': timestamp, 
                        'team': 'unknown'  # VEO doesn't specify team in this data
                    })
        
        return events

    def build_definite_events(self, match_id: str) -> bool:
        """Create definitive events list using direct timestamp matching"""
        print(f"🎯 Building definite events for {match_id}")
        
        data_dir = Path("../data") / match_id
        veo_ground_truth_path = data_dir / "1_veo_ground_truth.json"
        ai_timeline_path = data_dir / "5_complete_timeline.txt"  # Use complete timeline, not just validated
        output_path = data_dir / "7.5_definite_events.txt"
        
        # Check input files exist
        if not veo_ground_truth_path.exists():
            print(f"❌ VEO ground truth file not found: {veo_ground_truth_path}")
            return False
            
        if not ai_timeline_path.exists():
            print(f"❌ AI timeline file not found: {ai_timeline_path}")
            return False
        
        # Read input files
        print("📥 Reading VEO ground truth and AI timeline...")
        with open(veo_ground_truth_path, 'r') as f:
            veo_data = json.load(f)
            
        with open(ai_timeline_path, 'r') as f:
            ai_timeline = f.read()
        
        # Parse VEO events
        veo_events = self.parse_veo_events(veo_data)
        if not veo_events:
            print("⚠️ No VEO events found to match")
            return False
            
        print(f"📊 Found {len(veo_events)} VEO events to match")
        
        # Generate cross-reference analysis  
        print("🧠 Cross-referencing VEO events with AI timeline...")
        cross_reference_prompt = self.get_cross_reference_prompt(veo_events, ai_timeline)
        
        try:
            response = self.model.generate_content(cross_reference_prompt)
            definite_events_content = response.text
            
            # Save definite events
            print(f"💾 Saving definite events to: {output_path}")
            with open(output_path, 'w') as f:
                f.write(f"# Definite Events - {match_id}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Method: Direct VEO timestamp matching with AI descriptions\n")
                f.write(f"# Quality: VEO events matched within ±30 seconds\n\n")
                f.write(definite_events_content)
            
            print("✅ Definite events created successfully!")
            print(f"📊 Output: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during cross-referencing: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 7.5_definite_events_builder.py <match_id>")
        print("Example: python 7.5_definite_events_builder.py newmills-20250222")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    builder = DefiniteEventsBuilder()
    success = builder.build_definite_events(match_id)
    
    if success:
        print(f"\n🎯 Definite events ready for {match_id}!")
        print("📝 Contains only VEO-validated events with rich AI descriptions")
        print("🔄 Next: Run 8.5_other_events_extractor.py for additional events")
    else:
        print(f"\n❌ Failed to build definite events for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()