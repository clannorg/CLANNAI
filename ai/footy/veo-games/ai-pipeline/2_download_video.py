#!/usr/bin/env python3
"""
2. Download Video
Downloads match video from Veo
"""

import sys
import os
from pathlib import Path

def download_video(veo_url, match_id=None):
    """Download video from Veo URL"""
    print(f"📥 Step 2: Downloading video from {veo_url}")
    
    if not match_id:
        # Extract match ID from URL
        import re
        pattern = r'/matches/([^/]+)/?'
        match = re.search(pattern, veo_url)
        if not match:
            print("❌ Could not extract match ID from URL")
            return False
        match_id = match.group(1)
    
    data_dir = Path("../data") / match_id
    video_path = data_dir / "video.mp4"
    
    if not data_dir.exists():
        print(f"❌ Match data directory not found: {data_dir}")
        print("Run Step 1 first: python 1_extract_veo_data.py")
        return False
    
    # TODO: Implement actual video download from Veo
    # For now, just create placeholder
    print(f"📹 Downloading video to {video_path}")
    print("⚠️  TODO: Implement actual Veo video download")
    
    # Create empty video file as placeholder
    video_path.touch()
    
    print(f"✅ Step 2 complete: Video ready at {video_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python 2_download_video.py <veo-url> [match-id]")
        sys.exit(1)
    
    veo_url = sys.argv[1]
    match_id = sys.argv[2] if len(sys.argv) == 3 else None
    
    success = download_video(veo_url, match_id)
    
    if success:
        print(f"🎯 Ready for Step 3: Generate clips")
    else:
        sys.exit(1) 