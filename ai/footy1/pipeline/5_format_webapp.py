#!/usr/bin/env python3
"""
5. Format for Webapp
Convert highlights data into webapp-compatible JSON format
"""

import sys
import json
from pathlib import Path

def format_for_webapp(highlights_data: dict, team_config: dict, match_id: str) -> dict:
    """Convert highlights data to webapp format"""
    
    # Extract highlights and format for timeline
    timeline_events = []
    
    if 'highlights' in highlights_data:
        for highlight in highlights_data['highlights']:
            # Convert timestamp to seconds for webapp
            timestamp_str = highlight.get('timestamp', '00:00')
            try:
                minutes, seconds = map(int, timestamp_str.split(':'))
                timestamp_seconds = minutes * 60 + seconds
            except:
                timestamp_seconds = 0
            
            # Use actual colors from team config (repeatable for any colors)
            team = highlight.get('team', '')
            # Map to team colors from config
            if 'non-bibs' in team.lower() or 'non bibs' in team.lower():
                team_color = team_config['team_a']['colors']  # e.g. "non bibs / colours"
            elif 'orange' in team.lower() or 'bibs' in team.lower():
                team_color = team_config['team_b']['colors']  # e.g. "orange bibs"
            else:
                team_color = 'neutral'
            
            # Format event for webapp
            event = {
                'timestamp': timestamp_seconds,
                'type': highlight.get('type', 'moment'),
                'team': team_color,
                'description': highlight.get('description', ''),
                'excitement_level': highlight.get('excitement_level', 5),
                'original_team_name': team
            }
            
            timeline_events.append(event)
    
    # Sort events by timestamp
    timeline_events.sort(key=lambda x: x['timestamp'])
    
    # Create webapp-compatible structure
    webapp_data = {
        'match_id': match_id,
        'match_type': '5-a-side',
        'teams': {
            'team_a': {
                'name': team_config['team_a']['name'],
                'colors': team_config['team_a']['colors'],
                'webapp_color': 'red'
            },
            'team_b': {
                'name': team_config['team_b']['name'],
                'colors': team_config['team_b']['colors'],
                'webapp_color': 'blue'
            }
        },
        'match_summary': highlights_data.get('match_summary', 'No summary available'),
        'final_score': highlights_data.get('final_score', 'Unknown'),
        'total_highlights': len(timeline_events),
        'timeline_events': timeline_events,
        'top_moments': highlights_data.get('top_moments', []),
        'generated_at': str(Path(__file__).parent.parent / 'outputs' / match_id)
    }
    
    return webapp_data

def create_match_metadata(webapp_data: dict, match_id: str) -> dict:
    """Create metadata file for the match in v3 format (East London style)"""
    
    # Count events by type
    event_counts = {}
    for event in webapp_data['timeline_events']:
        event_type = event['type']
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    # Create v3 format metadata matching East London structure
    metadata = {
        'match_id': match_id,
        'teams': {
            'red_team': {
                'name': webapp_data['teams']['team_a']['name'],
                'jersey_color': webapp_data['teams']['team_a']['colors']
            },
            'blue_team': {
                'name': webapp_data['teams']['team_b']['name'], 
                'jersey_color': webapp_data['teams']['team_b']['colors']
            }
        },
        'counts': {
            'goals': event_counts.get('goal', 0),
            'shots': event_counts.get('shot', 0)
        },
        'files': {
            'video_mp4': f"https://end-nov-webapp-clann.s3.amazonaws.com/analysis-videos/{match_id}-video-mp4.mp4",
            'web_events_array_json': f"https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/{match_id}-web_events_array-json.json",
            'web_events_json': None,
            'timeline_txt': None,
            'ground_truth_json': None,
            'other_events_txt': None,
            'tactical_json': None
        },
        'final_score': webapp_data['final_score'],
        'match_summary': webapp_data['match_summary']
    }
    
    return metadata

def main():
    if len(sys.argv) != 2:
        print("Usage: python 5_format_webapp.py <match-id>")
        print("Example: python 5_format_webapp.py sunday-league-game-1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    # Load required files
    team_config_file = outputs_dir / 'team_config.json'
    highlights_file = outputs_dir / 'highlights.json'
    
    if not team_config_file.exists():
        print(f"❌ Error: Team configuration not found: {team_config_file}")
        sys.exit(1)
    
    if not highlights_file.exists():
        print(f"❌ Error: Highlights data not found: {highlights_file}")
        print("Run step 4 first: python 4_synthesize_highlights.py <match-id>")
        sys.exit(1)
    
    # Load data
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    with open(highlights_file, 'r') as f:
        highlights_data = json.load(f)
    
    print(f"🌐 Formatting for webapp: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print("=" * 50)
    
    # Format for webapp
    webapp_data = format_for_webapp(highlights_data, team_config, match_id)
    match_metadata = create_match_metadata(webapp_data, match_id)
    
    # Save webapp files
    webapp_file = outputs_dir / 'web_events_array.json'
    metadata_file = outputs_dir / 'match_metadata.json'
    
    with open(webapp_file, 'w') as f:
        json.dump(webapp_data['timeline_events'], f, indent=2)
    
    with open(metadata_file, 'w') as f:
        json.dump(match_metadata, f, indent=2)
    
    # Also save complete webapp data
    complete_file = outputs_dir / 'webapp_complete.json'
    with open(complete_file, 'w') as f:
        json.dump(webapp_data, f, indent=2)
    
    print(f"✅ Webapp formatting complete!")
    print(f"📄 Timeline events: {webapp_file}")
    print(f"📄 Match metadata: {metadata_file}")
    print(f"📄 Complete data: {complete_file}")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   Total events: {len(webapp_data['timeline_events'])}")
    print(f"   Goals: {match_metadata['counts'].get('goals', 0)}")
    print(f"   Shots: {match_metadata['counts'].get('shots', 0)}")
    print(f"   Final score: {webapp_data['final_score']}")
    
    if webapp_data['timeline_events']:
        print(f"\n🎯 Sample events:")
        for event in webapp_data['timeline_events'][:3]:
            mins = event['timestamp'] // 60
            secs = event['timestamp'] % 60
            print(f"   {mins:02d}:{secs:02d} - {event['type'].upper()}: {event['description'][:60]}...")
    
    print(f"\n🎉 Analysis complete! Ready for webapp integration.")
    print(f"📁 All files saved in: {outputs_dir}")

if __name__ == "__main__":
    main()