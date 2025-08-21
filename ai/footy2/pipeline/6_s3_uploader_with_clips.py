#!/usr/bin/env python3
"""
6. S3 Uploader with Clips Support (MAIN VERSION)
Uploads analysis files AND 15-second video clips to S3 for media conversion
"""

import sys
import os
import json
import boto3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import glob

def load_env_multisource() -> None:
    """Load env vars from multiple locations without overriding existing ones."""
    load_dotenv()  # keep shell values

    candidates = [
        Path(__file__).resolve().parent.parent / '.env',   # ai/footy2/.env
        Path(__file__).resolve().parents[2] / '.env',      # ai/.env
        Path(__file__).resolve().parents[3] / '.env',      # repo root .env
    ]
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            pass

load_env_multisource()

class S3MatchUploader:
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
        
        # Validate credentials are available (try a test call)
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 connection verified: {self.bucket_name}")
        except Exception as e:
            raise Exception(f"S3 connection failed: {e}")

    def upload_file(self, local_path, s3_folder, content_type="application/octet-stream"):
        """Upload a single file to S3"""
        if not local_path.exists():
            print(f"   ⚠️  Skipping {local_path.name} (not found)")
            return None
            
        try:
            # Create S3 key with match-id prefix for organization
            match_id = local_path.parent.name
            s3_key = f"{s3_folder}/{match_id}-{local_path.name.replace('.', '-')}.{local_path.suffix[1:]}"
            
            # Upload with proper content type
            self.s3_client.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            print(f"   ✅ Uploaded to: {s3_url}")
            return s3_url
            
        except Exception as e:
            print(f"   ❌ Failed to upload {local_path.name}: {e}")
            return None

    def upload_clips(self, clips_dir, match_id):
        """Upload all 15-second clips to S3"""
        clips_urls = []
        
        if not clips_dir.exists():
            print(f"   ⚠️  No clips directory found: {clips_dir}")
            return clips_urls
            
        clip_files = list(clips_dir.glob("*.mp4"))
        if not clip_files:
            print(f"   ⚠️  No clips found in: {clips_dir}")
            return clips_urls
            
        print(f"📹 Uploading {len(clip_files)} video clips...")
        
        for i, clip_path in enumerate(sorted(clip_files)):
            try:
                # Create S3 key for clips
                s3_key = f"clips/{match_id}/{clip_path.name}"
                
                # Upload clip
                self.s3_client.upload_file(
                    str(clip_path),
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={'ContentType': 'video/mp4'}
                )
                
                s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
                clips_urls.append({
                    "clip_name": clip_path.name,
                    "s3_url": s3_url,
                    "local_path": str(clip_path)
                })
                
                print(f"   ✅ [{i+1}/{len(clip_files)}] {clip_path.name}")
                
            except Exception as e:
                print(f"   ❌ [{i+1}/{len(clip_files)}] Failed {clip_path.name}: {e}")
                
        return clips_urls

