#!/usr/bin/env python3
"""
AI Pipeline → Website Automation
Monitors AI pipeline output and automatically uploads results to the web application
"""

import os
import json
import time
import requests
import logging
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PipelineAutomation:
    def __init__(self, config_path: str = "automation_config.yaml"):
        """Initialize the automation system"""
        self.config = self.load_config(config_path)
        self.api_base = self.config['api']['base_url']
        self.auth_token = None
        self.data_dir = Path(self.config['pipeline']['data_directory'])
        
        # Authenticate with the API
        self.authenticate()
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"✅ Loaded config from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file {config_path} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'api': {
                'base_url': 'https://api.clannai.com',
                'company_email': 'admin@clann.ai',
                'company_password': 'demo123'
            },
            'pipeline': {
                'data_directory': './data',
                'monitor_interval': 30,  # seconds
                'processed_games_file': 'processed_games.json'
            },
            'game_mapping': {
                # Format: "ai_folder_name": "game_id_in_database"
                # Example: "ballyclare-20250111": "uuid-from-database"
            }
        }
    
    def authenticate(self) -> bool:
        """Authenticate with the API and get access token"""
        try:
            response = requests.post(
                f"{self.api_base}/api/auth/login",
                json={
                    'email': self.config['api']['company_email'],
                    'password': self.config['api']['company_password']
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                logger.info("✅ Successfully authenticated with API")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        return {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
    
    def load_processed_games(self) -> Dict[str, str]:
        """Load list of already processed games"""
        processed_file = self.config['pipeline']['processed_games_file']
        try:
            with open(processed_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_processed_games(self, processed_games: Dict[str, str]):
        """Save list of processed games"""
        processed_file = self.config['pipeline']['processed_games_file']
        with open(processed_file, 'w') as f:
            json.dump(processed_games, f, indent=2)
    
    def detect_completed_analyses(self) -> List[str]:
        """Detect AI analyses that have completed but not been uploaded"""
        completed = []
        processed_games = self.load_processed_games()
        
        for game_dir in self.data_dir.iterdir():
            if not game_dir.is_dir():
                continue
                
            game_id = game_dir.name
            
            # Skip if already processed
            if game_id in processed_games:
                continue
            
            # Check if analysis is complete (has web_events.json or web_events_array.json)
            web_events_file = game_dir / "web_events.json"
            web_events_array_file = game_dir / "web_events_array.json"
            
            if web_events_file.exists() or web_events_array_file.exists():
                completed.append(game_id)
                logger.info(f"🔍 Found completed analysis: {game_id}")
        
        return completed
    
    def load_events_data(self, game_dir: Path) -> Optional[List[Dict]]:
        """Load events data from AI pipeline output"""
        # Try web_events_array.json first (direct array format)
        web_events_array_file = game_dir / "web_events_array.json"
        if web_events_array_file.exists():
            try:
                with open(web_events_array_file, 'r') as f:
                    events = json.load(f)
                logger.info(f"📊 Loaded {len(events)} events from web_events_array.json")
                return events
            except Exception as e:
                logger.error(f"❌ Failed to load web_events_array.json: {e}")
        
        # Try web_events.json (object format with events property)
        web_events_file = game_dir / "web_events.json"
        if web_events_file.exists():
            try:
                with open(web_events_file, 'r') as f:
                    data = json.load(f)
                events = data.get('events', []) if isinstance(data, dict) else data
                logger.info(f"📊 Loaded {len(events)} events from web_events.json")
                return events
            except Exception as e:
                logger.error(f"❌ Failed to load web_events.json: {e}")
        
        logger.warning(f"⚠️ No events files found in {game_dir}")
        return None
    
    def get_game_id_for_analysis(self, analysis_id: str) -> Optional[str]:
        """Get database game ID for analysis folder"""
        # Check manual mapping first
        game_mapping = self.config.get('game_mapping', {})
        if analysis_id in game_mapping:
            return game_mapping[analysis_id]
        
        # Auto-discovery: search for games with matching title/description
        try:
            response = requests.get(
                f"{self.api_base}/api/company/games",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                games = response.json().get('games', [])
                
                # Look for games with matching identifiers
                for game in games:
                    # Match by title containing analysis ID
                    if analysis_id.lower() in game.get('title', '').lower():
                        logger.info(f"🎯 Auto-matched {analysis_id} → {game['id']} ({game['title']})")
                        return game['id']
                    
                    # Match by description containing analysis ID  
                    if analysis_id.lower() in game.get('description', '').lower():
                        logger.info(f"🎯 Auto-matched {analysis_id} → {game['id']} ({game['title']})")
                        return game['id']
                
                logger.warning(f"⚠️ No game found for analysis: {analysis_id}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch games for matching: {e}")
            return None
    
    def upload_events_to_game(self, game_id: str, events: List[Dict]) -> bool:
        """Upload events to a specific game"""
        try:
            response = requests.post(
                f"{self.api_base}/api/games/{game_id}/upload-events-direct",
                json={
                    'events': events,
                    'source': 'ai_pipeline_automation'
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Successfully uploaded {len(events)} events to game {game_id}")
                logger.info(f"📋 Game: {data['game']['title']} - Status: {data['game']['status']}")
                return True
            else:
                logger.error(f"❌ Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return False
    
    def process_completed_analysis(self, analysis_id: str) -> bool:
        """Process a single completed analysis"""
        logger.info(f"🔄 Processing analysis: {analysis_id}")
        
        # Load events data
        game_dir = self.data_dir / analysis_id
        events = self.load_events_data(game_dir)
        
        if not events:
            logger.error(f"❌ No events data found for {analysis_id}")
            return False
        
        # Get corresponding game ID
        game_id = self.get_game_id_for_analysis(analysis_id)
        
        if not game_id:
            logger.warning(f"⚠️ No game ID found for analysis {analysis_id}")
            logger.info(f"💡 Add to automation_config.yaml: game_mapping.{analysis_id}: 'your-game-uuid'")
            return False
        
        # Upload events
        success = self.upload_events_to_game(game_id, events)
        
        if success:
            # Mark as processed
            processed_games = self.load_processed_games()
            processed_games[analysis_id] = {
                'game_id': game_id,
                'processed_at': datetime.now().isoformat(),
                'events_count': len(events)
            }
            self.save_processed_games(processed_games)
            logger.info(f"✅ Marked {analysis_id} as processed")
        
        return success
    
    def run_monitor_cycle(self):
        """Run one monitoring cycle"""
        logger.info("🔍 Scanning for completed AI analyses...")
        
        completed_analyses = self.detect_completed_analyses()
        
        if not completed_analyses:
            logger.info("😴 No new analyses found")
            return
        
        logger.info(f"🎯 Found {len(completed_analyses)} new analyses to process")
        
        for analysis_id in completed_analyses:
            try:
                self.process_completed_analysis(analysis_id)
            except Exception as e:
                logger.error(f"❌ Failed to process {analysis_id}: {e}")
    
    def run_continuous_monitor(self):
        """Run continuous monitoring"""
        interval = self.config['pipeline']['monitor_interval']
        logger.info(f"🚀 Starting continuous monitoring (checking every {interval}s)")
        
        while True:
            try:
                self.run_monitor_cycle()
            except KeyboardInterrupt:
                logger.info("👋 Shutting down monitor...")
                break
            except Exception as e:
                logger.error(f"❌ Monitor cycle error: {e}")
            
            time.sleep(interval)

def main():
    """Main entry point"""
    automation = PipelineAutomation()
    
    # Run single cycle or continuous monitoring
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        automation.run_monitor_cycle()
    else:
        automation.run_continuous_monitor()

if __name__ == "__main__":
    main()