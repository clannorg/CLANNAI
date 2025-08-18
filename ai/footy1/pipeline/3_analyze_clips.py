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
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def get_analysis_prompt(self, team_a_name: str, team_a_colors: str, team_b_name: str, team_b_colors: str) -> str:
        """Generate analysis prompt focused on 5-a-side goals and cool moments"""
        return f"""Analyze this 15-second clip from a 5-a-side football game.

**FOCUS ON: Goals and particularly cool moments**

Team identification:
- {team_a_name} (wearing {team_a_colors})
- {team_b_name} (wearing {team_b_colors})

Describe what happens in this clip, focusing on:

🥅 **GOALS**: Any goals scored - describe how it happened
⚡ **COOL MOMENTS**: Skills, nutmegs, great saves, near-misses, tackles
🏃 **KEY ACTIONS**: Who has the ball, attacking moves, defensive plays
⏰ **TIMING**: When in the clip things happen (e.g., "at 0:08")

**5-a-side context**: Fast-paced, smaller pitch, fewer players, more individual skill

Keep it concise but capture the excitement. If nothing interesting happens, just say "Routine play - [brief description]".

Format: One paragraph describing the action."""
    
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
                team_config['team_a']['name'],
                team_config['team_a']['colors'],
                team_config['team_b']['name'],
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
    
    # Load clips manifest
    manifest_file = outputs_dir / 'clips_manifest.json'
    if not manifest_file.exists():
        print(f"❌ Error: Clips manifest not found: {manifest_file}")
        sys.exit(1)
    
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    
    print(f"🎬 Analyzing clips for: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print(f"📊 Clips to analyze: {len(manifest['clips'])}")
    print("🎯 Focus: Goals and cool moments")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = ClipAnalyzer()
    
    # Analyze clips
    successful_analyses = []
    failed_analyses = []
    
    def analyze_single_clip(clip_filename):
        clip_path = clips_dir / clip_filename
        if not clip_path.exists():
            return clip_filename, f"Error: Clip file not found: {clip_path}"
        
        description = analyzer.analyze_clip(clip_path, team_config)
        
        # Save description
        description_filename = clip_filename.replace('.mp4', '.txt')
        description_path = descriptions_dir / description_filename
        
        with open(description_path, 'w') as f:
            f.write(description)
        
        return clip_filename, description
    
    # Process clips in parallel (but limit concurrency for API limits)
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_clip = {
            executor.submit(analyze_single_clip, clip): clip 
            for clip in manifest['clips']
        }
        
        for i, future in enumerate(as_completed(future_to_clip)):
            clip_filename = future_to_clip[future]
            try:
                clip_name, description = future.result()
                if description.startswith("Error:"):
                    failed_analyses.append(clip_name)
                    print(f"❌ [{i+1}/{len(manifest['clips'])}] Failed: {clip_name}")
                else:
                    successful_analyses.append(clip_name)
                    print(f"✅ [{i+1}/{len(manifest['clips'])}] {clip_name}")
                    # Show preview of interesting clips
                    if any(keyword in description.lower() for keyword in ['goal', 'cool', 'skill', 'save', 'shot']):
                        preview = description[:100] + "..." if len(description) > 100 else description
                        print(f"   🎯 {preview}")
            except Exception as e:
                failed_analyses.append(clip_filename)
                print(f"❌ [{i+1}/{len(manifest['clips'])}] Error: {clip_filename} - {e}")
    
    # Update manifest with analysis results
    manifest['analyzed_clips'] = len(successful_analyses)
    manifest['failed_analyses'] = len(failed_analyses)
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Clip analysis complete!")
    print(f"📊 Success: {len(successful_analyses)}/{len(manifest['clips'])} clips")
    if failed_analyses:
        print(f"❌ Failed: {len(failed_analyses)} clips")
    print(f"📁 Descriptions saved to: {descriptions_dir}")
    print(f"\n🎯 Ready for step 4: python 4_synthesize_highlights.py {match_id}")

if __name__ == "__main__":
    main()