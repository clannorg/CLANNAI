#!/usr/bin/env python3
"""
2. Simple Player Analyzer
Samples random clips and gets Gemini to describe all players in natural language
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

class SimplePlayerAnalyzer:
    def __init__(self):
        """Initialize the simple player analyzer with Gemini"""
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🤖 Simple player analyzer initialized with Gemini 2.0 Flash")

    def get_player_description_prompt(self, clip_path: str, clip_timestamp: str) -> str:
        """Create prompt for natural language player description"""
        return f"""You are analyzing a football video clip. 

CLIP INFO:
- Timestamp: {clip_timestamp}
- Duration: 15 seconds

TASK:
Describe ALL the players you can see in this clip. Focus on:

1. **Visual descriptions** - What they look like (clothes, colors, distinctive features)
2. **Team identification** - Which team they're on (by colors/bibs)
3. **Positions/roles** - What they seem to be doing (striker, midfielder, defender, etc.)
4. **Actions** - What they're doing in this clip
5. **Distinctive features** - Any unique characteristics (height, hair, equipment, etc.)

Write in natural, descriptive language. Be as detailed as possible about each player you can see.

Example format:
"Player 1: Wearing orange bib over dark kit, black hair, tall build. Appears to be a midfielder, making passes and moving around the center of the pitch."

"Player 2: Blue shirt, short dark hair, shorter stature. Playing as a striker, making runs toward goal and taking shots."

Analyze the video clip and describe all visible players."""

    def analyze_clip(self, clip_path: str, clip_timestamp: str) -> str:
        """Analyze a single clip for player descriptions"""
        print(f"🔍 Analyzing clip: {clip_timestamp}")
        
        try:
            # Create the prompt
            prompt = self.get_player_description_prompt(clip_path, clip_timestamp)
            
            # Generate response from Gemini
            response = self.model.generate_content([prompt, clip_path])
            
            print(f"✅ Got description for {clip_timestamp}")
            return response.text
                
        except Exception as e:
            print(f"❌ Error analyzing clip {clip_timestamp}: {e}")
            return f"Error analyzing clip {clip_timestamp}: {str(e)}"

    def sample_and_analyze(self, game_id: str, num_samples: int = 5) -> bool:
        """Sample random clips and analyze players"""
        print(f"🎯 Step 2: Simple Player Analysis for {game_id}")
        
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
        
        # Sample random clips
        if len(clips) < num_samples:
            num_samples = len(clips)
        
        sampled_clips = random.sample(clips, num_samples)
        print(f"🎲 Sampling {num_samples} random clips for analysis")
        
        # Analyze each sampled clip
        analyses = []
        for i, clip_info in enumerate(sampled_clips, 1):
            clip_filename = clip_info["filename"]
            clip_timestamp = clip_info["timestamp"]
            clip_path = clips_dir / clip_filename
            
            if not clip_path.exists():
                print(f"⚠️  Clip not found: {clip_filename}")
                continue
            
            print(f"🔄 Processing sample {i}/{num_samples}: {clip_filename}")
            
            # Analyze the clip
            analysis = self.analyze_clip(str(clip_path), clip_timestamp)
            analyses.append({
                "clip_filename": clip_filename,
                "clip_timestamp": clip_timestamp,
                "analysis": analysis
            })
            
            # Small delay to avoid rate limits
            time.sleep(1)
        
        # Create comprehensive summary
        print("🔄 Creating comprehensive player summary...")
        summary_prompt = f"""Based on these {len(analyses)} clip analyses, create a comprehensive summary of ALL players in this football game.

CLIP ANALYSES:
{chr(10).join([f"Clip {i+1} ({a['clip_timestamp']}): {a['analysis']}" for i, a in enumerate(analyses)])}

TASK:
Create a comprehensive summary that:
1. **Lists all unique players** identified across the clips
2. **Describes each player** with their visual characteristics, team, and role
3. **Mentions any patterns** you notice (formations, playing styles, etc.)
4. **Highlights distinctive players** (the ones that stand out)

Write in clear, natural language. Focus on the players you can consistently identify across multiple clips."""

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
        with open(output_dir / "clip_analyses.json", 'w') as f:
            json.dump(analyses, f, indent=2)
        
        # Save final summary
        with open(output_dir / "player_summary.txt", 'w') as f:
            f.write(f"PLAYER ANALYSIS SUMMARY\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Game: {game_id}\n")
            f.write(f"Clips analyzed: {len(analyses)}\n")
            f.write("=" * 50 + "\n\n")
            f.write(final_summary)
        
        print("\n🎯 SIMPLE PLAYER ANALYSIS COMPLETE!")
        print("=" * 50)
        print(f"✅ Analyzed {len(analyses)} sample clips")
        print(f"📁 Results saved to: {output_dir}")
        print(f"📄 Summary: {output_dir}/player_summary.txt")
        print(f"📊 Details: {output_dir}/clip_analyses.json")
        
        # Print summary
        print("\n📋 PLAYER SUMMARY:")
        print("=" * 30)
        print(final_summary)
        
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 2_simple_analyzer.py <game-id> [num-samples]")
        print("Example: python 2_simple_analyzer.py brixton5s-20240807 5")
        sys.exit(1)
    
    game_id = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    try:
        analyzer = SimplePlayerAnalyzer()
        success = analyzer.sample_and_analyze(game_id, num_samples)
        
        if success:
            print(f"🎯 Ready for Step 3: Individual player tracking")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 