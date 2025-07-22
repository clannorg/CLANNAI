#!/usr/bin/env python3
"""
JSON Schema Explorer for Football Data
---
This script analyzes football match data JSON files to understand their structure,
content, and relationships. It outputs a comprehensive understanding to a separate JSON file.

Usage: python schema_explorer.py td.json [physical.json] output_understanding.json
"""

import json
import sys
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any, Set, Optional, Tuple

def load_json_file(file_path: str) -> dict:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def explore_metadata(data: dict) -> dict:
    """Extract and analyze metadata from the match data."""
    if not data or 'metadata' not in data:
        return {"error": "No metadata found"}
    
    metadata = data['metadata']
    result = {
        "match_info": {
            "teams": {
                "home": metadata.get('home_team', {}).get('name', 'Unknown'),
                "away": metadata.get('away_team', {}).get('name', 'Unknown')
            },
            "score": f"{metadata.get('home_team_score', 0)} - {metadata.get('away_team_score', 0)}",
            "date": metadata.get('date', 'Unknown'),
            "venue": metadata.get('venue', {}).get('name', 'Unknown'),
            "competition": metadata.get('season', {}).get('competition', {}).get('name', 'Unknown')
        },
        "field_dimensions": {
            "length": metadata.get('pitch_length', 0),
            "width": metadata.get('pitch_width', 0)
        },
        "duration": {
            "value": metadata.get('duration', 0),
            "unit": "seconds",
            "minutes": metadata.get('duration', 0) / 60,
            "notes": "Check if this seems correct for a football match"
        }
    }
    
    # Extract player information
    if 'players' in metadata:
        teams = {}
        player_count_by_position = defaultdict(int)
        player_count_by_team = defaultdict(int)
        
        for player in metadata['players']:
            team_id = player.get('team_uuid', 'unknown')
            if team_id not in teams:
                teams[team_id] = {
                    "name": "Unknown",
                    "players": []
                }
                # Try to match team ID to find name
                if metadata.get('home_team', {}).get('uuid') == team_id:
                    teams[team_id]["name"] = metadata['home_team']['name']
                elif metadata.get('away_team', {}).get('uuid') == team_id:
                    teams[team_id]["name"] = metadata['away_team']['name']
            
            teams[team_id]["players"].append({
                "name": player.get('player_name', 'Unknown'),
                "position": player.get('position', 'Unknown'),
                "jersey": player.get('jersey_number', 0)
            })
            
            player_count_by_position[player.get('position', 'Unknown')] += 1
            player_count_by_team[teams[team_id]["name"]] += 1
        
        result["team_composition"] = {
            "teams": teams,
            "position_distribution": dict(player_count_by_position),
            "team_sizes": dict(player_count_by_team)
        }
    
    return result

def analyze_event_structure(data: dict) -> dict:
    """Analyze the structure and patterns of events in the data."""
    if not data or 'data' not in data:
        return {"error": "No event data found"}
    
    events = data['data']
    
    # Get a sample event for structure reference
    sample_event = events[0] if events else {}
    
    # Count event types
    event_types = Counter(event['type'] for event in events)
    
    # Analyze event fields
    event_fields = set()
    metric_types = set()
    role_types = set()
    
    for event in events[:100]:  # Limit to first 100 for performance
        event_fields.update(event.keys())
        
        # Extract metric types
        if 'metrics' in event:
            for metric in event['metrics']:
                metric_types.add(metric.get('type', 'Unknown'))
        
        # Extract role types
        if 'player_roles' in event:
            for role in event['player_roles']:
                role_types.add(role.get('type', 'Unknown'))
    
    # Team distribution
    team_distribution = Counter(event['team_uuid'] for event in events)
    
    # Temporal distribution (by frame)
    frame_counts = defaultdict(int)
    frame_ranges = []
    
    for event in events:
        start_frame = event.get('start_frame', 0)
        end_frame = event.get('end_frame', 0)
        frame_bucket = start_frame // 1000  # Group by thousands
        frame_counts[frame_bucket] += 1
        frame_ranges.append((start_frame, end_frame))
    
    # Calculate frame statistics
    if frame_ranges:
        min_start = min(start for start, _ in frame_ranges)
        max_end = max(end for _, end in frame_ranges)
        avg_duration = sum(end - start for start, end in frame_ranges) / len(frame_ranges)
    else:
        min_start, max_end, avg_duration = 0, 0, 0
    
    return {
        "event_count": len(events),
        "event_types": {
            "count": len(event_types),
            "distribution": dict(event_types.most_common()),
            "top_10": dict(event_types.most_common(10))
        },
        "event_structure": {
            "sample_event": sample_event,
            "common_fields": list(event_fields),
            "metric_types": list(metric_types),
            "player_role_types": list(role_types)
        },
        "team_distribution": dict(team_distribution),
        "temporal_analysis": {
            "frame_distribution": dict(sorted(frame_counts.items())),
            "frame_range": {
                "min_start": min_start,
                "max_end": max_end,
                "total_frames": max_end - min_start,
                "estimated_duration_seconds": (max_end - min_start) / 25,  # Assuming 25 fps
                "notes": "Check if fps assumption is correct"
            },
            "avg_event_duration_frames": avg_duration
        }
    }

