#!/usr/bin/env python3
"""
Enhanced Football Match Analyzer for LLM Insights
---
This script processes tactical and physical data from a football match,
extracting rich, multi-dimensional insights optimized for LLM analysis.

Usage: python match_analyzer_for_llm.py td.json physical.json output.json
"""

import json
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple, Set
import os
import math
from datetime import datetime
import numpy as np
from statistics import mean, median

# Pitch dimensions and zones
PITCH_LENGTH = 105  # standard pitch length in meters
PITCH_WIDTH = 68    # standard pitch width in meters
THIRDS_X = [0, 35, 70, 105]  # Dividing pitch into thirds lengthwise
THIRDS_Y = [0, 22.67, 45.33, 68]  # Dividing pitch into thirds widthwise

def load_json_data(file_path: str) -> dict:
    """Load JSON data from a file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_event_labels(tactical_data: dict, schema_path: str = None) -> dict:
    """Extract event labels from data or schema file."""
    # Try to get labels from the data file
    if 'labels' in tactical_data and 'events' in tactical_data['labels']:
        return tactical_data['labels']['events']
    
    # If not in data file, try schema file
    if schema_path and os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
                if 'labels' in schema and 'events' in schema['labels']:
                    return schema['labels']['events']
        except:
            print("Warning: Could not extract event labels from schema file")
    
    # Return empty dict if not found
    return {}

def get_metric_labels(schema_path: str) -> dict:
    """Extract metric labels from schema file."""
    if schema_path and os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
                if 'labels' in schema and 'metrics' in schema['labels']:
                    return schema['labels']['metrics']
        except:
            print("Warning: Could not extract metric labels from schema file")
    return {}

def extract_match_summary(tactical_data: dict) -> dict:
    """Extract comprehensive match information."""
    metadata = tactical_data['metadata']
    
    # Calculate actual match duration from frames if available
    events = tactical_data['data']
    if events:
        events_sorted = sorted(events, key=lambda e: e.get('end_frame', 0))
        first_frame = events_sorted[0].get('start_frame', 0)
        last_frame = events_sorted[-1].get('end_frame', 0)
        # Assuming 25 fps based on data understanding
        calculated_duration_minutes = (last_frame - first_frame) / (25 * 60)
    else:
        calculated_duration_minutes = 0
    
    # Get the metadata duration and compare
    metadata_duration_minutes = int(metadata.get('duration', 0) / 60)
    
    # Use calculated duration if metadata duration seems incorrect
    actual_duration = calculated_duration_minutes if metadata_duration_minutes < 80 else metadata_duration_minutes
    
    return {
        "teams": [metadata['home_team']['name'], metadata['away_team']['name']],
        "score": f"{metadata['home_team_score']} - {metadata['away_team_score']}",
        "date": metadata['date'],
        "competition": metadata.get('season', {}).get('competition', {}).get('name', "Unknown"),
        "venue": metadata.get('venue', {}).get('name', "Unknown"),
        "total_events": len(tactical_data['data']),
        "match_duration_minutes": round(actual_duration, 2),
        "first_half_length": round(actual_duration / 2, 2),  # Estimation
        "pitch_dimensions": {
            "length": metadata.get('pitch_length', PITCH_LENGTH),
            "width": metadata.get('pitch_width', PITCH_WIDTH)
        }
    }

def get_match_periods(tactical_data: dict) -> dict:
    """Identify match periods (halves and key moments)."""
    events = tactical_data['data']
    if not events:
        return {"error": "No events found"}
    
    # Sort events by time
    events_sorted = sorted(events, key=lambda e: e.get('start_frame', 0))
    first_frame = events_sorted[0].get('start_frame', 0)
    last_frame = events_sorted[-1].get('end_frame', 0)
    total_frames = last_frame - first_frame
    
    # Estimate halftime - looking for a significant gap in events
    frame_gaps = []
    for i in range(1, len(events_sorted)):
        gap = events_sorted[i].get('start_frame', 0) - events_sorted[i-1].get('end_frame', 0)
        frame_gaps.append((gap, i, events_sorted[i].get('start_frame', 0)))
    
    # Sort gaps by size, largest first
    frame_gaps.sort(reverse=True)
    
    # The largest gap is likely halftime
    if frame_gaps and frame_gaps[0][0] > 1000:  # Large gap (>40 seconds at 25fps)
        halftime_frame = frame_gaps[0][2]  # Frame where second half starts
    else:
        # If no clear gap, estimate halftime
        halftime_frame = first_frame + (total_frames / 2)
    
    # Create periods
    first_half_start = first_frame
    first_half_end = halftime_frame - 1
    second_half_start = halftime_frame
    second_half_end = last_frame
    
    return {
        "first_half": {
            "start_frame": first_half_start,
            "end_frame": first_half_end,
            "duration_frames": first_half_end - first_half_start
        },
        "second_half": {
            "start_frame": second_half_start,
            "end_frame": second_half_end,
            "duration_frames": second_half_end - second_half_start
        },
        "halftime_frame": halftime_frame,
        "total_frames": total_frames,
        "fps_estimate": 25  # Based on data understanding
    }

def identify_possession_sequences(tactical_data: dict, event_labels: dict) -> dict:
    """Identify and classify possession sequences."""
    events = tactical_data['data']
    if not events:
        return {"error": "No events found"}
    
    metadata = tactical_data['metadata']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Sort events by time
    events_sorted = sorted(events, key=lambda e: e.get('start_frame', 0))
    
    # Initialize sequences
    current_sequence = {"team": None, "events": [], "type": None}
    sequences = []
    
    # Events that typically start a possession
    possession_start_events = [
        'E21', 'E23', 'E63', 'E32',  # Goal kicks
        'E37',  # Recovered Ball
        'E20', 'E14', 'E51', 'E38', 'E15', 'E28', 'E10'  # Second ball winning
    ]
    
    # Events that typically end a possession
    possession_end_events = [
        'E07',  # Finishing
        'E33',  # Goal Chance
        'E75'   # Lost Ball
    ]
    
    # Counter-attack indicators
    counter_attack_indicators = [
        'E37',  # Recovered Ball
        'E13'   # Progression After Recovery
    ]
    
    # Events that indicate a high press
    high_press_indicators = [
        'E31',  # Pressure On The Ball Possessor
        'E09',  # Press After Loss
        'E12'   # Moving Forward During Organized Pressure
    ]
    
    for event in events_sorted:
        team_uuid = event.get('team_uuid')
        event_type = event.get('type')
        
        # Skip events without team or type
        if not team_uuid or not event_type:
            continue
        
        # New sequence when team changes or possession start event occurs
        if current_sequence["team"] != team_uuid or event_type in possession_start_events:
            # Save previous sequence if it exists and has events
            if current_sequence["team"] and current_sequence["events"]:
                classify_sequence(current_sequence, event_labels)
                sequences.append(current_sequence)
            
            # Start new sequence
            current_sequence = {
                "team": team_uuid,
                "team_name": home_name if team_uuid == home_uuid else away_name,
                "events": [event],
                "start_frame": event.get('start_frame', 0),
                "type": "counter_attack" if event_type in counter_attack_indicators else "build_up"
            }
        else:
            # Continue current sequence
            current_sequence["events"].append(event)
        
        # Update sequence end frame
        current_sequence["end_frame"] = event.get('end_frame', 0)
        
        # End sequence on possession end events
        if event_type in possession_end_events:
            current_sequence["outcome"] = event_type
            classify_sequence(current_sequence, event_labels)
            sequences.append(current_sequence)
            current_sequence = {"team": None, "events": []}
    
    # Add the last sequence if it exists
    if current_sequence["team"] and current_sequence["events"]:
        classify_sequence(current_sequence, event_labels)
        sequences.append(current_sequence)
    
    # Analyze sequences by team
    home_sequences = [s for s in sequences if s["team"] == home_uuid]
    away_sequences = [s for s in sequences if s["team"] == away_uuid]
    
    # Create sequence summary
    sequence_summary = {
        home_name: analyze_team_sequences(home_sequences, event_labels),
        away_name: analyze_team_sequences(away_sequences, event_labels)
    }
    
    return sequence_summary

def classify_sequence(sequence: dict, event_labels: dict) -> None:
    """Classify a possession sequence and add metrics."""
    events = sequence["events"]
    
    # Skip if no events
    if not events:
        return
    
    # Calculate duration in frames
    sequence["duration_frames"] = sequence.get("end_frame", 0) - sequence.get("start_frame", 0)
    
    # Count passes
    pass_types = ['E65', 'E16', 'E68', 'E44', 'E03', 'E11']
    sequence["pass_count"] = sum(1 for e in events if e.get('type') in pass_types)
    
    # Track players involved
    player_set = set()
    for event in events:
        if 'player_roles' in event:
            for role in event['player_roles']:
                if 'player_uuid' in role:
                    player_set.add(role['player_uuid'])
    sequence["players_involved"] = list(player_set)
    sequence["player_count"] = len(player_set)
    
    # Determine if high press based on field position
    high_press = False
    for event in events[:min(3, len(events))]:  # Check first 3 events
        # Check for pressure/press events in attacking third
        if event.get('type') in ['E31', 'E09'] and has_attacking_third_position(event):
            high_press = True
            break
    
    sequence["high_press"] = high_press
    
    # Refine sequence type based on more analysis
    if sequence["type"] == "counter_attack" and sequence["pass_count"] > 5:
        # Long counter-attacks may actually be build-up
        sequence["type"] = "sustained_attack"
    elif high_press:
        sequence["type"] = "high_press"
    elif "type" not in sequence or not sequence["type"]:
        sequence["type"] = "unclassified"
    
    # Determine outcome
    if any(e.get('type') == 'E07' for e in events):  # Finishing
        sequence["outcome"] = "shot"
    elif any(e.get('type') == 'E33' for e in events):  # Goal Chance
        sequence["outcome"] = "goal_chance"
    elif any(e.get('type') == 'E75' for e in events):  # Lost Ball
        sequence["outcome"] = "lost_possession"
    elif any(e.get('type') == 'E59' for e in events):  # Cross
        sequence["outcome"] = "cross"
    else:
        sequence["outcome"] = "other"
    
    # Add sequence zone progression
    start_zone = get_event_zone(events[0]) if events else None
    end_zone = get_event_zone(events[-1]) if events else None
    sequence["start_zone"] = start_zone
    sequence["end_zone"] = end_zone
    
    # Add named events for better LLM understanding
    sequence["event_types"] = [event_labels.get(e.get('type'), e.get('type')) for e in events]

def analyze_team_sequences(sequences: List[dict], event_labels: dict) -> dict:
    """Analyze sequences for a team."""
    if not sequences:
        return {"error": "No sequences found"}
    
    # Count sequence types
    sequence_types = Counter(s.get("type") for s in sequences)
    
    # Count outcomes by type
    outcomes_by_type = defaultdict(lambda: defaultdict(int))
    for s in sequences:
        seq_type = s.get("type")
        outcome = s.get("outcome")
        if seq_type and outcome:
            outcomes_by_type[seq_type][outcome] += 1
    
    # Calculate success rates
    success_rates = {}
    for seq_type, outcomes in outcomes_by_type.items():
        total = sum(outcomes.values())
        success = outcomes.get("shot", 0) + outcomes.get("goal_chance", 0)
        if total > 0:
            success_rates[seq_type] = round((success / total) * 100, 1)
        else:
            success_rates[seq_type] = 0
    
    # Get most involved players in successful sequences
    successful_sequences = [s for s in sequences if s.get("outcome") in ["shot", "goal_chance"]]
    player_involvements = defaultdict(int)
    for s in successful_sequences:
        for player in s.get("players_involved", []):
            player_involvements[player] += 1
    
    # Get zone progressions
    zone_progressions = []
    for s in sequences:
        start = s.get("start_zone")
        end = s.get("end_zone")
        if start and end:
            zone_progressions.append((start, end))
    
    # Calculate average duration and pass count
    avg_duration = sum(s.get("duration_frames", 0) for s in sequences) / len(sequences) if sequences else 0
    avg_pass_count = sum(s.get("pass_count", 0) for s in sequences) / len(sequences) if sequences else 0
    
    return {
        "total_sequences": len(sequences),
        "sequence_types": {
            "build_up": {
                "count": sequence_types.get("build_up", 0),
                "success_rate": success_rates.get("build_up", 0)
            },
            "counter_attack": {
                "count": sequence_types.get("counter_attack", 0),
                "success_rate": success_rates.get("counter_attack", 0)
            },
            "high_press": {
                "count": sequence_types.get("high_press", 0),
                "success_rate": success_rates.get("high_press", 0)
            },
            "sustained_attack": {
                "count": sequence_types.get("sustained_attack", 0),
                "success_rate": success_rates.get("sustained_attack", 0)
            }
        },
        "outcome_distribution": {
            "shots": sum(1 for s in sequences if s.get("outcome") == "shot"),
            "goal_chances": sum(1 for s in sequences if s.get("outcome") == "goal_chance"),
            "lost_possession": sum(1 for s in sequences if s.get("outcome") == "lost_possession"),
            "crosses": sum(1 for s in sequences if s.get("outcome") == "cross"),
            "other": sum(1 for s in sequences if s.get("outcome") == "other")
        },
        "top_players_in_successful_sequences": dict(Counter(player_involvements).most_common(5)),
        "zone_progressions": Counter(zone_progressions).most_common(5),
        "average_metrics": {
            "duration_frames": round(avg_duration, 2),
            "duration_seconds": round(avg_duration / 25, 2),  # Assuming 25 fps
            "pass_count": round(avg_pass_count, 2)
        }
    }

def has_attacking_third_position(event: dict) -> bool:
    """Check if an event has a position in the attacking third."""
    # This is a simplified implementation - in a real analysis
    # we'd check the actual position metrics from the event
    # For now, we'll assume certain event types happen in the attacking third
    attacking_third_events = ['E67', 'E59', 'E07', 'E33', 'E34']
    return event.get('type') in attacking_third_events

def get_event_zone(event: dict) -> str:
    """Get the zone of an event based on its metrics."""
    # Extract position from metrics if available
    position = None
    if 'metrics' in event:
        for metric in event['metrics']:
            if metric.get('type') in ['M02', 'M17', 'M26']:  # Position metrics
                if metric.get('value') and isinstance(metric.get('value'), list) and len(metric.get('value')) >= 2:
                    position = metric.get('value')
                    break
    
    if not position:
        # Fallback to event type-based estimation
        event_type = event.get('type', '')
        if event_type in ['E67', 'E59', 'E07', 'E33']:  # Attacking events
            return "attacking_third"
        elif event_type in ['E01', 'E65', 'E68']:  # Midfield events
            return "middle_third"
        elif event_type in ['E04', 'E22', 'E46']:  # Defensive events
            return "defensive_third"
        else:
            return "unknown"
    
    # If we have position data, determine the zone
    # Check if position[0] is itself a list - handle nested coordinates
    if isinstance(position[0], list):
        x, y = position[0][0], position[0][1]  # Extract x,y from nested list
    else:
        x, y = position[0], position[1]  # Standard format
    
    # Determine third based on x-coordinate
    if x < THIRDS_X[1]:
        x_third = "defensive"
    elif x < THIRDS_X[2]:
        x_third = "middle"
    else:
        x_third = "attacking"
    
    # Determine side based on y-coordinate
    if y < THIRDS_Y[1]:
        y_third = "left"
    elif y < THIRDS_Y[2]:
        y_third = "central"
    else:
        y_third = "right"
    
    return f"{x_third}_{y_third}"

def calculate_team_comparison(tactical_data: dict, periods: dict, possession_sequences: dict) -> dict:
    """Calculate enhanced team comparisons with temporal breakdown."""
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Split events by half
    first_half_events = [e for e in events if e.get('start_frame', 0) < periods['halftime_frame']]
    second_half_events = [e for e in events if e.get('start_frame', 0) >= periods['halftime_frame']]
    
    # Count events by team
    home_events = [e for e in events if e['team_uuid'] == home_uuid]
    away_events = [e for e in events if e['team_uuid'] == away_uuid]
    
    home_first_half = [e for e in first_half_events if e['team_uuid'] == home_uuid]
    home_second_half = [e for e in second_half_events if e['team_uuid'] == home_uuid]
    away_first_half = [e for e in first_half_events if e['team_uuid'] == away_uuid]
    away_second_half = [e for e in second_half_events if e['team_uuid'] == away_uuid]
    
    # Calculate possession (based on event count)
    def calc_possession(team_events, all_events):
        return round(len(team_events) / len(all_events) * 100, 1) if all_events else 0
    
    home_possession = calc_possession(home_events, events)
    away_possession = calc_possession(away_events, events)
    home_first_half_poss = calc_possession(home_first_half, first_half_events)
    home_second_half_poss = calc_possession(home_second_half, second_half_events)
    away_first_half_poss = calc_possession(away_first_half, first_half_events)
    away_second_half_poss = calc_possession(away_second_half, second_half_events)
    
    # Extract pass types
    completed_pass_types = ['E65', 'E16', 'E68']  # forward, backward, horizontal
    incomplete_pass_types = ['E44', 'E03', 'E11']  # forward, backward, horizontal
    
    # Calculate pass stats for each team and half
    def calc_pass_stats(team_events):
        completed = sum(1 for e in team_events if e['type'] in completed_pass_types)
        attempted = completed + sum(1 for e in team_events if e['type'] in incomplete_pass_types)
        completion_rate = round((completed / attempted) * 100, 1) if attempted else 0
        return {"completed": completed, "attempted": attempted, "completion_rate": completion_rate}
    
    home_passes = calc_pass_stats(home_events)
    away_passes = calc_pass_stats(away_events)
    home_first_half_passes = calc_pass_stats(home_first_half)
    home_second_half_passes = calc_pass_stats(home_second_half)
    away_first_half_passes = calc_pass_stats(away_first_half)
    away_second_half_passes = calc_pass_stats(away_second_half)
    
    # Calculate attacking stats
    goal_chances = [e for e in events if e['type'] == 'E33']  # Goal Chance
    finishing = [e for e in events if e['type'] == 'E07']  # Finishing
    crosses = [e for e in events if e['type'] == 'E59']  # Cross Into The Box
    
    # Get data from possession sequences
    home_sequences = possession_sequences.get(home_name, {})
    away_sequences = possession_sequences.get(away_name, {})
    
    # Calculate field tilt (territorial advantage)
    attacking_events = sum(1 for e in home_events if has_attacking_third_position(e))
    total_attacking = attacking_events + sum(1 for e in away_events if has_attacking_third_position(e))
    field_tilt = round((attacking_events / total_attacking) * 100, 1) if total_attacking else 50
    
    return {
        "overall": {
            "possession": {
                home_name: home_possession,
                away_name: away_possession
            },
            "pass_completion": {
                home_name: home_passes["completion_rate"],
                away_name: away_passes["completion_rate"]
            },
            "pass_volume": {
                home_name: home_passes["attempted"],
                away_name: away_passes["attempted"]
            },
            "shots": {
                home_name: len([e for e in finishing if e['team_uuid'] == home_uuid]),
                away_name: len([e for e in finishing if e['team_uuid'] == away_uuid])
            },
            "goal_chances": {
                home_name: len([e for e in goal_chances if e['team_uuid'] == home_uuid]),
                away_name: len([e for e in goal_chances if e['team_uuid'] == away_uuid])
            },
            "crosses": {
                home_name: len([e for e in crosses if e['team_uuid'] == home_uuid]),
                away_name: len([e for e in crosses if e['team_uuid'] == away_uuid])
            },
            "field_tilt": field_tilt  # % of attacking third events by home team
        },
        "first_half": {
            "possession": {
                home_name: home_first_half_poss,
                away_name: away_first_half_poss
            },
            "pass_completion": {
                home_name: home_first_half_passes["completion_rate"],
                away_name: away_first_half_passes["completion_rate"]
            }
        },
        "second_half": {
            "possession": {
                home_name: home_second_half_poss,
                away_name: away_second_half_poss
            },
            "pass_completion": {
                home_name: home_second_half_passes["completion_rate"],
                away_name: away_second_half_passes["completion_rate"]
            }
        },
        "attack_patterns": {
            home_name: {
                "counter_attacks": home_sequences.get("sequence_types", {}).get("counter_attack", {}).get("count", 0),
                "build_up_sequences": home_sequences.get("sequence_types", {}).get("build_up", {}).get("count", 0),
                "high_press_sequences": home_sequences.get("sequence_types", {}).get("high_press", {}).get("count", 0),
                "sustained_attacks": home_sequences.get("sequence_types", {}).get("sustained_attack", {}).get("count", 0)
            },
            away_name: {
                "counter_attacks": away_sequences.get("sequence_types", {}).get("counter_attack", {}).get("count", 0),
                "build_up_sequences": away_sequences.get("sequence_types", {}).get("build_up", {}).get("count", 0),
                "high_press_sequences": away_sequences.get("sequence_types", {}).get("high_press", {}).get("count", 0),
                "sustained_attacks": away_sequences.get("sequence_types", {}).get("sustained_attack", {}).get("count", 0)
            }
        },
        "attack_success_rates": {
            home_name: {
                "counter_attacks": home_sequences.get("sequence_types", {}).get("counter_attack", {}).get("success_rate", 0),
                "build_up": home_sequences.get("sequence_types", {}).get("build_up", {}).get("success_rate", 0),
                "high_press": home_sequences.get("sequence_types", {}).get("high_press", {}).get("success_rate", 0),
                "sustained_attacks": home_sequences.get("sequence_types", {}).get("sustained_attack", {}).get("success_rate", 0)
            },
            away_name: {
                "counter_attacks": away_sequences.get("sequence_types", {}).get("counter_attack", {}).get("success_rate", 0),
                "build_up": away_sequences.get("sequence_types", {}).get("build_up", {}).get("success_rate", 0),
                "high_press": away_sequences.get("sequence_types", {}).get("high_press", {}).get("success_rate", 0),
                "sustained_attacks": away_sequences.get("sequence_types", {}).get("sustained_attack", {}).get("success_rate", 0)
            }
        }
    }

def calculate_tactical_efficiency(tactical_data: dict, event_labels: dict) -> dict:
    """Calculate enhanced tactical efficiency metrics for both teams."""
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Get event counts by team
    def get_event_counts(team_uuid):
        team_events = [e for e in events if e['team_uuid'] == team_uuid]
        event_counter = Counter([e['type'] for e in team_events])
        return {event_labels.get(k, k): v for k, v in event_counter.items()}
    
    home_events = get_event_counts(home_uuid)
    away_events = get_event_counts(away_uuid)
    
    # Calculate pressing efficiency
    home_pressing = home_events.get('Pressure On The Ball Possessor', 0)
    home_recoveries = home_events.get('Recovered Ball', 0)
    
    away_pressing = away_events.get('Pressure On The Ball Possessor', 0)
    away_recoveries = away_events.get('Recovered Ball', 0)
    
    # Calculate PPDA (Passes Per Defensive Action)
    home_team_events = [e for e in events if e['team_uuid'] == home_uuid]
    away_team_events = [e for e in events if e['team_uuid'] == away_uuid]
    
    home_passes = sum(1 for e in away_team_events if e['type'] in ['E65', 'E16', 'E68', 'E44', 'E03', 'E11'])
    away_passes = sum(1 for e in home_team_events if e['type'] in ['E65', 'E16', 'E68', 'E44', 'E03', 'E11'])
    
    home_defensive_actions = sum(1 for e in home_team_events if e['type'] in ['E46', 'E22', 'E04', 'E37'])
    away_defensive_actions = sum(1 for e in away_team_events if e['type'] in ['E46', 'E22', 'E04', 'E37'])
    
    home_ppda = round(away_passes / home_defensive_actions, 2) if home_defensive_actions else 0
    away_ppda = round(home_passes / away_defensive_actions, 2) if away_defensive_actions else 0
    
    # Calculate crossing efficiency
    home_width = home_events.get('Width Of The Team', 0)
    home_crosses = home_events.get('Cross Into The Box', 0)
    
    away_width = away_events.get('Width Of The Team', 0)
    away_crosses = away_events.get('Cross Into The Box', 0)
    
    # Calculate passing direction ratio
    home_horizontal = home_events.get('Completed Horizontal Pass', 0)
    home_forward = home_events.get('Completed Forward Pass', 0)
    
    away_horizontal = away_events.get('Completed Horizontal Pass', 0)
    away_forward = away_events.get('Completed Forward Pass', 0)
    
    # Calculate progressive passes (forward passes that advance significantly)
    home_progressive = home_forward * 0.7  # Simplified - would need actual distance metrics
    away_progressive = away_forward * 0.7
    
    # Calculate defensive compactness
    # Simplified implementation - would need spatial data for actual calculation
    home_defensive_line_events = sum(1 for e in home_team_events if e['type'] in ['E27', 'E71'])
    away_defensive_line_events = sum(1 for e in away_team_events if e['type'] in ['E27', 'E71'])
    
    home_compactness = 100 - (home_defensive_line_events / max(1, len(home_team_events)) * 100)
    away_compactness = 100 - (away_defensive_line_events / max(1, len(away_team_events)) * 100)
    
    return {
        home_name: {
            "pressing_efficiency": {
                "pressing_actions": home_pressing,
                "ball_recoveries": home_recoveries,
                "recovery_percentage": round((home_recoveries / home_pressing * 100) if home_pressing else 0, 1),
                "ppda": home_ppda,
                "ppda_interpretation": "Lower PPDA indicates more intense pressing"
            },
            "crossing_efficiency": {
                "width_positions": home_width,
                "crosses_attempted": home_crosses,
                "conversion_ratio": round(home_crosses / home_width if home_width else 0, 3),
                "benchmark": 0.1  # Typical ratio in elite teams
            },
            "passing_direction_ratio": {
                "horizontal_passes": home_horizontal,
                "forward_passes": home_forward,
                "vertical_ratio": round(home_forward / home_horizontal if home_horizontal else 0, 3),
                "progressive_passes": round(home_progressive, 1)
            },
            "defensive_organization": {
                "compactness_estimate": round(home_compactness, 1),
                "defensive_line_events": home_defensive_line_events
            }
        },
        away_name: {
            "pressing_efficiency": {
                "pressing_actions": away_pressing,
                "ball_recoveries": away_recoveries,
                "recovery_percentage": round((away_recoveries / away_pressing * 100) if away_pressing else 0, 1),
                "ppda": away_ppda,
                "ppda_interpretation": "Lower PPDA indicates more intense pressing"
            },
            "crossing_efficiency": {
                "width_positions": away_width,
                "crosses_attempted": away_crosses,
                "conversion_ratio": round(away_crosses / away_width if away_width else 0, 3),
                "benchmark": 0.1  # Typical ratio in elite teams
            },
            "passing_direction_ratio": {
                "horizontal_passes": away_horizontal,
                "forward_passes": away_forward,
                "vertical_ratio": round(away_forward / away_horizontal if away_horizontal else 0, 3),
                "progressive_passes": round(away_progressive, 1)
            },
            "defensive_organization": {
                "compactness_estimate": round(away_compactness, 1),
                "defensive_line_events": away_defensive_line_events
            }
        }
    }

def analyze_player_network(tactical_data: dict, physical_data: dict = None) -> dict:
    """Extract comprehensive player connections and contributions."""
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Create player lookup
    player_lookup = {p['player_uuid']: p for p in metadata['players']}
    
    # Track all player involvements and positions
    player_involvements = defaultdict(int)
    player_events = defaultdict(list)
    player_positions = {}
    
    for event in events:
        for role in event['player_roles']:
            player_id = role.get('player_uuid')
            if player_id:
                player_involvements[player_id] += 1
                player_events[player_id].append(event)
    
    # Extract team players
    home_players = {p['player_uuid']: p for p in metadata['players'] if p['team_uuid'] == home_uuid}
    away_players = {p['player_uuid']: p for p in metadata['players'] if p['team_uuid'] == away_uuid}
    
    # Create pass networks
    home_pass_network = build_team_pass_network(events, home_players)
    away_pass_network = build_team_pass_network(events, away_players)
    
    # Extract player metrics
    home_player_metrics = extract_player_metrics(events, home_players, player_involvements, player_events, physical_data)
    away_player_metrics = extract_player_metrics(events, away_players, player_involvements, player_events, physical_data)
    
    return {
        "player_metrics": {
            home_name: home_player_metrics,
            away_name: away_player_metrics
        },
        "pass_networks": {
            home_name: home_pass_network,
            away_name: away_pass_network
        }
    }

def build_team_pass_network(events: List[dict], team_players: Dict[str, dict]) -> dict:
    """Build a pass network for a team."""
    # Track passes between players
    pass_connections = defaultdict(lambda: defaultdict(int))
    
    # Events that represent passes
    pass_events = [e for e in events if e['type'] in ['E65', 'E16', 'E68']]  # completed passes
    
    for event in pass_events:
        if 'player_roles' not in event or len(event['player_roles']) < 2:
            continue
            
        # Find passer and receiver
        passer = None
        receiver = None
        
        # This is simplified - would need role type detection for actual implementation
        if len(event['player_roles']) >= 2:
            passer_role = event['player_roles'][0]
            receiver_role = event['player_roles'][1]
            
            passer = passer_role.get('player_uuid')
            receiver = receiver_role.get('player_uuid')
        
        # Check if both players are on the same team
        if passer and receiver and passer in team_players and receiver in team_players and passer != receiver:
            pass_connections[passer][receiver] += 1
    
    # Convert to network format
    nodes = []
    edges = []
    
    # Add all players as nodes
    for player_id, player_info in team_players.items():
        nodes.append({
            "id": player_id,
            "name": player_info.get('player_name', 'Unknown'),
            "position": player_info.get('position', 'Unknown'),
            "jersey": player_info.get('jersey_number', 0)
        })
    
    # Add pass connections as edges
    for passer, receivers in pass_connections.items():
        for receiver, count in receivers.items():
            if count >= 2:  # Only include meaningful connections
                edges.append({
                    "source": passer,
                    "target": receiver,
                    "weight": count
                })
    
    # Calculate network centrality (simplistic implementation)
    centrality = {}
    for player_id in team_players:
        # Out-degree: how many passes a player makes to others
        out_degree = sum(pass_connections[player_id].values())
        
        # In-degree: how many passes a player receives from others
        in_degree = sum(pass_connections[other][player_id] for other in pass_connections)
        
        centrality[player_id] = {
            "out_degree": out_degree,
            "in_degree": in_degree,
            "centrality": out_degree + in_degree
        }
    
    # Find strongest connections
    all_connections = []
    for passer, receivers in pass_connections.items():
        for receiver, count in receivers.items():
            if passer in team_players and receiver in team_players:
                all_connections.append((passer, receiver, count))
    
    strongest_connections = sorted(all_connections, key=lambda x: x[2], reverse=True)[:10]
    
    # Convert to named connections for LLM readability
    named_connections = []
    for passer, receiver, count in strongest_connections:
        if passer in team_players and receiver in team_players:
            named_connections.append({
                "passer": team_players[passer].get('player_name', 'Unknown'),
                "receiver": team_players[receiver].get('player_name', 'Unknown'),
                "count": count
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "centrality": centrality,
        "strongest_connections": named_connections
    }

def extract_player_metrics(events: List[dict], team_players: Dict[str, dict], 
                           player_involvements: Dict[str, int], player_events: Dict[str, List[dict]], 
                           physical_data: dict = None) -> List[dict]:
    """Extract comprehensive metrics for each player."""
    player_metrics = []
    
    for player_id, player_info in team_players.items():
        # Skip players with minimal involvement
        if player_involvements.get(player_id, 0) < 10:
            continue
        
        # Count event types for this player
        player_event_list = player_events.get(player_id, [])
        event_types = Counter(e.get('type') for e in player_event_list)
        
        # Calculate key metrics
        player_profile = {
            "name": player_info.get('player_name', 'Unknown'),
            "position": player_info.get('position', 'Unknown'),
            "jersey": player_info.get('jersey_number', 0),
            "total_involvements": player_involvements.get(player_id, 0),
            "key_contributions": {
                "passes": sum(1 for e in player_event_list if e.get('type') in ['E65', 'E16', 'E68']),
                "defensive_actions": sum(1 for e in player_event_list if e.get('type') in ['E46', 'E22', 'E04', 'E18', 'E37']),
                "attacking_involvement": sum(1 for e in player_event_list if e.get('type') in ['E67', 'E59', 'E07', 'E42', 'E33', 'E34']),
                "pressing_actions": sum(1 for e in player_event_list if e.get('type') in ['E31', 'E09'])
            }
        }
        
        # Add physical data if available
        if physical_data:
            for player_metric in physical_data.get('data', []):
                if player_metric.get('player_uuid') == player_id:
                    metrics = {m.get('type'): m.get('value') for m in player_metric.get('metrics', [])}
                    player_profile["physical"] = {
                        "distance": metrics.get('PM09', 0),
                        "distance_unit": "meters",
                        "sprints": metrics.get('PM04', 0),
                        "top_speed": metrics.get('PM12', 0),
                        "top_speed_unit": "m/s",
                        "high_intensity_distance": metrics.get('PM25', 0),
                        "high_intensity_unit": "meters"
                    }
                    break
        
        # Add progressive actions
        player_profile["progressive_actions"] = {
            "forward_passes": sum(1 for e in player_event_list if e.get('type') == 'E65'),
            "successful_take_ons": sum(1 for e in player_event_list if e.get('type') in ['E55', 'E02']),
            "final_third_entries": sum(1 for e in player_event_list if has_attacking_third_position(e))
        }
        
        # Add zone-based analysis
        zones = [get_event_zone(e) for e in player_event_list]
        zone_counter = Counter(z for z in zones if z != "unknown")
        
        player_profile["zone_activity"] = dict(zone_counter.most_common(3))
        
        player_metrics.append(player_profile)
    
    # Sort by total involvements
    player_metrics.sort(key=lambda p: p.get('total_involvements', 0), reverse=True)
    
    return player_metrics

def analyze_sequential_patterns(tactical_data: dict, event_labels: dict, periods: dict) -> dict:
    """Analyze sequential patterns with enhanced context."""
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Function to analyze sequences for a team
    def analyze_team_sequences(team_uuid, team_name):
        team_events = [e for e in events if e['team_uuid'] == team_uuid]
        team_events = sorted(team_events, key=lambda x: x['start_frame'])
        
        # Split events by half
        first_half_events = [e for e in team_events if e.get('start_frame', 0) < periods['halftime_frame']]
        second_half_events = [e for e in team_events if e.get('start_frame', 0) >= periods['halftime_frame']]
        
        # Find common 3-event sequences
        def find_sequences(event_list):
            sequences = []
            for i in range(len(event_list) - 2):
                # Check if events are within 300 frames (10 seconds) of each other
                if (event_list[i+1]['start_frame'] - event_list[i]['end_frame'] < 300 and 
                    event_list[i+2]['start_frame'] - event_list[i+1]['end_frame'] < 300):
                    
                    # Create a named sequence
                    seq = [
                        event_labels.get(event_list[i]['type'], event_list[i]['type']),
                        event_labels.get(event_list[i+1]['type'], event_list[i+1]['type']),
                        event_labels.get(event_list[i+2]['type'], event_list[i+2]['type'])
                    ]
                    sequences.append(tuple(seq))
            return sequences
        
        all_sequences = find_sequences(team_events)
        first_half_sequences = find_sequences(first_half_events)
        second_half_sequences = find_sequences(second_half_events)
        
        # Count sequence occurrences
        all_counter = Counter(all_sequences)
        first_half_counter = Counter(first_half_sequences)
        second_half_counter = Counter(second_half_sequences)
        
        # Helper function to format sequence results
        def format_sequences(seq_counter):
            top_sequences = []
            for seq, count in seq_counter.most_common(5):
                # Calculate outcomes (simplified)
                outcomes = {"Possession Maintained": 0, "Shot": 0, "Lost Possession": 0}
                
                for i in range(len(team_events) - 3):
                    if (i+2 < len(team_events) and
                        event_labels.get(team_events[i]['type'], team_events[i]['type']) == seq[0] and
                        event_labels.get(team_events[i+1]['type'], team_events[i+1]['type']) == seq[1] and
                        event_labels.get(team_events[i+2]['type'], team_events[i+2]['type']) == seq[2]):
                        
                        # Check outcome (next event after sequence)
                        if i+3 < len(team_events):
                            next_event = team_events[i+3]
                            if next_event['type'] in ['E07', 'E33']:  # Finishing, Goal Chance
                                outcomes["Shot"] += 1
                            elif next_event['type'] in ['E75']:  # Lost Ball
                                outcomes["Lost Possession"] += 1
                            else:
                                outcomes["Possession Maintained"] += 1
                
                # Get average zone info
                zone_progression = []
                for i in range(len(team_events) - 3):
                    if (i+2 < len(team_events) and
                        event_labels.get(team_events[i]['type'], team_events[i]['type']) == seq[0] and
                        event_labels.get(team_events[i+1]['type'], team_events[i+1]['type']) == seq[1] and
                        event_labels.get(team_events[i+2]['type'], team_events[i+2]['type']) == seq[2]):
                        
                        start_zone = get_event_zone(team_events[i])
                        end_zone = get_event_zone(team_events[i+2])
                        if start_zone != "unknown" and end_zone != "unknown":
                            zone_progression.append((start_zone, end_zone))
                
                top_sequences.append({
                    "pattern": list(seq),
                    "occurrences": count,
                    "outcome_distribution": outcomes,
                    "zone_progression": Counter(zone_progression).most_common(1)[0][0] if zone_progression else ("unknown", "unknown"),
                    "tactical_interpretation": interpret_sequence(seq)
                })
            return top_sequences
        
        # Find successful attack patterns (leading to shots)
        attack_patterns = []
        for i in range(len(team_events) - 3):
            if team_events[i+3]['type'] in ['E07', 'E33']:  # Finishing, Goal Chance
                pattern = [
                    event_labels.get(team_events[i]['type'], team_events[i]['type']),
                    event_labels.get(team_events[i+1]['type'], team_events[i+1]['type']),
                    event_labels.get(team_events[i+2]['type'], team_events[i+2]['type'])
                ]
                attack_patterns.append(tuple(pattern))
        
        attack_counter = Counter(attack_patterns)
        highest_success_pattern = attack_counter.most_common(1)
        
        if highest_success_pattern:
            pattern, count = highest_success_pattern[0]
            success_rate = count / len([e for e in team_events if e['type'] in ['E07', 'E33']]) * 100 if team_events else 0
        else:
            pattern, count, success_rate = [], 0, 0
        
        return {
            "most_common_sequences": format_sequences(all_counter),
            "first_half_sequences": format_sequences(first_half_counter),
            "second_half_sequences": format_sequences(second_half_counter),
            "attack_success_paths": {
                "highest_percentage": list(pattern) if pattern else [],
                "success_rate": round(success_rate, 1),
                "tactical_interpretation": interpret_sequence(pattern) if pattern else "No clear pattern identified"
            }
        }
    
    return {
        home_name: analyze_team_sequences(home_uuid, home_name),
        away_name: analyze_team_sequences(away_uuid, away_name)
    }

def interpret_sequence(sequence) -> str:
    """Provide tactical interpretation of a sequence for better LLM understanding."""
    if not sequence:
        return "No sequence to interpret"
    
    # These are simplified interpretations - a real system would have more nuanced analysis
    seq_str = " → ".join(sequence)
    
    # Some example patterns to interpret
    if "Width Of The Team" in seq_str and "Cross Into The Box" in seq_str:
        return "Wing-based attack exploiting width"
    elif "Completed Forward Pass" in seq_str and "Running Into The Box" in seq_str:
        return "Direct vertical attack through the middle"
    elif "Recovered Ball" in seq_str and "Completed Forward Pass" in seq_str:
        return "Counter-attack after winning possession"
    elif "Pressure On The Ball Possessor" in seq_str and "Recovered Ball" in seq_str:
        return "High pressing sequence leading to turnover"
    elif "Width Of The Team" in seq_str and "Switch Of Play" in seq_str:
        return "Using width to stretch defense before switching play"
    elif "Completed Horizontal Pass" in seq_str and "Completed Horizontal Pass" in seq_str:
        return "Possession recycling, maintaining control without progression"
    elif "Defensive Line Imbalance" in seq_str:
        return "Exploiting defensive disorganization"
    elif all("Completed" in event for event in sequence):
        return "Controlled possession sequence"
    elif any("Pressure" in event for event in sequence) and any("Recovery" in event for event in sequence):
        return "Pressing sequence leading to ball recovery"
    else:
        return "General play sequence"

def generate_tactical_summary(tactical_data: dict, team_comparison: dict, tactical_efficiency: dict,
                           sequential_patterns: dict, tactical_imbalances: dict) -> dict:
    """Generate natural language tactical summaries to enhance LLM understanding."""
    metadata = tactical_data['metadata']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # General match summary
    match_score = f"{metadata['home_team_score']} - {metadata['away_team_score']}"
    winner = home_name if metadata['home_team_score'] > metadata['away_team_score'] else away_name if metadata['away_team_score'] > metadata['home_team_score'] else "Draw"
    
    # Get possession stats
    home_possession = team_comparison.get('overall', {}).get('possession', {}).get(home_name, 0)
    away_possession = team_comparison.get('overall', {}).get('possession', {}).get(away_name, 0)
    
    # Get passing stats
    home_pass_completion = team_comparison.get('overall', {}).get('pass_completion', {}).get(home_name, 0)
    away_pass_completion = team_comparison.get('overall', {}).get('pass_completion', {}).get(away_name, 0)
    
    # Get attack patterns
    home_attacks = team_comparison.get('attack_patterns', {}).get(home_name, {})
    away_attacks = team_comparison.get('attack_patterns', {}).get(away_name, {})
    
    # Identify key tactical theme for home team
    home_tactical_theme = "possession-based" if home_possession > 55 else "counter-attacking" if home_attacks.get('counter_attacks', 0) > home_attacks.get('build_up_sequences', 0) else "balanced"
    
    # Identify key tactical theme for away team
    away_tactical_theme = "possession-based" if away_possession > 55 else "counter-attacking" if away_attacks.get('counter_attacks', 0) > away_attacks.get('build_up_sequences', 0) else "balanced"
    
    # Find significant imbalances
    significant_imbalances_home = [imb for imb in tactical_imbalances.get('team_imbalances', {}).get(home_name, []) if abs(float(imb.get('deviation', '0%').rstrip('%'))) > 50]
    significant_imbalances_away = [imb for imb in tactical_imbalances.get('team_imbalances', {}).get(away_name, []) if abs(float(imb.get('deviation', '0%').rstrip('%'))) > 50]
    
    # Generate summaries
    summaries = {
        "match_overview": f"{home_name} {match_score} {away_name}. {winner} won the match with a {home_tactical_theme if winner == home_name else away_tactical_theme} approach.",
        "possession_summary": f"{home_name} had {home_possession}% possession compared to {away_name}'s {away_possession}%, showing a {'dominant' if abs(home_possession - away_possession) > 15 else 'balanced'} control of the ball.",
        "passing_summary": f"{home_name} completed {home_pass_completion}% of their passes, while {away_name} completed {away_pass_completion}%. {'This indicates a significant difference in passing quality.' if abs(home_pass_completion - away_pass_completion) > 10 else 'Both teams showed similar passing quality.'}",
        "attack_patterns": {
            home_name: f"Primary approach: {home_tactical_theme.title()}. Utilized {home_attacks.get('counter_attacks', 0)} counter-attacks and {home_attacks.get('build_up_sequences', 0)} build-up sequences.",
            away_name: f"Primary approach: {away_tactical_theme.title()}. Utilized {away_attacks.get('counter_attacks', 0)} counter-attacks and {away_attacks.get('build_up_sequences', 0)} build-up sequences."
        },
        "tactical_imbalances": {
            home_name: [imb.get('interpretation', 'Significant tactical imbalance') for imb in significant_imbalances_home],
            away_name: [imb.get('interpretation', 'Significant tactical imbalance') for imb in significant_imbalances_away]
        },
        "successful_patterns": {
            home_name: interpret_sequence(sequential_patterns.get(home_name, {}).get('attack_success_paths', {}).get('highest_percentage', [])),
            away_name: interpret_sequence(sequential_patterns.get(away_name, {}).get('attack_success_paths', {}).get('highest_percentage', []))
        }
    }
    
    return summaries

def identify_tactical_imbalances(tactical_data: dict, event_labels: dict, team_comparison: dict) -> dict:
    """Identify tactical imbalances and anomalies in team performances."""
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Get event counts by team
    def get_event_counts(team_uuid):
        team_events = [e for e in events if e['team_uuid'] == team_uuid]
        event_counter = Counter([e['type'] for e in team_events])
        return {event_labels.get(k, k): v for k, v in event_counter.items()}
    
    home_events = get_event_counts(home_uuid)
    away_events = get_event_counts(away_uuid)
    
    # Define benchmark ratios based on typical elite teams
    benchmark_ratios = {
        'Width vs Crossing': 20.0,  # Typical ratio of width events to crosses
        'Pressing vs Recovery': 6.0,  # Typical ratio of pressing actions to recoveries
        'Horizontal vs Forward': 1.8,  # Typical ratio of horizontal to forward passes
        'Shots vs Possession': 0.12  # Typical shots per 1% possession
    }
    
    # Track imbalances for each team
    home_imbalances = []
    away_imbalances = []
    
    # Width vs Crossing imbalance for home team
    width = home_events.get('Width Of The Team', 0)
    crosses = home_events.get('Cross Into The Box', 0)
    if width > 0 and crosses > 0:
        ratio = width / crosses
        deviation = (ratio / benchmark_ratios['Width vs Crossing'] - 1) * 100
        home_imbalances.append({
            "type": "Width vs Crossing",
            "metric1": {"name": "Width Positioning", "value": width},
            "metric2": {"name": "Crosses", "value": crosses},
            "ratio": round(ratio, 1),
            "benchmark_ratio": benchmark_ratios['Width vs Crossing'],
            "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
            "interpretation": "Higher ratio indicates team gets wide but doesn't deliver crosses" if deviation > 0 else 
                             "Lower ratio indicates team crosses efficiently from wide positions"
        })
    
    # Pressing vs Recovery imbalance for home team
    pressing = home_events.get('Pressure On The Ball Possessor', 0)
    recoveries = home_events.get('Recovered Ball', 0)
    if pressing > 0 and recoveries > 0:
        ratio = pressing / recoveries
        deviation = (ratio / benchmark_ratios['Pressing vs Recovery'] - 1) * 100
        home_imbalances.append({
            "type": "Pressing vs Recovery",
            "metric1": {"name": "Pressing Actions", "value": pressing},
            "metric2": {"name": "Ball Recoveries", "value": recoveries},
            "ratio": round(ratio, 1),
            "benchmark_ratio": benchmark_ratios['Pressing vs Recovery'],
            "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
            "interpretation": "Higher ratio indicates inefficient pressing" if deviation > 0 else 
                             "Lower ratio indicates effective pressing leading to recoveries"
        })
    
    # Horizontal vs Forward passing imbalance for home team
    horizontal = home_events.get('Completed Horizontal Pass', 0)
    forward = home_events.get('Completed Forward Pass', 0)
    if horizontal > 0 and forward > 0:
        ratio = horizontal / forward
        deviation = (ratio / benchmark_ratios['Horizontal vs Forward'] - 1) * 100
        home_imbalances.append({
            "type": "Horizontal vs Forward Passing",
            "metric1": {"name": "Horizontal Passes", "value": horizontal},
            "metric2": {"name": "Forward Passes", "value": forward},
            "ratio": round(ratio, 1),
            "benchmark_ratio": benchmark_ratios['Horizontal vs Forward'],
            "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
            "interpretation": "Higher ratio indicates excess sideways passing lacking progression" if deviation > 0 else
                             "Lower ratio indicates direct vertical play"
        })
    
    # Shots vs Possession efficiency for home team
    home_possession = team_comparison.get('overall', {}).get('possession', {}).get(home_name, 0)
    home_shots = team_comparison.get('overall', {}).get('shots', {}).get(home_name, 0)
    if home_possession > 0:
        shot_efficiency = home_shots / home_possession
        benchmark_efficiency = benchmark_ratios['Shots vs Possession']
        deviation = (shot_efficiency / benchmark_efficiency - 1) * 100
        if abs(deviation) > 20:  # Only add if significant
            home_imbalances.append({
                "type": "Shot Generation Efficiency",
                "metric1": {"name": "Shots", "value": home_shots},
                "metric2": {"name": "Possession %", "value": home_possession},
                "ratio": round(shot_efficiency * 100, 2),
                "benchmark_ratio": round(benchmark_efficiency * 100, 2),
                "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
                "interpretation": "Team generates shots efficiently from possession" if deviation > 0 else
                                 "Team struggles to convert possession into shots"
            })
    
    # Width vs Crossing imbalance for away team
    width = away_events.get('Width Of The Team', 0)
    crosses = away_events.get('Cross Into The Box', 0)
    if width > 0 and crosses > 0:
        ratio = width / crosses
        deviation = (ratio / benchmark_ratios['Width vs Crossing'] - 1) * 100
        away_imbalances.append({
            "type": "Width vs Crossing",
            "metric1": {"name": "Width Positioning", "value": width},
            "metric2": {"name": "Crosses", "value": crosses},
            "ratio": round(ratio, 1),
            "benchmark_ratio": benchmark_ratios['Width vs Crossing'],
            "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
            "interpretation": "Higher ratio indicates team gets wide but doesn't deliver crosses" if deviation > 0 else 
                             "Lower ratio indicates team crosses efficiently from wide positions"
        })
    
    # Pressing vs Recovery imbalance for away team
    pressing = away_events.get('Pressure On The Ball Possessor', 0)
    recoveries = away_events.get('Recovered Ball', 0)
    if pressing > 0 and recoveries > 0:
        ratio = pressing / recoveries
        deviation = (ratio / benchmark_ratios['Pressing vs Recovery'] - 1) * 100
        away_imbalances.append({
            "type": "Pressing vs Recovery",
            "metric1": {"name": "Pressing Actions", "value": pressing},
            "metric2": {"name": "Ball Recoveries", "value": recoveries},
            "ratio": round(ratio, 1),
            "benchmark_ratio": benchmark_ratios['Pressing vs Recovery'],
            "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
            "interpretation": "Higher ratio indicates inefficient pressing" if deviation > 0 else 
                             "Lower ratio indicates effective pressing leading to recoveries"
        })
    
    # Shots vs Possession efficiency for away team
    away_possession = team_comparison.get('overall', {}).get('possession', {}).get(away_name, 0)
    away_shots = team_comparison.get('overall', {}).get('shots', {}).get(away_name, 0)
    if away_possession > 0:
        shot_efficiency = away_shots / away_possession
        benchmark_efficiency = benchmark_ratios['Shots vs Possession']
        deviation = (shot_efficiency / benchmark_efficiency - 1) * 100
        if abs(deviation) > 20:  # Only add if significant
            away_imbalances.append({
                "type": "Shot Generation Efficiency",
                "metric1": {"name": "Shots", "value": away_shots},
                "metric2": {"name": "Possession %", "value": away_possession},
                "ratio": round(shot_efficiency * 100, 2),
                "benchmark_ratio": round(benchmark_efficiency * 100, 2),
                "deviation": f"{'+' if deviation > 0 else ''}{round(deviation, 1)}%",
                "interpretation": "Team generates shots efficiently from possession" if deviation > 0 else
                                 "Team struggles to convert possession into shots"
            })
    
    # Add comparative imbalances - where teams significantly differ from each other
    comparative_imbalances = []
    
    # Compare vertical passing approaches
    home_vertical_ratio = home_events.get('Completed Forward Pass', 0) / max(1, home_events.get('Completed Horizontal Pass', 0))
    away_vertical_ratio = away_events.get('Completed Forward Pass', 0) / max(1, away_events.get('Completed Horizontal Pass', 0))
    
    if home_vertical_ratio > 0 and away_vertical_ratio > 0:
        vertical_difference = (home_vertical_ratio / away_vertical_ratio - 1) * 100
        if abs(vertical_difference) > 30:  # Only add if significant
            comparative_imbalances.append({
                "type": "Vertical Passing Contrast",
                "team1": home_name,
                "team2": away_name,
                "team1_ratio": round(home_vertical_ratio, 2),
                "team2_ratio": round(away_vertical_ratio, 2),
                "difference": f"{'+' if vertical_difference > 0 else ''}{round(vertical_difference, 1)}%",
                "interpretation": f"{home_name} plays more vertically than {away_name}" if vertical_difference > 0 else
                                 f"{away_name} plays more vertically than {home_name}"
            })
    
    return {
        "team_imbalances": {
            home_name: home_imbalances,
            away_name: away_imbalances
        },
        "comparative_imbalances": comparative_imbalances
    }

def analyze_defensive_organization(tactical_data: dict, event_labels: dict) -> dict:
    """Analyze defensive organization patterns for both teams."""
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    home_name = metadata['home_team']['name']
    away_name = metadata['away_team']['name']
    
    # Defensive event types
    defending_events = ['E46', 'E22', 'E04', 'E27', 'E71', 'E18', 'E37']
    
    # Get defensive events by team
    home_defensive = [e for e in events if e['team_uuid'] == home_uuid and e['type'] in defending_events]
    away_defensive = [e for e in events if e['team_uuid'] == away_uuid and e['type'] in defending_events]
    
    # Calculate defensive metrics
    def calc_defensive_metrics(team_events):
        # Count event types
        event_counts = Counter([e['type'] for e in team_events])
        named_counts = {event_labels.get(k, k): v for k, v in event_counts.items()}
        
        # Track defensive line events
        line_events = sum(1 for e in team_events if e['type'] in ['E27', 'E71'])
        
        # Estimate defensive height based on event zones
        zones = [get_event_zone(e) for e in team_events]
        defensive_third_count = sum(1 for z in zones if z.startswith('defensive_'))
        middle_third_count = sum(1 for z in zones if z.startswith('middle_'))
        attacking_third_count = sum(1 for z in zones if z.startswith('attacking_'))
        
        total_zoned = defensive_third_count + middle_third_count + attacking_third_count
        
        if total_zoned > 0:
            defensive_height = round((middle_third_count + attacking_third_count * 2) / (total_zoned) * 50, 1)
        else:
            defensive_height = 0
        
        # Estimate defensive width based on central vs wide actions
        central_count = sum(1 for z in zones if '_central' in z)
        wide_count = sum(1 for z in zones if '_left' in z or '_right' in z)
        
        total_positioned = central_count + wide_count
        if total_positioned > 0:
            width_focus = round(wide_count / total_positioned * 100, 1)
        else:
            width_focus = 0
        
        # Estimate pressing intensity based on pressure events
        pressure_events = sum(1 for e in team_events if e['type'] in ['E31', 'E09'])
        
        return {
            "defensive_actions": {
                "total": len(team_events),
                "by_type": named_counts
            },
            "defensive_organization": {
                "line_discipline_issues": line_events,
                "defensive_height": defensive_height,
                "interpretation": interpret_defensive_height(defensive_height),
                "width_focus": width_focus,
                "interpretation_width": "Wide defensive block" if width_focus > 60 else 
                                      "Compact defensive block" if width_focus < 40 else
                                      "Balanced defensive width"
            },
            "pressing_intensity": {
                "pressure_actions": pressure_events,
                "pressure_per_defensive_action": round(pressure_events / max(1, len(team_events)), 2),
                "interpretation": "High-intensity pressing" if pressure_events / max(1, len(team_events)) > 0.5 else
                                "Medium pressing intensity" if pressure_events / max(1, len(team_events)) > 0.25 else
                                "Low pressing intensity"
            },
            "defensive_zones": {
                "defensive_third": defensive_third_count,
                "middle_third": middle_third_count,
                "attacking_third": attacking_third_count,
                "zone_distribution": {
                    "defensive_third": round(defensive_third_count / max(1, total_zoned) * 100, 1),
                    "middle_third": round(middle_third_count / max(1, total_zoned) * 100, 1),
                    "attacking_third": round(attacking_third_count / max(1, total_zoned) * 100, 1)
                }
            }
        }
    
    return {
        home_name: calc_defensive_metrics(home_defensive),
        away_name: calc_defensive_metrics(away_defensive)
    }

def interpret_defensive_height(height_value):
    """Interpret defensive height value."""
    if height_value < 20:
        return "Deep defensive block - team defends close to own goal"
    elif height_value < 40:
        return "Medium-low block - team defends in own defensive third"
    elif height_value < 60:
        return "Medium block - team defends around halfway line"
    elif height_value < 80:
        return "High block - team defends in opponent's half"
    else:
        return "Very high press - team defends in opponent's attacking third"

def extract_balanced_team_event_counts(tactical_data: dict, event_labels: dict) -> dict:
    """
    Extract event counts for both teams using the same consistent methodology.
    Ensures that the same event types are counted for both teams.
    """
    metadata = tactical_data['metadata']
    events = tactical_data['data']
    
    # Get team information
    home_team = metadata['home_team']['name']
    away_team = metadata['away_team']['name']
    home_uuid = metadata['home_team']['uuid']
    away_uuid = metadata['away_team']['uuid']
    
    # Count raw events by type for each team
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
    
    # Add derived metrics consistently for both teams
    
    # Add possession percentage (from elsewhere in analysis)
    if 'possession_percentage' in tactical_data.get('team_stats', {}).get(home_uuid, {}):
        home_events['Possession %'] = tactical_data['team_stats'][home_uuid]['possession_percentage']
    if 'possession_percentage' in tactical_data.get('team_stats', {}).get(away_uuid, {}):
        away_events['Possession %'] = tactical_data['team_stats'][away_uuid]['possession_percentage']
    
    # Ensure both teams have the same event types (with zero counts if needed)
    all_event_types = set(list(home_events.keys()) + list(away_events.keys()))
    for event_type in all_event_types:
        if event_type not in home_events:
            home_events[event_type] = 0
        if event_type not in away_events:
            away_events[event_type] = 0
    
    return {
        "teams": {
            home_team: dict(home_events),
            away_team: dict(away_events)
        },
        "event_types": list(all_event_types)
    }

def main():
    """Main function to process match data."""
    # Check arguments
    if len(sys.argv) < 3:
        print("Usage: python match_analyzer_for_llm.py td.json [physical.json] output.json")
        sys.exit(1)
    
    tactical_data_path = sys.argv[1]
    output_path = sys.argv[-1]
    
    # Determine if physical data is provided
    physical_data_path = None
    if len(sys.argv) == 4:
        physical_data_path = sys.argv[2]
    
    # Load tactical data
    print(f"Loading tactical data from {tactical_data_path}...")
    tactical_data = load_json_data(tactical_data_path)
    
    # Load physical data if provided
    physical_data = None
    if physical_data_path:
        print(f"Loading physical data from {physical_data_path}...")
        try:
            physical_data = load_json_data(physical_data_path)
        except:
            print(f"Warning: Could not load physical data from {physical_data_path}")
    
    # Check for schema
    schema_path = os.path.join(os.path.dirname(tactical_data_path), "tactical-data-schema.json")
    
    # Load event labels
    event_labels = get_event_labels(tactical_data, schema_path)
    
    # Add this after loading tactical data and event labels
    balanced_events = extract_balanced_team_event_counts(tactical_data, event_labels)
    
    # Begin enhanced analysis
    print("Performing comprehensive match analysis...")
    
    # Extract match summary
    match_summary = extract_match_summary(tactical_data)
    
    # Identify match periods
    periods = get_match_periods(tactical_data)
    
    # Identify possession sequences
    possession_sequences = identify_possession_sequences(tactical_data, event_labels)
    
    # Calculate team comparison metrics with temporal breakdown
    team_comparison = calculate_team_comparison(tactical_data, periods, possession_sequences)
    
    # Calculate tactical efficiency metrics
    tactical_efficiency = calculate_tactical_efficiency(tactical_data, event_labels)
    
    # Analyze player networks and contributions
    player_network = analyze_player_network(tactical_data, physical_data)
    
    # Analyze sequential patterns with enhanced context
    sequential_patterns = analyze_sequential_patterns(tactical_data, event_labels, periods)
    
    # Identify tactical imbalances and anomalies
    tactical_imbalances = identify_tactical_imbalances(tactical_data, event_labels, team_comparison)
    
    # Analyze defensive organization
    defensive_organization = analyze_defensive_organization(tactical_data, event_labels)
    
    # Generate tactical summaries
    tactical_summaries = generate_tactical_summary(tactical_data, team_comparison, tactical_efficiency, 
                                                sequential_patterns, tactical_imbalances)
    
    # Compile results into comprehensive analysis
    analysis_results = {
        "match_summary": match_summary,
        "match_periods": periods,
        "team_comparison": team_comparison,
        "tactical_efficiency": tactical_efficiency,
        "player_network": player_network,
        "sequential_patterns": sequential_patterns,
        "tactical_imbalances": tactical_imbalances,
        "defensive_organization": defensive_organization,
        "tactical_summaries": tactical_summaries,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    # Add the balanced events to your output data
    analysis_results["balanced_team_events"] = balanced_events
    
    # Output to JSON file
    print(f"Writing comprehensive analysis to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()