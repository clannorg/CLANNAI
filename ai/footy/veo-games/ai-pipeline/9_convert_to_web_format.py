#!/usr/bin/env python3
"""
9. Convert to Web Format
Converts AI pipeline outputs to web app compatible JSON format
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

class WebFormatConverter:
    def __init__(self):
        """Initialize converter with web app event format specifications"""
        # Web app event types with colors (from VIDEO_PLAYER_JSON_FORMAT.md)
        self.supported_event_types = {
            'goal': 'Goals scored',
            'shot': 'Shot attempts', 
            'save': 'Goalkeeper save',
            'foul': 'Fouls committed',
            'yellow_card': 'Yellow card shown',
            'red_card': 'Red card shown',
            'substitution': 'Player substitution',
            'corner': 'Corner kick',
            'offside': 'Offside call'
        }
        
        print(f"🔄 Web Format Converter initialized")

    def parse_timestamp_to_seconds(self, timestamp_str):
        """Convert timestamp string (MM:SS or HH:MM:SS) to seconds"""
        if not timestamp_str:
            return 0
            
        # Clean timestamp string
        timestamp_str = timestamp_str.strip()
        
        # Handle different timestamp formats
        if ':' in timestamp_str:
            parts = timestamp_str.split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS  
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        
        return 0

    def extract_team_from_description(self, description):
        """Extract team information from event description"""
        description_lower = description.lower()
        
        # Common team identifiers
        if any(word in description_lower for word in ['red team', 'red player', 'red']):
            return 'red'
        elif any(word in description_lower for word in ['black team', 'black player', 'black']):
            return 'black'
        elif any(word in description_lower for word in ['yellow team', 'yellow player', 'yellow']):
            return 'yellow'
        elif any(word in description_lower for word in ['blue team', 'blue player', 'blue']):
            return 'blue'
        elif any(word in description_lower for word in ['home team', 'home']):
            return 'home'
        elif any(word in description_lower for word in ['away team', 'away']):
            return 'away'
            
        return None

    def parse_validated_timeline(self, timeline_path):
        """Parse the AI-validated timeline text file"""
        events = []
        
        try:
            with open(timeline_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Failed to read timeline file: {e}")
            return events

        # Parse goals section
        goals_section = re.search(r'### VALIDATED GOALS\s*\n(.*?)(?=### |$)', content, re.DOTALL)
        if goals_section:
            goals_text = goals_section.group(1)
            
            # Extract individual goals
            goal_matches = re.finditer(r'\*\*Timestamp:\*\*\s*(\d{2}:\d{2})\s*\n.*?\*\*Scoring Team:\*\*\s*(.*?)\n.*?\*\*Description:\*\*\s*(.*?)(?=\n.*?\*\*|$)', goals_text, re.DOTALL)
            
            for match in goal_matches:
                timestamp_str = match.group(1)
                team_info = match.group(2).strip()
                description = match.group(3).strip()
                
                # Clean up description
                description = re.sub(r'\n.*?\*\*.*?\*\*.*', '', description, flags=re.DOTALL).strip()
                
                # Convert timestamp to seconds
                timestamp_seconds = self.parse_timestamp_to_seconds(timestamp_str)
                
                # Extract team
                team = self.extract_team_from_description(team_info) or self.extract_team_from_description(description)
                
                event = {
                    "type": "goal",
                    "timestamp": timestamp_seconds,
                    "description": description,
                }
                
                if team:
                    event["team"] = team
                    
                events.append(event)

        # Parse shots section (if exists)
        shots_section = re.search(r'### VALIDATED SHOTS\s*\n(.*?)(?=### |$)', content, re.DOTALL)
        if shots_section:
            shots_text = shots_section.group(1)
            
            # Extract individual shots
            shot_matches = re.finditer(r'\*\*Timestamp:\*\*\s*(\d{2}:\d{2})\s*\n.*?\*\*Team:\*\*\s*(.*?)\n.*?\*\*Description:\*\*\s*(.*?)(?=\n.*?\*\*|$)', shots_text, re.DOTALL)
            
            for match in shot_matches:
                timestamp_str = match.group(1)
                team_info = match.group(2).strip()
                description = match.group(3).strip()
                
                # Clean up description
                description = re.sub(r'\n.*?\*\*.*?\*\*.*', '', description, flags=re.DOTALL).strip()
                
                # Convert timestamp to seconds
                timestamp_seconds = self.parse_timestamp_to_seconds(timestamp_str)
                
                # Extract team
                team = self.extract_team_from_description(team_info) or self.extract_team_from_description(description)
                
                event = {
                    "type": "shot",
                    "timestamp": timestamp_seconds,
                    "description": description,
                }
                
                if team:
                    event["team"] = team
                    
                events.append(event)

        return events

    def parse_goals_shots_json(self, json_path):
        """Parse the goals_and_shots_timeline.json file as backup"""
        events = []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read JSON file: {e}")
            return events

        # Extract goals
        goals = data.get('goals_and_shots_analysis', {}).get('goals', [])
        for goal in goals:
            team = None
            if 'team' in goal:
                team_str = goal['team'].lower()
                if 'red' in team_str:
                    team = 'red'
                elif 'black' in team_str:
                    team = 'black'
                elif 'yellow' in team_str:
                    team = 'yellow'
                elif 'blue' in team_str:
                    team = 'blue'

            event = {
                "type": "goal",
                "timestamp": goal.get('precise_seconds', 0),
                "description": goal.get('description', 'Goal scored'),
            }
            
            if team:
                event["team"] = team
                
            events.append(event)

        # Extract shots
        shots_saved = data.get('goals_and_shots_analysis', {}).get('shots_saved', [])
        shots_wide = data.get('goals_and_shots_analysis', {}).get('shots_wide', [])
        
        for shot in shots_saved + shots_wide:
            team = None
            if 'team' in shot:
                team_str = shot['team'].lower()
                if 'red' in team_str:
                    team = 'red'
                elif 'black' in team_str:
                    team = 'black'
                elif 'yellow' in team_str:
                    team = 'yellow'
                elif 'blue' in team_str:
                    team = 'blue'

            event = {
                "type": "shot",
                "timestamp": shot.get('precise_seconds', 0),
                "description": shot.get('description', 'Shot attempt'),
            }
            
            if team:
                event["team"] = team
                
            events.append(event)

        return events

    def convert_match_to_web_format(self, match_id):
        """Convert AI pipeline outputs to web app format"""
        print(f"🔄 Converting {match_id} to web format")
        
        # Define paths
        data_dir = Path("../data") / match_id
        if not data_dir.exists():
            print(f"❌ Data directory not found: {data_dir}")
            return False

        # Try validated timeline first (most accurate)
        validated_timeline_path = data_dir / "6_validated_timeline.txt"
        events = []
        
        if validated_timeline_path.exists():
            print(f"📖 Reading validated timeline: {validated_timeline_path}")
            events = self.parse_validated_timeline(validated_timeline_path)
            print(f"✅ Extracted {len(events)} events from validated timeline")
        else:
            # Fallback to JSON format
            json_timeline_path = data_dir / "goals_and_shots_timeline.json"
            if json_timeline_path.exists():
                print(f"📖 Reading JSON timeline: {json_timeline_path}")
                events = self.parse_goals_shots_json(json_timeline_path)
                print(f"✅ Extracted {len(events)} events from JSON timeline")
            else:
                print(f"❌ No timeline files found in {data_dir}")
                return False

        if not events:
            print(f"⚠️  No events found to convert")
            return False

        # Sort events by timestamp
        events.sort(key=lambda x: x['timestamp'])

        # Create web app compatible JSON
        web_events = {
            "match_id": match_id,
            "generated_timestamp": datetime.now().isoformat(),
            "events_count": len(events),
            "source": "clann_ai_pipeline",
            "events": events
        }

        # Save web-compatible events file
        web_events_path = data_dir / "web_events.json"
        try:
            with open(web_events_path, 'w', encoding='utf-8') as f:
                json.dump(web_events, f, indent=2, ensure_ascii=False)
            print(f"✅ Web events saved to: {web_events_path}")
        except Exception as e:
            print(f"❌ Failed to save web events: {e}")
            return False

        # Also save just the events array (direct format)
        events_array_path = data_dir / "web_events_array.json"
        try:
            with open(events_array_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            print(f"✅ Events array saved to: {events_array_path}")
        except Exception as e:
            print(f"❌ Failed to save events array: {e}")

        # Print summary for easy copy-paste
        print(f"\n📋 COPY-PASTE SUMMARY:")
        print(f"   🎯 Match: {match_id}")
        print(f"   📊 Events: {len(events)} total")
        print(f"   📁 Web Events File: {web_events_path}")
        
        # Show sample events
        print(f"\n🎮 Sample Events:")
        for i, event in enumerate(events[:5]):
            timestamp_min = event['timestamp'] // 60
            timestamp_sec = event['timestamp'] % 60
            print(f"   {i+1}. {timestamp_min:02d}:{timestamp_sec:02d} - {event['type'].upper()} - {event['description'][:50]}")
        
        if len(events) > 5:
            print(f"   ... and {len(events) - 5} more events")

        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 9_convert_to_web_format.py <match_id>")
        sys.exit(1)

    match_id = sys.argv[1]
    converter = WebFormatConverter()
    
    success = converter.convert_match_to_web_format(match_id)
    
    if success:
        print(f"\n🎉 Conversion completed for {match_id}")
        print(f"🌐 Files ready for web app integration")
    else:
        print(f"\n❌ Conversion failed for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()