def analyze_player_involvement(data: dict) -> dict:
    """Analyze how players are involved in events."""
    if not data or 'data' not in data or 'metadata' not in data:
        return {"error": "Missing data or metadata"}
    
    events = data['data']
    
    # Create player lookup
    player_lookup = {}
    if 'players' in data['metadata']:
        player_lookup = {
            p['player_uuid']: {
                "name": p.get('player_name', 'Unknown'),
                "position": p.get('position', 'Unknown'),
                "team": p.get('team_uuid', 'Unknown')
            }
            for p in data['metadata']['players']
        }
    
    # Map team IDs to names
    team_names = {}
    if 'home_team' in data['metadata']:
        team_names[data['metadata']['home_team']['uuid']] = data['metadata']['home_team']['name']
    if 'away_team' in data['metadata']:
        team_names[data['metadata']['away_team']['uuid']] = data['metadata']['away_team']['name']
    
    # Count player involvements by event type
    player_involvements = defaultdict(lambda: defaultdict(int))
    player_role_types = defaultdict(lambda: defaultdict(int))
    
    for event in events:
        event_type = event['type']
        if 'player_roles' in event:
            for role in event['player_roles']:
                player_id = role.get('player_uuid')
                if player_id:
                    player_involvements[player_id][event_type] += 1
                    role_type = role.get('type', 'Unknown')
                    player_role_types[player_id][role_type] += 1
    
    # Organize player involvements with names and positions
    player_data = []
    for player_id, event_counts in player_involvements.items():
        if player_id in player_lookup:
            player_info = player_lookup[player_id]
            team_name = team_names.get(player_info['team'], player_info['team'])
            
            total_involvements = sum(event_counts.values())
            
            player_data.append({
                "id": player_id,
                "name": player_info['name'],
                "position": player_info['position'],
                "team": team_name,
                "total_involvements": total_involvements,
                "top_event_types": dict(Counter(event_counts).most_common(5)),
                "role_distribution": dict(player_role_types[player_id])
            })
    
    # Sort by total involvements
    player_data.sort(key=lambda p: p['total_involvements'], reverse=True)
    
    return {
        "player_involvement": {
            "total_players_involved": len(player_data),
            "top_20_players": player_data[:20],
            "position_involvements": {
                p: sum(player['total_involvements'] 
                      for player in player_data 
                      if player['position'] == p)
                for p in set(player['position'] for player in player_data)
            }
        }
    }

def analyze_physical_data(data: dict) -> dict:
    """Analyze physical performance data."""
    if not data or 'data' not in data:
        return {"error": "No physical data found"}
    
    physical_metrics = data['data']
    
    # Extract available metric types
    all_metric_types = set()
    metric_distributions = defaultdict(list)
    
    for player_metrics in physical_metrics:
        player_id = player_metrics.get('player_uuid', 'Unknown')
        team_id = player_metrics.get('team_uuid', 'Unknown')
        
        if 'metrics' in player_metrics:
            for metric in player_metrics['metrics']:
                metric_type = metric.get('type', 'Unknown')
                all_metric_types.add(metric_type)
                
                value = metric.get('value', 0)
                unit = metric.get('unit', 'Unknown')
                
                metric_distributions[metric_type].append(value)
    
    # Calculate statistics for each metric type
    metric_stats = {}
    for metric_type, values in metric_distributions.items():
        if not values:
            continue
            
        values = [v for v in values if v is not None]
        if not values:
            continue
            
        metric_stats[metric_type] = {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sample_count": len(values)
        }
    
    return {
        "physical_data": {
            "player_count": len(physical_metrics),
            "metric_types": list(all_metric_types),
            "metric_statistics": metric_stats
        }
    }

