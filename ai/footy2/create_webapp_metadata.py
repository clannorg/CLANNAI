#!/usr/bin/env python3
"""
Simple script to create webapp-compatible metadata file with corrected footy2 events.
Just replaces the metadata - no complex uploads or database changes.
"""

import json
import os

def create_webapp_metadata():
    """Create a simple webapp metadata file with the corrected events."""
    
    print("🎯 Creating webapp metadata with corrected footy2 events...")
    
    # Load the corrected events
    events_file = "/home/ubuntu/CLANNAI/ai/footy2/outputs/leo1/web_events_array.json"
    with open(events_file, 'r') as f:
        corrected_events = json.load(f)
    
    # Load team config
    team_config_file = "/home/ubuntu/CLANNAI/ai/footy2/outputs/leo1/team_config.json"
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    # Calculate team scores
    team_scores = {"clann": 0, "lostthehead": 0}
    for event in corrected_events:
        if event["type"] == "goal":
            team_scores[event["team"]] += 1
    
    # Create webapp-compatible metadata
    webapp_metadata = {
        "title": "Footy2: Clann vs Lostthehead (Corrected Events)",
        "description": f"5-a-side match with corrected goal events. Final Score: Clann {team_scores['clann']} - {team_scores['lostthehead']} Lostthehead",
        "video_url": "https://end-nov-webapp-clann.s3.amazonaws.com/analysis-videos/leo1-video-mp4.mp4",
        "events": corrected_events,
        "teams": {
            "clann": {
                "name": "Clann",
                "color": "#FFFFFF",
                "goals": team_scores["clann"],
                "description": "No bibs/colours team"
            },
            "lostthehead": {
                "name": "Lostthehead", 
                "color": "#FFA500",
                "goals": team_scores["lostthehead"],
                "description": "Orange bibs team"
            }
        },
        "match_info": {
            "duration": "52:00",
            "total_events": len(corrected_events),
            "total_goals": sum(team_scores.values()),
            "match_type": "5-a-side",
            "correction_notes": "Events manually corrected based on actual match detection"
        },
        "metadata": {
            "analysis_date": "2025-08-22",
            "ai_model": "clann-v4-corrected",
            "source": "footy2-leo1"
        }
    }
    
    # Save the webapp metadata
    output_file = "/home/ubuntu/CLANNAI/ai/footy2/outputs/leo1/webapp_metadata.json"
    with open(output_file, 'w') as f:
        json.dump(webapp_metadata, f, indent=2)
    
    print(f"✅ Created webapp metadata: {output_file}")
    print(f"📊 Total events: {len(corrected_events)}")
    print(f"⚽ Final score: Clann {team_scores['clann']} - {team_scores['lostthehead']} Lostthehead")
    print(f"🎬 Video URL: {webapp_metadata['video_url']}")
    
    print(f"\n🎯 To use this in the webapp:")
    print(f"   1. Copy the events array from: {output_file}")
    print(f"   2. Paste into your webapp's game data")
    print(f"   3. The corrected events will display in the timeline")
    
    return output_file

if __name__ == "__main__":
    create_webapp_metadata()
