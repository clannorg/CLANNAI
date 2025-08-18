#!/usr/bin/env python3
"""
4. Simple Clip Analyzer
One sentence per 15-second clip using Gemini 2.5 Pro
Clean, fast, minimal context usage
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
    """Load environment variables from multiple likely locations without overriding.

    Search order:
    1) Current shell environment (default load_dotenv with no path keeps env intact)
    2) ai/veo-games-v3/.env
    3) ai/.env
    4) repo-root/.env
    """
    # Keep anything already exported in the shell
    load_dotenv()  # override=False by default

    candidates = [
        Path(__file__).resolve().parent.parent / '.env',   # ai/veo-games-v3/.env
        Path(__file__).resolve().parents[2] / '.env',      # ai/.env
        Path(__file__).resolve().parents[3] / '.env',      # repo root .env
    ]
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            # Best-effort loading; ignore malformed files
            pass

load_env_multisource()

class SimpleClipAnalyzer:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for simple analysis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
    
    def load_team_config(self, match_id: str) -> dict:
        """Load team configuration for consistent naming"""
        config_path = Path(f"../outputs/{match_id}/match_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to generic names if config missing
            return {
                'team_a': {'name': 'Team A', 'jersey': 'first team colors'},
                'team_b': {'name': 'Team B', 'jersey': 'second team colors'}
            }

    def get_simple_analysis_prompt(self, team_a_name: str, team_a_colors: str, team_b_name: str, team_b_colors: str) -> str:
        """Generate analysis prompt with actual team names and colors"""
        return f"""Analyze this 15-second football clip. This is one segment from a 90-minute match.

Describe what is happening as accurately as possible. Your analysis will be combined with other clips to create a complete match timeline.

Team identification:
- {team_a_name} (wearing {team_a_colors})
- {team_b_name} (wearing {team_b_colors})

Focus on:
- Which team has possession
- Main actions: passing, defending, attacking, set pieces, throw-ins
- Only mention significant events if they clearly occur (actual shots on goal, saves, fouls, cards, goals)
- Use timing 00:00 to 00:15 only for clear events

Be precise and avoid speculation. Most clips will show routine play - that's normal.

Format: "[Team Name] [main action]. [Any clear events with timing if they occur]"

Example: "{team_a_name} maintains possession in midfield" or "{team_b_name} takes throw-in. Key events: 00:08 shot taken, 00:10 saved by keeper" """

    def analyze_single_clip(self, clip_path: Path) -> tuple:
        """Analyze a single clip and return timestamp + description"""
        try:
            # Extract timestamp from filename (e.g., clip_05m30s.mp4 -> 05:30)
            filename = clip_path.stem
            if 'clip_' in filename:
                time_part = filename.replace('clip_', '').replace('m', ':').replace('s', '')
                # Convert to mm:ss format
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
                return timestamp, "Analysis failed"

            # Load team config for this match
            match_id = clip_path.parent.parent.name  # Extract match_id from path
            team_config = self.load_team_config(match_id)
            
            # Generate analysis with actual team names
            response = self.model.generate_content([
                uploaded_file,
                self.get_simple_analysis_prompt(
                    team_config['team_a']['name'],
                    team_config['team_a']['jersey'],
                    team_config['team_b']['name'], 
                    team_config['team_b']['jersey']
                )
            ])
            
            # Clean up uploaded file
            genai.delete_file(uploaded_file.name)
            
            description = response.text.strip()
            print(f"✅ {timestamp}: {description}")
            
            return timestamp, description
            
        except Exception as e:
            print(f"❌ Error analyzing {clip_path.name}: {str(e)}")
            return timestamp, f"Error: {str(e)}"

    def analyze_all_clips(self, match_id: str) -> bool:
        """Analyze all clips in parallel and save to individual text files"""
        print(f"🎬 Simple Clip Analysis for {match_id}")
        
        data_dir = Path("../outputs") / match_id
        clips_dir = data_dir / "clips"  # Use original clips directly
        output_dir = data_dir / "4_clip_descriptions"
        
        if not clips_dir.exists():
            print(f"❌ Clips directory not found: {clips_dir}")
            return False
        
        # Create output directory
        output_dir.mkdir(exist_ok=True)
        
        # Get all clip files and sort by timestamp
        def extract_time_for_sorting(clip_path):
            """Extract timestamp for proper numerical sorting"""
            try:
                filename = clip_path.stem
                if 'clip_' in filename:
                    time_part = filename.replace('clip_', '').replace('m', ':').replace('s', '')
                    if ':' in time_part:
                        parts = time_part.split(':')
                        minutes = int(parts[0])
                        seconds = int(parts[1])
                        return minutes * 60 + seconds  # Convert to total seconds for sorting
                return 0
            except:
                return 0
        
        clip_files = sorted(clips_dir.glob("clip_*.mp4"), key=extract_time_for_sorting)
        
        if not clip_files:
            print(f"❌ No clips found in {clips_dir}")
            return False
        
        # Filter out clips that already have description files (to avoid API waste)
        unprocessed_clips = []
        for clip_path in clip_files:
            # Generate expected output filename
            clip_name = clip_path.stem  # e.g., "clip_05m30s"
            timestamp = clip_name.replace('clip_', '').replace('m', ':').replace('s', '')
            output_filename = f"clip_{timestamp.replace(':', 'm')}s.txt"
            output_path = output_dir / output_filename
            
            if not output_path.exists():
                unprocessed_clips.append(clip_path)
            else:
                print(f"⏭️  Skipping {clip_path.name} (already analyzed)")
        
        clip_files = unprocessed_clips
        
        if not clip_files:
            print(f"✅ All clips already analyzed!")
            return True
        
        # Process remaining clips in parallel
        print(f"⚽ RESUMING ANALYSIS: Processing {len(clip_files)} remaining clips")
        
        print(f"📊 Found {len(clip_files)} clips to analyze")
        print(f"🎯 Using parallel processing with Gemini 2.5 Pro (30 workers)")
        
        # Process clips in parallel
        successful_analyses = 0
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            # Submit all tasks
            future_to_clip = {
                executor.submit(self.analyze_single_clip, clip_path): clip_path 
                for clip_path in clip_files
            }
            
            # Process results as they complete
            for future in as_completed(future_to_clip):
                clip_path = future_to_clip[future]
                
                try:
                    timestamp, description = future.result()
                    
                    # Save to individual text file
                    output_filename = f"clip_{timestamp.replace(':', 'm')}s.txt"
                    output_path = output_dir / output_filename
                    
                    with open(output_path, 'w') as f:
                        f.write(description)
                    
                    successful_analyses += 1
                    
                except Exception as e:
                    print(f"❌ Failed to process {clip_path.name}: {str(e)}")
        
        print(f"✅ Analysis complete!")
        print(f"📊 Successfully analyzed: {successful_analyses}/{len(clip_files)} clips")
        print(f"📁 Output saved to: {output_dir}")
        
        return successful_analyses > 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4_simple_clip_analyzer.py <match-id>")
        print("Example: python 4_simple_clip_analyzer.py ballyclare-20250111")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        analyzer = SimpleClipAnalyzer()
        success = analyzer.analyze_all_clips(match_id)
        
        if success:
            print("🎉 Simple clip analysis completed successfully!")
        else:
            print("❌ Clip analysis failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()