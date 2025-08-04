#!/usr/bin/env python3
"""
Setup script for AI Pipeline → Website Automation
Helps configure game mappings and test the connection
"""

import os
import json
import requests
import yaml
from pathlib import Path

def load_config():
    """Load automation config"""
    with open('automation_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def authenticate(config):
    """Test authentication with API"""
    print("🔐 Testing API authentication...")
    
    try:
        response = requests.post(
            f"{config['api']['base_url']}/api/auth/login",
            json={
                'email': config['api']['company_email'],
                'password': config['api']['company_password']
            }
        )
        
        if response.status_code == 200:
            token = response.json().get('token')
            print("✅ Authentication successful!")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def get_games_list(config, token):
    """Fetch all games from the API"""
    print("📊 Fetching games from database...")
    
    try:
        response = requests.get(
            f"{config['api']['base_url']}/api/company/games",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            games = response.json().get('games', [])
            print(f"✅ Found {len(games)} games in database")
            return games
        else:
            print(f"❌ Failed to fetch games: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching games: {e}")
        return []

def scan_ai_analyses():
    """Scan for AI analysis folders"""
    print("🔍 Scanning for AI analysis folders...")
    
    data_dir = Path('./data')
    if not data_dir.exists():
        print("❌ Data directory not found: ./data")
        return []
    
    analyses = []
    for item in data_dir.iterdir():
        if item.is_dir():
            # Check if it has analysis output files
            has_events = (item / 'web_events.json').exists() or (item / 'web_events_array.json').exists()
            analyses.append({
                'folder': item.name,
                'has_events': has_events,
                'events_file': 'web_events.json' if (item / 'web_events.json').exists() else 'web_events_array.json'
            })
    
    print(f"✅ Found {len(analyses)} analysis folders")
    return analyses

def suggest_mappings(games, analyses):
    """Suggest game mappings based on titles and folder names"""
    print("\n🎯 Suggested game mappings:")
    print("=" * 50)
    
    mappings = {}
    
    for analysis in analyses:
        if not analysis['has_events']:
            continue
            
        folder_name = analysis['folder']
        best_match = None
        best_score = 0
        
        # Try to find matching games
        for game in games:
            score = 0
            title = game.get('title', '').lower()
            description = game.get('description', '').lower()
            
            # Exact folder name match
            if folder_name.lower() in title or folder_name.lower() in description:
                score += 10
            
            # Partial matches
            folder_parts = folder_name.lower().replace('-', ' ').split()
            for part in folder_parts:
                if len(part) > 2:  # Skip short parts
                    if part in title:
                        score += 2
                    if part in description:
                        score += 1
            
            if score > best_score:
                best_score = score
                best_match = game
        
        if best_match and best_score > 0:
            mappings[folder_name] = best_match['id']
            print(f"📁 {folder_name}")
            print(f"   → {best_match['title']} (ID: {best_match['id']})")
            print(f"   → Confidence: {best_score}/10")
            print()
        else:
            print(f"❓ {folder_name}")
            print(f"   → No clear match found")
            print()
    
    return mappings

def update_config_with_mappings(mappings):
    """Update the configuration file with suggested mappings"""
    print("📝 Updating automation_config.yaml with mappings...")
    
    with open('automation_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Update game mappings
    if 'game_mapping' not in config:
        config['game_mapping'] = {}
    
    config['game_mapping'].update(mappings)
    
    with open('automation_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print("✅ Configuration updated!")

def test_upload(config, token):
    """Test uploading events to verify the system works"""
    print("\n🧪 Testing event upload...")
    
    # Find first analysis with events
    analyses = scan_ai_analyses()
    test_analysis = None
    
    for analysis in analyses:
        if analysis['has_events']:
            test_analysis = analysis
            break
    
    if not test_analysis:
        print("❌ No analyses with events found for testing")
        return False
    
    # Load config to get mapping
    with open('automation_config.yaml', 'r') as f:
        updated_config = yaml.safe_load(f)
    
    folder_name = test_analysis['folder']
    game_id = updated_config.get('game_mapping', {}).get(folder_name)
    
    if not game_id:
        print(f"❌ No game mapping found for {folder_name}")
        return False
    
    # Load events
    events_file = Path(f"./data/{folder_name}/{test_analysis['events_file']}")
    try:
        with open(events_file, 'r') as f:
            events_data = json.load(f)
        
        # Handle both formats
        events = events_data.get('events', []) if isinstance(events_data, dict) else events_data
        
        print(f"📊 Testing with {len(events)} events from {folder_name}")
        
        # Test upload
        response = requests.post(
            f"{config['api']['base_url']}/api/games/{game_id}/upload-events-direct",
            json={
                'events': events[:5],  # Only upload first 5 events for testing
                'source': 'automation_test'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            print("✅ Test upload successful!")
            return True
        else:
            print(f"❌ Test upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test upload error: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 AI Pipeline → Website Automation Setup")
    print("=" * 50)
    
    # Check if config exists
    if not os.path.exists('automation_config.yaml'):
        print("❌ automation_config.yaml not found!")
        print("Please ensure you're in the ai/veo-games/ directory")
        return
    
    # Load config
    config = load_config()
    
    # Test authentication
    token = authenticate(config)
    if not token:
        print("❌ Setup failed - please check your API credentials")
        return
    
    # Get games and analyses
    games = get_games_list(config, token)
    analyses = scan_ai_analyses()
    
    if not games:
        print("❌ No games found in database")
        return
    
    if not analyses:
        print("❌ No AI analyses found")
        return
    
    # Suggest mappings
    mappings = suggest_mappings(games, analyses)
    
    if mappings:
        # Ask user if they want to update config
        response = input("\n💾 Update configuration with these mappings? (y/n): ")
        if response.lower() == 'y':
            update_config_with_mappings(mappings)
            
            # Test upload
            test_response = input("🧪 Test the upload system? (y/n): ")
            if test_response.lower() == 'y':
                if test_upload(config, token):
                    print("\n🎉 Setup complete! The automation system is ready.")
                    print("To start monitoring: python pipeline_automation.py")
                    print("To run once: python pipeline_automation.py --once")
                else:
                    print("\n⚠️ Setup complete but test failed. Check the mappings.")
            else:
                print("\n✅ Setup complete! Run 'python pipeline_automation.py' to start.")
        else:
            print("\n📝 Please manually update the game_mapping section in automation_config.yaml")
    else:
        print("\n❓ No automatic mappings found.")
        print("Please manually update the game_mapping section in automation_config.yaml")
        print("Format: 'analysis_folder_name': 'database_game_uuid'")

if __name__ == "__main__":
    main()