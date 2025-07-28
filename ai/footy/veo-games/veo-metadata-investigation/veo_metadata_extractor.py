#!/usr/bin/env python3
"""
Veo Metadata Extractor
Extracts built-in event data from Veo platform (goals, shots, etc.)
This gives us ground truth data to compare against our AI analysis
"""

import requests
import json
import logging
from pathlib import Path
from urllib.parse import urlparse
import time
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VeoMetadataExtractor:
    """
    Extracts event metadata from Veo platform
    """
    
    def __init__(self):
        self.session = requests.Session()
        
        # Veo-specific headers (same as VeoDownloader)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_match_id(self, url: str) -> str:
        """Extract match ID from Veo URL"""
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        
        for i, part in enumerate(path_parts):
            if part == "matches" and i + 1 < len(path_parts):
                return path_parts[i + 1]
        
        # Fallback
        for part in path_parts:
            if part and len(part) > 10 and '-' in part:
                return part
        
        raise ValueError(f"Could not extract match ID from URL: {url}")
    
    def get_match_metadata(self, match_id: str) -> Optional[Dict]:
        """
        Get basic match information
        """
        try:
            # Try different API endpoints that might exist
            endpoints_to_try = [
                f"https://app.veo.co/api/app/matches/{match_id}",
                f"https://app.veo.co/api/app/matches/{match_id}/metadata",
                f"https://app.veo.co/api/app/matches/{match_id}/info",
                f"https://app.veo.co/api/matches/{match_id}",
                f"https://app.veo.co/api/matches/{match_id}/metadata",
                f"https://api.veo.co/matches/{match_id}",
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = self.session.get(endpoint)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ Success with endpoint: {endpoint}")
                        return data
                    else:
                        logger.debug(f"❌ Endpoint returned {response.status_code}: {endpoint}")
                        
                except Exception as e:
                    logger.debug(f"❌ Endpoint failed: {endpoint} - {e}")
                    continue
            
            logger.warning("No metadata endpoints worked")
            return None
            
        except Exception as e:
            logger.error(f"Error getting match metadata: {e}")
            return None
    
    def get_match_events(self, match_id: str) -> Optional[List[Dict]]:
        """
        Get match events (goals, shots, saves, etc.)
        """
        try:
            # Try different event API endpoints
            endpoints_to_try = [
                f"https://app.veo.co/api/app/matches/{match_id}/events",
                f"https://app.veo.co/api/app/matches/{match_id}/highlights",
                f"https://app.veo.co/api/app/matches/{match_id}/timeline",
                f"https://app.veo.co/api/app/matches/{match_id}/annotations",
                f"https://app.veo.co/api/matches/{match_id}/events",
                f"https://app.veo.co/api/matches/{match_id}/highlights",
                f"https://app.veo.co/api/matches/{match_id}/timeline",
                f"https://api.veo.co/matches/{match_id}/events",
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    logger.info(f"Trying events endpoint: {endpoint}")
                    response = self.session.get(endpoint)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ Events found with endpoint: {endpoint}")
                        logger.info(f"📊 Response type: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
                        
                        # Handle different response formats
                        if isinstance(data, list):
                            logger.info(f"📋 Found {len(data)} events in list format")
                            return data
                        elif isinstance(data, dict):
                            # Look for events in different keys
                            for key in ['events', 'highlights', 'timeline', 'annotations', 'data', 'results']:
                                if key in data and isinstance(data[key], list):
                                    logger.info(f"📋 Found {len(data[key])} events in key '{key}'")
                                    return data[key]
                            # If no list found, return the whole dict as it might be event data
                            logger.info(f"📋 No event list found, returning full dict")
                            return [data]  # Single event object
                        
                except Exception as e:
                    logger.debug(f"❌ Events endpoint failed: {endpoint} - {e}")
                    continue
            
            logger.warning("No events endpoints worked")
            return None
            
        except Exception as e:
            logger.error(f"Error getting match events: {e}")
            return None
    
    def scrape_page_metadata(self, url: str) -> Optional[Dict]:
        """
        Fallback: scrape the Veo page directly for event data
        """
        try:
            logger.info("Attempting to scrape page metadata...")
            response = self.session.get(url)
            response.raise_for_status()
            
            html = response.text
            
            # Look for JSON data in script tags
            import re
            
            # Common patterns for embedded JSON data
            patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                r'window\.__NUXT__\s*=\s*(\{.*?\});',
                r'window\.APP_DATA\s*=\s*(\{.*?\});',
                r'"events":\s*(\[.*?\])',
                r'"highlights":\s*(\[.*?\])',
                r'"timeline":\s*(\[.*?\])',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches[0])
                        logger.info(f"✅ Found data with pattern: {pattern}")
                        return data
                    except json.JSONDecodeError:
                        continue
            
            # Look for specific event indicators in HTML
            events = []
            
            # Look for "Shot on goal" and other event markers
            event_patterns = [
                (r'Shot on goal.*?(\d{1,2}:\d{2})', 'SHOT'),
                (r'Goal.*?(\d{1,2}:\d{2})', 'GOAL'),
                (r'Save.*?(\d{1,2}:\d{2})', 'SAVE'),
                (r'Yellow card.*?(\d{1,2}:\d{2})', 'YELLOW_CARD'),
                (r'Red card.*?(\d{1,2}:\d{2})', 'RED_CARD'),
                (r'Corner.*?(\d{1,2}:\d{2})', 'CORNER'),
                (r'Free kick.*?(\d{1,2}:\d{2})', 'FREE_KICK'),
            ]
            
            for pattern, event_type in event_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    events.append({
                        'type': event_type,
                        'timestamp': match,
                        'source': 'scraped'
                    })
            
            if events:
                logger.info(f"✅ Scraped {len(events)} events from HTML")
                return {'events': events}
            
            logger.warning("No events found in page scraping")
            return None
            
        except Exception as e:
            logger.error(f"Error scraping page metadata: {e}")
            return None
    
    def extract_all_metadata(self, veo_url: str) -> Dict:
        """
        Extract all available metadata from a Veo match
        """
        logger.info(f"🔍 Extracting metadata from: {veo_url}")
        
        match_id = self.extract_match_id(veo_url)
        logger.info(f"📋 Match ID: {match_id}")
        
        result = {
            'match_id': match_id,
            'veo_url': veo_url,
            'extracted_at': datetime.now().isoformat(),
            'metadata': None,
            'events': None,
            'scraped_data': None
        }
        
        # Try API endpoints first
        logger.info("🌐 Trying API endpoints...")
        metadata = self.get_match_metadata(match_id)
        if metadata:
            result['metadata'] = metadata
            logger.info("✅ Got match metadata via API")
        
        events = self.get_match_events(match_id)
        if events:
            result['events'] = events
            logger.info(f"✅ Got {len(events)} events via API")
        
        # Fallback to scraping
        if not result['metadata'] and not result['events']:
            logger.info("🕷️ Falling back to page scraping...")
            scraped = self.scrape_page_metadata(veo_url)
            if scraped:
                result['scraped_data'] = scraped
                logger.info("✅ Got data via scraping")
        
        return result
    
    def save_metadata(self, metadata: Dict, output_path: str):
        """Save extracted metadata to file"""
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"💾 Saved metadata to: {output_path}")


def main():
    """Test the metadata extractor"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python veo_metadata_extractor.py <veo_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    extractor = VeoMetadataExtractor()
    metadata = extractor.extract_all_metadata(url)
    
    print("\n" + "="*60)
    print("🎯 VEO METADATA EXTRACTION RESULTS")
    print("="*60)
    
    print(f"📋 Match ID: {metadata['match_id']}")
    print(f"🌐 URL: {metadata['veo_url']}")
    
    if metadata['metadata']:
        print("✅ API Metadata: Found")
    else:
        print("❌ API Metadata: Not found")
    
    if metadata['events']:
        print(f"✅ API Events: {len(metadata['events'])} found")
    else:
        print("❌ API Events: Not found")
    
    if metadata['scraped_data']:
        print("✅ Scraped Data: Found")
        if 'events' in metadata['scraped_data']:
            print(f"   📊 Scraped Events: {len(metadata['scraped_data']['events'])}")
    else:
        print("❌ Scraped Data: Not found")
    
    # Save results
    output_file = f"veo_metadata_{metadata['match_id']}.json"
    extractor.save_metadata(metadata, output_file)
    
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main() 