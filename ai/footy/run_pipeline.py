#!/usr/bin/env python3
"""
Master Pipeline Script for Football Video Analysis
Orchestrates the entire workflow from video segmentation to event synthesis for all games.
"""

import subprocess
import logging
from pathlib import Path
import sys
import argparse
from datetime import datetime

# --- Configuration ---
# Define the base directory of the project
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# --- Logging Setup ---
LOGS_DIR = BASE_DIR / "pipeline_logs"
LOGS_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_path = LOGS_DIR / f"pipeline_run_{timestamp}.log"

# Configure logging to write to both a file and the console
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger() # Get the root logger
logger.setLevel(logging.INFO)

# File handler for writing to the log file
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Console handler for printing to the console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


# Define paths to the scripts that will be executed
SEGMENTATION_SCRIPT = BASE_DIR / "0_utils" / "video_segmentation.py"
ANALYZER_SCRIPT = BASE_DIR / "1_game_events" / "football_events_analyzer.py"
SYNTHESIS_SCRIPT = BASE_DIR / "1_game_events" / "football_events_synthesis.py"

# Use the same Python executable that is running this script
PYTHON_EXECUTABLE = sys.executable

def run_step(command: list):
    """Runs a command as a subprocess and handles errors."""
    command_str = " ".join(map(str, command))
    logger.info(f"🚀 Running command: {command_str}")
    try:
        result = subprocess.run(
            command,
            check=True,        # Raise an exception for non-zero exit codes
            capture_output=True, # Capture stdout and stderr
            text=True          # Decode stdout/stderr as text
        )
        logger.info(f"✅ Step successful.\n--- STDOUT ---\n{result.stdout}\n--------------")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Step failed with exit code {e.returncode}.")
        logger.error(f"--- STDERR ---\n{e.stderr}\n--------------")
        return False

def main():
    """Main pipeline orchestration function."""
    logger.info("====== ⚽ KICKING OFF FOOTBALL ANALYSIS PIPELINE ⚽ ======")

    parser = argparse.ArgumentParser(description="Master Football Analysis Pipeline")
    parser.add_argument("--game_name", help="Specify a single game to process (e.g., Game298_0601).")
    parser.add_argument("--force", action="store_true", help="Force re-analysis of events for the specified game(s).")
    args = parser.parse_args()

    if not DATA_DIR.exists():
        logger.error(f"Data directory not found at: {DATA_DIR}")
        return

    # Find all game directories in the data folder
    if args.game_name:
        game_folders = [DATA_DIR / args.game_name]
        if not game_folders[0].exists():
            logger.error(f"Specified game folder not found: {game_folders[0]}")
            return
    else:
        game_folders = [d for d in DATA_DIR.iterdir() if d.is_dir()]
    
    if not game_folders:
        logger.warning(f"No game folders found in {DATA_DIR}. Nothing to process.")
        return

    logger.info(f"Found {len(game_folders)} games to process: {[g.name for g in game_folders]}")
    
    total_games = len(game_folders)
    for i, game_dir in enumerate(game_folders, 1):
        game_name = game_dir.name
        run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"\n====== PROCESSING GAME {i}/{total_games}: {game_name} (RUN ID: {run_timestamp}) ======")

        # --- STEP 1: Video Segmentation ---
        logger.info(f"--- Step 1: Video Segmentation for {game_name} ---")
        segment_command = [PYTHON_EXECUTABLE, str(SEGMENTATION_SCRIPT), "--game_name", game_name]
        if not run_step(segment_command):
            logger.error(f"Skipping further processing for {game_name} due to segmentation failure.")
            continue

        # --- STEP 2: Event Analysis ---
        logger.info(f"\n--- Step 2: Event Analysis for {game_name} ---")
        analyze_command = [
            PYTHON_EXECUTABLE, str(ANALYZER_SCRIPT),
            "--game_name", game_name,
            "--run_timestamp", run_timestamp
        ]
        if args.force:
            analyze_command.append("--force")
        
        # We now allow this step to "fail" (i.e., return a non-zero exit code)
        # if only a few clips are unsuccessful. The analysis script itself will log the errors.
        # We will proceed to synthesis regardless, to get a report on the successful clips.
        run_step(analyze_command)

        # --- STEP 3: Event Synthesis ---
        logger.info(f"\n--- Step 3: Event Synthesis for {game_name} ---")
        synthesis_command = [
            PYTHON_EXECUTABLE, str(SYNTHESIS_SCRIPT),
            "--game_name", game_name,
            "--run_timestamp", run_timestamp
        ]
        run_step(synthesis_command)

        logger.info(f"====== ✅ FINISHED PROCESSING GAME: {game_name} ======")

    logger.info("\n====== 🎉 PIPELINE COMPLETE 🎉 ======")

if __name__ == "__main__":
    main() 