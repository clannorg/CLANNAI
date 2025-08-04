#!/usr/bin/env python3
"""
Football Analysis Configuration
Settings and paths for football video analysis
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Base directories
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"


# Video processing settings
VIDEO_SETTINGS = {
    "clip_duration": 30,  # 30 seconds (vs 15 for basketball)
    "target_fps": 2,  # 2 FPS for API optimization
    "target_resolution": (1280, 720),  # 720p for better field visibility
    "codec": "libx264",
    "preset": "ultrafast",
    "crf": 28,  # Slightly higher compression for longer clips
    "api_optimized_resolution": (640, 480),
    "api_optimized_fps": 2,
    "api_optimized_crf": 30
}

# Football-specific settings
FOOTBALL_SETTINGS = {
    "events": [
        "goal", "shot", "pass", "tackle", "foul", "card", 
        "corner", "free_kick", "penalty", "offside", "substitution"
    ],
    "positions": ["GK", "DEF", "MID", "FWD"],
    "formations": ["4-3-3", "4-4-2", "3-5-2", "4-2-3-1", "3-4-3", "5-3-2"],
    "card_types": ["yellow", "red", "second_yellow"]
}

# API settings
API_SETTINGS = {
    "model": "gemini-2.0-flash",  # changed from gemini-2.0-flash-exp
    "tactical_model": "gemini-2.5-flash-exp",  # Better for tactical analysis
    "max_tokens": 1024,
    "temperature": 0.1,
    "top_p": 0.8,
    "rate_limit_delay": 1.0  # Seconds between API calls
}

# --- Pricing Definitions ---
# Pulled from ai.google.dev/gemini-api/docs/pricing
# This structure allows multiple model name keys to reference the same pricing object.

GEMINI_2_0_FLASH_PRICING = {
    "input_cost_per_1k_tokens": 0.00010,  # $0.10 per 1M tokens (video)
    "output_cost_per_1k_tokens": 0.00040  # $0.40 per 1M tokens
}

GEMINI_2_5_FLASH_PRICING = {
    # NOTE: This uses the rate for video input. Audio input has a different rate.
    "input_cost_per_1k_tokens": 0.00030, # $0.30 per 1M tokens
    "output_cost_per_1k_tokens": 0.00250 # $2.50 per 1M tokens
}

GEMINI_2_5_FLASH_LITE_PRICING = {
    "input_cost_per_1k_tokens": 0.00010, # $0.10 per 1M tokens
    "output_cost_per_1k_tokens": 0.00040 # $0.40 per 1M tokens
}

# Cost tracking
COST_SETTINGS = {
    "models": {
        # --- Gemini 2.0 Flash ---
        "gemini-2.0-flash-exp": GEMINI_2_0_FLASH_PRICING,
        "gemini-2.0-flash": GEMINI_2_0_FLASH_PRICING,

        # --- Gemini 2.5 Flash ---
        "gemini-2.5-flash-exp": GEMINI_2_5_FLASH_PRICING,
        "gemini-2.5-flash": GEMINI_2_5_FLASH_PRICING,

        # --- Gemini 2.5 Flash Lite ---
        "gemini-2.5-flash-lite-preview": GEMINI_2_5_FLASH_LITE_PRICING,
    },
    "cost_per_clip": 0.001,  # Kept for legacy, but will be replaced by token-based calculation
    "estimated_clips_per_match": 150
}

# File paths
PATHS = {
    "input_dir": INPUT_DIR,
    "output_dir": OUTPUT_DIR,
    "processed_clips": BASE_DIR / "Game298_0601" / "clips",
    "events_output": BASE_DIR / "1_game_events" / "output",
    "player_output": BASE_DIR / "2_player_profiling" / "output",
    "tactical_output": BASE_DIR / "3_tactical_analysis" / "output",
    "cost_output": BASE_DIR / "4_cost_analysis" / "output",
    "reports_dir": BASE_DIR / "reports"
}

# Sample video URLs
SAMPLE_VIDEOS = {
    "veo_url": "https://app.veo.co/matches/20250518-boys-academy-u16-vs-north-west-london-jets-1358e452/?highlight=c057a484-5e30-46cf-b295-00cc632a8e36&scroll=MT",
    "direct_url": "https://c.veocdn.com/c9543847-6cfa-45ad-bc85-60a6cafb7a5d/standard/machine/7775a871/video.mp4"
}
INTRO_TEXTS={
    "Game298_0601": "You are analyzing a {duration}-second football video clip. ",
    "Game269_0511": "You are analyzing a {duration}-second football video clip. ",
    "Game277_0526": "You are analyzing a {duration}-second football video clip. ",
    "Game297_0616": "You are analyzing two synchronised {duration}-second football video clips. ",
    "Game304_0618": "You are analyzing two synchronised {duration}-second football video clips. ",
}
CAMERA_SETUPS = {
    "Game298_0601": """- This is a single camera setup where the camera is positioned on the sideline of the field. 
        - The camera is observing a 5 vs 5 football game played on a sub region of a full size football field.
        - The camera pans left to view the LEFT GOAL and pans right to view the RIGHT GOAL.""",
    "Game269_0511": """- This is a single camera setup where the camera is positioned on the sideline of the field. 
        - The camera is observing a 11 vs 11 football game played on a full size football field.
        - The camera pans left to view the LEFT GOAL and pans right to view the RIGHT GOAL.""",
    "Game277_0526": """- This is a single camera setup where the camera is positioned on the sideline of the field. 
        - The camera is observing a 11 vs 11 football game played on a full size football field.
        - The camera pans left to view the LEFT GOAL and pans right to view the RIGHT GOAL.""",
    "Game297_0616":"""- This is a dual camera setup where the cameras are positioned on the sideline of the field. 
        -The left camera shows the left side of the field and the LEFT GOAL.
        -The right camera shows the right side of the field and the RIGHT GOAL.
        -The cameras are synchronised and show the same {duration}-second time period.
        -THe cameras are observing a 8 vs 8 football game played on a sub region of a full size football field.
        """,
    "Game304_0618":"""- This is a dual camera setup where the cameras are positioned on the sideline of the field. 
        -The left camera shows the left side of the field and the LEFT GOAL.
        -The right camera shows the right side of the field and the RIGHT GOAL.
        -The cameras are synchronised and show the same {duration}-second time period.
        -THe cameras are observing a 8 vs 8 football game played on a sub region of a full size football field.
        """
}

def create_directories():
    """Create all necessary directories"""
    for path in PATHS.values():
        if isinstance(path, Path):
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {path}")

def get_api_key():
    """Returns the single Tier 1 API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please export it in your terminal.")
    return api_key

def validate_config():
    """Validate configuration settings"""
    print("🔧 Football Analysis Configuration")
    print("=" * 40)
    print(f"Clip duration: {VIDEO_SETTINGS['clip_duration']} seconds")
    print(f"Target FPS: {VIDEO_SETTINGS['target_fps']}")
    print(f"Target resolution: {VIDEO_SETTINGS['target_resolution']}")
    print(f"Football events: {len(FOOTBALL_SETTINGS['events'])} types")
    print(f"Formations: {len(FOOTBALL_SETTINGS['formations'])} types")
    print(f"Estimated cost per match: ${COST_SETTINGS['estimated_cost_per_match']:.4f}")
    print("✅ Configuration validated")

if __name__ == "__main__":
    create_directories()
    validate_config()
    print("\n🚀 Football analysis system ready!") 