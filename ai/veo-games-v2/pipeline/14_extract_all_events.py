#!/usr/bin/env python3
"""
14. Extract All Events
Quick script to extract ALL events from mega_analysis.json into a comprehensive web_events_array.json
"""

import sys
import json
from pathlib import Path

def time_to_seconds(time_str):
    """Converts 'MM:SS' or 'HH:MM:SS' string to seconds."""
    if not time_str or time_str == "N/A":
        return 0
    parts = [int(p) for p in time_str.split(':')]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0

def extract_all_events(match_id):
    """Extract ALL events from mega_analysis.json"""
    output_dir = Path("../outputs") / match_id
    mega_analysis_path = output_dir / "mega_analysis.json"
    
    if not mega_analysis_path.exists():
        print(f"❌ Error: mega_analysis.json not found at {mega_analysis_path}")
        return
    
    with open(mega_analysis_path, 'r') as f:
        mega_analysis = json.load(f)
    
    events = []
    
    print("🎯 Extracting verified goals...")
    # Extract verified goals
    for goal in mega_analysis.get('goals_analysis', {}).get('verified_goals', []):
        team_name = goal.get('team', 'Unknown Team')
        veo_time = goal.get('veo_timestamp', '0:00')
        timestamp = time_to_seconds(veo_time)
        events.append({
            "type": "goal",
            "timestamp": timestamp,
            "team": "red" if "black" in team_name.lower() or "white" in team_name.lower() else "blue",
            "description": f"{team_name} scores"
        })
    
    print("🎯 Extracting verified shots...")
    # Extract verified shots
    for shot in mega_analysis.get('shots_analysis', {}).get('verified_shots', []):
        team_name = shot.get('team', 'Unknown Team')
        veo_time = shot.get('veo_timestamp', '0:00')
        timestamp = time_to_seconds(veo_time)
        events.append({
            "type": "shot",
            "timestamp": timestamp,
            "team": "red" if "black" in team_name.lower() or "white" in team_name.lower() else "blue",
            "description": f"{team_name} shot"
        })
    
    print("🎯 Extracting fouls and cards...")
    # Extract fouls against blue team (committed by black/white)
    fouls_cards = mega_analysis.get('other_significant_events', {}).get('fouls_cards', {})
    for foul in fouls_cards.get('fouls_against_blue_team', []):
        timestamp_str = foul.get('timestamp', '0:00')
        timestamp = time_to_seconds(timestamp_str)
        note = foul.get('note')
        description = f"Black/White team foul" + (f" ({note})" if note else "")
        events.append({
            "type": "foul",
            "timestamp": timestamp,
            "team": "red",  # Black/White team committed the foul
            "description": description
        })
    
    # Extract fouls against black/white team (committed by blue)
    for foul in fouls_cards.get('fouls_against_black_white_team', []):
        timestamp_str = foul.get('timestamp', '0:00')
        timestamp = time_to_seconds(timestamp_str)
        note = foul.get('note')
        description = f"Blue team foul" + (f" ({note})" if note else "")
        events.append({
            "type": "foul",
            "timestamp": timestamp,
            "team": "blue",  # Blue team committed the foul
            "description": description
        })
    
    # Extract yellow cards
    for card in fouls_cards.get('yellow_cards', []):
        team_name = card.get('team', 'Unknown')
        timestamp_str = card.get('timestamp', '0:00')
        timestamp = time_to_seconds(timestamp_str)
        events.append({
            "type": "card",
            "timestamp": timestamp,
            "team": "red" if "black" in team_name.lower() or "white" in team_name.lower() else "blue",
            "description": f"{team_name} yellow card"
        })
    
    print("🎯 Extracting set pieces...")
    # Extract set pieces for both teams
    set_pieces = mega_analysis.get('other_significant_events', {}).get('set_pieces', {})
    
    # Black/White team set pieces
    bw_set_pieces = set_pieces.get('black_white_team', {})
    for fk in bw_set_pieces.get('free_kicks', []):
        timestamp = time_to_seconds(fk.get('timestamp', '0:00'))
        note = fk.get('note')
        description = f"Black/White free kick" + (f" ({note})" if note else "")
        events.append({
            "type": "freekick",
            "timestamp": timestamp,
            "team": "red",
            "description": description
        })
    
    for corner in bw_set_pieces.get('corners', []):
        timestamp = time_to_seconds(corner.get('timestamp', '0:00'))
        note = corner.get('note')
        description = f"Black/White corner" + (f" ({note})" if note else "")
        events.append({
            "type": "corner",
            "timestamp": timestamp,
            "team": "red",
            "description": description
        })
    
    for throw in bw_set_pieces.get('throw_ins', []):
        timestamp = time_to_seconds(throw.get('timestamp', '0:00'))
        events.append({
            "type": "throwin",
            "timestamp": timestamp,
            "team": "red",
            "description": "Black/White throw-in"
        })
    
    # Blue team set pieces
    blue_set_pieces = set_pieces.get('blue_team', {})
    for fk in blue_set_pieces.get('free_kicks', []):
        timestamp = time_to_seconds(fk.get('timestamp', '0:00'))
        note = fk.get('note')
        description = f"Blue free kick" + (f" ({note})" if note else "")
        events.append({
            "type": "freekick",
            "timestamp": timestamp,
            "team": "blue",
            "description": description
        })
    
    for corner in blue_set_pieces.get('corners', []):
        timestamp = time_to_seconds(corner.get('timestamp', '0:00'))
        note = corner.get('note')
        description = f"Blue corner" + (f" ({note})" if note else "")
        events.append({
            "type": "corner",
            "timestamp": timestamp,
            "team": "blue",
            "description": description
        })
    
    for throw in blue_set_pieces.get('throw_ins', []):
        timestamp = time_to_seconds(throw.get('timestamp', '0:00'))
        events.append({
            "type": "throwin",
            "timestamp": timestamp,
            "team": "blue",
            "description": "Blue throw-in"
        })
    
    print("🎯 Extracting turnovers...")
    # Extract turnovers - these are stored as timestamp examples, not detailed objects
    turnovers = mega_analysis.get('other_significant_events', {}).get('turnovers_possession_changes', {})
    for timestamp_str in turnovers.get('examples', []):
        timestamp = time_to_seconds(timestamp_str)
        events.append({
            "type": "turnover",
            "timestamp": timestamp,
            "team": "neutral",  # Don't know which team, so neutral
            "description": "Possession change"
        })
    
    print("🎯 Extracting stoppages...")
    # Extract stoppages/injuries - these are also stored as timestamp examples
    stoppages = mega_analysis.get('other_significant_events', {}).get('stoppages_injuries', {})
    for timestamp_str in stoppages.get('examples', []):
        timestamp = time_to_seconds(timestamp_str)
        events.append({
            "type": "stoppage",
            "timestamp": timestamp,
            "team": "neutral",
            "description": "Match stoppage"
        })
    
    # Sort events by timestamp
    events.sort(key=lambda x: x['timestamp'])
    
    print(f"✅ Extracted {len(events)} total events")
    print(f"   - Goals: {len([e for e in events if e['type'] == 'goal'])}")
    print(f"   - Shots: {len([e for e in events if e['type'] == 'shot'])}")
    print(f"   - Fouls: {len([e for e in events if e['type'] == 'foul'])}")
    print(f"   - Cards: {len([e for e in events if e['type'] == 'card'])}")
    print(f"   - Free kicks: {len([e for e in events if e['type'] == 'freekick'])}")
    print(f"   - Corners: {len([e for e in events if e['type'] == 'corner'])}")
    print(f"   - Throw-ins: {len([e for e in events if e['type'] == 'throwin'])}")
    print(f"   - Other: {len([e for e in events if e['type'] not in ['goal', 'shot', 'foul', 'card', 'freekick', 'corner', 'throwin']])}")
    
    # Save comprehensive events
    web_events_array_path = output_dir / "web_events_array.json"
    with open(web_events_array_path, 'w') as f:
        json.dump(events, f, indent=2)
    print(f"✅ Saved: {web_events_array_path}")
    
    # Save legacy format
    web_events_path = output_dir / "web_events.json"
    with open(web_events_path, 'w') as f:
        json.dump({"events": events}, f, indent=2)
    print(f"✅ Saved: {web_events_path}")
    
    return events

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 14_extract_all_events.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    try:
        events = extract_all_events(match_id)
        print(f"\n🎉 COMPLETE! Generated {len(events)} events for webapp")
        print("💾 Files ready for S3 upload")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        sys.exit(1)