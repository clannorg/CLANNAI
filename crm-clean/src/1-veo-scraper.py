#!/usr/bin/env python3
"""
STAGE 1: VEO Club Scraper
Gets all clubs from VEO directory with core data: name, recordings, teams
Output: data/1-veo-scraper/veo_clubs.csv
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import json
from pathlib import Path
import logging

class VeoScraper:
    def __init__(self):
        self.clubs = []
        self.progress_file = Path('data/1-veo-scraper/scraper_progress.json')
        self.setup_logging()
        self.load_progress()
        
    def setup_logging(self):
        """Setup basic logging"""
        Path('data/1-veo-scraper').mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler('data/1-veo-scraper/scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_progress(self):
        """Load previous progress if exists"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self.clubs = data.get('clubs', [])
                self.last_page = data.get('last_page', 0)
                self.logger.info(f"📚 Loaded {len(self.clubs)} existing clubs")
        else:
            self.last_page = 0
            
    def save_progress(self):
        """Save current progress"""
        with open(self.progress_file, 'w') as f:
            json.dump({
                'clubs': self.clubs,
                'last_page': self.last_page,
                'total_clubs': len(self.clubs)
            }, f, indent=2)
            
    def setup_driver(self):
        """Setup Chrome driver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        return webdriver.Chrome(options=options)
        
    def extract_club_data(self, club_element):
        """Extract core data from a club element"""
        try:
            # Get club name
            name_element = club_element.find_element(By.CSS_SELECTOR, "[class*='club-name'], h3, .name")
            club_name = name_element.text.strip()
            
            # Get recordings count
            text = club_element.text
            recordings = 0
            teams = 0
            
            # Extract numbers from text
            import re
            recording_match = re.search(r'(\d+)\s*recordings?', text, re.IGNORECASE)
            if recording_match:
                recordings = int(recording_match.group(1))
                
            team_match = re.search(r'(\d+)\s*teams?', text, re.IGNORECASE)
            if team_match:
                teams = int(team_match.group(1))
            
            return {
                'Club Name': club_name,
                'Recordings': recordings,
                'Teams': teams,
                'Source': 'VEO Directory',
                'Scraped_At': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to extract club data: {e}")
            return None
            
    def scrape_clubs(self):
        """Main scraping function"""
        self.logger.info("🚀 STAGE 1: Starting VEO club scraping...")
        
        driver = self.setup_driver()
        
        try:
            # Navigate to VEO directory
            driver.get("https://app.veo.co/all-clubs/")
            time.sleep(5)
            
            # Find scrollable container
            main_content = driver.find_element(By.CSS_SELECTOR, "main")
            last_height = driver.execute_script("return arguments[0].scrollHeight", main_content)
            
            scroll_attempts = 0
            max_scrolls = 1000  # Prevent infinite loops
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", main_content)
                time.sleep(2)
                
                # Try to find club elements
                try:
                    club_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='club'], .club-item, [data-testid*='club']")
                    
                    # Process new clubs
                    current_count = len(self.clubs)
                    for element in club_elements[current_count:]:
                        club_data = self.extract_club_data(element)
                        if club_data and club_data not in self.clubs:
                            self.clubs.append(club_data)
                            
                    self.logger.info(f"📊 Found {len(self.clubs)} total clubs...")
                    
                    # Save progress every 100 clubs
                    if len(self.clubs) % 100 == 0:
                        self.save_progress()
                        
                except Exception as e:
                    self.logger.warning(f"Error finding club elements: {e}")
                
                # Check if we've reached the bottom
                new_height = driver.execute_script("return arguments[0].scrollHeight", main_content)
                if new_height == last_height:
                    self.logger.info("Reached bottom of page")
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            
        finally:
            driver.quit()
            self.save_progress()
            
        return self.clubs
        
    def save_to_csv(self, filename='data/1-veo-scraper/veo_clubs.csv'):
        """Save clubs to CSV file"""
        if self.clubs:
            df = pd.DataFrame(self.clubs)
            df = df.drop_duplicates(subset=['Club Name'])  # Remove duplicates
            df.to_csv(filename, index=False)
            self.logger.info(f"✅ STAGE 1 COMPLETE: Saved {len(df)} clubs to {filename}")
            return filename
        else:
            self.logger.warning("No clubs to save")
            return None

def main():
    """Run the VEO scraper"""
    print("🎯 STAGE 1: VEO CLUB SCRAPER")
    print("=" * 40)
    print("This will scrape ALL clubs from VEO directory")
    print("Output: data/1-veo-scraper/veo_clubs.csv")
    print()
    
    scraper = VeoScraper()
    clubs = scraper.scrape_clubs()
    
    if clubs:
        output_file = scraper.save_to_csv()
        print(f"\n✅ STAGE 1 COMPLETE!")
        print(f"📊 Total clubs found: {len(clubs)}")
        print(f"💾 Saved to: {output_file}")
        print(f"➡️  Next: Run '2-location-sorter.py'")
    else:
        print("❌ No clubs found")

if __name__ == "__main__":
    main()