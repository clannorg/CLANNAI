#!/usr/bin/env python3
"""
Football Events Synthesis
Combines all clip analyses into complete match timeline
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent / "0_utils"))
from config import PATHS, FOOTBALL_SETTINGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballEventsSynthesis:
    """
    Synthesizes football events from individual clip analyses
    Creates complete match timeline and statistics
    """
    
    def __init__(self):
        """Initialize the synthesis system"""
        self.input_dir = PATHS["events_output"]
        self.output_dir = PATHS["events_output"].parent / "synthesis"
        self.output_dir.mkdir(exist_ok=True)
        
        # Event tracking
        self.all_events = []
        self.event_statistics = {
            "goals": 0,
            "shots": 0,
            "passes": 0,
            "tackles": 0,
            "fouls": 0,
            "cards": 0,
            "corners": 0,
            "free_kicks": 0,
            "penalties": 0,
            "substitutions": 0,
            "turnovers": 0,
            "referee_action": 0,
            "game_start": 0,
            "general_play": 0,
            "other": 0
        }
    
    def parse_event_line(self, line: str, clip_number: int) -> Dict[str, Any]:
        """Parse a single event line from analysis"""
        # Skip header lines
        if not line.strip() or "=" in line or "FOOTBALL EVENTS" in line or "KEY MOMENTS" in line or "MATCH FLOW" in line:
            return None
        
        # Extract timestamp and event details - handle both formats
        # New format: "0s: Event description - EVENT TYPE"
        # Old format: "0.6s: Event description"
        timestamp_match = re.match(r'(\d+\.?\d*)s?:', line)
        if not timestamp_match:
            return None
        
        timestamp = float(timestamp_match.group(1))
        event_text = line[line.find(':') + 1:].strip()
        
        # Calculate absolute time (clip start + relative time)
        # For match time clips, clip_number is already the start time in seconds
        if clip_number >= 1000:  # If clip_number is large, it's likely match time in seconds
            absolute_time = clip_number + timestamp
        else:
            # Fallback for old format (clip index * 30 seconds)
            absolute_time = (clip_number * 30) + timestamp
        
        # Parse event details
        event_data = {
            "clip_number": clip_number,
            "relative_time": timestamp,
            "absolute_time": absolute_time,
            "event_text": event_text,
            "formatted_time": self.format_time(absolute_time)
        }
        
        # Categorize event type
        event_type = self.categorize_event(event_text)
        event_data["event_type"] = event_type
        
        return event_data
    
    def categorize_event(self, event_text: str) -> str:
        """Categorize event based on text content"""
        event_text_lower = event_text.lower()
        
        if any(word in event_text_lower for word in ["goal", "scores", "scored"]):
            return "goal"
        elif any(word in event_text_lower for word in ["shot", "shoots", "on target", "off target", "saved", "blocked"]):
            return "shot"
        elif any(word in event_text_lower for word in ["penalty"]):
            return "penalty"
        elif any(word in event_text_lower for word in ["yellow card", "red card", "card"]):
            return "card"
        elif any(word in event_text_lower for word in ["corner", "corner kick"]):
            return "corner"
        elif any(word in event_text_lower for word in ["free kick", "foul"]):
            return "foul"
        elif any(word in event_text_lower for word in ["substitution", "sub"]):
            return "substitution"
        elif any(word in event_text_lower for word in ["tackle", "tackles"]):
            return "tackle"
        elif any(word in event_text_lower for word in ["pass", "passes"]):
            return "pass"
        elif any(word in event_text_lower for word in ["turnover", "possession change", "interception", "kick-off", "restart"]):
            return "turnover"
        elif any(word in event_text_lower for word in ["referee", "referee indication", "signal"]):
            return "referee_action"
        elif any(word in event_text_lower for word in ["game start", "kick-off", "start of"]):
            return "game_start"
        elif any(word in event_text_lower for word in ["dribble", "dribbles", "general play"]):
            return "general_play"
        else:
            return "other"
    
    def format_time(self, seconds: float) -> str:
        """Format time as MM:SS.ss"""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:05.2f}"
    
    def load_clip_analyses(self) -> List[Dict[str, Any]]:
        """Load all clip analysis files"""
        analyses = []
        
        # Find all analysis files
        analysis_files = sorted([
            f for f in self.input_dir.glob("events_analysis_*.txt")
        ])
        
        if not analysis_files:
            logger.error("No analysis files found")
            return []
        
        logger.info(f"Found {len(analysis_files)} analysis files")
        
        for analysis_file in analysis_files:
            # Extract clip number
            clip_number = int(analysis_file.stem.split('_')[-1])
            
            try:
                with open(analysis_file, 'r') as f:
                    content = f.read()
                
                # Parse events from content
                events = []
                for line in content.split('\n'):
                    event_data = self.parse_event_line(line, clip_number)
                    if event_data:
                        events.append(event_data)
                
                analyses.append({
                    "clip_number": clip_number,
                    "file_path": str(analysis_file),
                    "events": events
                })
                
                logger.info(f"✅ Loaded clip {clip_number:03d}: {len(events)} events")
                
            except Exception as e:
                logger.error(f"❌ Error loading clip {clip_number}: {e}")
        
        return analyses
    
    def create_match_timeline(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create chronological match timeline"""
        all_events = []
        
        for analysis in analyses:
            all_events.extend(analysis["events"])
        
        # Sort by absolute time
        all_events.sort(key=lambda x: x["absolute_time"])
        
        # Add event numbers
        for i, event in enumerate(all_events, 1):
            event["event_number"] = i
        
        return all_events
    
    def generate_statistics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate match statistics"""
        stats = {
            "total_events": len(events),
            "goals": 0,
            "shots": 0,
            "passes": 0,
            "tackles": 0,
            "fouls": 0,
            "cards": 0,
            "corners": 0,
            "free_kicks": 0,
            "penalties": 0,
            "substitutions": 0,
            "turnovers": 0,
            "referee_action": 0,
            "game_start": 0,
            "general_play": 0,
            "other": 0
        }
        
        for event in events:
            event_type = event["event_type"]
            if event_type in stats:
                stats[event_type] += 1
        
        return stats
    
    def create_timeline_text(self, events: List[Dict[str, Any]]) -> str:
        """Create human-readable timeline"""
        timeline = "⚽ FOOTBALL MATCH EVENTS TIMELINE\n"
        timeline += "=" * 50 + "\n\n"
        timeline += f"Total Events: {len(events)}\n"
        
        if events:
            start_time = events[0]["formatted_time"]
            end_time = events[-1]["formatted_time"]
            timeline += f"Time Range: {start_time} - {end_time}\n"
        
        timeline += "\nCHRONOLOGICAL EVENTS:\n"
        timeline += "-" * 30 + "\n\n"
        
        for event in events:
            timeline += f"{event['event_number']:3d}. {event['formatted_time']} - {event['event_text']}\n"
        
        return timeline
    
    def synthesize_events(self):
        """Main synthesis process"""
        logger.info("🔄 Starting football events synthesis...")
        
        # Load all clip analyses
        analyses = self.load_clip_analyses()
        
        if not analyses:
            logger.error("No analyses to synthesize")
            return
        
        # Create match timeline
        timeline_events = self.create_match_timeline(analyses)
        
        # Generate statistics
        statistics = self.generate_statistics(timeline_events)
        
        # Create timeline text
        timeline_text = self.create_timeline_text(timeline_events)
        
        # Save timeline
        timeline_path = self.output_dir / "events_timeline.txt"
        with open(timeline_path, 'w') as f:
            f.write(timeline_text)
        
        # Save timeline JSON
        timeline_json = {
            "match_info": {
                "total_events": len(timeline_events),
                "total_clips": len(analyses),
                "synthesis_date": datetime.now().isoformat()
            },
            "statistics": statistics,
            "events": timeline_events
        }
        
        timeline_json_path = self.output_dir / "events_timeline.json"
        with open(timeline_json_path, 'w') as f:
            json.dump(timeline_json, f, indent=2)
        
        # Save statistics
        stats_path = self.output_dir / "event_statistics.json"
        with open(stats_path, 'w') as f:
            json.dump(statistics, f, indent=2)
        
        logger.info(f"✅ Synthesis complete:")
        logger.info(f"   📄 Timeline: {timeline_path}")
        logger.info(f"   📊 Statistics: {stats_path}")
        logger.info(f"   📈 Total events: {len(timeline_events)}")
        
        return {
            "timeline_path": str(timeline_path),
            "timeline_json_path": str(timeline_json_path),
            "stats_path": str(stats_path),
            "total_events": len(timeline_events),
            "statistics": statistics
        }

def main():
    """Main function for football events synthesis"""
    synthesizer = FootballEventsSynthesis()
    
    print("🔄 Football Events Synthesis")
    print("=" * 30)
    print(f"Input directory: {PATHS['events_output']}")
    print(f"Output directory: {PATHS['events_output'].parent / 'synthesis'}")
    print()
    
    # Run synthesis
    result = synthesizer.synthesize_events()
    
    if result:
        print(f"\n✅ Synthesis complete!")
        print(f"📄 Timeline saved: {result['timeline_path']}")
        print(f"📊 Statistics saved: {result['stats_path']}")
        print(f"📈 Total events: {result['total_events']}")
        
        # Print summary statistics
        stats = result['statistics']
        print(f"\n📊 Event Summary:")
        print(f"   Goals: {stats['goals']}")
        print(f"   Shots: {stats['shots']}")
        print(f"   Passes: {stats['passes']}")
        print(f"   Tackles: {stats['tackles']}")
        print(f"   Fouls: {stats['fouls']}")
        print(f"   Cards: {stats['cards']}")
    else:
        print("\n❌ Synthesis failed")

if __name__ == "__main__":
    main() 