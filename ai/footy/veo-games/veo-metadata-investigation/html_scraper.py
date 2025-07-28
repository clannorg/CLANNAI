#!/usr/bin/env python3
"""
Veo HTML Scraper
Analyzes the Veo page HTML source to find embedded event data
"""

import requests
import json
import re
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VeoHTMLScraper:
    """
    Scrapes Veo HTML for embedded event data
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def extract_match_id(self, url: str) -> str:
        """Extract match ID from Veo URL"""
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        
        for i, part in enumerate(path_parts):
            if part == "matches" and i + 1 < len(path_parts):
                return path_parts[i + 1]
        
        raise ValueError(f"Could not extract match ID from URL: {url}")
    
    def get_page_html(self, url: str) -> str:
        """Get the full HTML of the Veo page"""
        try:
            logger.info(f"Fetching HTML from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info(f"✅ Got HTML ({len(response.text)} characters)")
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching HTML: {e}")
            return ""
    
    def find_json_in_scripts(self, html: str) -> list:
        """Find JSON data embedded in script tags"""
        logger.info("🔍 Searching for JSON in script tags...")
        
        soup = BeautifulSoup(html, 'html.parser')
        script_tags = soup.find_all('script')
        
        json_data = []
        
        for i, script in enumerate(script_tags):
            if script.string:
                script_content = script.string.strip()
                
                # Look for common patterns
                patterns = [
                    r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
                    r'window\.__NUXT__\s*=\s*(\{.*?\});',
                    r'window\.APP_DATA\s*=\s*(\{.*?\});',
                    r'window\.VEO_DATA\s*=\s*(\{.*?\});',
                    r'__VEO_INITIAL_DATA__\s*=\s*(\{.*?\});',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    if matches:
                        try:
                            data = json.loads(matches[0])
                            logger.info(f"✅ Found JSON in script {i} with pattern: {pattern}")
                            json_data.append({
                                'script_index': i,
                                'pattern': pattern,
                                'data': data
                            })
                        except json.JSONDecodeError as e:
                            logger.debug(f"JSON parse error in script {i}: {e}")
        
        return json_data
    
    def search_for_events(self, html: str) -> list:
        """Search for event-related keywords in HTML"""
        logger.info("🔍 Searching for event keywords...")
        
        events = []
        
        # Event patterns to search for
        event_patterns = [
            (r'[Ss]hot\s+on\s+goal.*?(\d{1,2}:\d{2})', 'SHOT_ON_GOAL'),
            (r'[Gg]oal.*?(\d{1,2}:\d{2})', 'GOAL'),
            (r'[Ss]ave.*?(\d{1,2}:\d{2})', 'SAVE'),
            (r'[Yy]ellow\s+card.*?(\d{1,2}:\d{2})', 'YELLOW_CARD'),
            (r'[Rr]ed\s+card.*?(\d{1,2}:\d{2})', 'RED_CARD'),
            (r'[Cc]orner.*?(\d{1,2}:\d{2})', 'CORNER'),
            (r'[Ff]ree\s+kick.*?(\d{1,2}:\d{2})', 'FREE_KICK'),
        ]
        
        for pattern, event_type in event_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                events.append({
                    'type': event_type,
                    'timestamp': match,
                    'source': 'html_text_search'
                })
        
        if events:
            logger.info(f"✅ Found {len(events)} events in HTML text")
        else:
            logger.info("❌ No events found in HTML text")
        
        return events
    
    def analyze_page_structure(self, html: str) -> dict:
        """Analyze the overall structure of the page"""
        logger.info("🔍 Analyzing page structure...")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            'title': soup.title.string if soup.title else None,
            'scripts_count': len(soup.find_all('script')),
            'divs_with_id': [div.get('id') for div in soup.find_all('div') if div.get('id')],
            'data_attributes': [],
            'interesting_classes': []
        }
        
        # Look for elements with data attributes
        for element in soup.find_all(attrs={'data-testid': True}):
            analysis['data_attributes'].append({
                'tag': element.name,
                'data-testid': element.get('data-testid'),
                'text': element.get_text()[:100] if element.get_text() else None
            })
        
        # Look for interesting class names
        for element in soup.find_all(class_=True):
            classes = element.get('class')
            for cls in classes:
                if any(keyword in cls.lower() for keyword in ['event', 'timeline', 'highlight', 'match']):
                    if cls not in analysis['interesting_classes']:
                        analysis['interesting_classes'].append(cls)
        
        return analysis
    
    def full_analysis(self, url: str) -> dict:
        """Perform complete analysis of Veo page"""
        logger.info(f"🔍 Starting full analysis of: {url}")
        
        match_id = self.extract_match_id(url)
        html = self.get_page_html(url)
        
        if not html:
            return {'error': 'Failed to fetch HTML'}
        
        analysis = {
            'match_id': match_id,
            'url': url,
            'html_length': len(html),
            'json_data': self.find_json_in_scripts(html),
            'events_found': self.search_for_events(html),
            'page_structure': self.analyze_page_structure(html)
        }
        
        logger.info("✅ Analysis complete")
        return analysis
    
    def save_analysis(self, analysis: dict, filename: str):
        """Save analysis to file"""
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        logger.info(f"💾 Analysis saved to: {filename}")


def main():
    """Test the HTML scraper"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python html_scraper.py <veo_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    scraper = VeoHTMLScraper()
    analysis = scraper.full_analysis(url)
    
    print("\n" + "="*60)
    print("🔍 VEO HTML ANALYSIS RESULTS")
    print("="*60)
    
    print(f"📋 Match ID: {analysis['match_id']}")
    print(f"📄 HTML Length: {analysis['html_length']:,} characters")
    print(f"📜 Scripts Found: {len(analysis.get('json_data', []))}")
    print(f"⚽ Events Found: {len(analysis.get('events_found', []))}")
    
    if analysis.get('events_found'):
        print("\n🎯 Events Discovered:")
        for event in analysis['events_found']:
            print(f"   {event['type']} at {event['timestamp']}")
    
    if analysis.get('json_data'):
        print(f"\n📊 JSON Data Sources:")
        for data in analysis['json_data']:
            print(f"   Script {data['script_index']}: {data['pattern']}")
    
    # Save results
    output_file = f"html_analysis_{analysis['match_id']}.json"
    scraper.save_analysis(analysis, output_file)
    
    print(f"\n💾 Full analysis saved to: {output_file}")


if __name__ == "__main__":
    main() 