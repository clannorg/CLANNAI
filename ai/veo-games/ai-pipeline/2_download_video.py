#!/usr/bin/env python3
"""
2. Download Video
Downloads match video from Veo using working VeoDownloader implementation
"""

import sys
import os
from pathlib import Path
import re

# Import the working VeoDownloader from the original file
sys.path.append('../../superseded/footy-legacy/0_utils')
from veo_downloader import VeoDownloader

def create_readable_match_id(veo_match_id, veo_url=""):
    """Convert raw Veo match ID to human-readable format"""
    # Example: 20250111-ballyclare-425e4c3f -> ballyclare-20250111
    
    try:
        # Split by hyphens
        parts = veo_match_id.split('-')
        
        if len(parts) >= 3:
            # Expected format: YYYYMMDD-team-hash
            date_part = parts[0]  # 20250111
            team_part = parts[1]  # ballyclare
            
            # Validate date part
            if len(date_part) == 8 and date_part.isdigit():
                # Format: team-YYYYMMDD
                readable_id = f"{team_part}-{date_part}"
                return readable_id
            
        # Fallback: if we can't parse properly, use first 2 parts
        if len(parts) >= 2:
            return f"{parts[1]}-{parts[0]}"
            
        # Last fallback: use the original ID
        return veo_match_id
        
    except Exception:
        # If anything fails, use original ID
        return veo_match_id

def download_video(veo_url, match_id=None):
    """Download video using direct CDN URL - exactly like the working bash command"""
    print(f"📥 Step 2: Downloading video from {veo_url}")
    
    if not match_id:
        # Extract raw match ID from URL and convert to readable format
        pattern = r'/matches/([^/]+)/?'
        match = re.search(pattern, veo_url)
        if not match:
            print("❌ Could not extract match ID from URL")
            return False
        
        raw_match_id = match.group(1)
        match_id = create_readable_match_id(raw_match_id, veo_url)
        print(f"📋 Raw Veo ID: {raw_match_id}")
        print(f"📁 Using Match ID: {match_id}")
    
    data_dir = Path("../data") / match_id
    video_path = data_dir / "video.mp4"
    
    if not data_dir.exists():
        print(f"❌ Match data directory not found: {data_dir}")
        print("Run Step 1 first: python 1_extract_veo_data.py")
        return False
    
    print(f"📹 Downloading video to {video_path}")
    
    # Direct CDN URL (exactly what worked with wget)
    cdn_url = "https://c.veocdn.com/1d3c2587-0e9e-403d-a5c0-bb560d279c0c/standard/machine/32b61fa1/video.mp4"
    
    print(f"🎯 Using direct CDN URL: {cdn_url}")
    
    # Use wget exactly like the working bash command
    import subprocess
    try:
        result = subprocess.run([
            'wget', '-O', str(video_path), cdn_url
        ], check=True)
        
        if video_path.exists() and video_path.stat().st_size > 0:
            size_mb = video_path.stat().st_size / (1024 * 1024)
            print(f"✅ Step 2 complete: Video ready ({size_mb:.1f}MB)")
            return True
        else:
            print("❌ Download failed - file missing or empty")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ wget failed: {e}")
        return False

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