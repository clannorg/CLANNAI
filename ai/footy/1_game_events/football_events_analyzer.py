#!/usr/bin/env python3
"""
Football Events Analyzer
Analyzes football video clips for events using Gemini AI
"""

import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import sys
from datetime import datetime
import argparse
import asyncio

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "0_utils"))
from config import get_api_key, CAMERA_SETUPS, INTRO_TEXTS

# Import Gemini
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballEventsAnalyzer:
    """
    Analyzes football video clips for events using Gemini AI
    Detects: goals, shots, passes, tackles, fouls, cards, set pieces
    """
    
    def __init__(self, game_name: str):
        """Initialize the analyzer with API configuration"""
        self.api_key = get_api_key()
        genai.configure(api_key=self.api_key)
        
        self.game_name = game_name

        # Initialize Gemini model
        self.model_name = 'gemini-2.0-flash' 
        self.model = genai.GenerativeModel(self.model_name)
        
        # Output directory will be set by the main function
        self.output_dir = None
        self.prompts_dir = None
        
        # API call metadata tracking
        self.api_call_metadata = []
        
        # Simple statistics tracking
        self.stats = {
            "clips_processed": 0,
            "errors": 0
        }
    
    async def encode_video_base64(self, video_path: str) -> bytes:
        """Convert video to base64 for Gemini API"""
        try:
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-i', str(video_path),
                '-vf', 'scale=640:480',
                '-r', '2',
                '-f', 'image2pipe', '-pix_fmt', 'yuv420p',
                '-vcodec', 'libx264', '-preset', 'ultrafast',
                '-t', '15',
                '-y', '-',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, "ffmpeg", stderr=stderr)
            return stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error encoding video: {e.stderr.decode()}")
            return None
    
    def get_events_prompt(self, clip_identifier: str) -> str:
        """Generate prompt for football event analysis"""
        duration = 15

        # Dynamically set the camera setup based on the game name
        default_camera_setup = """- This is a single camera setup where the camera is positioned on the sideline of the field. 
        - The camera is observing a 5 vs 5 football game played on a sub region of a full size football field.
        - The camera pans left to view the LEFT GOAL and pans right to view the RIGHT GOAL."""
        default_intro_template = "You are analyzing a {duration}-second football video clip. "
        
        intro_template = INTRO_TEXTS.get(self.game_name, default_intro_template)
        introductory_text = intro_template.format(duration=duration)
        camera_setup_text = CAMERA_SETUPS.get(self.game_name, default_camera_setup)

        # This is the user's original, unmodified prompt for a single clip.
        return f"""{introductory_text}

        CAMERA SETUP:
        {camera_setup_text}

        AUDIO:
        - Utilise the clip's audio to improve event identification.
        - The language of the clip will typically be in english or hindi.
        - Use crowd reactions (cheers etc) to fine-tune key moments like goals, shots or saves.
        - Use the referee's whistle (if present) to identify match decisions likegoals, corner kicks, penalties, etc. 

        ACTIVE PLAYERS: People actively participating in competitive gameplay
        - Engaged in the actual football game with other players
        - Part of competitive action and game flow
        - Playing with/against other active participants
        - Defensive pressure or competitive conditions present

        REFEREE: The referee is the person in charge of the game.
        - The referee wears a unique colour compared to other players. Typical colours include fluorescent yellow or black.
        - The referee is the person in charge of the game and uses a whistle and hand actions to signal decisions.

        BYSTANDERS: People present but not actively participating in the game
        - Walking around the pitch during active gameplay
        - Taking casual shots while others are competing elsewhere
        - Present but not engaged in the actual competitive game
        - Just shooting for fun while the real game happens
        - Not part of the competitive action
        - Players and other games happenign in the background of this clip should be ignored. 

        TASK:
        Analyze the clip and describe, in plain text, critical football events you see. Your response must follow the ANALYSIS FORMAT below. Include:
        - The exact time in the clip (in seconds) for each event
        - Who was involved (active player or bystander, with description)
        - What happened (shot, save, block, tackle, turnover, foul, etc.)
        - The outcome (made/missed, etc.)
        - Which goal the event occurred at (LEFT GOAL or RIGHT GOAL)
        - If referee is present, include the referee's actions in the event description.
        - Do not include any text not requested by ANALYSIS FORMAT.

        **CRITICAL FOOTBALL EVENT TYPES:**
        - GOALS (with team and player if visible)
        - GOALKICK
        - GOALKEEPER SAVES 
        - TURNOVERS (possession changes, interceptions, clear possession switches)
        - SHOTS ON TARGET (saved/blocked/missed)
        - PENALTIES awarded or taken
        - RED/YELLOW CARDS shown
        - MAJOR FOULS (that result in free kicks/penalties)
        - CORNER KICKS awarded
        - SUBSTITUTIONS
        - BLOCKS 
        - SKILLS football skills like stepovers, rabonas, bicycle kicks, etc. or long solo dribbles through several (3 or more) players.

        **ALWAYS IGNORE:**
        - Routine passes
        - Basic dribbling
        - Minor movements
        - Unclear/uncertain events

        **ANALYSIS FORMAT:** 
        ```
        FOOTBALL EVENTS ANALYSIS - CLIP_{clip_identifier}
        ==================================================

        [Seconds]s: [EVENT TYPE] - [EVENT DESCRIPTION]
        [Seconds]s: [EVENT TYPE] - [EVENT DESCRIPTION]
        ...
        **AUDIO DESCRIPTION:**
        - [Seconds]s: [AUDIO DESCRIPTION]

        **KEY MOMENTS:**
        - [Summary of major events]

        **MATCH FLOW:**
        - [Brief tactical overview]
        ```

        **TIMESTAMP FORMAT:**
        - Use format: "27s:" (not "00:27s:" or "27.5s:")
        - Just the number of seconds from clip start
        - Example: "15s: Goal scored by team A - GOAL"

        **IMPORTANT:**
        - Only report events you are confident about
        - If unsure about a foul/card/penalty, don't call it
        - Focus on clear, significant moments
        - Be conservative - quality over quantity
        - If there are no events, state that explicitly.

        Analyze this {duration}-second football clip and identify ONLY the major football events that occurred.
        """
    
    async def analyze_clip(self, clip_path: str, clip_identifier: str, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Analyze a single football clip for events, managed by a semaphore."""
        async with semaphore:
            try:
                logger.info(f"🚀 Starting analysis for clip {clip_identifier}...")
                
                prompt = self.get_events_prompt(clip_identifier)
                generation_config = {
                    "temperature": 0.2,
                    "top_k": 30,
                    "max_output_tokens": 1024,
                }
                video_data = await self.encode_video_base64(clip_path)
                if not video_data:
                    raise Exception("Failed to encode video")
                
                start_time = time.time()
                response = await self.model.generate_content_async(
                    [prompt, {"mime_type": "video/mp4", "data": video_data}],
                    generation_config=generation_config
                )
                duration = time.time() - start_time
                
                if response.usage_metadata:
                    metadata = {
                        "clip_identifier": clip_identifier, "model_name": self.model_name,
                        "prompt_token_count": response.usage_metadata.prompt_token_count,
                        "candidates_token_count": response.usage_metadata.candidates_token_count,
                        "total_token_count": response.usage_metadata.total_token_count,
                        "api_call_duration_seconds": duration
                    }
                    self.api_call_metadata.append(metadata)

                analysis_text = response.text
                
                output_filename = f"events_analysis_{clip_identifier}.txt"
                output_path = self.output_dir / output_filename
                
                with open(output_path, 'w') as f:
                    f.write(analysis_text)
                
                logger.info(f"✅ Clip {clip_identifier} analyzed successfully in {duration:.2f}s")
                
                return {"success": True, "clip_identifier": clip_identifier, "analysis": analysis_text, "output_path": str(output_path), "duration": duration}
                
            except Exception as e:
                logger.error(f"❌ Error analyzing clip {clip_identifier}: {e}")
                self.stats["errors"] += 1
                if "429" in str(e):
                    return {"success": False, "clip_identifier": clip_identifier, "error": "QUOTA_EXCEEDED"}
                return {"success": False, "clip_identifier": clip_identifier, "error": str(e)}
    
    async def analyze_all_clips(self, clips_dir: str) -> List[Dict[str, Any]]:
        """Analyze all football clips in directory"""
        clips_path = Path(clips_dir)
        
        if not clips_path.exists():
            logger.error(f"Clips directory not found: {clips_dir}")
            return []
        
        def sort_key(path):
            # Expected filename format: clip_STARTmSECs_to_ENDmSECs.mp4
            try:
                time_part = path.stem.split('_')[1] # e.g., "0m00s"
                time_str = time_part.replace("m", ":").replace("s", "")
                minutes, seconds = map(int, time_str.split(":"))
                return minutes * 60 + seconds
            except (IndexError, ValueError):
                logger.warning(f"Could not parse start time from {path.name}, using default sorting.")
                return 0

        clip_files = sorted([f for f in clips_path.glob("*.mp4") if f.name.startswith("clip_")], key=sort_key)
        
        if not clip_files:
            logger.error(f"No football clips found in: {clips_dir}")
            return []
        
        logger.info(f"Found {len(clip_files)} total clips.")

        # Filter out clips that have already been analyzed
        unprocessed_clips = []
        for clip_path in clip_files:
            clip_identifier = clip_path.stem.replace("clip_", "")
            output_filename = f"events_analysis_{clip_identifier}.txt"
            output_path = self.output_dir / output_filename
            if not output_path.exists():
                unprocessed_clips.append(clip_path)

        # If --force is used, ignore existing files and re-process all
        if self.force_reanalysis:
            logger.warning("🚨 --force flag detected. Re-analyzing all clips.")
            unprocessed_clips = clip_files

        skipped_count = len(clip_files) - len(unprocessed_clips)
        if skipped_count > 0 and not self.force_reanalysis:
            logger.info(f"⏭️  Skipping {skipped_count} clips that have already been analyzed.")

        if not unprocessed_clips:
            logger.info("✅ All clips have been analyzed. Nothing to do.")
            return []

        # Save the prompt template for this run
        if self.prompts_dir:
            # Use the first clip to generate a representative prompt
            first_clip_identifier = unprocessed_clips[0].stem.replace("clip_", "")
            prompt_content = self.get_events_prompt(first_clip_identifier)
            prompt_path = self.prompts_dir / "prompt_template.txt"
            with open(prompt_path, 'w') as f:
                f.write(prompt_content)
            logger.info(f"📝 Prompt template for this run saved to: {prompt_path}")

        logger.info(f"▶️  Processing {len(unprocessed_clips)} new clips with up to 4 concurrent tasks...")
        
        semaphore = asyncio.Semaphore(4)
        tasks = []
        for clip_path in unprocessed_clips:
            try:
                # Use the filename stem (e.g., "clip_0m00s_to_0m15s") as the identifier
                clip_identifier = clip_path.stem.replace("clip_", "")
                tasks.append(self.analyze_clip(str(clip_path), clip_identifier, semaphore))
            except Exception as e:
                logger.error(f"Error creating task for {clip_path.name}: {e}")

        results = await asyncio.gather(*tasks)

        # Check for quota errors after all tasks are complete
        if any(r.get("error") == "QUOTA_EXCEEDED" for r in results):
             logger.error("🛑 Daily quota exceeded during processing. Some clips may have failed.")
            
        self.save_api_call_metadata()
        return [r for r in results if r is not None] # Filter out potential None results from errors
    
    def save_api_call_metadata(self):
        """Saves the collected API call metadata to a JSON file."""
        if not self.api_call_metadata:
            logger.info("No API call metadata to save.")
            return

        runs_dir = Path.cwd() / "gemini_runs"
        runs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"events_analyzer_run_{timestamp}.json"
        filepath = runs_dir / filename

        try:
            with open(filepath, 'w') as f:
                json.dump(self.api_call_metadata, f, indent=2)
            logger.info(f"💾 API call metadata saved to: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save API call metadata: {e}")

def main():
    """Main function for football events analysis"""
    parser = argparse.ArgumentParser(description="Analyze football video clips for a specific game.")
    parser.add_argument("--game_name", required=True, help="The name of the game to analyze (e.g., Game298_0601).")
    parser.add_argument("--run_timestamp", required=True, help="The timestamp for this pipeline run.")
    parser.add_argument("--force", action="store_true", help="Force re-analysis of all clips, even if output files exist.")
    args = parser.parse_args()

    analyzer = FootballEventsAnalyzer(game_name=args.game_name)
    analyzer.force_reanalysis = args.force
    
    # Update paths to be game-specific and include the run timestamp
    base_data_dir = Path.cwd() / "data"
    clips_dir = base_data_dir / args.game_name / "clips"
    analyzer.output_dir = Path.cwd() / "1_game_events" / "output" / args.game_name / args.run_timestamp
    analyzer.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create and set prompts directory
    analyzer.prompts_dir = Path.cwd() / "prompts" / args.game_name / args.run_timestamp
    analyzer.prompts_dir.mkdir(parents=True, exist_ok=True)

    print("⚽ Football Events Analysis (Single-Clip Mode)")
    print("=" * 30)
    print(f"Analyzing clips from: {clips_dir}")
    print(f"Output directory: {analyzer.output_dir}")
    print(f"Prompts directory: {analyzer.prompts_dir}")
    print()
    
    results = asyncio.run(analyzer.analyze_all_clips(str(clips_dir)))
    
    if results:
        successful_count = len([r for r in results if r and r.get("success")])
        total_count = len(results)
        print(f"\n✅ Analysis complete: {successful_count}/{total_count} clips successful")
        print(f"📁 Results saved in: {analyzer.output_dir}")

        # If any clips failed, the script should exit with an error code.
        if successful_count < total_count:
            logger.error(f"❌ Analysis failed for {total_count - successful_count} clip(s). See logs above for details.")
            sys.exit(1)
            
    else:
        # This case now specifically handles when no *new* clips were processed.
        print("\n✅ All clips have already been analyzed. No new analysis was needed.")

if __name__ == "__main__":
    main() 