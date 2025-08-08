#!/usr/bin/env python3
"""
Step 4: Detailed Player Tracker (Parallel Version)
Tracks a specific player throughout the game using file upload and parallel processing.
Based on the working 4_simple_clip_analyzer.py approach.
"""

import os
import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / 'ai' / '.env')

class DetailedPlayerTrackerParallel:
    def __init__(self):
        """Initialize the detailed player tracker with Gemini 2.5 Pro."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        print("🤖 Detailed player tracker initialized with Gemini 2.5 Pro")

    def get_detailed_tracking_prompt(self, clip_timestamp: str) -> str:
        """Generate prompt for detailed player tracking."""
        return f"""You are tracking a SPECIFIC player throughout this football clip.
        TARGET PLAYER:
        - **White guy with grey t-shirt** under orange bib
        - Track EVERY action this player makes in this 15-second clip
        CLIP INFO:
        - Timestamp: {clip_timestamp}
        - Duration: 15 seconds
        TASK:
        Track the target player's EXACT actions with timestamps within this 15-second clip (00:00 to 00:15).
        For each action, note:
        - **Timestamp** (00:00 to 00:15 within this clip)
        - **Action type** (pass, shot, tackle, dribble, run, etc.)
        - **Description** (what exactly happened)
        - **Position** (where on pitch)
        - **Quality** (good, poor, excellent, etc.)
        Format your response as:
        "TARGET PLAYER ACTIONS IN THIS CLIP:
        00:02 - Receives pass from teammate, controls ball well
        00:05 - Makes short pass to left, good accuracy
        00:08 - Runs to space, good movement
        00:12 - Tackles opponent, wins ball back"
        If the target player is not visible, say "TARGET PLAYER NOT VISIBLE IN THIS CLIP."
        If the target player is visible but not active, say "TARGET PLAYER VISIBLE BUT NOT ACTIVE - [describe what they're doing]"
        Be EXACT and DETAILED about every action the target player makes."""

    def analyze_single_clip(self, clip_path: Path) -> tuple:
        """Analyze a single clip for detailed player tracking."""
        try:
            # Extract timestamp from filename
            filename = clip_path.stem
            if 'clip_' in filename:
                time_part = filename.replace('clip_', '').replace('m', ':').replace('s', '')
                if ':' in time_part:
                    parts = time_part.split(':')
                    timestamp = f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
                else:
                    timestamp = "00:00"
            else:
                timestamp = "00:00"

            print(f"📹 Analyzing {timestamp}: {clip_path.name}")
            
            # Upload and analyze clip
            uploaded_file = genai.upload_file(str(clip_path))
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name == "FAILED":
                return timestamp, "Analysis failed", False

            # Generate analysis
            response = self.model.generate_content([
                uploaded_file,
                self.get_detailed_tracking_prompt(timestamp)
            ])
            
            # Clean up uploaded file
            genai.delete_file(uploaded_file.name)
            
            analysis = response.text.strip()
            player_found = "TARGET PLAYER NOT VISIBLE" not in analysis
            
            print(f"✅ {timestamp}: {'PLAYER FOUND' if player_found else 'Player not found'}")
            
            return timestamp, analysis, player_found
            
        except Exception as e:
            print(f"❌ Error analyzing {clip_path.name}: {str(e)}")
            return timestamp, f"Error: {str(e)}", False

    def track_player_throughout_game(self, game_id: str, start_clip: int = 0, end_clip: Optional[int] = None) -> bool:
        """Track the target player throughout the game using parallel processing."""
        print(f"🎯 Step 4: Detailed Player Tracking (Parallel) for {game_id}")
        
        # Setup paths
        data_dir = Path(f"../data/{game_id}")
        clips_dir = data_dir / "clips"
        output_dir = Path(f"../output/{game_id}")
        output_dir.mkdir(exist_ok=True)
        
        # Get all clip files
        clip_files = sorted([f for f in clips_dir.glob("clip_*.mp4")])
        total_clips = len(clip_files)
        
        if not clip_files:
            print("❌ No clip files found")
            return False
        
        print(f"📊 Found {total_clips} total clips")
        
        # Determine clip range
        if end_clip is None:
            end_clip = total_clips
        
        clips_to_analyze = clip_files[start_clip:end_clip]
        print(f"🎯 Analyzing clips {start_clip} to {end_clip} ({len(clips_to_analyze)} clips)")
        
        # Process clips in parallel
        detailed_analyses = []
        player_found_count = 0
        
        print(f"🎯 Using parallel processing with Gemini 2.5 Pro (10 workers)")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks
            future_to_clip = {
                executor.submit(self.analyze_single_clip, clip_path): clip_path 
                for clip_path in clips_to_analyze
            }
            
            # Process results as they complete
            for future in as_completed(future_to_clip):
                clip_path = future_to_clip[future]
                
                try:
                    timestamp, analysis, player_found = future.result()
                    
                    # Store analysis
                    detailed_analyses.append({
                        "clip_filename": clip_path.name,
                        "clip_timestamp": timestamp,
                        "analysis": analysis,
                        "player_found": player_found
                    })
                    
                    if player_found:
                        player_found_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to process {clip_path.name}: {str(e)}")
        
        # Save detailed analyses
        detailed_analyses_path = output_dir / "detailed_player_analyses_parallel.json"
        with open(detailed_analyses_path, 'w') as f:
            json.dump(detailed_analyses, f, indent=2)
        
        # Generate summary
        summary_lines = [
            f"🎯 DETAILED PLAYER TRACKING SUMMARY (Parallel)",
            f"Game: {game_id}",
            f"Clips analyzed: {len(clips_to_analyze)}",
            f"Player found in: {player_found_count} clips",
            f"Success rate: {(player_found_count/len(clips_to_analyze)*100):.1f}%",
            f"",
            f"📊 CLIP-BY-CLIP ANALYSIS:",
            f""
        ]
        
        for analysis in detailed_analyses:
            summary_lines.append(f"🕐 {analysis['clip_timestamp']}:")
            if analysis['player_found']:
                summary_lines.append(f"   ✅ Player found - {analysis['analysis'][:100]}...")
            else:
                summary_lines.append(f"   ❌ Player not found")
            summary_lines.append("")
        
        # Save summary
        summary_path = output_dir / "detailed_player_summary_parallel.txt"
        with open(summary_path, 'w') as f:
            f.write('\n'.join(summary_lines))
        
        print(f"✅ Detailed tracking complete!")
        print(f"📁 Results saved to:")
        print(f"   - {detailed_analyses_path}")
        print(f"   - {summary_path}")
        print(f"🎯 Player found in {player_found_count}/{len(clips_to_analyze)} clips")
        
        return True

def main():
    """Main function to run detailed player tracking."""
    if len(sys.argv) < 2:
        print("Usage: python 4_detailed_tracker_parallel.py <game-id> [start_clip] [end_clip]")
        print("Example: python 4_detailed_tracker_parallel.py brixton5s-20240807 0 40")
        sys.exit(1)
    
    game_id = sys.argv[1]
    start_clip = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end_clip = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    tracker = DetailedPlayerTrackerParallel()
    success = tracker.track_player_throughout_game(game_id, start_clip, end_clip)
    
    if success:
        print(f"🎯 Ready for Step 5: Final player analysis and insights")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 