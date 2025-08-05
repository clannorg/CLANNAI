from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import json
from pathlib import Path

class InfiniteScrollScraper:
    def __init__(self):
        self.clubs = []
        self.progress_file = Path('data/infinite_scroll_progress.json')
        self.load_progress()
        
    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
                self.clubs = data.get('clubs', [])
        else:
            self.clubs = []
            
    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump({'clubs': self.clubs}, f)
            
    def setup_driver(self):
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-data-dir=/tmp/infinite-{random.randint(1000,9999)}')
        
        driver = webdriver.Chrome(options=options)
        return driver
        
    def trigger_infinite_scroll(self, driver):
        """Properly trigger infinite scroll by simulating user behavior"""
        print("Starting infinite scroll detection...")
        
        # Wait for page to load
        time.sleep(5)
        
        last_club_count = 0
        no_new_clubs_count = 0
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # Get current clubs
            current_clubs = self.extract_clubs_from_page(driver)
            
            if len(current_clubs) > last_club_count:
                print(f"Found {len(current_clubs)} clubs (was {last_club_count})")
                last_club_count = len(current_clubs)
                no_new_clubs_count = 0
            else:
                no_new_clubs_count += 1
                print(f"No new clubs found. Attempt {no_new_clubs_count}/10")
            
            # Try different scroll methods
            self.scroll_methods(driver)
            
            # Wait for content to load
            time.sleep(random.uniform(1, 2))
            
            # Check if we've stopped finding new clubs
            if no_new_clubs_count >= 10:
                print("No new clubs found for 10 attempts. Stopping.")
                break
                
            # Save progress every 10 attempts
            if attempt % 10 == 0:
                self.save_progress()
                
    def scroll_methods(self, driver):
        """Try different methods to trigger infinite scroll"""
        methods = [
            self.scroll_to_bottom,
            self.scroll_by_window,
            self.scroll_by_element,
            self.scroll_by_javascript
        ]
        
        for method in methods:
            try:
                method(driver)
                time.sleep(0.5)
            except Exception as e:
                print(f"Scroll method failed: {e}")
                continue
                
    def scroll_to_bottom(self, driver):
        """Scroll to bottom of page"""
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
    def scroll_by_window(self, driver):
        """Scroll by window height"""
        current_height = driver.execute_script("return window.pageYOffset")
        window_height = driver.execute_script("return window.innerHeight")
        driver.execute_script(f"window.scrollTo(0, {current_height + window_height});")
        
    def scroll_by_element(self, driver):
        """Scroll by finding scrollable elements"""
        scrollable_elements = driver.find_elements(By.CSS_SELECTOR, "[style*='overflow']")
        for element in scrollable_elements:
            try:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
            except:
                continue
                
    def scroll_by_javascript(self, driver):
        """Trigger scroll events via JavaScript"""
        driver.execute_script("""
            // Trigger scroll event
            window.dispatchEvent(new Event('scroll'));
            
            // Trigger wheel event
            window.dispatchEvent(new WheelEvent('wheel', {
                deltaY: 100
            }));
            
            // Trigger touch events
            window.dispatchEvent(new TouchEvent('touchmove', {
                touches: [new Touch({identifier: 1, target: document.body})]
            }));
        """)
        
    def extract_clubs_from_page(self, driver):
        """Extract all clubs from current page content"""
        try:
            # Get all text content
            content = driver.find_element(By.TAG_NAME, "body").text
            lines = content.split('\n')
            
            clubs_found = []
            
            # Process lines to find club data
            for i in range(len(lines)):
                line = lines[i].strip()
                
                # Look for patterns like "X recordings, Y teams"
                if 'recordings' in line.lower() and 'teams' in line.lower():
                    # Get club name from previous line
                    club_name = lines[i-1].strip() if i > 0 else "Unknown"
                    
                    # Skip navigation elements and special characters
                    if club_name in ['Login', 'Clubs', 'Search', 'Filter', '>', 'µ', '_', '__', '-', '--']:
                        continue
                        
                    # Parse recordings and teams
                    try:
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
                                'Activity_Score': recordings + (teams * 10)
                            }
                            
                            # Check if we already have this club
                            existing_clubs = [c['Club Name'] for c in self.clubs]
                            if club_name not in existing_clubs and club_name != "Unknown":
                                self.clubs.append(club_data)
                                clubs_found.append(club_data)
                                print(f"Added: {club_name} - {recordings} recordings, {teams} teams")
                                
                                # Save to file immediately
                                self.save_clubs_to_file()
                                
                    except (ValueError, IndexError) as e:
                        continue
                        
            return self.clubs
            
        except Exception as e:
            print(f"Error extracting clubs: {e}")
            return self.clubs
            
    def save_clubs_to_file(self):
        """Save clubs to CSV file immediately"""
        if self.clubs:
            df = pd.DataFrame(self.clubs)
            df = df.sort_values(['Activity_Score', 'Teams', 'Recordings'], ascending=[False, False, False])
            df.to_csv('data/veo_clubs_infinite.csv', index=False)
            
    def scrape_all_clubs(self):
        """Main scraping function"""
        driver = self.setup_driver()
        
        try:
            print("Starting infinite scroll Veo scraper...")
            print(f"Already have {len(self.clubs)} clubs from previous runs")
            start_time = time.time()
            
            # Navigate to Veo clubs page
            driver.get("https://app.veo.co/all-clubs/")
            
            # Trigger infinite scroll
            self.trigger_infinite_scroll(driver)
            
            # Final save
            if self.clubs:
                self.save_clubs_to_file()
                
                total_time = time.time() - start_time
                print(f"\n=== SCRAPING COMPLETE ===")
                print(f"Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
                print(f"Total clubs found: {len(self.clubs)}")
                print(f"Clubs per minute: {len(self.clubs)/(total_time/60):.1f}")
                
                # Show top clubs
                df = pd.DataFrame(self.clubs)
                if not df.empty:
                    print(f"\nTop 5 most active clubs:")
                    print(df.head().to_string())
                    
        except Exception as e:
            print(f"Scraping failed: {e}")
        finally:
            driver.quit()

if __name__ == "__main__":
    scraper = InfiniteScrollScraper()
    scraper.scrape_all_clubs() 