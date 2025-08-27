#!/usr/bin/env python3
"""
6. S3 Uploader - Analysis Files Only
Uploads key analysis files to S3 and tracks cloud locations
"""

import sys
import os
import json
import boto3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def load_env_multisource() -> None:
    """Load env vars from multiple locations without overriding existing ones."""
    load_dotenv()  # keep shell values

    candidates = [
        Path(__file__).resolve().parent.parent / '.env',   # ai/veo-games-v3/.env
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
            print(f"✅ AWS credentials valid")
        except Exception as e:
            if "NoSuchBucket" in str(e):
                print(f"✅ AWS credentials valid (bucket may not exist yet)")
            else:
                raise Exception(f"AWS credentials not found. Either set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or run 'aws configure'")
        
        print(f"🌩️  Connected to S3 bucket: {self.bucket_name} ({os.getenv('AWS_REGION', 'eu-west-1')})")

    def upload_file_to_s3(self, local_path, s3_key, content_type=None):
        """Upload a single file to S3 and return the URL"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            # Add cache control for better performance
            extra_args['CacheControl'] = 'max-age=31536000'
            
            file_size_mb = local_path.stat().st_size / 1024 / 1024
            print(f"   📤 Uploading {local_path.name} ({file_size_mb:.1f}MB)")
            
            self.s3_client.upload_file(
                str(local_path), 
                self.bucket_name, 
                s3_key,
                ExtraArgs=extra_args
            )
            
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            print(f"   ✅ Uploaded to: {s3_url}")
            return s3_url
            
        except Exception as e:
            print(f"   ❌ Failed to upload {local_path.name}: {e}")
            return None

def upload_match_to_s3(match_id):
    """Upload key match analysis files to S3"""
    print(f"🌩️  Starting S3 upload for {match_id}")
    
    # Initialize uploader
    try:
        uploader = S3MatchUploader()
    except Exception as e:
        print(f"❌ S3 setup failed: {e}")
        return False
    
    # Define paths
    data_dir = Path("../outputs") / match_id
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Define files to upload (v2 pipeline outputs only)
    upload_files = {
        # Core webapp files (highest priority)
        "web_events.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Web app compatible events timeline"
        },
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
        
        # V2 pipeline intermediate files
        "6_validated_timeline.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "AI validated match timeline (goals/shots)"
        },
        "6.5_accuracy_comparison.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "AI vs VEO accuracy comparison"
        },
        "7_definite_events.txt": {
            "s3_folder": "analysis-data", 
            "content_type": "text/plain",
            "description": "VEO-confirmed events only"
        },
        "8_other_events.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain", 
            "description": "Fouls, cards, corners and other events"
        },
        "tactical_analysis.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "Complete tactical analysis using full game timeline + highlights"
        },
        "tactical_analysis.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Webapp-compatible tactical analysis JSON format"
        },
        "sick_tactical_analysis.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Interactive tactical analysis with player cards, clickable moments, and rich data"
        },
        "5_complete_timeline.txt": {
            "s3_folder": "analysis-data",
            "content_type": "text/plain",
            "description": "Complete detailed play-by-play timeline"
        },
        "1_veo_ground_truth.json": {
            "s3_folder": "analysis-data",
            "content_type": "application/json",
            "description": "Original Veo ground truth data for comparison"
        },
        # Large files (upload last)
        "video.mp4": {
            "s3_folder": "analysis-videos",
            "content_type": "video/mp4", 
            "description": "Full match video"
        }
    }
    
    # Track successful uploads
    s3_locations = {
        "match_id": match_id,
        "upload_timestamp": datetime.now().isoformat(),
        "bucket": uploader.bucket_name,
        "region": os.getenv('AWS_REGION', 'eu-west-1'),
        "s3_urls": {},
        "upload_summary": {
            "total_files": len(upload_files),
            "successful_uploads": 0,
            "failed_uploads": 0,
            "total_size_mb": 0
        }
    }
    
    print(f"📋 Found {len(upload_files)} files to upload")
    
    # Upload each file
    for filename, config in upload_files.items():
        local_path = data_dir / filename
        
        if not local_path.exists():
            print(f"⚠️  Skipping {filename} (not found)")
            s3_locations["upload_summary"]["failed_uploads"] += 1
            continue
            
        # Generate S3 key with match_id prefix
        file_extension = local_path.suffix
        clean_filename = f"{match_id}-{filename.replace('.', '-')}{file_extension}"
        s3_key = f"{config['s3_folder']}/{clean_filename}"
        
        # Upload file
        s3_url = uploader.upload_file_to_s3(
            local_path, 
            s3_key, 
            config["content_type"]
        )
        
        if s3_url:
            s3_locations["s3_urls"][filename] = {
                "url": s3_url,
                "s3_key": s3_key,
                "description": config["description"],
                "file_size_mb": round(local_path.stat().st_size / 1024 / 1024, 2)
            }
            s3_locations["upload_summary"]["successful_uploads"] += 1
            s3_locations["upload_summary"]["total_size_mb"] += s3_locations["s3_urls"][filename]["file_size_mb"]
        else:
            s3_locations["upload_summary"]["failed_uploads"] += 1
    
    # Save S3 locations tracker
    s3_locations_file = data_dir / "3.2_s3_locations.json"
    try:
        with open(s3_locations_file, 'w') as f:
            json.dump(s3_locations, f, indent=2)
        print(f"📋 S3 locations saved to: {s3_locations_file}")
    except Exception as e:
        print(f"⚠️  Failed to save S3 locations: {e}")
    
    # Create focused core locations file (events only - no AI insights)
    try:
        core_locations = {
            "match_id": match_id,
            "upload_timestamp": s3_locations["upload_timestamp"],
            "bucket": s3_locations["bucket"],
            "region": s3_locations["region"],
            "core_files": {}
        }
        
        # Core file mapping for website (essential files only)
        core_file_mapping = {
            "web_events_array_json": "3.1_web_events_array.json",  # Main events file
            "video_mp4": "video.mp4",                          # Match video
            "match_metadata_json": "3.1_match_metadata.json",       # Final score, teams
            "team_config_json": "1_team_config.json"  # Team configuration
        }
        
        for key, filename in core_file_mapping.items():
            if filename in s3_locations["s3_urls"]:
                core_locations["core_files"][key] = s3_locations["s3_urls"][filename]["url"]
        
        core_locations_file = data_dir / "3.2_s3_core_locations.json"
        with open(core_locations_file, 'w') as f:
            json.dump(core_locations, f, indent=2)
        print(f"📋 Core locations saved to: {core_locations_file}")
        
    except Exception as e:
        print(f"⚠️  Failed to create core locations: {e}")

    # Print summary
    summary = s3_locations["upload_summary"]
    print(f"\n📊 Upload Summary:")
    print(f"   ✅ Successful: {summary['successful_uploads']}/{summary['total_files']} files")
    print(f"   📦 Total uploaded: {summary['total_size_mb']:.1f}MB")
    print(f"   🌐 S3 bucket: {uploader.bucket_name}")
    
    if summary["failed_uploads"] > 0:
        print(f"   ⚠️  Failed uploads: {summary['failed_uploads']}")
    
    # Show key URLs for easy access
    if s3_locations["s3_urls"]:
        print(f"\n🔗 Key S3 URLs:")
        priority_files = ["web_events_array.json", "web_events.json", "8_tactical_match_summary.txt", "video.mp4"]
        for key_file in priority_files:
            if key_file in s3_locations["s3_urls"]:
                url = s3_locations["s3_urls"][key_file]["url"]
                print(f"   📄 {key_file}: {url}")
    
    # Company Dashboard Instructions
    if s3_locations["s3_urls"]:
        print(f"\n🎯 COMPANY DASHBOARD INSTRUCTIONS:")
        print(f"   📋 Copy-paste the following into ClannAI company dashboard:")
        print(f"")
        
        # Video URL
        if "video.mp4" in s3_locations["s3_urls"]:
            video_url = s3_locations["s3_urls"]["video.mp4"]["url"]
            print(f"   🎬 1. CLICK 'Add S3 Video' → Paste this URL:")
            print(f"      {video_url}")
            print(f"")
        
        # Events JSON
        if "web_events_array.json" in s3_locations["s3_urls"]:
            events_url = s3_locations["s3_urls"]["web_events_array.json"]["url"]
            print(f"   🎮 2. CLICK 'Add Analysis' → Download and paste JSON content:")
            print(f"      curl -s {events_url}")
            print(f"      (Or download: {events_url})")
            print(f"")
        
        # Analysis files  
        analysis_files = ["6_validated_timeline.txt", "8_tactical_match_summary.txt", "8_tactical_analysis_red_team.txt", "8_tactical_analysis_yellow_team.txt", "5_complete_timeline.txt"]
        analysis_urls = {}
        for file_name in analysis_files:
            if file_name in s3_locations["s3_urls"]:
                analysis_urls[file_name] = s3_locations["s3_urls"][file_name]["url"]
        
        if analysis_urls:
            print(f"   📊 3. CLICK 'Add S3 Analysis Files' → Paste this JSON:")
            print(f"      {{")
            for i, (file_name, url) in enumerate(analysis_urls.items()):
                comma = "," if i < len(analysis_urls) - 1 else ""
                print(f'        "{file_name}": "{url}"{comma}')
            print(f"      }}")
            print(f"")
        
        print(f"   ✅ 4. CLICK 'Mark Analyzed' to enable user access")
        print(f"   🌐 Users can now view the game with interactive timeline!")
    
    # Update source.json with cloud status
    try:
        source_file = data_dir / "source.json"
        if source_file.exists():
            with open(source_file, 'r') as f:
                source_data = json.load(f)
            
            source_data["cloud_status"] = "uploaded"
            source_data["s3_upload_timestamp"] = s3_locations["upload_timestamp"]
            source_data["s3_files_count"] = summary["successful_uploads"]
            source_data["s3_bucket"] = uploader.bucket_name
            
            with open(source_file, 'w') as f:
                json.dump(source_data, f, indent=2)
            print(f"📝 Updated source.json with cloud status")
    except Exception as e:
        print(f"⚠️  Failed to update source.json: {e}")
    
    return summary["successful_uploads"] > 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 8_s3_uploader.py <match_id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = upload_match_to_s3(match_id)
    
    if success:
        print(f"🎉 S3 upload completed for {match_id}")
        print(f"🌐 Files now available in cloud for web app integration")
    else:
        print(f"❌ S3 upload failed for {match_id}")
        sys.exit(1)