def upload_match_to_s3(match_id):
    """Upload match analysis files AND clips to S3"""
    print(f"🌩️  Starting S3 upload for {match_id} (with clips)")
    
    # Initialize uploader
    try:
        uploader = S3MatchUploader()
    except Exception as e:
        print(f"❌ S3 setup failed: {e}")
        return False
    
    # Define paths
    data_dir = Path("../outputs") / match_id
    clips_dir = data_dir / "clips"
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Define analysis files to upload
    upload_files = {
        # Core webapp files (highest priority)
        "web_events_array.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json", 
            "description": "Direct events array for web app"
        },
        "match_metadata.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Match metadata with team colors and stats"
        },
        
        # Footy2 pipeline files
        "highlights.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "Generated highlights with exact timestamps"
        },
        "tactical_analysis.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "SICK tactical analysis (plain text)"
        },
        "sick_tactical_analysis.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "SICK tactical analysis in webapp JSON format"
        },
        
        # Supporting files
        "team_config.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Team configuration and appearance details"
        },
        "full_timeline.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "Complete match timeline from all clips"
        },
        "clips_manifest.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Manifest of all created clips"
        }
    }
    
    # Track uploads
    successful_uploads = []
    failed_uploads = []
    s3_locations = {}
    total_size = 0
    
    # Upload analysis files
    print("📄 Uploading analysis files...")
    for filename, config in upload_files.items():
        file_path = data_dir / filename
        print(f"📤 {filename}")
        
        s3_url = uploader.upload_file(
            file_path, 
            config["s3_folder"], 
            config["content_type"]
        )
        
        if s3_url:
            successful_uploads.append(filename)
            s3_locations[filename] = {
                "url": s3_url,
                "description": config["description"],
                "uploaded_at": datetime.now().isoformat()
            }
            if file_path.exists():
                total_size += file_path.stat().st_size
        else:
            failed_uploads.append(filename)
    
    # Upload video clips
    clips_urls = uploader.upload_clips(clips_dir, match_id)
    
    # Add clips to locations
    if clips_urls:
        s3_locations["clips"] = {
            "count": len(clips_urls),
            "clips": clips_urls,
            "description": "15-second video clips for analysis",
            "uploaded_at": datetime.now().isoformat()
        }
        
        # Add clips size to total
        for clip_info in clips_urls:
            clip_path = Path(clip_info["local_path"])
            if clip_path.exists():
                total_size += clip_path.stat().st_size
    
    # Save S3 locations
    s3_locations_file = data_dir / "s3_locations_with_clips.json"
    with open(s3_locations_file, 'w') as f:
        json.dump(s3_locations, f, indent=2)
    
    # Create core locations for webapp (without clips)
    core_locations = {k: v for k, v in s3_locations.items() if k != "clips"}
    core_locations_file = data_dir / "s3_core_locations.json"
    with open(core_locations_file, 'w') as f:
        json.dump(core_locations, f, indent=2)
    
    # Print summary
    print(f"📋 S3 locations saved to: {s3_locations_file}")
    print(f"📋 Core locations saved to: {core_locations_file}")
    print(f"📊 Upload Summary:")
    print(f"   ✅ Analysis files: {len(successful_uploads)}/{len(upload_files)}")
    print(f"   🎬 Video clips: {len(clips_urls)}")
    print(f"   📦 Total uploaded: {total_size / (1024*1024):.1f}MB")
    print(f"   🌐 S3 bucket: {uploader.bucket_name}")
    
    if failed_uploads:
        print(f"   ⚠️  Failed uploads: {len(failed_uploads)}")
    
    # Print key URLs
    if "web_events_array.json" in s3_locations:
        print(f"🔗 Key S3 URLs:")
        print(f"   📄 web_events_array.json: {s3_locations['web_events_array.json']['url']}")
    
    if clips_urls:
        print(f"   🎬 First clip: {clips_urls[0]['s3_url']}")
        print(f"   🎬 Last clip: {clips_urls[-1]['s3_url']}")
    
    # Print webapp instructions
    if "web_events_array.json" in s3_locations:
        print(f"🎯 COMPANY DASHBOARD INSTRUCTIONS:")
        print(f"   📋 Copy-paste the following into ClannAI company dashboard:")
        print(f"   🎮 2. CLICK 'Add Analysis' → Download and paste JSON content:")
        print(f"      curl -s {s3_locations['web_events_array.json']['url']}")
        print(f"      (Or download: {s3_locations['web_events_array.json']['url']})")
        print(f"   ✅ 4. CLICK 'Mark Analyzed' to enable user access")
        print(f"   🌐 Users can now view the game with interactive timeline!")
    
    print(f"🎉 S3 upload completed for {match_id}")
    print(f"🌐 Files now available in cloud for web app integration")
    print(f"🎬 Video clips ready for media conversion!")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 6_s3_uploader_with_clips.py <match-id>")
        print("Example: python 6_s3_uploader_with_clips.py sunday-league-game-1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = upload_match_to_s3(match_id)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()