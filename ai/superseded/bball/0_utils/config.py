#!/usr/bin/env python3
"""
Configuration for Basketball Analysis MVP
"""

import os
from pathlib import Path

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# File paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "0_utils" / "output"
REPORTS_DIR = BASE_DIR / "reports"

# Video processing settings
CLIP_DURATION = 15  # seconds
MAX_CLIPS = 40  # 10 minutes worth of clips

# Firebase video URLs
LEFT_CAMERA_URL = "https://firebasestorage.googleapis.com/v0/b/hooper-ac7b0.appspot.com/o/sessions%2FHGRnfBNFWKR5tUJokUHF?alt=media&token=c54da24b-d465-4e10-a936-5d380b65cbb9"
RIGHT_CAMERA_URL = "https://firebasestorage.googleapis.com/v0/b/hooper-ac7b0.appspot.com/o/sessions%2Fe2nPtR6FznYcSmaGSKGL?alt=media&token=2a336399-d1f8-427e-b62b-8dfdaa5dc924"

# Video filenames
LEFT_VIDEO_FILENAME = "left_camera.mp4"
RIGHT_VIDEO_FILENAME = "right_camera.mp4"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True) 