def explore_event_relationships(data: dict) -> dict:
    """Explore relationships between different event types."""
    if not data or 'data' not in data:
        return {"error": "No event data found"}
    
    events = data['data']
    if not events:
        return {"error": "Empty event data"}
    
    # Sort events by start_frame to establish sequence
    events = sorted(events, key=lambda e: e.get('start_frame', 0))
    
    # Calculate transition probabilities between event types
    transitions = defaultdict(lambda: defaultdict(int))
    
    for i in range(len(events) - 1):
        current_type = events[i]['type']
        next_type = events[i+1]['type']
        
        # Only count transitions within the same team or when possession changes
        current_team = events[i]['team_uuid']
        next_team = events[i+1]['team_uuid']
        
        transitions[current_type][next_type] += 1
    
    # Find common sequences of 3 events
    sequences = []
    for i in range(len(events) - 2):
        # Only consider events close to each other in time
        if (events[i+1]['start_frame'] - events[i]['end_frame'] < 300 and
            events[i+2]['start_frame'] - events[i+1]['end_frame'] < 300):
            
            sequence = (events[i]['type'], events[i+1]['type'], events[i+2]['type'])
            sequences.append(sequence)
    
    sequence_counter = Counter(sequences)
    
    return {
        "event_relationships": {
            "transition_probabilities": {
                evt: dict(Counter(next_events).most_common(5))
                for evt, next_events in transitions.items()
            },
            "common_sequences": {
                " -> ".join(seq): count
                for seq, count in sequence_counter.most_common(10)
            }
        }
    }

def analyze_match_phases(data: dict) -> dict:
    """Analyze different phases of the match."""
    if not data or 'data' not in data or 'metadata' not in data:
        return {"error": "Missing data or metadata"}
    
    events = data['data']
    if not events:
        return {"error": "Empty event data"}
    
    # Sort events by start_frame
    events = sorted(events, key=lambda e: e.get('start_frame', 0))
    
    # Identify match duration in frames
    min_frame = events[0].get('start_frame', 0)
    max_frame = events[-1].get('end_frame', 0)
    
    # Assuming 45 minutes per half (plus some stoppage time)
    # This is a simplification - would need to identify halftime break properly
    half_point = (min_frame + max_frame) / 2
    estimated_halftime = half_point
    
    # Divide into periods (quarters for more granular analysis)
    quarter_size = (max_frame - min_frame) / 4
    
    periods = {
        "first_quarter": (min_frame, min_frame + quarter_size),
        "second_quarter": (min_frame + quarter_size, min_frame + 2*quarter_size),
        "third_quarter": (min_frame + 2*quarter_size, min_frame + 3*quarter_size),
        "fourth_quarter": (min_frame + 3*quarter_size, max_frame)
    }
    
    # Count events by type in each period
    period_counts = {}
    for period_name, (start, end) in periods.items():
        period_events = [e for e in events if start <= e.get('start_frame', 0) <= end]
        
        # Count by event type
        type_counts = Counter(e['type'] for e in period_events)
        
        # Count by team
        team_counts = Counter(e['team_uuid'] for e in period_events)
        
        period_counts[period_name] = {
            "event_count": len(period_events),
            "top_event_types": dict(type_counts.most_common(5)),
            "team_distribution": dict(team_counts)
        }
    
    return {
        "match_phases": {
            "total_frames": max_frame - min_frame,
            "estimated_halftime_frame": estimated_halftime,
            "periods": period_counts
        }
    }

def explore_schema_fields(data: dict, schema_path: Optional[str] = None) -> dict:
    """Explore schema fields and their usage in the data."""
    result = {
        "schema_fields": {
            "event_types": {},
            "metric_types": {},
            "player_role_types": {}
        }
    }
    
    # Load schema if available
    schema = {}
    if schema_path and os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
        except Exception as e:
            result["schema_load_error"] = str(e)
    
    # Extract labels from schema
    labels = {}
    if 'labels' in schema:
        for category in ['events', 'metrics', 'player_roles']:
            if category in schema['labels']:
                labels[category] = schema['labels'][category]
    
    # Map actual data to schema labels
    if 'data' in data:
        # Check data structure first
        if data['data'] and isinstance(data['data'], list):
            first_item = data['data'][0]
            
            # Handle tactical data (events)
            if 'type' in first_item:
                # Event types
                event_types = Counter(event.get('type', '') for event in data['data'] if 'type' in event)
                
                for event_type, count in event_types.items():
                    name = labels.get('events', {}).get(event_type, event_type)
                    result["schema_fields"]["event_types"][event_type] = {
                        "name": name,
                        "count": count,
                        "sample": next((e for e in data['data'] if e.get('type') == event_type), {})
                    }
                
                # Metric types
                metric_types = Counter()
                for event in data['data']:
                    if 'metrics' in event and isinstance(event['metrics'], list):
                        for metric in event['metrics']:
                            if 'type' in metric:
                                metric_types[metric['type']] += 1
                
                for metric_type, count in metric_types.items():
                    name = labels.get('metrics', {}).get(metric_type, metric_type)
                    result["schema_fields"]["metric_types"][metric_type] = {
                        "name": name,
                        "count": count
                    }
                
                # Player role types
                role_types = Counter()
                for event in data['data']:
                    if 'player_roles' in event and isinstance(event['player_roles'], list):
                        for role in event['player_roles']:
                            if 'type' in role:
                                role_types[role['type']] += 1
                
                for role_type, count in role_types.items():
                    name = labels.get('player_roles', {}).get(role_type, role_type)
                    result["schema_fields"]["player_role_types"][role_type] = {
                        "name": name,
                        "count": count
                    }
            
            # Handle physical data (player metrics)
            elif 'player_uuid' in first_item and 'metrics' in first_item:
                result["data_type"] = "physical_data"
                
                # Extract physical metrics
                metric_types = Counter()
                for player_data in data['data']:
                    if 'metrics' in player_data and isinstance(player_data['metrics'], list):
                        for metric in player_data['metrics']:
                            if 'type' in metric:
                                metric_types[metric['type']] += 1
                
                for metric_type, count in metric_types.items():
                    name = labels.get('metrics', {}).get(metric_type, metric_type)
                    result["schema_fields"]["metric_types"][metric_type] = {
                        "name": name,
                        "count": count
                    }
    
    return result

