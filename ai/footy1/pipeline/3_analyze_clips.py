#!/usr/bin/env python3
"""
3. Analyze Clips
Analyze each 15-second clip focusing on goals and cool moments for 5-a-side
"""

import sys
import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from dotenv import load_dotenv

def load_env_multisource() -> None:
    """Load environment variables from multiple likely locations"""
    load_dotenv()  # Keep shell environment
    
    candidates = [
        Path(__file__).resolve().parent.parent / '.env',   # ai/footy1/.env
        Path(__file__).resolve().parents[2] / '.env',      # ai/.env
        Path(__file__).resolve().parents[3] / '.env',      # repo root .env
    ]
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            pass

load_env_multisource()

class ClipAnalyzer:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for clip analysis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
    
    def get_analysis_prompt(self, team_a_colors: str, team_b_colors: str) -> str:
        """Generate analysis prompt focused on event detection for 5-a-side games"""
        return f"""Analyze this 15-second clip from a 5-a-side football game for notable events.

Team identification:
- Team A: {team_a_colors}
- Team B: {team_b_colors}

**TASK**: Detect if there's a notable event worth highlighting. If yes, provide ONE sentence with:
1. Exact timestamp (MM:SS format)
2. What happened
3. Who was involved (by team colors only)

**Notable events include:**
- Goals or shots on target
- Great saves by keeper
- Skills (nutmegs, turns, dribbles)
- Near misses or post hits
- Fouls or cards
- Key tackles or interceptions

**Format:**
- If notable event: "[MM:SS] [Team color] [player action] - [brief why it's notable]"
- If routine play: "No notable events - routine possession play"

**Examples:**
- "03:42 Orange bibs player scores from close range - clinical finish"
- "08:15 Non-bibs keeper makes diving save - excellent reflexes"
- "No notable events - routine possession play" """
    
    def analyze_clip(self, clip_path: Path, team_config: dict) -> str:
        """Analyze a single clip"""
        try:
            # Upload clip to Gemini
            video_file = genai.upload_file(path=str(clip_path))
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(1)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                return "Error: Video processing failed"
            
            # Get analysis prompt
            prompt = self.get_analysis_prompt(
                team_config['team_a']['colors'],
                team_config['team_b']['colors']
            )
            
            # Analyze clip
            response = self.model.generate_content([video_file, prompt])
            
            # Clean up uploaded file
            genai.delete_file(video_file.name)
            
            return response.text.strip()
            
        except Exception as e:
            return f"Error analyzing clip: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python 3_analyze_clips.py <match-id>")
        print("Example: python 3_analyze_clips.py sunday-league-game-1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    clips_dir = outputs_dir / 'clips'
    descriptions_dir = outputs_dir / 'clip_descriptions'
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        print("Run step 1 first: python 1_setup_teams.py <match-id>")
        sys.exit(1)
    
    if not clips_dir.exists():
        print(f"❌ Error: Clips directory not found: {clips_dir}")
        print("Run step 2 first: python 2_make_clips.py <video-path> <match-id>")
        sys.exit(1)
    
    descriptions_dir.mkdir(exist_ok=True)
    
    # Load team configuration
    team_config_file = outputs_dir / 'team_config.json'
    if not team_config_file.exists():
        print(f"❌ Error: Team configuration not found: {team_config_file}")
        sys.exit(1)
    
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    # Get all clip files
    clip_files = sorted(clips_dir.glob("clip_*.mp4"))
    if not clip_files:
        print(f"❌ No clips found in {clips_dir}")
        sys.exit(1)
    
    print(f"🎬 Analyzing clips for: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print(f"📊 Clips to analyze: {len(clip_files)}")
    print("🎯 Focus: Goals and cool moments (factual analysis)")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = ClipAnalyzer()
    
    # Analyze clips
    successful_analyses = []
    failed_analyses = []
    
    def analyze_single_clip(clip_path):
        if not clip_path.exists():
            return clip_path.name, f"Error: Clip file not found: {clip_path}"
        
        # Check if already analyzed
        description_filename = clip_path.name.replace('.mp4', '.txt')
        description_path = descriptions_dir / description_filename
        
        if description_path.exists():
            print(f"⏭️  Skipping {clip_path.name} (already analyzed)")
            return clip_path.name, "Already analyzed"
        
        description = analyzer.analyze_clip(clip_path, team_config)
        
        # Save description
        with open(description_path, 'w') as f:
            f.write(description)
        
        return clip_path.name, description
    
    # Process clips in parallel (but limit concurrency for API limits)
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_clip = {
            executor.submit(analyze_single_clip, clip_path): clip_path 
            for clip_path in clip_files
        }
        
        for i, future in enumerate(as_completed(future_to_clip)):
            clip_path = future_to_clip[future]
            try:
                clip_name, description = future.result()
                if description.startswith("Error:") or description == "Already analyzed":
                    if description != "Already analyzed":
                        failed_analyses.append(clip_name)
                        print(f"❌ [{i+1}/{len(clip_files)}] Failed: {clip_name}")
                else:
                    successful_analyses.append(clip_name)
                    print(f"✅ [{i+1}/{len(clip_files)}] {clip_name}")
                    # Show preview of interesting clips
                    if any(keyword in description.lower() for keyword in ['goal', 'skill', 'save', 'shot', 'nutmeg']):
                        preview = description[:100] + "..." if len(description) > 100 else description
                        print(f"   🎯 HIGHLIGHT: {preview}")
            except Exception as e:
                failed_analyses.append(clip_path.name)
                print(f"❌ [{i+1}/{len(clip_files)}] Error: {clip_path.name} - {e}")
    
    print(f"\n✅ Clip analysis complete!")
    print(f"📊 Success: {len(successful_analyses)}/{len(clip_files)} clips")
    if failed_analyses:
        print(f"❌ Failed: {len(failed_analyses)} clips")
    print(f"📁 Descriptions saved to: {descriptions_dir}")
    print(f"\n🎯 Ready for step 4: python 4_synthesize_highlights.py {match_id}")

if __name__ == "__main__":
    main()