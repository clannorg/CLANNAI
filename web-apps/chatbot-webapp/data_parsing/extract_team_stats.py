#!/usr/bin/env python3
"""
Team Statistics Extractor
---
Extracts key event statistics for both teams in a match from tactical data.
Produces a concise, balanced JSON output that ensures consistent counting for both teams.

Usage: python extract_team_stats.py ../input_data/td.json team_stats.json
"""

import json
import sys
import os
from collections import Counter

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def extract_team_stats(tactical_data):
    """Extract key statistics for both teams, ensuring balanced metrics."""
    if not tactical_data or 'metadata' not in tactical_data or 'data' not in tactical_data:
        return {"error": "Invalid tactical data format"}
    
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    
    # Get team information
    home_team = metadata['home_team']['name']
    away_team = metadata['away_team']['name']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    
    # Load event labels from schema if available
    event_labels = {}
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "input_data", "tactical-data-schema.json")
    if os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
                if 'labels' in schema and 'events' in schema['labels']:
                    event_labels = schema['labels']['events']
        except Exception as e:
            print(f"Warning: Could not load schema: {e}")
    
    # Count events by type for each team
    home_events = Counter()
    away_events = Counter()
    
    # Process all events with consistent naming
    for event in events:
        team_uuid = event['team_uuid']
        event_type = event['type']
        
        # Use consistent event name mapping from schema
        event_name = event_labels.get(event_type, event_type)
        
        if team_uuid == home_uuid:
            home_events[event_name] += 1
        elif team_uuid == away_uuid:
            away_events[event_name] += 1
    
    # Calculate possession percentages
    total_events = len(events)
    home_possession = round(sum(home_events.values()) / total_events * 100, 1)
    away_possession = round(sum(away_events.values()) / total_events * 100, 1)
    
    # Add possession to the stats
    home_events['Possession %'] = home_possession
    away_events['Possession %'] = away_possession
    
    # Calculate passing stats
    home_pass_completed = (home_events.get('Completed Forward Pass', 0) + 
                          home_events.get('Completed Horizontal Pass', 0) + 
                          home_events.get('Completed Backward Pass', 0))
    
    home_pass_attempted = home_pass_completed + (
                          home_events.get('Uncompleted Forward Pass', 0) + 
                          home_events.get('Uncompleted Horizontal Pass', 0) + 
                          home_events.get('Uncompleted Backward Pass', 0))
    
    away_pass_completed = (away_events.get('Completed Forward Pass', 0) + 
                          away_events.get('Completed Horizontal Pass', 0) + 
                          away_events.get('Completed Backward Pass', 0))
    
    away_pass_attempted = away_pass_completed + (
                          away_events.get('Uncompleted Forward Pass', 0) + 
                          away_events.get('Uncompleted Horizontal Pass', 0) + 
                          away_events.get('Uncompleted Backward Pass', 0))
    
    # Add passing stats
    if home_pass_attempted > 0:
        home_events['Pass Completion %'] = round(home_pass_completed / home_pass_attempted * 100, 1)
    else:
        home_events['Pass Completion %'] = 0
        
    if away_pass_attempted > 0:
        away_events['Pass Completion %'] = round(away_pass_completed / away_pass_attempted * 100, 1)
    else:
        away_events['Pass Completion %'] = 0
    
    # Categorize events for analysis
    categories = {
        "Attacking": [
            "Running Into The Box", "Occupying Space In The Box", "Cross Into The Box",
            "Finishing", "Finishing Pass", "Goal Chance", "Goal Assist"
        ],
        "Possession": [
            "Completed Forward Pass", "Completed Horizontal Pass", "Completed Backward Pass",
            "Possession After Recovery", "Width Of The Team"
        ],
        "Defensive": [
            "Defending Against The Possessor", "Defending Running Into The Box",
            "Defensive Line Imbalance In Depth", "Defensive Line Imbalance In Width",
            "Marking Opponents Inside The Box", "Recovered Ball"
        ],
        "Pressing": [
            "Pressure On The Ball Possessor", "Press After Loss"
        ],
        "Transitions": [
            "Balance Of The Team After Loss", "Balance Of The Team After Recovery",
            "Progression After Recovery"
        ]
    }
    
    # Count events by category
    home_categories = {cat: sum(home_events.get(event, 0) for event in events) 
                      for cat, events in categories.items()}
    away_categories = {cat: sum(away_events.get(event, 0) for event in events)
                      for cat, events in categories.items()}
    
    # Calculate ball recoveries and pressing efficiency
    home_recoveries = home_events.get('Recovered Ball', 0)
    home_pressing = home_events.get('Pressure On The Ball Possessor', 0)
    
    away_recoveries = away_events.get('Recovered Ball', 0)
    away_pressing = away_events.get('Pressure On The Ball Possessor', 0)
    
    home_events['Pressing Actions'] = home_pressing
    home_events['Ball Recoveries'] = home_recoveries
    if home_pressing > 0:
        home_events['Recovery Percentage'] = round(home_recoveries / home_pressing * 100, 1)
    else:
        home_events['Recovery Percentage'] = 0
    
    away_events['Pressing Actions'] = away_pressing
    away_events['Ball Recoveries'] = away_recoveries
    if away_pressing > 0:
        away_events['Recovery Percentage'] = round(away_recoveries / away_pressing * 100, 1)
    else:
        away_events['Recovery Percentage'] = 0
    
    # Calculate horizontal vs forward passing ratios
    home_horizontal = home_events.get('Completed Horizontal Pass', 0)
    home_forward = home_events.get('Completed Forward Pass', 0)
    
    away_horizontal = away_events.get('Completed Horizontal Pass', 0)
    away_forward = away_events.get('Completed Forward Pass', 0)
    
    if home_forward > 0:
        home_events['Horizontal Passes'] = home_horizontal
        home_events['Forward Passes'] = home_forward
        home_events['Horizontal to Forward Ratio'] = round(home_horizontal / home_forward, 2)
    else:
        home_events['Horizontal Passes'] = home_horizontal
        home_events['Forward Passes'] = home_forward
        home_events['Horizontal to Forward Ratio'] = 0
    
    if away_forward > 0:
        away_events['Horizontal Passes'] = away_horizontal
        away_events['Forward Passes'] = away_forward
        away_events['Horizontal to Forward Ratio'] = round(away_horizontal / away_forward, 2)
    else:
        away_events['Horizontal Passes'] = away_horizontal
        away_events['Forward Passes'] = away_forward
        away_events['Horizontal to Forward Ratio'] = 0
    
    # Ensure both teams have the same event types (with zero counts if needed)
    all_event_types = set(list(home_events.keys()) + list(away_events.keys()))
    for event_type in all_event_types:
        if event_type not in home_events:
            home_events[event_type] = 0
        if event_type not in away_events:
            away_events[event_type] = 0
    
    # Prepare final statistics
    match_stats = {
        "match_info": {
            "home_team": home_team,
            "away_team": away_team,
            "score": f"{metadata.get('home_team_score', 0)} - {metadata.get('away_team_score', 0)}",
            "match_date": metadata.get('date', 'Unknown'),
            "venue": metadata.get('venue', {}).get('name', 'Unknown'),
            "total_events": total_events
        },
        "team_stats": {
            home_team: dict(home_events),
            away_team: dict(away_events)
        },
        "category_stats": {
            home_team: home_categories,
            away_team: away_categories
        }
    }
    
    return match_stats

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_team_stats.py tactical_data.json output.json")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Load tactical data
    tactical_data = load_json_file(input_path)
    
    # Extract team statistics
    team_stats = extract_team_stats(tactical_data)
    
    # Write to output file
    with open(output_path, 'w') as f:
        json.dump(team_stats, f, indent=2)
    
    print(f"Team statistics extracted and saved to {output_path}")
    
    # Print a summary
    if "error" not in team_stats:
        teams = list(team_stats["team_stats"].keys())
        print("\nMatch Summary:")
        print(f"  {teams[0]} vs {teams[1]}")
        print(f"  Score: {team_stats['match_info']['score']}")
        print(f"  Total Events: {team_stats['match_info']['total_events']}")
        print("\nKey Statistics:")
        
        common_stats = [
            "Possession %", "Pass Completion %", "Horizontal Passes", "Forward Passes", 
            "Pressing Actions", "Ball Recoveries", "Recovery Percentage"
        ]
        
        # Print key stats in a table format
        print(f"{'Statistic':<25} {teams[0]:<15} {teams[1]:<15}")
        print("-" * 55)
        
        for stat in common_stats:
            team1_val = team_stats["team_stats"][teams[0]].get(stat, 0)
            team2_val = team_stats["team_stats"][teams[1]].get(stat, 0)
            print(f"{stat:<25} {team1_val:<15} {team2_val:<15}")

if __name__ == "__main__":
    main() 