def main():
    """Main function to explore the schema and output understanding."""
    if len(sys.argv) < 3:
        print("Usage: python schema_explorer.py td.json [physical.json] output_understanding.json")
        sys.exit(1)
    
    tactical_data_path = sys.argv[1]
    output_path = sys.argv[-1]
    
    # Determine if physical data is provided
    physical_data_path = None
    if len(sys.argv) == 4:
        physical_data_path = sys.argv[2]
    
    # Load tactical data
    print(f"Loading tactical data from {tactical_data_path}...")
    tactical_data = load_json_file(tactical_data_path)
    
    # Get schema path
    schema_path = os.path.join(os.path.dirname(tactical_data_path), "tactical-data-schema.json")
    if not os.path.exists(schema_path):
        schema_path = None
        print("No schema file found, proceeding without schema information")
    
    # Analyze tactical data
    metadata_analysis = explore_metadata(tactical_data)
    event_structure = analyze_event_structure(tactical_data)
    player_analysis = analyze_player_involvement(tactical_data)
    event_relationships = explore_event_relationships(tactical_data)
    match_phases = analyze_match_phases(tactical_data)
    schema_fields = explore_schema_fields(tactical_data, schema_path)
    
    understanding = {
        "tactical_data": {
            "file_path": tactical_data_path,
            "metadata_analysis": metadata_analysis,
            "event_structure": event_structure,
            "player_analysis": player_analysis,
            "event_relationships": event_relationships,
            "match_phases": match_phases,
            "schema_fields": schema_fields
        }
    }
    
    # Load and analyze physical data if provided
    if physical_data_path:
        print(f"Loading physical data from {physical_data_path}...")
        physical_data = load_json_file(physical_data_path)
        
        physical_schema_path = os.path.join(os.path.dirname(physical_data_path), "physical-schema.json")
        if not os.path.exists(physical_schema_path):
            physical_schema_path = None
        
        physical_analysis = analyze_physical_data(physical_data)
        physical_schema_fields = explore_schema_fields(physical_data, physical_schema_path)
        
        understanding["physical_data"] = {
            "file_path": physical_data_path,
            "analysis": physical_analysis,
            "schema_fields": physical_schema_fields
        }
    
    # Generate summary of findings
    event_counts = event_structure.get('event_count', 0)
    player_count = player_analysis.get('player_involvement', {}).get('total_players_involved', 0)
    
    understanding["summary"] = {
        "total_events": event_counts,
        "event_types": len(event_structure.get('event_types', {}).get('distribution', {})),
        "players_involved": player_count,
        "match_duration_frames": event_structure.get('temporal_analysis', {}).get('frame_range', {}).get('total_frames', 0),
        "match_duration_minutes": event_structure.get('temporal_analysis', {}).get('frame_range', {}).get('estimated_duration_seconds', 0) / 60,
        "has_physical_data": physical_data_path is not None,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Add recommendations for better analysis
    understanding["recommendations"] = [
        "Verify the frame rate assumption (currently 25 fps) for accurate timing analysis",
        "Check if the match duration calculation is correct",
        "Consider mapping event sequences to pitch positions for spatial analysis",
        "Create network analysis between players based on connected events",
        "Identify possession sequences by analyzing consecutive team events"
    ]
    
    # Output understanding to JSON file
    print(f"Writing understanding to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(understanding, f, indent=2)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()