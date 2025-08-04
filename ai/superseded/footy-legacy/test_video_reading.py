#!/usr/bin/env python3
"""
Test script to check video file reading
"""

import os
from pathlib import Path

def test_video_reading():
    """Test reading video files without API calls"""
    
    # Check if clips exist
    clips_dir = Path("0_utils/output")
    if not clips_dir.exists():
        print("❌ Clips directory not found")
        return
    
    clip_files = list(clips_dir.glob("*.mp4"))
    print(f"Found {len(clip_files)} video files")
    
    if not clip_files:
        print("❌ No video files found")
        return
    
    # Test reading first clip
    first_clip = clip_files[0]
    print(f"Testing with: {first_clip.name}")
    
    try:
        with open(first_clip, 'rb') as f:
            data = f.read()
            print(f"✅ Successfully read {len(data)} bytes")
            print(f"First 100 bytes: {data[:100]}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    test_video_reading() 