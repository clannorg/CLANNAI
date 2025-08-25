#!/usr/bin/env python3
"""
Update footy2 events with corrected goal data from actual match detection.

This script replaces the original AI-detected events with the corrected events
that were manually verified from the actual match footage.
"""

import json
import os
from typing import List, Dict, Any

def parse_corrected_events() -> List[Dict[str, Any]]:
    """Parse the corrected events from the user's data into structured format."""
    
    # Corrected events data from user (converted from MM:SS to seconds)
    corrected_events = [
        {"time": "3:01", "team": "Lostthehead", "description": "The ball is seen hitting the back of the net of the no bibs/colours team"},
        {"time": "5:22", "team": "Lostthehead", "description": "The ball is seen hitting the back of the net of the no bibs/colours team"},
        {"time": "6:27", "team": "Clann", "description": "A right-footed shot from just outside the penalty area goes into the top right corner of the goal."},
        {"time": "6:53", "team": "Clann", "description": "A player in a white shirt shoots from distance, and the ball goes low into the bottom left corner."},
        {"time": "8:49", "team": "Clann", "description": "A powerful shot hits the top bar of the goal and deflects down into the net."},
        {"time": "13:03", "team": "Lostthehead", "description": "A long-range shot from just behind the halfway line goes into the goal."},
        {"time": "15:05", "team": "Clann", "description": "A powerful shot hits the inside of the left goalpost and deflects into the net."},
        {"time": "23:00", "team": "Clann", "description": "White jersey player scores another screamer"},
        {"time": "26:00", "team": "Clann", "description": "Outside of boot"},
        {"time": "26:21", "team": "Lostthehead", "description": "A long-range shot from behind the center line goes into the top left corner."},
        {"time": "27:38", "team": "Lostthehead", "description": "A shot from just outside the center circle goes into the bottom left of the goal."},
        {"time": "29:45", "team": "Clann", "description": "A goal is inferred from the players resetting for a kickoff."},
        {"time": "32:20", "team": "Clann", "description": "A shot from the left just outside the penalty area goes into the bottom left corner of the goal."},
        {"time": "34:10", "team": "Lostthehead", "description": "A powerful, low shot with the left foot goes into the bottom corner of the net."},
        {"time": "34:57", "team": "Clann", "description": "A shot from the left side flies into the top right corner of the net."},
        {"time": "35:30", "team": "Clann", "description": "A shot hits the underside of the crossbar and bounces down over the goal line."},
        {"time": "36:33", "team": "Clann", "description": "outside frame"},
        {"time": "37:04", "team": "Lostthehead", "description": ""},
        {"time": "39:55", "team": "Lostthehead", "description": ""},
        {"time": "49:17", "team": "Clann", "description": "A long-range shot from just outside the center circle goes into the top left corner of the goal."},
        {"time": "50:25", "team": "Clann", "description": "A shot from near the center circle line goes into the bottom left of the net."},
        {"time": "51:20", "team": "Lostthehead", "description": ""},
        {"time": "51:57", "team": "Clann", "description": "White jersey far post"},
    ]
    
    def time_to_seconds(time_str: str) -> int:
        """Convert MM:SS format to seconds."""
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1])
        return minutes * 60 + seconds
    
    # Convert to the webapp format
    webapp_events = []
    for i, event in enumerate(corrected_events):
        # Map team names to match the existing configuration
        team_mapping = {
            "Clann": "clann",
            "Lostthehead": "lostthehead"
        }
        
        # Determine original team name based on team
        original_team_mapping = {
            "clann": "no bibs/colours",
            "lostthehead": "orange bibs"
        }
        
        team = team_mapping.get(event["team"], event["team"].lower())
        
        webapp_event = {
            "timestamp": time_to_seconds(event["time"]),
            "type": "goal",
            "team": team,
            "description": event["description"] if event["description"] else f"Goal scored by {event['team']}",
            "excitement_level": 8,  # Default excitement level
            "original_team_name": original_team_mapping.get(team, "unknown")
        }
        webapp_events.append(webapp_event)
    
    # Sort by timestamp
    webapp_events.sort(key=lambda x: x["timestamp"])
    
    return webapp_events

