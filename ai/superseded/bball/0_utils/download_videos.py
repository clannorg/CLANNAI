#!/usr/bin/env python3
"""
Download Basketball Videos from Firebase
Downloads the dual-camera basketball session videos for analysis
"""

import os
import requests
import time
from pathlib import Path

# Firebase video URLs
LEFT_CAMERA_URL = "https://firebasestorage.googleapis.com/v0/b/hooper-ac7b0.appspot.com/o/sessions%2FHGRnfBNFWKR5tUJokUHF?alt=media&token=c54da24b-d465-4e10-a936-5d380b65cbb9"
RIGHT_CAMERA_URL = "https://firebasestorage.googleapis.com/v0/b/hooper-ac7b0.appspot.com/o/sessions%2Fe2nPtR6FznYcSmaGSKGL?alt=media&token=2a336399-d1f8-427e-b62b-8dfdaa5dc924"

def download_video(url, filename, description):
    """Download a video file from URL"""
    print(f"📥 Downloading {description}...")
    print(f"   URL: {url[:80]}...")
    
    try:
        # Stream the download to handle large files
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        
        # Create output directory in 0_utils
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / filename
        
        # Skip if file already exists
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024*1024)
            print(f"♻️  File already exists: {file_path} ({size_mb:.1f}MB)")
            return file_path
        
        # Download with progress
        downloaded_size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}% ({downloaded_size:,}/{total_size:,} bytes)", end="")
        
        print(f"\n✅ Downloaded: {file_path}")
        size_mb = downloaded_size / (1024*1024)
        print(f"   Size: {size_mb:.1f}MB")
        return file_path
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Download both basketball videos"""
    print("🏀 BASKETBALL VIDEO DOWNLOADER")
    print("=" * 50)
    
    # Download left camera view
    left_video = download_video(
        LEFT_CAMERA_URL, 
        "left_camera.mp4", 
        "Left Camera Video"
    )
    
    print()
    
    # Download right camera view
    right_video = download_video(
        RIGHT_CAMERA_URL,
        "right_camera.mp4", 
        "Right Camera Video"
    )
    
    print("\n" + "=" * 50)
    
    if left_video and right_video:
        print("🎉 DOWNLOAD COMPLETE!")
        print(f"✅ Left camera: {left_video}")
        print(f"✅ Right camera: {right_video}")
        print("\n📋 Next steps:")
        print("1. Run video splitter: python 0_utils/split_videos.py")
        print("2. Run video compression: python 0_utils/compress_videos.py")
    else:
        print("❌ Some downloads failed. Check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    main() 