#!/usr/bin/env python3
"""
Basketball Events JSON Converter
Converts basketball timeline to structured JSON for web visualization
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class BasketballJSONConverter:
    """
    Converts basketball events timeline to structured JSON
    """
    
    def __init__(self):
        self.events = []
        self.teams = {
            "left_team": {
                "name": "Left Team",
                "color": "#FF6B6B",
                "score": 0,
                "shots_made": 0,
                "shots_missed": 0,
                "rebounds": 0,
                "players": {}
            },
            "right_team": {
                "name": "Right Team",
                "color": "#4ECDC4", 
                "score": 0,
                "shots_made": 0,
                "shots_missed": 0,
                "rebounds": 0,
                "players": {}
            }
        }
        
        self.analysis = {
            "possession_changes": 0,
            "fast_breaks": 0,
            "three_pointers": 0,
            "layups": 0,
            "free_throws": 0,
            "turnovers": 0,
            "steals": 0,
            "bystander_shots": 0,
            "game_shots": 0
        }
    
    def parse_timestamp(self, timestamp_str: str) -> float:
        """Convert timestamp string to seconds"""
        # Format: "00:005.9" -> 5.9 seconds
        match = re.match(r'(\d+):(\d+\.?\d*)', timestamp_str)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            return minutes * 60 + seconds
        return 0.0
    
    def determine_team(self, description: str) -> str:
        """Determine which team the player belongs to based on basket location"""
        # The key insight: which basket they're shooting at determines their team
        if "[LEFT BASKET]" in description:
            return "left"
        elif "[RIGHT BASKET]" in description:
            return "right"
        else:
            # Fallback to jersey colors if basket not specified
            description_lower = description.lower()
            if any(color in description_lower for color in ["white jersey", "blue jersey", "purple jersey"]):
                return "left"
            elif any(color in description_lower for color in ["black jersey", "red jersey", "gray jersey", "black shirt"]):
                return "right"
            else:
                return "left"  # Default
    
    def extract_player_info(self, description: str) -> Dict[str, str]:
        """Extract player information from description"""
        player_info = {
            "player": "Unknown",
            "jersey": "Unknown",
            "team_color": "Unknown"
        }
        
        # Extract player name and jersey
        player_match = re.search(r'Player_(\w+)', description)
        if player_match:
            player_info["player"] = f"Player_{player_match.group(1)}"
        
        # Extract jersey number
        jersey_match = re.search(r'#(\d+)', description)
        if jersey_match:
            player_info["jersey"] = f"#{jersey_match.group(1)}"
        
        # Extract team color
        color_match = re.search(r'(\w+)\s+jersey', description)
        if color_match:
            player_info["team_color"] = color_match.group(1)
        
        # Filter out bystanders and practice players
        description_lower = description.lower()
        if any(word in description_lower for word in ["bystander", "practice shot", "sideline", "walks away"]):
            player_info["player"] = "Bystander"
            player_info["jersey"] = "Bystander"
        
        return player_info
    
    def categorize_event(self, description: str) -> Dict[str, str]:
        """Categorize event type and details"""
        description_lower = description.lower()
        
        event_info = {
            "event_type": "other",
            "shot_type": None,
            "outcome": None,
            "rebound_type": None
        }
        
        # Shot events
        if any(word in description_lower for word in ["jump shot", "layup", "shot"]):
            event_info["event_type"] = "shot"
            
            if "layup" in description_lower:
                event_info["shot_type"] = "layup"
            elif "three point" in description_lower:
                event_info["shot_type"] = "three_pointer"
            elif "free throw" in description_lower:
                event_info["shot_type"] = "free_throw"
            else:
                event_info["shot_type"] = "jump_shot"
            
            if "MADE" in description:
                event_info["outcome"] = "made"
            elif "MISSED" in description:
                event_info["outcome"] = "missed"
        
        # Rebound events
        elif "rebound" in description_lower:
            event_info["event_type"] = "rebound"
            if "defensive" in description_lower:
                event_info["rebound_type"] = "defensive"
            else:
                event_info["rebound_type"] = "offensive"
        
        # Pass events
        elif "pass" in description_lower:
            event_info["event_type"] = "pass"
        
        # Dribble events
        elif "dribble" in description_lower:
            event_info["event_type"] = "dribble"
        
        return event_info
    
    def determine_basket(self, description: str) -> str:
        """Determine which basket the event occurred at"""
        if "[LEFT BASKET]" in description:
            return "left"
        elif "[RIGHT BASKET]" in description:
            return "right"
        else:
            return "unknown"
    
    def parse_event_line(self, line: str, event_id: int) -> Dict[str, Any]:
        """Parse a single event line"""
        # Skip header lines
        if not line.strip() or "=" in line or "BASKETBALL" in line or "CHRONOLOGICAL" in line:
            return None
        
        # Extract timestamp and description
        # Format: "1. 00:005.9 - Player_86 (White jersey #86) takes a jump shot – MISSED [LEFT BASKET]"
        match = re.match(r'\s*(\d+)\.\s+(\d+:\d+\.?\d*)\s+-\s+(.+)', line)
        if not match:
            return None
        
        event_number = int(match.group(1))
        timestamp = match.group(2)
        description = match.group(3)
        
        # Parse timestamp
        seconds = self.parse_timestamp(timestamp)
        
        # Determine team
        team = self.determine_team(description)
        
        # Extract player info
        player_info = self.extract_player_info(description)
        
        # Categorize event
        event_details = self.categorize_event(description)
        
        # Determine basket
        basket = self.determine_basket(description)
        
        return {
            "id": event_id,
            "timestamp": timestamp,
            "seconds": seconds,
            "team": team,
            "player": player_info["player"],
            "jersey": player_info["jersey"],
            "team_color": player_info["team_color"],
            "event_type": event_details["event_type"],
            "shot_type": event_details["shot_type"],
            "outcome": event_details["outcome"],
            "rebound_type": event_details["rebound_type"],
            "basket": basket,
            "description": description,
            "bystander": player_info["player"] == "Bystander"
        }
    
    def update_team_stats(self, event: Dict[str, Any]):
        """Update team statistics based on event"""
        team_key = f"{event['team']}_team"
        
        # Only count actual game players (not bystanders)
        player = event['player']
        if player != "Bystander" and player != "Unknown":
            if player not in self.teams[team_key]["players"]:
                self.teams[team_key]["players"][player] = {
                    "jersey": event['jersey'],
                    "events": 0
                }
            self.teams[team_key]["players"][player]["events"] += 1
        
        # Update shot stats (only for actual game players)
        if event['event_type'] == 'shot':
            if player == "Bystander":
                # Count bystander shots but don't add to team score
                self.analysis["bystander_shots"] += 1
            else:
                # Count game shots and add to team score
                self.analysis["game_shots"] += 1
                if event['outcome'] == 'made':
                    self.teams[team_key]["shots_made"] += 1
                    self.teams[team_key]["score"] += 2  # Assume 2 points
                else:
                    self.teams[team_key]["shots_missed"] += 1
        
        # Update rebound stats (only for actual game players)
        elif event['event_type'] == 'rebound' and player != "Bystander":
            self.teams[team_key]["rebounds"] += 1
    
    def update_analysis_stats(self, event: Dict[str, Any]):
        """Update analysis statistics"""
        if event['event_type'] == 'shot':
            if event['shot_type'] == 'three_pointer':
                self.analysis["three_pointers"] += 1
            elif event['shot_type'] == 'layup':
                self.analysis["layups"] += 1
            elif event['shot_type'] == 'free_throw':
                self.analysis["free_throws"] += 1
        
        # Simple possession change detection (when team changes)
        if len(self.events) > 0:
            prev_event = self.events[-1]
            if prev_event['team'] != event['team']:
                self.analysis["possession_changes"] += 1
    
    def convert_timeline(self, timeline_path: str) -> Dict[str, Any]:
        """Convert timeline file to structured JSON"""
        timeline_file = Path(timeline_path)
        
        if not timeline_file.exists():
            raise FileNotFoundError(f"Timeline file not found: {timeline_path}")
        
        # Read timeline file
        with open(timeline_file, 'r') as f:
            lines = f.readlines()
        
        # Parse events
        event_id = 1
        for line in lines:
            event = self.parse_event_line(line, event_id)
            if event:
                self.events.append(event)
                self.update_team_stats(event)
                self.update_analysis_stats(event)
                event_id += 1
        
        # Calculate match info
        if self.events:
            start_time = self.events[0]["timestamp"]
            end_time = self.events[-1]["timestamp"]
            duration = f"{int(self.events[-1]['seconds'] // 60)}:{self.events[-1]['seconds'] % 60:05.1f}"
        else:
            start_time = "00:000.0"
            end_time = "00:000.0"
            duration = "0:00.0"
        
        # Limit each team to top 5 players (actual game players)
        for team_key in ["left_team", "right_team"]:
            if team_key in self.teams:
                # Sort players by event count and keep only top 5
                sorted_players = sorted(
                    self.teams[team_key]["players"].items(),
                    key=lambda x: x[1]["events"],
                    reverse=True
                )
                self.teams[team_key]["players"] = dict(sorted_players[:5])
        
        # Create final JSON structure
        result = {
            "match_info": {
                "title": "Basketball Game Analysis",
                "duration": duration,
                "time_range": f"{start_time} - {end_time}",
                "total_events": len(self.events)
            },
            "teams": self.teams,
            "events": self.events,
            "analysis": self.analysis
        }
        
        return result
    
    def save_json(self, data: Dict[str, Any], output_path: str):
        """Save JSON data to file"""
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ JSON saved to: {output_path}")

def main():
    """Main function"""
    converter = BasketballJSONConverter()
    
    # Input and output paths (relative to A2 directory)
    timeline_path = "1_game_events/synthesis_output/events_timeline.txt"
    output_path = "1_game_events/synthesis_output/basketball_analysis.json"
    
    print("🏀 Basketball Events JSON Converter")
    print("=" * 40)
    print(f"Input: {timeline_path}")
    print(f"Output: {output_path}")
    print()
    
    try:
        # Convert timeline to JSON
        result = converter.convert_timeline(timeline_path)
        
        # Save JSON
        converter.save_json(result, output_path)
        
        # Print summary
        print(f"\n📊 Conversion Summary:")
        print(f"   Total events: {result['match_info']['total_events']}")
        print(f"   Duration: {result['match_info']['duration']}")
        print(f"   Left team score: {result['teams']['left_team']['score']}")
        print(f"   Right team score: {result['teams']['right_team']['score']}")
        print(f"   Left team players: {len(result['teams']['left_team']['players'])}")
        print(f"   Right team players: {len(result['teams']['right_team']['players'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 