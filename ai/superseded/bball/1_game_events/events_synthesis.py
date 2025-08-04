#!/usr/bin/env python3
"""
Basketball Events Synthesis - Simple Timeline
Combines all event text files into a chronological timeline
"""

import re
from pathlib import Path
from datetime import datetime

class EventsSynthesis:
    def __init__(self):
        """Initialize the events synthesis"""
        pass
    
    def load_raw_events(self) -> list:
        """Load all event text files and extract events with timestamps"""
        output_dir = Path(__file__).parent / "output"
        
        all_events = []
        
        # Find all event text files
        text_files = list(output_dir.glob("events_analysis_*.txt"))
        
        if not text_files:
            raise FileNotFoundError("No event analysis text files found in output directory")
        
        print(f"📂 Loading {len(text_files)} event analysis files...")
        
        for text_file in text_files:
            with open(text_file, 'r') as f:
                content = f.read()
                
            # Extract clip timestamp from filename
            filename = text_file.stem
            clip_timestamp = filename.replace('events_analysis_', '')
            
            # Parse events from the text content
            events = self._parse_events_from_text(content, clip_timestamp)
            all_events.extend(events)
        
        # Sort by absolute game time
        all_events.sort(key=lambda x: x['absolute_time'])
        
        print(f"✅ Found {len(all_events)} total events")
        return all_events
    
    def _parse_events_from_text(self, content: str, clip_timestamp: str) -> list:
        """Parse events from text content with basket identification"""
        events = []
        
        # Calculate base time for this clip
        base_minutes, base_seconds = map(int, clip_timestamp.split('_'))
        base_time = base_minutes * 60 + base_seconds
        
        # Look for lines with timestamps (e.g., "8.5s:", "12.3s:")
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Match timestamp pattern (e.g., "8.5s:", "12.3s:", "1:05.2s:")
            timestamp_match = re.search(r'(\d+(?:\.\d+)?)s?:', line)
            if timestamp_match:
                clip_time = float(timestamp_match.group(1))
                absolute_time = base_time + clip_time
                
                # Extract the event description
                event_description = line[line.find(':') + 1:].strip()
                
                # Extract basket information if present
                basket_info = ""
                if "[LEFT BASKET]" in event_description:
                    basket_info = " [LEFT BASKET]"
                    event_description = event_description.replace("[LEFT BASKET]", "").strip()
                elif "[RIGHT BASKET]" in event_description:
                    basket_info = " [RIGHT BASKET]"
                    event_description = event_description.replace("[RIGHT BASKET]", "").strip()
                
                events.append({
                    'clip_timestamp': clip_timestamp,
                    'clip_time': clip_time,
                    'absolute_time': absolute_time,
                    'description': event_description,
                    'basket_info': basket_info,
                    'formatted_time': self._format_time(absolute_time)
                })
        
        return events
    
    def _format_time(self, seconds: float) -> str:
        """Format absolute time as MM:SS.ss"""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:05.1f}"
    
    def create_timeline(self, events: list) -> str:
        """Create a simple chronological timeline"""
        timeline = "🏀 BASKETBALL GAME EVENTS TIMELINE\n"
        timeline += "=" * 50 + "\n\n"
        
        if not events:
            timeline += "No events detected in any clips.\n"
            return timeline
        
        timeline += f"Total Events: {len(events)}\n"
        timeline += f"Time Range: {events[0]['formatted_time']} - {events[-1]['formatted_time']}\n\n"
        
        timeline += "CHRONOLOGICAL EVENTS:\n"
        timeline += "-" * 30 + "\n\n"
        
        for i, event in enumerate(events, 1):
            timeline += f"{i:2d}. {event['formatted_time']} - {event['description']}{event['basket_info']}\n"
        
        return timeline
    
    def save_timeline(self, timeline: str):
        """Save timeline to synthesis_output directory"""
        synthesis_dir = Path(__file__).parent / "synthesis_output"
        synthesis_dir.mkdir(exist_ok=True)
        
        # Save timeline
        timeline_file = synthesis_dir / "events_timeline.txt"
        with open(timeline_file, 'w') as f:
            f.write(timeline)
        
        print(f"📁 Timeline saved to: {synthesis_dir}")
        print("   📝 Text: events_timeline.txt")

def main():
    """Run simple events timeline synthesis"""
    print("🏀 BASKETBALL EVENTS TIMELINE SYNTHESIS")
    print("=" * 40)
    
    synthesizer = EventsSynthesis()
    
    try:
        # Load raw events
        print("📂 Loading raw event analysis...")
        events = synthesizer.load_raw_events()
        
        if events:
            # Create timeline
            timeline = synthesizer.create_timeline(events)
            
            # Print timeline to console
            print("\n" + timeline)
            
            # Save timeline
            synthesizer.save_timeline(timeline)
            
            print(f"\n✅ Timeline synthesis complete!")
            print(f"   📊 Processed {len(events)} events")
            print(f"   🎯 Created chronological timeline")
        else:
            print("\n❌ No events found to synthesize")
            
    except Exception as e:
        print(f"❌ Error in synthesis: {e}")

if __name__ == "__main__":
    main() 