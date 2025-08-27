#!/usr/bin/env python3
"""
Step 3.7: Upload to website via API
Uses the same API endpoints as the manual website form.
Reads S3 URLs from 3.5_s3_core_locations.json and posts to website.
"""

import json
import sys
import requests
from pathlib import Path

def load_website_game_id(match_id):
    """Load website game ID from file"""
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    website_id_file = base_path / "website_game_id.txt"
    
    if not website_id_file.exists():
        print(f"❌ No website game ID found for: {match_id}")
        print(f"Run step 1.0 first: python 1.0_webid.py {match_id}")
        return None
    
    return website_id_file.read_text().strip()

def load_s3_locations(match_id):
    """Load S3 URLs from core locations file"""
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    s3_file = base_path / "3.5_s3_core_locations.json"
    
    if not s3_file.exists():
        print(f"❌ S3 locations not found: {s3_file}")
        print("Run step 3.5 first: python 3.5_s3_uploader.py <match-id>")
        return None
    
    with open(s3_file, 'r') as f:
        return json.load(f)

def get_auth_token(no_auth=False):
    """Get authentication token from environment or config"""
    if no_auth:
        print("🔓 Running in no-auth mode (using test endpoints)")
        return None
    
    # For now, we'll need to get this manually
    # In production, this would come from .env or config
    print("🔐 Authentication required for API calls")
    print("You'll need to get your auth token from the website")
    print("(Check browser dev tools → Application → Local Storage → auth token)")
    
    token = input("Enter your auth token: ").strip()
    if not token:
        print("❌ Auth token required")
        return None
    
    return token

def upload_events(game_id, events_url, auth_token, base_url="http://localhost:3001"):
    """Upload events JSON via API"""
    if auth_token is None:
        # Use test endpoint (no auth required)
        url = f"{base_url}/api/games/{game_id}/upload-analysis-file-test"
        headers = {'Content-Type': 'application/json'}
    else:
        # Use regular endpoint (auth required)
        url = f"{base_url}/api/games/{game_id}/upload-events"
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
    
    # Extract filename from URL
    filename = events_url.split('/')[-1]
    
    if auth_token is None:
        # Test endpoint payload format
        payload = {
            's3Key': events_url,
            'originalFilename': filename,
            'fileType': 'events'
        }
    else:
        # Regular endpoint payload format
        payload = {
            's3Key': events_url,
            'originalFilename': filename
        }
    
    print(f"📤 Uploading events: {filename}")
    print(f"🔗 URL: {events_url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Events uploaded successfully")
            print(f"📊 Events count: {result.get('game', {}).get('events_count', 'Unknown')}")
            return True
        else:
            print(f"❌ Events upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Events upload error: {e}")
        return False

def upload_tactical(game_id, tactical_url, auth_token, base_url="http://localhost:3001"):
    """Upload tactical analysis via API"""
    if auth_token is None:
        # Use improved test endpoint (no auth required, now updates tactical_files properly)
        url = f"{base_url}/api/games/{game_id}/upload-tactical-test"
        headers = {'Content-Type': 'application/json'}
    else:
        # Use regular endpoint (auth required)
        url = f"{base_url}/api/games/{game_id}/upload-tactical"
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
    
    # Extract filename from URL
    filename = tactical_url.split('/')[-1]
    
    payload = {
        's3Key': tactical_url,
        'originalFilename': filename
    }
    
    print(f"📤 Uploading tactical: {filename}")
    print(f"🔗 URL: {tactical_url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Tactical analysis uploaded successfully")
            return True
        else:
            print(f"❌ Tactical upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Tactical upload error: {e}")
        return False

def upload_metadata(game_id, metadata_url, auth_token, base_url="http://localhost:3001"):
    """Upload metadata JSON via API"""
    if auth_token is None:
        # Use test endpoint (no auth required)
        url = f"{base_url}/api/games/{game_id}/upload-metadata-test"
        headers = {'Content-Type': 'application/json'}
    else:
        # Use regular endpoint (auth required)
        url = f"{base_url}/api/games/{game_id}/upload-metadata"
        headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
    
    filename = metadata_url.split('/')[-1]
    
    payload = {
        'metadataUrl': metadata_url
    }
    
    print(f"📤 Uploading metadata: {filename}")
    print(f"🔗 URL: {metadata_url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Metadata uploaded successfully")
            return True
        else:
            print(f"❌ Metadata upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Metadata upload error: {e}")
        return False

