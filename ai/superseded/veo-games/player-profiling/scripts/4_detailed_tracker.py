#!/usr/bin/env python3
"""
4. Detailed Player Tracker
Track specific player's exact actions, movements, and timestamps throughout the game
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

class DetailedPlayerTracker:
    def __init__(self):
        """Initialize the detailed player tracker with Gemini"""
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🤖 Detailed player tracker initialized with Gemini 2.0 Flash")

    def get_detailed_tracking_prompt(self, clip_path: str, clip_timestamp: str) -> str:
        """Create prompt for detailed player tracking"""
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

    def analyze_clip_for_detailed_tracking(self, clip_path: str, clip_timestamp: str) -> str:
        """Analyze a single clip for detailed player tracking"""
        print(f"🔍 Detailed tracking in clip: {clip_timestamp}")
        
        try:
            # Create the prompt
            prompt = self.get_detailed_tracking_prompt(clip_path, clip_timestamp)
            
            # Generate response from Gemini
            response = self.model.generate_content([prompt, clip_path])
            
            print(f"✅ Detailed analysis for {clip_timestamp}")
            return response.text
                
        except Exception as e:
            print(f"❌ Error analyzing clip {clip_timestamp}: {e}")
            return f"Error analyzing clip {clip_timestamp}: {str(e)}"

    def track_player_throughout_game(self, game_id: str, start_clip: int = 0, end_clip: int = None) -> bool:
        """Track the target player throughout the entire game"""
        print(f"🎯 Step 4: Detailed Player Tracking for {game_id}")
        
        data_dir = Path("../data") / game_id
        clips_dir = data_dir / "clips"
        segments_file = clips_dir / "segments.json"
        
        if not clips_dir.exists():
            print(f"❌ Clips directory not found: {clips_dir}")
            print("Run Step 1 first: python 1_generate_clips.py")
            return False
        
        if not segments_file.exists():
            print(f"❌ Segments file not found: {segments_file}")
            return False
        
        # Load clips metadata
        with open(segments_file, 'r') as f:
            segments_data = json.load(f)
        
        clips = segments_data.get("clips", [])
        print(f"📊 Found {len(clips)} total clips")
        
        # Filter clips by range if specified
        if end_clip is None:
            end_clip = len(clips)
        
        clips_to_analyze = clips[start_clip:end_clip]
        print(f"🎯 Analyzing clips {start_clip} to {end_clip} ({len(clips_to_analyze)} clips)")
        
        # Analyze each clip
        detailed_analyses = []
        player_found_count = 0
        
        for i, clip_info in enumerate(clips_to_analyze, 1):
            clip_filename = clip_info["filename"]
            clip_timestamp = clip_info["timestamp"]
            clip_path = clips_dir / clip_filename
            
            if not clip_path.exists():
                print(f"⚠️  Clip not found: {clip_filename}")
                continue
            
            print(f"🔄 Processing clip {i}/{len(clips_to_analyze)}: {clip_filename}")
            
            # Analyze the clip
            analysis = self.analyze_clip_for_detailed_tracking(str(clip_path), clip_timestamp)
            
            # Check if target player was found
            if "not visible" not in analysis.lower():
                player_found_count += 1
                print(f"🎯 PLAYER FOUND in {clip_timestamp}!")
            
            detailed_analyses.append({
                "clip_filename": clip_filename,
                "clip_timestamp": clip_timestamp,
                "game_timestamp": clip_timestamp,  # This is the actual game time
                "analysis": analysis,
                "player_found": "not visible" not in analysis.lower()
            })
            
            # Small delay to avoid rate limits
            time.sleep(1)
            
            # Show progress every 10 clips
            if i % 10 == 0:
                print(f"  📊 Progress: {i}/{len(clips_to_analyze)} clips analyzed")
        
        # Create comprehensive action summary
        print("🔄 Creating comprehensive action summary...")
        summary_prompt = f"""Based on these {len(detailed_analyses)} detailed clip analyses, create a comprehensive summary of the TARGET PLAYER's performance throughout the game.

TARGET PLAYER: White guy with grey t-shirt under orange bib

CLIP ANALYSES:
{chr(10).join([f"Clip {i+1} ({a['game_timestamp']}): {a['analysis']}" for i, a in enumerate(detailed_analyses)])}

TASK:
Create a comprehensive summary that includes:

1. **ALL GOALS** - List any goals scored by the target player with timestamps
2. **ALL SHOTS** - List any shots taken by the target player with timestamps
3. **ALL DRIBBLES** - List any dribbling actions with timestamps
4. **ALL TACKLES** - List any tackles made by the target player with timestamps
5. **ALL PASSES** - Summarize passing performance (successful/failed, types)
6. **POSITIONING** - Where the player spent most time on the pitch
7. **MOVEMENT PATTERNS** - How the player moved throughout the game
8. **KEY MOMENTS** - Most important actions or moments
9. **PERFORMANCE SUMMARY** - Overall assessment of the player's game

Format as:
**GOALS:** [list with timestamps]
**SHOTS:** [list with timestamps]
**DRIBBLES:** [list with timestamps]
**TACKLES:** [list with timestamps]
**PASSING:** [summary]
**POSITIONING:** [description]
**KEY MOMENTS:** [list]
**OVERALL PERFORMANCE:** [summary]"""

        try:
            summary_response = self.model.generate_content(summary_prompt)
            final_summary = summary_response.text
        except Exception as e:
            print(f"❌ Error creating summary: {e}")
            final_summary = "Error creating summary"
        
        # Save results
        output_dir = Path("../output") / game_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed analyses
        with open(output_dir / "detailed_player_analyses.json", 'w') as f:
            json.dump(detailed_analyses, f, indent=2)
        
        # Save final summary
        with open(output_dir / "detailed_player_summary.txt", 'w') as f:
            f.write(f"DETAILED PLAYER ANALYSIS SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Game: {game_id}\n")
            f.write(f"Clips analyzed: {len(detailed_analyses)}\n")
            f.write(f"Player found in: {player_found_count} clips\n")
            f.write(f"Analysis range: clips {start_clip} to {end_clip}\n")
            f.write("=" * 50 + "\n\n")
            f.write(final_summary)
        
        print("\n🎯 DETAILED PLAYER TRACKING COMPLETE!")
        print("=" * 50)
        print(f"✅ Analyzed {len(detailed_analyses)} clips")
        print(f"🎯 Player found in {player_found_count} clips")
        print(f"📁 Results saved to: {output_dir}")
        print(f"📄 Summary: {output_dir}/detailed_player_summary.txt")
        print(f"📊 Details: {output_dir}/detailed_player_analyses.json")
        
        # Print summary
        print("\n📋 DETAILED PLAYER SUMMARY:")
        print("=" * 30)
        print(final_summary)
        
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 4_detailed_tracker.py <game-id> [start-clip] [end-clip]")
        print("Example: python 4_detailed_tracker.py brixton5s-20240807")
        print("Example: python 4_detailed_tracker.py brixton5s-20240807 0 50")
        sys.exit(1)
    
    game_id = sys.argv[1]
    start_clip = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end_clip = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    try:
        tracker = DetailedPlayerTracker()
        success = tracker.track_player_throughout_game(game_id, start_clip, end_clip)
        
        if success:
            print(f"🎯 Ready for Step 5: Performance analysis")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 