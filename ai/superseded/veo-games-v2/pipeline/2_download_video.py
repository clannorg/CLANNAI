#!/usr/bin/env python3
"""
2. Download Video + Create Sample Clip + Upload to S3
Downloads match video, creates 15-second sample clip, uploads to S3, prints URL
"""

import sys
import os
import json
import boto3
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class S3SampleUploader:
    def __init__(self):
        """Initialize S3 client with environment credentials"""
        if os.getenv('AWS_ACCESS_KEY_ID'):
            self.s3_client = boto3.client(
                's3',
                region_name=os.getenv('AWS_REGION', 'eu-west-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        else:
            self.s3_client = boto3.client('s3', region_name='eu-west-1')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME', 'end-nov-webapp-clann')
        print(f"🌩️  Connected to S3 bucket: {self.bucket_name}")

    def upload_sample_clip(self, local_path, match_id):
        """Upload sample clip to S3 and return the URL"""
        try:
            file_size_mb = local_path.stat().st_size / 1024 / 1024
            print(f"📤 Uploading sample clip ({file_size_mb:.1f}MB)")
            
            s3_key = f"sample-clips/{match_id}/sample_clip.mp4"
            
            self.s3_client.upload_file(
                str(local_path), 
                self.bucket_name, 
                s3_key,
                ExtraArgs={
                    'ContentType': 'video/mp4',
                    'CacheControl': 'max-age=31536000'
                }
            )
            
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            print(f"✅ Uploaded to: {s3_url}")
            return s3_url
            
        except Exception as e:
            print(f"❌ Failed to upload sample clip: {e}")
            return None

def create_sample_clip(video_path, match_id):
    """Create a 15-second sample clip from the downloaded video"""
    print(f"✂️  Creating 15-second sample clip...")
    
    sample_path = video_path.parent / "sample_clip.mp4"
    
    try:
        # Create 15-second clip starting at 5 minutes - FAST STREAM COPY!
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-ss', '00:05:00',  # Start at 5 minutes
            '-t', '00:00:15',   # 15 seconds duration
            '-c', 'copy',  # Stream copy - NO RE-ENCODING = FAST!
            '-avoid_negative_ts', 'make_zero',
            '-y',  # Overwrite
            str(sample_path)
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if sample_path.exists():
            size_mb = sample_path.stat().st_size / 1024 / 1024
            print(f"✅ Sample clip created: {size_mb:.1f}MB")
            return sample_path
        else:
            print("❌ Sample clip creation failed")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create sample clip: {e}")
        return None

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

def download_video_with_sample(veo_url, match_id=None):
    """Download video, create sample clip, upload to S3, print URL"""
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
    
    data_dir = Path("../outputs") / match_id
    video_path = data_dir / "video.mp4"
    
    if not data_dir.exists():
        print(f"❌ Match data directory not found: {data_dir}")
        print("Run Step 1 first: python 1_extract_veo_data.py")
        return False
    
    print(f"📹 Downloading video to {video_path}")
    print(f"🎯 Using yt-dlp to download zoomed footage from: {veo_url}")
    
    # Step 1: Download the video
    try:
        result = subprocess.run([
            'yt-dlp', '-f', 'standard-1080p', '-o', str(video_path), veo_url
        ], check=True)
        
        if not (video_path.exists() and video_path.stat().st_size > 0):
            print("❌ Download failed - file missing or empty")
            return False
            
        size_mb = video_path.stat().st_size / (1024 * 1024)
        print(f"✅ Video downloaded: {size_mb:.1f}MB")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        return False
    
    # Step 2: Create sample clip
    sample_path = create_sample_clip(video_path, match_id)
    if not sample_path:
        print("❌ Sample clip creation failed")
        return False
    
    # Step 3: Upload to S3
    try:
        uploader = S3SampleUploader()
        s3_url = uploader.upload_sample_clip(sample_path, match_id)
        
        if s3_url:
            print(f"\n🎯 SAMPLE CLIP READY!")
            print(f"📹 Clip: sample_clip.mp4")
            print(f"🌐 URL: {s3_url}")
            print(f"📊 Check this clip to verify:")
            print(f"   - Is it zoomed footage (not panoramic)?")
            print(f"   - Is it the correct Edinburgh United game?")
            print(f"   - Is the quality good for AI analysis?")
            return True
        else:
            print("❌ S3 upload failed")
            return False
            
    except Exception as e:
        print(f"❌ S3 setup failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python 2_download_video.py <veo-url> [match-id]")
        print("Example: python 2_download_video.py 'https://app.veo.co/matches/20250726-edinburgh-united-vs-cowdenbeath-central-75b2c59d/'")
        sys.exit(1)
    
    veo_url = sys.argv[1]
    match_id = sys.argv[2] if len(sys.argv) == 3 else None
    
    success = download_video_with_sample(veo_url, match_id)
    
    if success:
        print(f"\n✅ COMPLETE! Sample clip uploaded and ready for verification")
        print(f"🎯 Ready for Step 3: Generate clips (if sample looks good)")
    else:
        sys.exit(1) 