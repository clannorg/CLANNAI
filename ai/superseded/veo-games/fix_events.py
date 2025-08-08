#!/usr/bin/env python3
"""
Quick fix for Green Island events - map unsupported types to supported ones
"""

import json
from pathlib import Path

def fix_event_types():
    # Read the current events
    events_file = Path("data/19-20250419/web_events_array.json")
    with open(events_file, 'r') as f:
        events = json.load(f)
    
    print(f"🔄 Fixing {len(events)} events...")
    
    # Mapping unsupported → supported event types
    type_mapping = {
        'throw_in': 'corner',       # Throw-ins become corners
        'free_kick': 'foul',        # Free kicks are from fouls
        'goal_kick': 'foul',        # Goal kicks become fouls (close enough)
        'tackle': 'foul',           # Tackles become fouls
        'tackle_foul': 'foul',      # Already a foul
        'tackle_miss': 'foul',      # Missed tackle becomes foul
        'header': 'shot',           # Headers become shots
        'dribbling': 'foul',        # Dribbling becomes foul (defensive action)
        'interception': 'foul',     # Interception becomes foul
        'stoppage': 'foul',         # Stoppage becomes foul
        'pre_match': 'foul',        # Pre-match becomes foul (will filter out)
    }
    
    # Fix each event
    fixed_events = []
    for event in events:
        old_type = event['type']
        
        # Skip pre_match events
        if old_type == 'pre_match':
            print(f"⏭️  Skipping pre_match event")
            continue
            
        # Map to supported type
        new_type = type_mapping.get(old_type, old_type)
        
        if old_type != new_type:
            print(f"🔄 {old_type} → {new_type}")
        
        # Update event
        event['type'] = new_type
        
        # Fix team names (replace spaces with underscores)
        if 'team' in event and event['team']:
            event['team'] = event['team'].lower().replace(' ', '_')
        
        fixed_events.append(event)
    
    print(f"✅ Fixed {len(fixed_events)} events (removed {len(events) - len(fixed_events)})")
    
    # Save fixed events
    with open(events_file, 'w') as f:
        json.dump(fixed_events, f, indent=2)
    
    print(f"💾 Saved to: {events_file}")
    
    # Show event type summary
    type_counts = {}
    for event in fixed_events:
        event_type = event['type']
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
    
    print(f"\n📊 FIXED EVENT SUMMARY:")
    for event_type, count in sorted(type_counts.items()):
        print(f"   {event_type}: {count}")

if __name__ == "__main__":
    fix_event_types()