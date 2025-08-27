#!/usr/bin/env python3
"""
Auto-upload script for VEO Games v4 pipeline
Connects VM analysis to ClannAI website via interactive game selection
"""

import json
import sys
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional

class ClannAIUploader:
    def __init__(self):
        # Website API configuration
        self.api_base = os.getenv('CLANNAI_API_BASE', "http://localhost:3002/api")
        self.api_token = os.getenv('CLANNAI_API_TOKEN')
        
        # For local development, we can skip token requirement
        if not self.api_token:
            print("⚠️  Warning: CLANNAI_API_TOKEN not set")
            print("   For production use, set your API token")
            print("   For local testing, we'll try without authentication...")
            self.api_token = None
    
    def get_recent_games(self) -> List[Dict]:
        """Fetch recent games from website API"""
        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            # Try to get all games first, fallback to demo games
            response = requests.get(
                f"{self.api_base}/games/all-test", 
                headers=headers,
                timeout=10
            )
            
            # If all-games endpoint doesn't exist, try demo games
            if response.status_code == 404:
                response = requests.get(
                    f"{self.api_base}/games/demo-test", 
                    headers=headers,
                    timeout=10
                )
            
            if response.status_code == 200:
                games = response.json().get('games', [])
                return games[:10]  # Return top 10 recent games
            else:
                print(f"❌ Failed to fetch games: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            print(f"❌ Network error fetching games: {e}")
            return []
    
    def display_game_menu(self, games: List[Dict]) -> Optional[str]:
        """Display interactive game selection menu"""
        print("\n🎮 CLANNAI - Game Selection")
        print("=" * 50)
        
        if not games:
            print("❌ No games found. Please create a game on the website first.")
            return None
        
        print("📋 Select a game to upload analysis to:\n")
        
        for i, game in enumerate(games, 1):
            # Determine game status
            has_analysis = bool(game.get('ai_analysis'))
            has_tactical = bool(game.get('tactical_analysis'))
            
            if has_analysis and has_tactical:
                status = "[HAS DATA]"
            elif has_analysis or has_tactical:
                status = "[PARTIAL DATA]"
            else:
                status = "[EMPTY]"
            
            # Format creation date
            created = game.get('created_at', 'Unknown date')
            if 'T' in created:
                created = created.split('T')[0]  # Just the date part
            
            print(f"[{i}] {game.get('title', 'Untitled Game')} {status}")
            print(f"    Created: {created} | ID: {game.get('id', 'Unknown')[:8]}...")
            print()
        
        print("[N] Create new game instead")
        print("[Q] Quit")
        print()
        
        while True:
            choice = input("Enter your choice (1-{}, N, Q): ".format(len(games))).strip().upper()
            
            if choice == 'Q':
                return None
            elif choice == 'N':
                return 'NEW'
            elif choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(games):
                    return games[choice_num - 1]['id']
            
            print("❌ Invalid choice. Please try again.")
    
    def load_analysis_files(self, match_id: str) -> Dict:
        """Load all analysis files for the match"""
        outputs_dir = Path(f"../outputs/{match_id}")
        
        if not outputs_dir.exists():
            raise FileNotFoundError(f"Outputs directory not found: {outputs_dir}")
        
        files = {}
        
        # Load match metadata (contains S3 URLs)
        metadata_file = outputs_dir / "match_metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                files['metadata'] = json.load(f)
        else:
            raise FileNotFoundError("match_metadata.json not found")
        
        # Load S3 locations
        s3_file = outputs_dir / "s3_locations.json"
        if s3_file.exists():
            with open(s3_file) as f:
                files['s3_locations'] = json.load(f)
        else:
            raise FileNotFoundError("s3_locations.json not found")
        
        return files
    
    def upload_to_game(self, game_id: str, files: Dict) -> bool:
        """Upload analysis files to specific game"""
        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            s3_urls = files['s3_locations'].get('s3_urls', {})
            metadata = files['metadata']
            
            print(f"📤 Uploading analysis to game {game_id[:8]}...")
            
            # 1. Upload events (timeline data)
            if 'web_events_array.json' in s3_urls:
                events_url = s3_urls['web_events_array.json']['url']
                print("📊 Uploading events data...")
                
                response = requests.post(
                    f"{self.api_base}/games/{game_id}/upload-analysis-file-test",
                    headers=headers,
                    json={
                        's3Key': events_url,
                        'originalFilename': 'web_events_array.json',
                        'fileType': 'events'
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"❌ Events upload failed: {response.status_code}")
                    return False
                print("✅ Events uploaded successfully")
            
            # 2. Upload tactical analysis
            if '11_tactical_analysis.json' in s3_urls:
                tactical_url = s3_urls['11_tactical_analysis.json']['url']
                print("🧠 Uploading tactical analysis...")
                
                response = requests.post(
                    f"{self.api_base}/games/{game_id}/upload-tactical-test",
                    headers=headers,
                    json={
                        's3Key': tactical_url,
                        'originalFilename': '11_tactical_analysis.json',
                        'fileType': 'tactical'
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"❌ Tactical upload failed: {response.status_code}")
                    return False
                print("✅ Tactical analysis uploaded successfully")
            
            # 3. Update game metadata
            if 'video.mp4' in s3_urls:
                video_url = s3_urls['video.mp4']['url']
                print("🎬 Updating video URL...")
                
                # Update game with video URL and metadata
                game_update = {
                    'video_url': video_url,
                    'status': 'analyzed',
                    'metadata': {
                        'analysis_completed_at': files['s3_locations'].get('upload_timestamp'),
                        'match_id': metadata.get('match_id'),
                        'teams': metadata.get('teams', {}),
                        'final_score': metadata.get('final_score'),
                        'file_urls': s3_urls
                    }
                }
                
                # Note: You'll need to add this endpoint to your backend
                response = requests.put(
                    f"{self.api_base}/games/{game_id}/test",
                    headers=headers,
                    json=game_update,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print("✅ Game metadata updated successfully")
                else:
                    print(f"⚠️  Metadata update failed: {response.status_code} (analysis still uploaded)")
            
            return True
            
        except requests.RequestException as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def create_new_game(self, files: Dict) -> Optional[str]:
        """Create a new game from analysis data"""
        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            metadata = files['metadata']
            s3_urls = files['s3_locations'].get('s3_urls', {})
            
            # Extract team names for title
            teams = metadata.get('teams', {})
            red_team = teams.get('red_team', {}).get('name', 'Team A')
            blue_team = teams.get('blue_team', {}).get('name', 'Team B')
            
            game_data = {
                'title': f"Auto: {red_team} vs {blue_team}",
                'description': f"AI analysis from VEO match {metadata.get('match_id', 'Unknown')}",
                'video_url': s3_urls.get('video.mp4', {}).get('url', ''),
                'team_name': red_team,
                'is_demo': True,
                'status': 'analyzed'
            }
            
            print("🆕 Creating new game...")
            response = requests.post(
                f"{self.api_base}/games",
                headers=headers,
                json=game_data,
                timeout=30
            )
            
            if response.status_code == 201:
                game = response.json().get('game', {})
                game_id = game.get('id')
                print(f"✅ New game created: {game.get('title')} (ID: {game_id[:8]}...)")
                return game_id
            else:
                print(f"❌ Failed to create game: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Game creation failed: {e}")
            return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 3.3_auto_upload.py <match-id>")
        print("Example: python3 3.3_auto_upload.py cookstown-youth-football-club-20250729")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    print("🚀 CLANNAI Auto-Upload Tool")
    print("=" * 50)
    print(f"📁 Match ID: {match_id}")
    
    uploader = ClannAIUploader()
    
    try:
        # Load analysis files
        print("📂 Loading analysis files...")
        files = uploader.load_analysis_files(match_id)
        print("✅ Analysis files loaded successfully")
        
        # Get recent games
        print("🌐 Fetching recent games from website...")
        games = uploader.get_recent_games()
        
        # Display menu and get selection
        selected_game_id = uploader.display_game_menu(games)
        
        if not selected_game_id:
            print("👋 Upload cancelled")
            return
        
        # Handle selection
        if selected_game_id == 'NEW':
            game_id = uploader.create_new_game(files)
            if not game_id:
                print("❌ Failed to create new game")
                return
        else:
            game_id = selected_game_id
        
        # Upload analysis to selected/created game
        success = uploader.upload_to_game(game_id, files)
        
        if success:
            print(f"\n🎉 SUCCESS!")
            print(f"📊 Analysis uploaded to game: {game_id[:8]}...")
            print(f"🌐 View at: {uploader.api_base.replace('/api', '')}/games/{game_id}")
        else:
            print("\n❌ Upload failed. Check the errors above.")
            
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        print("💡 Make sure you've run the full pipeline and S3 upload first")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