def update_events_file(corrected_events: List[Dict[str, Any]], output_dir: str):
    """Update the web_events_array.json file with corrected events."""
    
    events_file = os.path.join(output_dir, "web_events_array.json")
    
    # Backup original file
    backup_file = events_file + ".backup"
    if os.path.exists(events_file):
        with open(events_file, 'r') as f:
            original_data = json.load(f)
        with open(backup_file, 'w') as f:
            json.dump(original_data, f, indent=2)
        print(f"✅ Backed up original events to {backup_file}")
    
    # Write corrected events
    with open(events_file, 'w') as f:
        json.dump(corrected_events, f, indent=2)
    
    print(f"✅ Updated {events_file} with {len(corrected_events)} corrected events")

def update_webapp_metadata(corrected_events: List[Dict[str, Any]], output_dir: str):
    """Update webapp metadata files with corrected event counts and scores."""
    
    # Calculate team scores
    team_scores = {"clann": 0, "lostthehead": 0}
    for event in corrected_events:
        if event["type"] == "goal":
            team_scores[event["team"]] += 1
    
    print(f"📊 Final Score: Clann {team_scores['clann']} - {team_scores['lostthehead']} Lostthehead")
    
    # Update webapp_complete.json if it exists
    webapp_complete_file = os.path.join(output_dir, "webapp_complete.json")
    if os.path.exists(webapp_complete_file):
        with open(webapp_complete_file, 'r') as f:
            webapp_data = json.load(f)
        
        # Update events array
        webapp_data["events"] = corrected_events
        
        # Update metadata if present
        if "metadata" in webapp_data:
            webapp_data["metadata"]["total_events"] = len(corrected_events)
            webapp_data["metadata"]["total_goals"] = sum(team_scores.values())
        
        # Backup and save
        backup_file = webapp_complete_file + ".backup"
        with open(backup_file, 'w') as f:
            json.dump(webapp_data, f, indent=2)
        
        with open(webapp_complete_file, 'w') as f:
            json.dump(webapp_data, f, indent=2)
        
        print(f"✅ Updated {webapp_complete_file}")
    
    # Update match_metadata.json if it exists
    metadata_file = os.path.join(output_dir, "match_metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Update event counts
        metadata["total_events"] = len(corrected_events)
        metadata["total_goals"] = sum(team_scores.values())
        metadata["team_scores"] = team_scores
        
        # Backup and save
        backup_file = metadata_file + ".backup"
        with open(backup_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Updated {metadata_file}")

def main():
    """Main function to update footy2 events with corrected data."""
    
    print("🚀 Updating footy2 events with corrected goal data...")
    
    # Parse corrected events
    print("📝 Parsing corrected events...")
    corrected_events = parse_corrected_events()
    print(f"✅ Parsed {len(corrected_events)} corrected events")
    
    # Define output directory
    output_dir = "/home/ubuntu/CLANNAI/ai/footy2/outputs/leo1"
    
    if not os.path.exists(output_dir):
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    # Update events file
    print("📁 Updating events file...")
    update_events_file(corrected_events, output_dir)
    
    # Update webapp metadata
    print("🔧 Updating webapp metadata...")
    update_webapp_metadata(corrected_events, output_dir)
    
    print("🎉 Successfully updated footy2 events with corrected data!")
    print("\nSummary:")
    print(f"- Total events: {len(corrected_events)}")
    
    # Count goals per team
    team_goals = {}
    for event in corrected_events:
        if event["type"] == "goal":
            team_goals[event["team"]] = team_goals.get(event["team"], 0) + 1
    
    for team, goals in team_goals.items():
        print(f"- {team.title()}: {goals} goals")

if __name__ == "__main__":
    main()
