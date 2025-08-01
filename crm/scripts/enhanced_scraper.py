from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
import json
from pathlib import Path
import logging

class EnhancedVeoScraper:
    def __init__(self):
        self.setup_logging()
        self.clubs = []
        self.progress_file = Path('logs/enhanced_scraper_progress.json')
        self.load_progress()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='logs/enhanced_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self.clubs = data.get('clubs', [])
                self.last_count = data.get('last_count', 0)
        else:
            self.last_count = 0
            
    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump({
                'clubs': self.clubs,
                'last_count': len(self.clubs)
            }, f)
            
    def setup_driver(self):
        """Setup Chrome driver with optimal settings for scraping"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument(f'--user-data-dir=/tmp/chrome-scraper-{random.randint(1000,9999)}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
        
    def scroll_strategies(self, driver):
        """Multiple scrolling strategies to ensure we get all content"""
        strategies = [
            self.scroll_by_height,
            self.scroll_by_pixels,
            self.scroll_by_elements,
            self.scroll_by_time
        ]
        
        for i, strategy in enumerate(strategies):
            print(f"Trying strategy {i+1}/{len(strategies)}...")
            clubs_before = len(self.clubs)
            strategy(driver)
            clubs_after = len(self.clubs)
            
            if clubs_after > clubs_before:
                print(f"Strategy {i+1} found {clubs_after - clubs_before} new clubs")
            else:
                print(f"Strategy {i+1} found no new clubs")
                
            # Save progress after each strategy
            self.save_progress()
            time.sleep(random.uniform(2, 5))
            
    def scroll_by_height(self, driver):
        """Scroll by checking height changes"""
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 1000  # Much longer - let it run all night
        start_time = time.time()
        
        while scroll_attempts < max_attempts:
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(0.3, 0.8))
            
            # Check for new content
            self.extract_clubs_from_page(driver)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_height = new_height
                
            elapsed_time = time.time() - start_time
            print(f"Time: {elapsed_time:.1f}s, Height: {new_height}px, Clubs found: {len(self.clubs)}")
            
            # Save progress every 50 attempts
            if scroll_attempts % 50 == 0:
                self.save_progress()
                print(f"Progress saved - {len(self.clubs)} clubs so far")
            
    def scroll_by_pixels(self, driver):
        """Scroll in smaller increments"""
        current_position = 0
        scroll_increment = 1000
        max_scrolls = 2000  # Much longer - let it run all night
        start_time = time.time()
        
        for i in range(max_scrolls):
            current_position += scroll_increment
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.2, 0.5))
            
            self.extract_clubs_from_page(driver)
            elapsed_time = time.time() - start_time
            print(f"Time: {elapsed_time:.1f}s, Scroll position: {current_position}px, Clubs: {len(self.clubs)}")
            
    def scroll_by_elements(self, driver):
        """Scroll by finding and clicking on elements"""
        try:
            # Look for any clickable elements that might load more content
            elements = driver.find_elements(By.TAG_NAME, "button")
            for element in elements:
                if any(keyword in element.text.lower() for keyword in ['load', 'more', 'show', 'next']):
                    try:
                        element.click()
                        time.sleep(random.uniform(2, 4))
                        self.extract_clubs_from_page(driver)
                    except:
                        continue
        except:
            pass
            
    def scroll_by_time(self, driver):
        """Scroll continuously for a set time period"""
        start_time = time.time()
        duration = 36000  # 10 hours - let it run all night
        
        while time.time() - start_time < duration:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(random.uniform(1, 2))
            self.extract_clubs_from_page(driver)
            
            elapsed_time = time.time() - start_time
            if len(self.clubs) % 5 == 0:  # Print every 5 clubs
                print(f"Time: {elapsed_time:.1f}s, Clubs: {len(self.clubs)}")
                self.save_progress()  # Save more frequently
                
    def extract_clubs_from_page(self, driver):
        """Extract clubs from current page content"""
        try:
            # Get all text content
            content = driver.find_element(By.TAG_NAME, "body").text
            lines = content.split('\n')
            
            new_clubs_found = 0
            
            # Process lines to find club data
            for i in range(len(lines)):
                line = lines[i].strip()
                
                # Look for patterns like "X recordings, Y teams" (separate lines)
                if 'recordings' in line.lower() and 'teams' in line.lower():
                    # Get club name from previous line
                    club_name = lines[i-1].strip() if i > 0 else "Unknown"
                    
                    # Skip navigation elements and special characters
                    if club_name in ['Login', 'Clubs', 'Search', 'Filter', '>', 'µ', '_', '__']:
                        continue
                        
                    # Parse recordings and teams
                    try:
                        # Extract numbers from "X recordings, Y teams"
                        recordings_match = None
                        teams_match = None
                        
                        # Look for "X recordings"
                        if 'recordings' in line.lower():
                            parts = line.split(',')
                            if len(parts) >= 2:
                                recordings_text = parts[0].strip()
                                teams_text = parts[1].strip()
                                
                                # Extract numbers
                                recordings = int(''.join(filter(str.isdigit, recordings_text)))
                                teams = int(''.join(filter(str.isdigit, teams_text)))
                                
                                # Create club entry
                                club_data = {
                                    'Club Name': club_name,
                                    'Recordings': recordings,
                                    'Teams': teams,
                                    'Activity_Score': recordings + (teams * 10)  # Simple scoring
                                }
                                
                                # Check if we already have this club
                                existing_clubs = [c['Club Name'] for c in self.clubs]
                                if club_name not in existing_clubs and club_name != "Unknown":
                                    self.clubs.append(club_data)
                                    new_clubs_found += 1
                                    logging.info(f"Added club: {club_name} - {recordings} recordings, {teams} teams")
                                    
                                    # Save to file immediately
                                    self.save_clubs_to_file()
                                    
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Failed to parse line: {line} - {e}")
                        continue
            
            if new_clubs_found > 0:
                print(f"Found {new_clubs_found} new clubs!")
                        
        except Exception as e:
            logging.error(f"Error extracting clubs: {e}")
            
    def save_clubs_to_file(self):
        """Save clubs to CSV file immediately"""
        if self.clubs:
            df = pd.DataFrame(self.clubs)
            df = df.sort_values(['Activity_Score', 'Teams', 'Recordings'], ascending=[False, False, False])
            df.to_csv('data/raw/all_veo_clubs.csv', index=False)
            print(f"Saved {len(self.clubs)} clubs to file")
            
    def scrape_all_clubs(self):
        """Main scraping function"""
        driver = self.setup_driver()
        
        try:
            print("Starting enhanced Veo scraper (Overnight Mode)...")
            print(f"Already have {len(self.clubs)} clubs from previous runs")
            print("This will run for hours - you can interrupt anytime safely!")
            overall_start_time = time.time()
            
            # Navigate to Veo clubs page
            driver.get("https://app.veo.co/all-clubs/")
            time.sleep(5)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                print("Page took too long to load")
                
            # Try multiple scrolling strategies
            self.scroll_strategies(driver)
            
            # Final extraction
            self.extract_clubs_from_page(driver)
            
            # Final save (in case any clubs weren't saved yet)
            if self.clubs:
                self.save_clubs_to_file()
                
                total_time = time.time() - overall_start_time
                print(f"\n=== SCRAPING COMPLETE ===")
                print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
                print(f"Total clubs found: {len(self.clubs)}")
                print(f"Clubs per minute: {len(self.clubs)/(total_time/60):.1f}")
                print(f"Total recordings: {df['Recordings'].sum():,}")
                print(f"Total teams: {df['Teams'].sum():,}")
                print(f"Average recordings per club: {df['Recordings'].mean():.1f}")
                print(f"Clubs with no teams: {len(df[df['Teams'] == 0])}")
                print(f"Top 5 most active clubs:")
                print(df.head().to_string())
                
                # Save progress
                self.save_progress()
                
        except Exception as e:
            logging.error(f"Scraping failed: {e}")
            print(f"Scraping failed: {e}")
        finally:
            driver.quit()
            
    def resume_scraping(self):
        """Resume scraping from where we left off"""
        print(f"Resuming with {len(self.clubs)} existing clubs...")
        self.scrape_all_clubs()

if __name__ == "__main__":
    scraper = EnhancedVeoScraper()
    scraper.scrape_all_clubs() 