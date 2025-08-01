#!/usr/bin/env python3
"""
6. Goals & Shots Validator
Smart goal detection with kickoff validation to prevent false positives
Ultra-strict validation rules
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

class GoalsShotsValidator:
    def __init__(self):
        """Initialize the validator with strict patterns"""
        
        # Goal detection patterns
        self.goal_patterns = [
            r'\bgoal\b',
            r'\bscores?\b',
            r'\bfinds?\s+the\s+net\b',
            r'\binto\s+the\s+net\b',
            r'\bback\s+of\s+the\s+net\b'
        ]
        
        # Shot patterns
        self.shot_patterns = [
            r'\bshot\b',
            r'\bshoots?\b',
            r'\btakes?\s+a\s+shot\b',
            r'\bfires?\b',
            r'\bstrike\b'
        ]
        
        # Save patterns
        self.save_patterns = [
            r'\bsaved?\b',
            r'\bsave\b',
            r'\bkeeper\s+stops?\b',
            r'\bgoalkeeper\s+saves?\b',
            r'\bparried\b',
            r'\btipped\s+away\b'
        ]
        
        # Miss patterns  
        self.miss_patterns = [
            r'\bwide\b',
            r'\bover\b',
            r'\bmisses?\b',
            r'\boff\s+target\b',
            r'\binto\s+the\s+stands\b'
        ]
        
        # Kickoff validation patterns
        self.kickoff_patterns = [
            r'\bkickoff\b',
            r'\bkick\s+off\b',
            r'\brestart\b',
            r'\bcentre\s+circle\b',
            r'\bcenter\s+circle\b'
        ]

    def extract_team_from_line(self, line: str) -> str:
        """Extract team (Red/Black) from timeline line"""
        line_lower = line.lower()
        if 'red' in line_lower:
            return 'Red'
        elif 'black' in line_lower:
            return 'Black'
        else:
            return 'Unknown'

    def parse_timestamp(self, timestamp_str: str) -> int:
        """Convert MM:SS to total seconds"""
        try:
            parts = timestamp_str.split(':')
            minutes = int(parts[0])
            seconds = int(parts[1]) if len(parts) > 1 else 0
            return minutes * 60 + seconds
        except:
            return 0

    def is_goal(self, line: str) -> bool:
        """Check if line describes a goal"""
        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in self.goal_patterns)

    def is_shot(self, line: str) -> bool:
        """Check if line describes a shot"""
        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in self.shot_patterns)

    def get_shot_outcome(self, line: str) -> str:
        """Determine shot outcome (goal, saved, missed, blocked)"""
        line_lower = line.lower()
        
        if self.is_goal(line):
            return 'goal'
        elif any(re.search(pattern, line_lower) for pattern in self.save_patterns):
            return 'saved'
        elif any(re.search(pattern, line_lower) for pattern in self.miss_patterns):
            return 'missed'
        elif 'block' in line_lower:
            return 'blocked'
        else:
            return 'shot'  # Generic shot

    def validate_goal_with_kickoff(self, timeline_lines: list, goal_index: int, goal_team: str) -> bool:
        """Validate goal by checking for opposing team kickoff afterwards"""
        
        # Look for kickoff in next 3-5 lines
        start_search = goal_index + 1
        end_search = min(goal_index + 6, len(timeline_lines))
        
        for i in range(start_search, end_search):
            line = timeline_lines[i]
            line_lower = line.lower()
            
            # Check for kickoff patterns
            if any(re.search(pattern, line_lower) for pattern in self.kickoff_patterns):
                kickoff_team = self.extract_team_from_line(line)
                
                # Valid if opposing team takes kickoff
                if goal_team == 'Red' and kickoff_team == 'Black':
                    return True
                elif goal_team == 'Black' and kickoff_team == 'Red':
                    return True
                    
        return False  # No valid kickoff found

    def analyze_timeline(self, match_id: str) -> bool:
        """Analyze timeline for goals and shots with validation"""
        print(f"⚽ Goals & Shots Validation for {match_id}")
        
        data_dir = Path("../data") / match_id
        timeline_path = data_dir / "complete_timeline.txt"
        output_path = data_dir / "validated_events.json"
        
        if not timeline_path.exists():
            print(f"❌ Timeline file not found: {timeline_path}")
            return False
        
        # Read timeline
        with open(timeline_path, 'r') as f:
            content = f.read()
        
        # Parse timeline lines (skip header comments)
        timeline_lines = [line.strip() for line in content.split('\n') 
                         if line.strip() and not line.startswith('#')]
        
        print(f"📊 Analyzing {len(timeline_lines)} timeline entries")
        
        # Detect events
        events = []
        goals_detected = 0
        shots_detected = 0
        
        for i, line in enumerate(timeline_lines):
            if ' - ' not in line:
                continue
                
            timestamp_str, description = line.split(' - ', 1)
            timestamp_seconds = self.parse_timestamp(timestamp_str)
            team = self.extract_team_from_line(description)
            
            # Check for shots/goals
            if self.is_shot(description) or self.is_goal(description):
                outcome = self.get_shot_outcome(description)
                
                # Special validation for goals
                if outcome == 'goal':
                    is_valid_goal = self.validate_goal_with_kickoff(timeline_lines, i, team)
                    
                    if is_valid_goal:
                        print(f"✅ VALID GOAL: {timestamp_str} - {team} team - {description}")
                        goals_detected += 1
                    else:
                        print(f"⚠️ REJECTED GOAL (no kickoff validation): {timestamp_str} - {description}")
                        outcome = 'shot'  # Downgrade to shot
                
                if outcome in ['goal', 'saved', 'missed', 'blocked']:
                    shots_detected += 1
                
                # Add event
                event = {
                    'timestamp': timestamp_str,
                    'timestamp_seconds': timestamp_seconds,
                    'team': team,
                    'type': outcome.upper(),
                    'description': description,
                    'validated': outcome == 'goal'
                }
                events.append(event)
        
        # Save results
        results = {
            'match_id': match_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'validation_method': 'kickoff_validation',
            'summary': {
                'total_events': len(events),
                'goals': goals_detected,
                'shots': shots_detected,
                'timeline_entries_analyzed': len(timeline_lines)
            },
            'events': events
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Validation complete!")
        print(f"📊 Summary:")
        print(f"   Goals detected: {goals_detected}")
        print(f"   Total shots: {shots_detected}")
        print(f"   Events found: {len(events)}")
        print(f"📁 Output saved to: {output_path}")
        
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 6_goals_shots_validator.py <match-id>")
        print("Example: python 6_goals_shots_validator.py ballyclare-20250111")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        validator = GoalsShotsValidator()
        success = validator.analyze_timeline(match_id)
        
        if success:
            print("🎉 Goals & shots validation completed successfully!")
        else:
            print("❌ Validation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()