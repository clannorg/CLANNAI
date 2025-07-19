#!/usr/bin/env python3
"""
Player Tracking Synthesis - Simple Timeline
Combines all player tracking results into a chronological timeline
"""

import re
from pathlib import Path
from datetime import datetime

class PlayerTrackingSynthesis:
    def __init__(self, target_player: str = "Player_31"):
        """Initialize the player tracking synthesis"""
        self.target_player = target_player
        
    def load_raw_tracking(self) -> list:
        """Load all player tracking text files and extract performance data"""
        output_dir = Path(__file__).parent / "output"
        
        all_tracking = []
        
        # Find all player tracking text files
        text_files = list(output_dir.glob("player_tracking_*.txt"))
        
        if not text_files:
            raise FileNotFoundError("No player tracking text files found in output directory")
        
        print(f"📂 Loading {len(text_files)} player tracking files...")
        
        for text_file in text_files:
            with open(text_file, 'r') as f:
                content = f.read()
                
            # Extract clip timestamp from filename
            filename = text_file.stem
            clip_timestamp = filename.replace('player_tracking_', '')
            
            # Parse tracking data from the text content
            tracking_data = self._parse_tracking_from_text(content, clip_timestamp)
            if tracking_data:
                all_tracking.append(tracking_data)
        
        # Sort by absolute game time
        all_tracking.sort(key=lambda x: x['absolute_time'])
        
        print(f"✅ Found {len(all_tracking)} tracking segments")
        return all_tracking
    
    def _parse_tracking_from_text(self, content: str, clip_timestamp: str) -> dict:
        """Parse player tracking data from text content"""
        # Calculate base time for this clip
        base_minutes, base_seconds = map(int, clip_timestamp.split('_'))
        base_time = base_minutes * 60 + base_seconds
        
        # Check if player was visible
        if f"{self.target_player} not visible" in content:
            return {
                'clip_timestamp': clip_timestamp,
                'absolute_time': base_time,
                'visible': False,
                'actions': [],
                'formatted_time': self._format_time(base_time)
            }
        
        # Extract actions with timestamps
        actions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Match timestamp pattern (e.g., "0.5s:", "2.1s:", "1:05.2s:")
            timestamp_match = re.search(r'(\d+(?:\.\d+)?)s?:', line)
            if timestamp_match:
                clip_time = float(timestamp_match.group(1))
                absolute_time = base_time + clip_time
                
                # Extract the action description
                action_description = line[line.find(':') + 1:].strip()
                
                actions.append({
                    'clip_time': clip_time,
                    'absolute_time': absolute_time,
                    'description': action_description,
                    'formatted_time': self._format_time(absolute_time)
                })
        
        return {
            'clip_timestamp': clip_timestamp,
            'absolute_time': base_time,
            'visible': True,
            'actions': actions,
            'formatted_time': self._format_time(base_time)
        }
    
    def _format_time(self, seconds: float) -> str:
        """Format absolute time as MM:SS.ss"""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:05.1f}"
    
    def create_timeline(self, tracking_data: list) -> str:
        """Create simple chronological timeline"""
        timeline = f"📅 {self.target_player} GAME TIMELINE\n"
        timeline += "=" * 50 + "\n\n"
        
        if not tracking_data:
            timeline += "No tracking data available.\n"
            return timeline
        
        timeline += f"Total Segments: {len(tracking_data)}\n"
        timeline += f"Time Range: {tracking_data[0]['formatted_time']} - {tracking_data[-1]['formatted_time']}\n\n"
        
        timeline += "CHRONOLOGICAL ACTIVITY:\n"
        timeline += "-" * 40 + "\n\n"
        
        for i, segment in enumerate(tracking_data, 1):
            timeline += f"{i:2d}. {segment['formatted_time']} - "
            
            if not segment['visible']:
                timeline += f"{self.target_player} not visible\n"
            elif not segment['actions']:
                timeline += f"{self.target_player} visible but no specific actions tracked\n"
            else:
                # Show first and last action in segment
                first_action = segment['actions'][0]
                last_action = segment['actions'][-1]
                
                if first_action == last_action:
                    timeline += f"{first_action['description']}\n"
                else:
                    timeline += f"{first_action['description']} → ... → {last_action['description']}\n"
        
        return timeline
    
    def save_timeline(self, timeline: str):
        """Save timeline to synthesis_output directory"""
        synthesis_dir = Path(__file__).parent / "synthesis_output"
        synthesis_dir.mkdir(exist_ok=True)
        
        # Save timeline
        timeline_file = synthesis_dir / f"{self.target_player.lower()}_timeline.txt"
        with open(timeline_file, 'w') as f:
            f.write(timeline)
        
        print(f"📁 Timeline saved to: {synthesis_dir}")
        print(f"   📅 Timeline: {self.target_player.lower()}_timeline.txt")

def main():
    """Run simple player tracking timeline synthesis"""
    print("🎯 PLAYER TRACKING TIMELINE SYNTHESIS")
    print("=" * 40)
    
    # Get target player from the tracking script
    from tracking_clip_analyzer import TARGET_PLAYER
    
    synthesizer = PlayerTrackingSynthesis(target_player=TARGET_PLAYER)
    
    try:
        # Load raw tracking data
        print("📂 Loading raw player tracking data...")
        tracking_data = synthesizer.load_raw_tracking()
        
        if tracking_data:
            # Create timeline
            timeline = synthesizer.create_timeline(tracking_data)
            
            # Print timeline to console
            print("\n" + timeline)
            
            # Save timeline
            synthesizer.save_timeline(timeline)
            
            print(f"\n✅ Timeline synthesis complete!")
            print(f"   📊 Processed {len(tracking_data)} tracking segments")
            print(f"   📅 Created chronological timeline")
        else:
            print("\n❌ No tracking data found to synthesize")
            
    except Exception as e:
        print(f"❌ Error in synthesis: {e}")

if __name__ == "__main__":
    main() 