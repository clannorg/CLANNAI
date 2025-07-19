#!/usr/bin/env python3
"""
Football Analysis Configuration
Settings and paths for football video analysis
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

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
    "model": "gemini-2.0-flash-exp",  # Best for events
    "tactical_model": "gemini-2.5-flash-exp",  # Better for tactical analysis
    "max_tokens": 1000,
    "temperature": 0.1,
    "top_p": 0.8,
    "rate_limit_delay": 1.0  # Seconds between API calls
}

# Cost tracking
COST_SETTINGS = {
    "cost_per_clip": 0.000210,  # Based on basketball analysis
    "estimated_clips_per_match": 180,  # 90 minutes / 30 seconds
    "estimated_api_calls_per_match": 360,  # Events + insights
    "estimated_cost_per_match": 0.0756
}

# File paths
PATHS = {
    "input_dir": INPUT_DIR,
    "output_dir": OUTPUT_DIR,
    "processed_clips": BASE_DIR / "0_utils" / "output",
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

def create_directories():
    """Create all necessary directories"""
    for path in PATHS.values():
        if isinstance(path, Path):
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {path}")

def get_api_key():
    """Get API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
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