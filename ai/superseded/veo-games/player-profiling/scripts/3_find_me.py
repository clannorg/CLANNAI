#!/usr/bin/env python3
"""
3. Find Me - Track specific player
Find and track the white guy with grey t-shirt under orange bib
"""

import sys
import os
import json
import random
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

class PlayerTracker:
    def __init__(self):
        """Initialize the player tracker with Gemini"""
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🤖 Player tracker initialized with Gemini 2.0 Flash")

    def get_specific_player_prompt(self, clip_path: str, clip_timestamp: str) -> str:
        """Create prompt to find specific player"""
        return f"""You are looking for a SPECIFIC player in this football clip.

TARGET PLAYER:
- **White guy with grey t-shirt** under orange bib
- This is the player we want to track
- Look for: white skin, grey t-shirt visible under orange bib

CLIP INFO:
- Timestamp: {clip_timestamp}
- Duration: 15 seconds

TASK:
1. **Find the white guy with grey t-shirt** under orange bib
2. **Describe what he's doing** in this clip
3. **Note his position** on the pitch
4. **Describe his actions** (passing, running, shooting, etc.)
5. **Note any distinctive movements** or behaviors

If you can't see the target player (white guy with grey t-shirt under orange bib), say "Target player not visible in this clip."

If you DO see him, describe:
- What he's doing
- Where he is on the pitch
- His actions and movements
- Any notable moments

Be specific and detailed about the target player's actions."""

    def analyze_clip_for_target(self, clip_path: str, clip_timestamp: str) -> str:
        """Analyze a single clip for the target player"""
        print(f"🔍 Looking for target player in clip: {clip_timestamp}")
        
        try:
            # Create the prompt
            prompt = self.get_specific_player_prompt(clip_path, clip_timestamp)
            
            # Generate response from Gemini
            response = self.model.generate_content([prompt, clip_path])
            
            print(f"✅ Analyzed clip: {clip_timestamp}")
            return response.text
                
        except Exception as e:
            print(f"❌ Error analyzing clip {clip_timestamp}: {e}")
            return f"Error analyzing clip {clip_timestamp}: {str(e)}"

    def find_target_player(self, game_id: str, num_samples: int = 10) -> bool:
        """Find and track the target player across clips"""
        print(f"🎯 Step 3: Finding Target Player in {game_id}")
        
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
        
        # Sample more clips to increase chances of finding target player
        if len(clips) < num_samples:
            num_samples = len(clips)
        
        sampled_clips = random.sample(clips, num_samples)
        print(f"🎲 Sampling {num_samples} clips to find target player")
        
        # Analyze each sampled clip
        analyses = []
        target_found_count = 0
        
        for i, clip_info in enumerate(sampled_clips, 1):
            clip_filename = clip_info["filename"]
            clip_timestamp = clip_info["timestamp"]
            clip_path = clips_dir / clip_filename
            
            if not clip_path.exists():
                print(f"⚠️  Clip not found: {clip_filename}")
                continue
            
            print(f"🔄 Processing sample {i}/{num_samples}: {clip_filename}")
            
            # Analyze the clip
            analysis = self.analyze_clip_for_target(str(clip_path), clip_timestamp)
            
            # Check if target player was found
            if "not visible" not in analysis.lower() and "target player" in analysis.lower():
                target_found_count += 1
                print(f"🎯 TARGET PLAYER FOUND in {clip_timestamp}!")
            
            analyses.append({
                "clip_filename": clip_filename,
                "clip_timestamp": clip_timestamp,
                "analysis": analysis,
                "target_found": "not visible" not in analysis.lower() and "target player" in analysis.lower()
            })
            
            # Small delay to avoid rate limits
            time.sleep(1)
        
        # Create summary of target player findings
        print("🔄 Creating target player summary...")
        summary_prompt = f"""Based on these {len(analyses)} clip analyses, create a summary of the TARGET PLAYER (white guy with grey t-shirt under orange bib).

CLIP ANALYSES:
{chr(10).join([f"Clip {i+1} ({a['clip_timestamp']}): {a['analysis']}" for i, a in enumerate(analyses)])}

TASK:
Create a summary that:
1. **Lists all clips where target player was found**
2. **Describes what he was doing** in each clip
3. **Tracks his movements** and positions across clips
4. **Identifies patterns** in his playing style
5. **Notes any distinctive actions** or behaviors

Focus ONLY on the target player (white guy with grey t-shirt under orange bib). If he wasn't found in many clips, note that and suggest sampling more clips."""

        try:
            summary_response = self.model.generate_content(summary_prompt)
            final_summary = summary_response.text
        except Exception as e:
            print(f"❌ Error creating summary: {e}")
            final_summary = "Error creating summary"
        
        # Save results
        output_dir = Path("../output") / game_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual analyses
        with open(output_dir / "target_player_analyses.json", 'w') as f:
            json.dump(analyses, f, indent=2)
        
        # Save final summary
        with open(output_dir / "target_player_summary.txt", 'w') as f:
            f.write(f"TARGET PLAYER ANALYSIS SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Game: {game_id}\n")
            f.write(f"Clips analyzed: {len(analyses)}\n")
            f.write(f"Target player found in: {target_found_count} clips\n")
            f.write("=" * 50 + "\n\n")
            f.write(final_summary)
        
        print("\n🎯 TARGET PLAYER ANALYSIS COMPLETE!")
        print("=" * 50)
        print(f"✅ Analyzed {len(analyses)} sample clips")
        print(f"🎯 Target player found in {target_found_count} clips")
        print(f"📁 Results saved to: {output_dir}")
        print(f"📄 Summary: {output_dir}/target_player_summary.txt")
        
        # Print summary
        print("\n📋 TARGET PLAYER SUMMARY:")
        print("=" * 30)
        print(final_summary)
        
        if target_found_count == 0:
            print("\n⚠️  Target player not found in any clips!")
            print("💡 Try sampling more clips or different time periods")
        
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 3_find_me.py <game-id> [num-samples]")
        print("Example: python 3_find_me.py brixton5s-20240807 15")
        sys.exit(1)
    
    game_id = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    try:
        tracker = PlayerTracker()
        success = tracker.find_target_player(game_id, num_samples)
        
        if success:
            print(f"🎯 Ready for Step 4: Individual performance analysis")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 