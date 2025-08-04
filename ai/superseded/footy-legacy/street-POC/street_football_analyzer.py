#!/usr/bin/env python3
"""
Street Football Analyzer - Complete Pipeline
Split video → Analyze with Gemini → Output CSV
"""

import os
import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

class StreetFootballAnalyzer:
    def __init__(self):
        """Initialize the analyzer"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Setup directories
        self.base_dir = Path(__file__).parent
        self.video_dir = self.base_dir / "videos"
        self.clips_dir = self.base_dir / "clips"
        self.output_dir = self.base_dir / "output"
        
        # Create directories
        self.video_dir.mkdir(exist_ok=True)
        self.clips_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        self.all_events = []
        
    def split_video(self, video_path: str, clip_duration: int = 15) -> List[str]:
        """Split video into 15-second clips"""
        print(f"🎬 Splitting video into {clip_duration}s clips...")
        
        # Get video duration
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', video_path
        ], capture_output=True, text=True)
        
        duration = float(result.stdout.strip())
        print(f"Video duration: {duration:.2f} seconds")
        
        clips = []
        start_time = 0
        
        while start_time < duration:
            clip_name = f"clip_{start_time:06.1f}.mp4"
            clip_path = self.clips_dir / clip_name
            
            # Extract clip
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-ss', str(start_time),
                '-t', str(clip_duration),
                '-c', 'copy',
                '-y', str(clip_path)
            ], capture_output=True)
            
            clips.append(str(clip_path))
            start_time += clip_duration
            
            print(f"✅ Created {clip_name}")
        
        print(f"📁 Created {len(clips)} clips")
        return clips
    
    def analyze_clip(self, clip_path: str, clip_start_time: float) -> List[Dict]:
        """Analyze a single clip with Gemini"""
        try:
            # Encode video for Gemini
            result = subprocess.run([
                'ffmpeg', '-i', clip_path,
                '-vf', 'scale=640:480',
                '-r', '2',
                '-f', 'image2pipe', '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264', '-preset', 'ultrafast',
                '-y', '-'
            ], capture_output=True, check=True)
            
            video_data = result.stdout
            
            prompt = f"""
            Analyze this 15-second football video clip and identify all football events.

            TASK: Detect football events with precise timestamps.

            FOOTBALL EVENTS TO DETECT:
            - Goal: Ball goes into the net
            - Shot: Attempt to score (on target or off target)
            - Save: Goalkeeper saves a shot
            - Pass: Ball passed between players
            - Tackle: Player wins ball from opponent
            - Foul: Illegal contact or play
            - Card: Yellow or red card shown
            - Corner: Corner kick taken
            - Free Kick: Free kick taken
            - Offside: Offside called

            OUTPUT FORMAT (JSON array):
            [
                {{
                    "timestamp": "MM;SS",
                    "event_type": "Goal|Shot|Save|Pass|Tackle|Foul|Card|Corner|Free Kick|Offside",
                    "description": "Brief description of the event",
                    "confidence": 0.85
                }}
            ]

            IMPORTANT:
            - Use MM;SS format for timestamps (e.g., "0;15" for 15 seconds)
            - Only include events that actually happen in the clip
            - Be precise with timestamps relative to the clip start
            - Return valid JSON array only
            """
            
            response = self.model.generate_content([prompt, video_data])
            
            # Parse JSON response
            events = json.loads(response.text)
            
            # Add clip start time to timestamps
            for event in events:
                if "timestamp" in event:
                    # Convert MM;SS to seconds, add clip start, convert back
                    time_parts = event["timestamp"].split(";")
                    if len(time_parts) == 2:
                        minutes, seconds = int(time_parts[0]), int(time_parts[1])
                        total_seconds = minutes * 60 + seconds + clip_start_time
                        new_minutes = int(total_seconds // 60)
                        new_seconds = int(total_seconds % 60)
                        event["timestamp"] = f"{new_minutes};{new_seconds:02d}"
            
            print(f"✅ Analyzed {clip_path}: {len(events)} events")
            return events
            
        except Exception as e:
            print(f"❌ Error analyzing {clip_path}: {e}")
            return []
    
    def synthesize_events(self, all_events: List[Dict]) -> pd.DataFrame:
        """Synthesize all events into CSV format matching manual annotations"""
        
        print("🔄 Synthesizing events into CSV format...")
        
        # Convert to DataFrame format matching manual annotations
        rows = []
        for event in all_events:
            row = {
                'Timestamp': event.get('timestamp', ''),
                'Label': event.get('event_type', ''),
                'Start_offset': 3,  # Default offset
                'End_offset': 2,    # Default offset
                'Description': event.get('description', ''),
                'Camera_view': '',
                'Annotation_view': ''
            }
            rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Sort by timestamp
        df = df.sort_values('Timestamp')
        
        print(f"📊 Created {len(df)} events in CSV format")
        return df
    
    def run_analysis(self, video_path: str):
        """Run complete analysis pipeline"""
        print("🚀 Starting Street Football Analysis Pipeline")
        print("=" * 50)
        
        # Step 1: Split video
        clips = self.split_video(video_path)
        
        # Step 2: Analyze each clip
        all_events = []
        for i, clip_path in enumerate(clips):
            clip_start_time = i * 15  # 15 seconds per clip
            events = self.analyze_clip(clip_path, clip_start_time)
            all_events.extend(events)
            
            # Rate limiting
            time.sleep(1)
        
        print(f"\n📈 Total events detected: {len(all_events)}")
        
        # Step 3: Synthesize into CSV
        df = self.synthesize_events(all_events)
        
        # Save results
        output_csv = self.output_dir / "gemini_events.csv"
        df.to_csv(output_csv, index=False)
        
        print(f"\n✅ Analysis complete!")
        print(f"📁 Results saved to: {output_csv}")
        print(f"📊 Events detected: {len(df)}")
        
        return df

def main():
    """Main function"""
    analyzer = StreetFootballAnalyzer()
    
    # Use the working video file
    video_path = "../Game298_0601/output/Game298_0601_all_music_video_vm004.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    print(f"🎥 Analyzing: {video_path}")
    results = analyzer.run_analysis(video_path)
    
    # Show comparison with manual annotations
    manual_csv = "../Game298_0601/Game298_0601_p1_timestamps.csv"
    if os.path.exists(manual_csv):
        manual_df = pd.read_csv(manual_csv)
        print(f"\n📊 COMPARISON:")
        print(f"Manual annotations: {len(manual_df)} events")
        print(f"Gemini detected: {len(results)} events")

if __name__ == "__main__":
    main() 