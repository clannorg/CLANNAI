#!/usr/bin/env python3
"""
Upload Sample Clip to S3
Uploads a 15-second clip to S3 for footage verification
"""

import sys
import os
import json
import boto3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class S3ClipUploader:
    def __init__(self):
        """Initialize S3 client with environment credentials"""
        # Try environment variables first, then AWS CLI/profile
        if os.getenv('AWS_ACCESS_KEY_ID'):
            self.s3_client = boto3.client(
                's3',
                region_name=os.getenv('AWS_REGION', 'eu-west-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        else:
            # Use default AWS profile/credentials
            self.s3_client = boto3.client('s3', region_name='eu-west-1')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME', 'end-nov-webapp-clann')
        
        print(f"🌩️  Connected to S3 bucket: {self.bucket_name}")

    def upload_clip_to_s3(self, local_path, s3_key):
        """Upload a clip to S3 and return the URL"""
        try:
            file_size_mb = local_path.stat().st_size / 1024 / 1024
            print(f"📤 Uploading {local_path.name} ({file_size_mb:.1f}MB)")
            
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
            print(f"❌ Failed to upload {local_path.name}: {e}")
            return None

def upload_sample_clip(match_id, clip_name="clip_05m00s.mp4"):
    """Upload a sample clip to S3 for verification"""
    print(f"🎬 Uploading sample clip for {match_id}")
    
    # Initialize uploader
    try:
        uploader = S3ClipUploader()
    except Exception as e:
        print(f"❌ S3 setup failed: {e}")
        return False
    
    # Define paths
    data_dir = Path("../data") / match_id
    clip_path = data_dir / "clips" / clip_name
    
    if not clip_path.exists():
        print(f"❌ Clip not found: {clip_path}")
        print(f"Available clips:")
        clips_dir = data_dir / "clips"
        if clips_dir.exists():
            clips = list(clips_dir.glob("*.mp4"))[:5]
            for clip in clips:
                print(f"  - {clip.name}")
        return False
    
    # Create S3 key
    s3_key = f"sample-clips/{match_id}/{clip_name}"
    
    # Upload the clip
    s3_url = uploader.upload_clip_to_s3(clip_path, s3_key)
    
    if s3_url:
        print(f"\n🎯 SAMPLE CLIP UPLOADED!")
        print(f"📹 Clip: {clip_name}")
        print(f"🌐 URL: {s3_url}")
        print(f"📊 Check this clip to verify:")
        print(f"   - Is it zoomed footage (not panoramic)?")
        print(f"   - Is it the correct Edinburgh United game?")
        print(f"   - Is the quality good for AI analysis?")
        return True
    else:
        print(f"❌ Upload failed")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_sample_clip.py <match-id> [clip-name]")
        print("Example: python upload_sample_clip.py edinburgh-20250726 clip_05m00s.mp4")
        sys.exit(1)
    
    match_id = sys.argv[1]
    clip_name = sys.argv[2] if len(sys.argv) > 2 else "clip_05m00s.mp4"
    
    success = upload_sample_clip(match_id, clip_name)
    
    if success:
        print(f"\n✅ Sample clip uploaded successfully!")
        print(f"🔍 Check the S3 URL to verify footage quality")
    else:
        sys.exit(1) 