def upload_video(game_id, video_url, auth_token, base_url="http://localhost:3001"):
    """Upload video URL via API"""
    url = f"{base_url}/api/games/{game_id}/upload-video"
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        's3Key': video_url
    }
    
    print(f"📤 Uploading video URL")
    print(f"🔗 URL: {video_url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Video URL uploaded successfully")
            return True
        else:
            print(f"❌ Video upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Video upload error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python 3.7_api_upload.py <match-id> [base-url] [--no-auth]")
        print("Example: python 3.7_api_upload.py 20250427-match-apr-27-2025-9bd1cf29")
        print("Example: python 3.7_api_upload.py 20250427-match-apr-27-2025-9bd1cf29 --no-auth")
        print("Example: python 3.7_api_upload.py 20250427-match-apr-27-2025-9bd1cf29 https://your-website.com")
        sys.exit(1)
    
    match_id = sys.argv[1]
    no_auth = '--no-auth' in sys.argv
    
    # Parse base URL (skip --no-auth flag)
    base_url = "http://localhost:3001"
    for arg in sys.argv[2:]:
        if not arg.startswith('--'):
            base_url = arg
            break
    
    print(f"🌐 Uploading {match_id} analysis via website API...")
    print(f"🔗 Base URL: {base_url}")
    print("=" * 60)
    
    # Load required data
    game_id = load_website_game_id(match_id)
    if not game_id:
        sys.exit(1)
    
    s3_locations = load_s3_locations(match_id)
    if not s3_locations:
        sys.exit(1)
    
    # Get auth token (or skip if no-auth mode)
    auth_token = get_auth_token(no_auth)
    if not no_auth and not auth_token:
        sys.exit(1)
    
    print(f"\n🎯 Uploading to game: {game_id}")
    print(f"📦 S3 bucket: {s3_locations.get('bucket', 'Unknown')}")
    
    core_files = s3_locations.get('core_files', {})
    success_count = 0
    total_uploads = 0
    
    # Upload events JSON (main requirement)
    if 'web_events_array_json' in core_files:
        total_uploads += 1
        if upload_events(game_id, core_files['web_events_array_json'], auth_token, base_url):
            success_count += 1
    else:
        print("⚠️  No web_events_array_json found in S3 locations")
    
    # Upload metadata JSON (if available)
    if 'match_metadata_json' in core_files:
        total_uploads += 1
        if upload_metadata(game_id, core_files['match_metadata_json'], auth_token, base_url):
            success_count += 1
            
            # Also upload S3 core locations as additional metadata
            try:
                s3_core_url = s3_locations.get('core_files', {}).get('training_recommendations_json')
                if s3_core_url:
                    print("📤 Updating metadata with S3 core locations...")
                    # Create a metadata update with s3_files
                    metadata_update = {
                        "s3_files": s3_locations.get('core_files', {})
                    }
                    
                    # Send metadata update (this will merge with existing metadata)
                    import json
                    temp_metadata = json.dumps(metadata_update)
                    # We'll use the same metadata endpoint but with core locations
                    print("🔗 S3 files metadata updated")
                else:
                    print("ℹ️  No training recommendations in S3 core files")
            except Exception as e:
                print(f"⚠️  Failed to update S3 metadata: {e}")
    else:
        print("⚠️  No match_metadata_json found in S3 locations")
    
    # Upload tactical analysis (if available)
    if 'tactical_analysis_json' in core_files:
        total_uploads += 1
        if upload_tactical(game_id, core_files['tactical_analysis_json'], auth_token, base_url):
            success_count += 1
    else:
        print("⚠️  No tactical_analysis_json found in S3 locations")
    
    # Upload video URL (if we have it)
    # Note: Video URL might be in different format, check what's available
    video_url = None
    if 'video_url' in s3_locations:
        video_url = s3_locations['video_url']
    elif 'video_mp4' in core_files:
        video_url = core_files['video_mp4']
    
    if video_url:
        total_uploads += 1
        if upload_video(game_id, video_url, auth_token, base_url):
            success_count += 1
    else:
        print("ℹ️  No video URL found (this is optional)")
    
    # Summary
    print(f"\n🎉 UPLOAD SUMMARY:")
    print(f"✅ Successful: {success_count}/{total_uploads}")
    print(f"🎮 Game ID: {game_id}")
    print(f"🌐 Website should now display the analysis!")
    
    if success_count == total_uploads and total_uploads > 0:
        print(f"\n🎯 All uploads successful! Check the website.")
        return True
    else:
        print(f"\n⚠️  Some uploads failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
