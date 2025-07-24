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
import argparse

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
    
    def parse_event_line(self, line: str, clip_number: int) -> Dict[str, Any]:
        """Parse a single event line from analysis"""
        # Skip header lines, empty lines, and section titles
        line_upper = line.strip().upper()
        if not line_upper or "=" in line_upper or "FOOTBALL EVENTS" in line_upper or "KEY MOMENTS" in line_upper or "MATCH FLOW" in line_upper or "AUDIO DESCRIPTION" in line_upper:
            return None
        
        # Extract timestamp and event details
        timestamp_match = re.match(r'(\d+\.?\d*)s?:', line)
        if not timestamp_match:
            return None
        
        timestamp = float(timestamp_match.group(1))
        event_text = line[line.find(':') + 1:].strip()
        
        # Calculate absolute time (clip start + relative time)
        absolute_time = clip_number + timestamp
        
        # New format: "EVENT_TYPE - Event description"
        match = re.match(r'([A-Z\s_]+)\s*-\s*(.*)', event_text)
        if match:
            event_type_str = match.group(1).strip()
            event_text = match.group(2).strip()
            event_type = event_type_str.lower().replace(" ", "_")
        else:
            # Fallback for lines without an explicit event type
            event_type = "other"
            logger.warning(f"Could not parse explicit event type from line: '{line.strip()}'")

        # Parse event details
        event_data = {
            "clip_number": clip_number,
            "relative_time": timestamp,
            "absolute_time": absolute_time,
            "event_text": event_text,
            "formatted_time": self.format_time(absolute_time)
        }
        
        # Categorize event type
        event_data["event_type"] = event_type
        
        return event_data
    
    # def categorize_event(self, event_text: str) -> str:
    #     """Categorize event based on text content"""
    #     event_text_lower = event_text.lower()
        
    #     if any(word in event_text_lower for word in ["goal", "scores", "scored"]):
    #         return "goals"
    #     elif any(word in event_text_lower for word in ["shot", "shoots", "on target", "off target", "saved", "blocked"]):
    #         return "shots"
    #     elif any(word in event_text_lower for word in ["penalty"]):
    #         return "penalties"
    #     elif any(word in event_text_lower for word in ["yellow card", "red card", "card"]):
    #         return "cards"
    #     elif any(word in event_text_lower for word in ["corner", "corner kick"]):
    #         return "corners"
    #     elif any(word in event_text_lower for word in ["free kick", "foul"]):
    #         return "fouls"
    #     elif any(word in event_text_lower for word in ["substitution", "sub"]):
    #         return "substitutions"
    #     elif any(word in event_text_lower for word in ["tackle", "tackles"]):
    #         return "tackles"
    #     elif any(word in event_text_lower for word in ["pass", "passes"]):
    #         return "passes"
    #     elif any(word in event_text_lower for word in ["turnover", "possession change", "interception", "kick-off", "restart"]):
    #         return "turnovers"
    #     elif any(word in event_text_lower for word in ["referee", "referee indication", "signal"]):
    #         return "referee_action"
    #     elif any(word in event_text_lower for word in ["game start", "kick-off", "start of"]):
    #         return "game_start"
    #     elif any(word in event_text_lower for word in ["dribble", "dribbles", "general play"]):
    #         return "general_play"
    #     elif any(word in event_text_lower for word in ["block"]):
    #         return "blocks"
    #     elif any(word in event_text_lower for word in ["on_ball_action"]):
    #         return "on_ball_actions"
    #     else:
    #         return "other"
    
    def format_time(self, seconds: float) -> str:
        """Format time as MM:SS.ss"""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:05.2f}"
    
    def load_clip_analyses(self) -> List[Dict[str, Any]]:
        """Load all clip analysis files"""
        analyses = []
        
        # Define a sort key to handle the new filename format
        def sort_key(path):
            try:
                time_part = path.stem.split('_')[2] # e.g., "0m00s" from "events_analysis_0m00s_to_0m15s"
                time_str = time_part.replace("m", ":").replace("s", "")
                minutes, seconds = map(int, time_str.split(":"))
                return minutes * 60 + seconds
            except (IndexError, ValueError):
                logger.warning(f"Could not parse start time from {path.name}, using default sorting.")
                return 0

        # Find and sort all analysis files
        analysis_files = sorted(
            [f for f in self.input_dir.glob("events_analysis_*.txt")],
            key=sort_key
        )
        
        if not analysis_files:
            logger.error("No analysis files found")
            return []
        
        logger.info(f"Found {len(analysis_files)} analysis files")
        
        for analysis_file in analysis_files:
            try:
                # Extract the start time in seconds to use as the clip_number
                time_part = analysis_file.stem.split('_')[2]
                time_str = time_part.replace("m", ":").replace("s", "")
                minutes, seconds = map(int, time_str.split(":"))
                clip_number = minutes * 60 + seconds
                clip_identifier = analysis_file.stem.replace("events_analysis_", "")

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
                    "clip_identifier": clip_identifier,
                    "file_path": str(analysis_file),
                    "events": events
                })
                
                logger.info(f"✅ Loaded clip {clip_identifier}: {len(events)} events")
                
            except Exception as e:
                logger.error(f"❌ Error loading clip {analysis_file.name}: {e}")
        
        return analyses
    
    def create_match_timeline(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create chronological match timeline"""
        all_events = []
        
        for analysis in analyses:
            all_events.extend(analysis["events"])
        
        # Sort by absolute time
        all_events.sort(key=lambda x: x["absolute_time"])
        
        # De-duplicate events from overlapping clips
        if not all_events:
            return []

        deduplicated_events = [all_events[0]]
        for i in range(1, len(all_events)):
            current_event = all_events[i]
            last_event = deduplicated_events[-1]
            
            time_difference = abs(current_event['absolute_time'] - last_event['absolute_time'])
            
            # If events are very close in time (within overlap window) and have the same type,
            # they are likely duplicates.
            if time_difference < 4.0 and current_event['event_type'] == last_event['event_type']:
                logger.info(f"Skipping potential duplicate event at {current_event['formatted_time']}: {current_event['event_text']}")
                continue
            
            deduplicated_events.append(current_event)

        # Add event numbers
        for i, event in enumerate(deduplicated_events, 1):
            event["event_number"] = i
        
        return deduplicated_events
    
    def generate_statistics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate match statistics dynamically"""
        stats = {}
        
        for event in events:
            event_type = event.get("event_type", "unknown")
            stats[event_type] = stats.get(event_type, 0) + 1
            
        stats["total_events"] = len(events)
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

    def synthesize_events(self, game_name: str):
        """Main synthesis process"""
        logger.info("🔄 Starting football events synthesis...")
        
        # Paths are now set in the main() function based on args
        
        # Check if synthesis is needed
        timeline_path = self.output_dir / "events_timeline.json"
        if timeline_path.exists():
            last_synthesis_time = timeline_path.stat().st_mtime
            analysis_files = self.input_dir.glob("events_analysis_*.txt")
            
            # Find the most recently modified analysis file
            latest_analysis_time = 0
            if any(analysis_files):
                 latest_analysis_time = max(f.stat().st_mtime for f in self.input_dir.glob("events_analysis_*.txt") if f.is_file())

            if latest_analysis_time and last_synthesis_time >= latest_analysis_time:
                logger.info("✅ Synthesis is up-to-date. Nothing to do.")
                return None # Indicate that no work was done
        
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
    parser = argparse.ArgumentParser(description="Synthesize football event analyses for a specific game.")
    parser.add_argument("--game_name", required=True, help="The name of the game to synthesize (e.g., Game298_0601).")
    parser.add_argument("--run_timestamp", required=True, help="The timestamp for this pipeline run.")
    args = parser.parse_args()

    synthesizer = FootballEventsSynthesis()
    
    # Update paths to be game-specific and include the run timestamp
    synthesizer.input_dir = Path.cwd() / "1_game_events" / "output" / args.game_name / args.run_timestamp
    synthesizer.output_dir = Path.cwd() / "1_game_events" / "synthesis" / args.game_name / args.run_timestamp
    synthesizer.output_dir.mkdir(parents=True, exist_ok=True)

    print("🔄 Football Events Synthesis")
    print("=" * 30)
    print(f"Input directory: {synthesizer.input_dir}")
    print(f"Output directory: {synthesizer.output_dir}")
    print()
    
    # Run synthesis
    result = synthesizer.synthesize_events(args.game_name)
    
    if result:
        print(f"\n✅ Synthesis complete!")
        print(f"📄 Timeline saved: {result['timeline_path']}")
        print(f"📊 Statistics saved: {result['stats_path']}")
        print(f"📈 Total events: {result['total_events']}")
        
        # Print summary statistics
        stats = result['statistics']
        print(f"\n📊 Event Summary:")
        
        # Dynamically print all statistics, sorted alphabetically
        # Exclude 'total_events' from the sorted list to avoid printing it here
        sorted_stats = sorted([item for item in stats.items() if item[0] != 'total_events'])
        
        for event_type, count in sorted_stats:
            # Make the event type name pretty for printing
            display_name = event_type.replace("_", " ").title()
            print(f"   {display_name}: {count}")
    else:
        print("\nℹ️  No new events to synthesize or synthesis was not required.")

if __name__ == "__main__":
    main() 