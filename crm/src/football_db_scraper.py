import requests
import pandas as pd
import json
import time
from pathlib import Path
import logging
from urllib.parse import urljoin
import re

class FootballDatabaseScraper:
    """
    Scraper for structured football databases and APIs
    Targets databases with comprehensive club listings
    """
    
    def __init__(self):
        self.setup_logging()
        self.clubs = []
        self.progress_file = Path('data/football_db_progress.json')
        self.load_progress()
        
        # Headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def setup_logging(self):
        logging.basicConfig(
            filename='data/football_db_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self.clubs = data.get('clubs', [])
                self.processed_sources = data.get('processed_sources', [])
        else:
            self.processed_sources = []
            
    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump({
                'clubs': self.clubs,
                'processed_sources': self.processed_sources,
                'total_clubs': len(self.clubs)
            }, f, indent=2)

    def scrape_football_webpages(self):
        """Scrape from known football club listing pages"""
        if 'football_webpages' in self.processed_sources:
            print("Football webpages already processed, skipping...")
            return
            
        print("🔍 Scraping football club listing websites...")
        
        # Known sources with club listings
        sources = [
            {
                'name': 'English Football League',
                'urls': [
                    'https://www.efl.com/clubs-and-competitions/sky-bet-championship/',
                    'https://www.efl.com/clubs-and-competitions/sky-bet-league-one/',
                    'https://www.efl.com/clubs-and-competitions/sky-bet-league-two/'
                ],
                'country': 'England',
                'level': 'professional'
            },
            {
                'name': 'Premier League',
                'urls': ['https://www.premierleague.com/clubs'],
                'country': 'England', 
                'level': 'premier'
            },
            {
                'name': 'Scottish Premier League',
                'urls': ['https://spfl.co.uk/clubs'],
                'country': 'Scotland',
                'level': 'premier'
            }
        ]
        
        for source in sources:
            print(f"📡 Scraping {source['name']}...")
            
            for url in source['urls']:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Extract club names using regex patterns
                        club_patterns = [
                            r'<[^>]*class="[^"]*club[^"]*"[^>]*>([^<]+)</[^>]*>',
                            r'<a[^>]*href="[^"]*club[^"]*"[^>]*>([^<]+)</a>',
                            r'>([A-Z][A-Za-z\s]+(?:FC|United|City|Town|Athletic|Rovers|Wanderers|County))<',
                            r'data-club="([^"]+)"',
                            r'club-name[^>]*>([^<]+)<'
                        ]
                        
                        for pattern in club_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                club_name = match.strip()
                                if len(club_name) > 3 and not any(x in club_name.lower() for x in ['javascript', 'function', 'var ', 'null']):
                                    self.clubs.append({
                                        'name': club_name,
                                        'source': source['name'],
                                        'url': url,
                                        'country': source['country'],
                                        'level': source['level'],
                                        'type': 'club_listing'
                                    })
                    
                    time.sleep(1)  # Be respectful
                    
                except Exception as e:
                    logging.error(f"Error scraping {url}: {e}")
                    continue
                    
        self.processed_sources.append('football_webpages')
        print(f"✅ Football webpages complete: {len(self.clubs)} total clubs")

    def scrape_county_fas(self):
        """Scrape County Football Association websites"""
        if 'county_fas' in self.processed_sources:
            print("County FAs already processed, skipping...")
            return
            
        print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Scraping County Football Associations...")
        
        # Major County FA websites
        county_fas = [
            {'name': 'Lancashire FA', 'url': 'https://www.lancashirefa.com'},
            {'name': 'Yorkshire FA', 'url': 'https://www.yorkshirefa.com'},
            {'name': 'Surrey FA', 'url': 'https://www.surreyfa.com'},
            {'name': 'Kent FA', 'url': 'https://www.kentfa.com'},
            {'name': 'Essex FA', 'url': 'https://www.essexfa.com'},
            {'name': 'Manchester FA', 'url': 'https://www.manchesterfa.com'},
            {'name': 'Birmingham FA', 'url': 'https://www.birminghamfa.com'},
            {'name': 'Liverpool FA', 'url': 'https://www.liverpoolfa.com'},
            {'name': 'London FA', 'url': 'https://www.londonfa.com'}
        ]
        
        for fa in county_fas:
            print(f"📡 Scraping {fa['name']}...")
            
            # Try common club directory paths
            club_paths = ['/clubs', '/find-a-club', '/club-directory', '/teams', '/leagues']
            
            for path in club_paths:
                try:
                    url = fa['url'] + path
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        content = response.text
                        
                        # Extract club names
                        club_patterns = [
                            r'>([A-Z][A-Za-z\s&\-\']+(?:FC|United|City|Town|Athletic|Rovers|Wanderers|County|AFC|Sports|Club))<',
                            r'<a[^>]*>([A-Z][A-Za-z\s&\-\']+(?:FC|United|City|Town|Athletic|Rovers|Wanderers|County|AFC|Sports|Club))</a>',
                            r'club["\s>][^>]*>([A-Z][A-Za-z\s&\-\']{3,30})<'
                        ]
                        
                        for pattern in club_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                club_name = match.strip()
                                if len(club_name) > 3:
                                    self.clubs.append({
                                        'name': club_name,
                                        'source': fa['name'],
                                        'url': url,
                                        'country': 'England',
                                        'level': 'county',
                                        'type': 'county_fa'
                                    })
                        
                        break  # Found clubs on this path, move to next FA
                        
                except Exception as e:
                    continue
                    
            time.sleep(2)  # Be respectful between FA requests
            
        self.processed_sources.append('county_fas')
        print(f"✅ County FAs complete: {len(self.clubs)} total clubs")

    def scrape_scottish_leagues(self):
        """Scrape Scottish football league websites"""
        if 'scottish_leagues' in self.processed_sources:
            print("Scottish leagues already processed, skipping...")
            return
            
        print("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scraping Scottish football leagues...")
        
        scottish_sources = [
            {'name': 'SPFL', 'url': 'https://spfl.co.uk/clubs'},
            {'name': 'Scottish Highland League', 'url': 'https://www.highlandleague.com'},
            {'name': 'East of Scotland League', 'url': 'https://www.eastscottishfootball.com'},
            {'name': 'South of Scotland League', 'url': 'https://www.southofscotlandleague.co.uk'},
            {'name': 'West of Scotland League', 'url': 'https://www.westofscotlandleague.co.uk'}
        ]
        
        for source in scottish_sources:
            print(f"📡 Scraping {source['name']}...")
            
            try:
                response = requests.get(source['url'], headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Scottish club patterns
                    patterns = [
                        r'>([A-Z][A-Za-z\s&\-\']+(?:FC|United|City|Town|Athletic|Rovers|Wanderers|County|AFC|Thistle|Hearts|Celtic|Rangers))<',
                        r'<a[^>]*club[^>]*>([A-Z][A-Za-z\s&\-\']+)</a>',
                        r'team["\s>][^>]*>([A-Z][A-Za-z\s&\-\']{3,30})<'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            club_name = match.strip()
                            # Filter for Scottish-style names
                            if len(club_name) > 3 and any(word in club_name for word in ['FC', 'United', 'City', 'Town', 'Athletic', 'Rovers', 'Wanderers', 'Hearts', 'Celtic', 'Rangers', 'Thistle']):
                                self.clubs.append({
                                    'name': club_name,
                                    'source': source['name'],
                                    'url': source['url'],
                                    'country': 'Scotland',
                                    'level': 'league',
                                    'type': 'scottish_league'
                                })
                
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error scraping {source['name']}: {e}")
                continue
                
        self.processed_sources.append('scottish_leagues')
        print(f"✅ Scottish leagues complete: {len(self.clubs)} total clubs")

    def scrape_football_apis(self):
        """Scrape public football APIs and databases"""
        if 'football_apis' in self.processed_sources:
            print("Football APIs already processed, skipping...")
            return
            
        print("🌐 Scraping public football APIs...")
        
        # Try some public football APIs (many require keys, but some endpoints are open)
        api_sources = [
            {
                'name': 'Football-Data.org',
                'base_url': 'http://api.football-data.org/v2',
                'endpoints': ['/competitions/2021/teams', '/competitions/2016/teams']  # Premier League, Championship
            }
        ]
        
        for api in api_sources:
            print(f"📡 Trying {api['name']}...")
            
            for endpoint in api['endpoints']:
                try:
                    url = api['base_url'] + endpoint
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'teams' in data:
                            for team in data['teams']:
                                club_name = team.get('name', team.get('shortName', ''))
                                if club_name:
                                    self.clubs.append({
                                        'name': club_name,
                                        'source': api['name'],
                                        'url': team.get('website', ''),
                                        'country': team.get('area', {}).get('name', 'Unknown'),
                                        'level': 'professional',
                                        'type': 'api_data',
                                        'founded': team.get('founded'),
                                        'venue': team.get('venue')
                                    })
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"Error with API {url}: {e}")
                    continue
                    
        self.processed_sources.append('football_apis')
        print(f"✅ Football APIs complete: {len(self.clubs)} total clubs")

    def deduplicate_clubs(self):
        """Remove duplicate clubs"""
        print("🔄 Deduplicating clubs...")
        
        unique_clubs = []
        seen_names = set()
        
        for club in self.clubs:
            normalized_name = club['name'].lower().strip()
            normalized_name = re.sub(r'[^\w\s]', '', normalized_name)
            normalized_name = re.sub(r'\s+', ' ', normalized_name)
            
            if normalized_name not in seen_names and len(normalized_name) > 2:
                seen_names.add(normalized_name)
                unique_clubs.append(club)
                
        removed_count = len(self.clubs) - len(unique_clubs)
        self.clubs = unique_clubs
        
        print(f"✅ Removed {removed_count} duplicates. {len(self.clubs)} unique clubs remaining.")

    def save_results(self):
        """Save results to CSV"""
        if not self.clubs:
            print("❌ No clubs found")
            return
            
        df = pd.DataFrame(self.clubs)
        df['scraped_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        output_file = 'data/football_database_clubs.csv'
        df.to_csv(output_file, index=False)
        
        # Summary
        summary = {
            'total_clubs': len(df),
            'by_country': df['country'].value_counts().to_dict(),
            'by_source': df['source'].value_counts().to_dict(),
            'by_level': df['level'].value_counts().to_dict()
        }
        
        with open('data/football_database_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"💾 Saved {len(df)} clubs to {output_file}")
        print(f"📊 Summary: {summary}")
        
        return output_file

    def run_scrape(self):
        """Run the complete database scraping process"""
        print("🚀 Starting football database scraping...")
        
        self.scrape_football_webpages()
        self.save_progress()
        
        self.scrape_county_fas()
        self.save_progress()
        
        self.scrape_scottish_leagues()
        self.save_progress()
        
        self.scrape_football_apis()
        self.save_progress()
        
        self.deduplicate_clubs()
        output_file = self.save_results()
        
        print(f"\n🎉 Database scraping complete!")
        print(f"📁 Results: {output_file}")
        print(f"📊 Total clubs: {len(self.clubs)}")
        
        return output_file

if __name__ == "__main__":
    scraper = FootballDatabaseScraper()
    scraper.run_scrape()