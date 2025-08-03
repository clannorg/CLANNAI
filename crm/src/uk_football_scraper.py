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
import requests
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse
import re

class UKFootballClubScraper:
    def __init__(self):
        self.setup_logging()
        self.clubs = []
        self.progress_file = Path('data/uk_football_progress.json')
        self.load_progress()
        
        # Target sources for comprehensive UK club coverage
        self.sources = {
            'fa_fulltime': {
                'name': 'FA Full-Time',
                'base_url': 'https://fulltime.thefa.com',
                'search_url': 'https://fulltime.thefa.com/clubs.html',
                'method': 'selenium'
            },
            'scottish_fa': {
                'name': 'Scottish FA',
                'base_url': 'https://www.scottishfa.co.uk',
                'search_url': 'https://www.scottishfa.co.uk/clubs/',
                'method': 'selenium'
            },
            'non_league': {
                'name': 'Non-League Directory',
                'base_url': 'https://www.nonleaguedirectory.co.uk',
                'search_url': 'https://www.nonleaguedirectory.co.uk/clubs/',
                'method': 'selenium'
            },
            'pitchero': {
                'name': 'Pitchero Club Directory',
                'base_url': 'https://www.pitchero.com',
                'search_url': 'https://www.pitchero.com/clubs',
                'method': 'selenium'
            }
        }
        
    def setup_logging(self):
        logging.basicConfig(
            filename='data/uk_football_scraper.log',
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
            
    def setup_driver(self):
        """Setup Chrome driver with optimal settings for scraping"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def scrape_fa_fulltime(self):
        """Scrape FA Full-Time club directory"""
        if 'fa_fulltime' in self.processed_sources:
            print("FA Full-Time already processed, skipping...")
            return
            
        print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Scraping FA Full-Time club directory...")
        driver = self.setup_driver()
        
        try:
            # Strategy 1: Try the club search page
            driver.get('https://fulltime.thefa.com/clubs.html')
            time.sleep(3)
            
            # Look for club listings
            club_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/club/"]')
            
            for element in club_elements:
                try:
                    club_name = element.text.strip()
                    club_url = element.get_attribute('href')
                    
                    if club_name and len(club_name) > 2:
                        self.clubs.append({
                            'name': club_name,
                            'source': 'FA Full-Time',
                            'url': club_url,
                            'country': 'England',
                            'type': 'affiliated'
                        })
                        
                except Exception as e:
                    continue
                    
            # Strategy 2: Try league-based search
            league_urls = [
                'https://fulltime.thefa.com/league.html?leagueId=',
                'https://fulltime.thefa.com/fixtures.html'
            ]
            
            for url in league_urls:
                try:
                    driver.get(url)
                    time.sleep(2)
                    
                    # Look for team/club names in fixtures and league tables
                    team_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="team"], a[href*="club"]')
                    
                    for link in team_links:
                        try:
                            team_name = link.text.strip()
                            if team_name and len(team_name) > 2 and 'FC' in team_name or 'United' in team_name or 'Town' in team_name:
                                self.clubs.append({
                                    'name': team_name,
                                    'source': 'FA Full-Time',
                                    'url': link.get_attribute('href'),
                                    'country': 'England',
                                    'type': 'league_team'
                                })
                        except:
                            continue
                            
                except Exception as e:
                    logging.error(f"Error scraping FA Full-Time league page {url}: {e}")
                    continue
                    
            self.processed_sources.append('fa_fulltime')
            print(f"✅ FA Full-Time complete: {len(self.clubs)} total clubs")
            
        except Exception as e:
            logging.error(f"Error scraping FA Full-Time: {e}")
            
        finally:
            driver.quit()

    def scrape_scottish_fa(self):
        """Scrape Scottish FA club directory"""
        if 'scottish_fa' in self.processed_sources:
            print("Scottish FA already processed, skipping...")
            return
            
        print("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scraping Scottish FA club directory...")
        driver = self.setup_driver()
        
        try:
            # Try main clubs page
            driver.get('https://www.scottishfa.co.uk/clubs/')
            time.sleep(3)
            
            # Look for club listings
            club_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="club"], .club-name, .team-name')
            
            for link in club_links:
                try:
                    club_name = link.text.strip()
                    club_url = link.get_attribute('href') if link.get_attribute('href') else ''
                    
                    if club_name and len(club_name) > 2:
                        self.clubs.append({
                            'name': club_name,
                            'source': 'Scottish FA',
                            'url': club_url,
                            'country': 'Scotland',
                            'type': 'affiliated'
                        })
                        
                except Exception as e:
                    continue
                    
            # Try league/division pages
            division_selectors = [
                'a[href*="premiership"]',
                'a[href*="championship"]',
                'a[href*="league"]',
                'a[href*="division"]'
            ]
            
            for selector in division_selectors:
                try:
                    division_links = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for div_link in division_links[:5]:  # Limit to avoid infinite loops
                        try:
                            driver.get(div_link.get_attribute('href'))
                            time.sleep(2)
                            
                            team_elements = driver.find_elements(By.CSS_SELECTOR, '.team, .club, a[href*="team"]')
                            
                            for team in team_elements:
                                team_name = team.text.strip()
                                if team_name and len(team_name) > 2:
                                    self.clubs.append({
                                        'name': team_name,
                                        'source': 'Scottish FA',
                                        'url': team.get_attribute('href') or '',
                                        'country': 'Scotland',
                                        'type': 'league_team'
                                    })
                                    
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
                    
            self.processed_sources.append('scottish_fa')
            print(f"✅ Scottish FA complete: {len(self.clubs)} total clubs")
            
        except Exception as e:
            logging.error(f"Error scraping Scottish FA: {e}")
            
        finally:
            driver.quit()

    def scrape_non_league_directory(self):
        """Scrape Non-League Directory for grassroots clubs"""
        if 'non_league' in self.processed_sources:
            print("Non-League Directory already processed, skipping...")
            return
            
        print("⚽ Scraping Non-League Directory...")
        driver = self.setup_driver()
        
        try:
            driver.get('https://www.nonleaguedirectory.co.uk/clubs/')
            time.sleep(3)
            
            # Handle cookie consent if present
            try:
                cookie_button = driver.find_element(By.CSS_SELECTOR, '[data-dismiss="cookie"], .cookie-accept, #accept-cookies')
                cookie_button.click()
                time.sleep(1)
            except:
                pass
                
            # Look for club listings
            club_selectors = [
                'a[href*="/club/"]',
                '.club-name a',
                '.team-name a',
                'a.club-link'
            ]
            
            for selector in club_selectors:
                try:
                    club_links = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for link in club_links:
                        try:
                            club_name = link.text.strip()
                            club_url = link.get_attribute('href')
                            
                            if club_name and len(club_name) > 2:
                                self.clubs.append({
                                    'name': club_name,
                                    'source': 'Non-League Directory',
                                    'url': club_url,
                                    'country': 'England',
                                    'type': 'non_league'
                                })
                                
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
                    
            self.processed_sources.append('non_league')
            print(f"✅ Non-League Directory complete: {len(self.clubs)} total clubs")
            
        except Exception as e:
            logging.error(f"Error scraping Non-League Directory: {e}")
            
        finally:
            driver.quit()

    def scrape_pitchero_clubs(self):
        """Scrape Pitchero club directory for grassroots clubs"""
        if 'pitchero' in self.processed_sources:
            print("Pitchero already processed, skipping...")
            return
            
        print("🌱 Scraping Pitchero grassroots clubs...")
        driver = self.setup_driver()
        
        try:
            driver.get('https://www.pitchero.com/clubs')
            time.sleep(3)
            
            # Handle cookie consent
            try:
                cookie_button = driver.find_element(By.CSS_SELECTOR, '.cookie-consent-accept, #accept-cookies')
                cookie_button.click()
                time.sleep(1)
            except:
                pass
                
            # Look for club listings
            club_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/clubs/"], .club-tile a, .club-name a')
            
            for element in club_elements:
                try:
                    club_name = element.text.strip()
                    club_url = element.get_attribute('href')
                    
                    if club_name and len(club_name) > 2 and ('FC' in club_name or 'United' in club_name or 'Athletic' in club_name or 'Town' in club_name):
                        self.clubs.append({
                            'name': club_name,
                            'source': 'Pitchero',
                            'url': club_url,
                            'country': 'UK',
                            'type': 'grassroots'
                        })
                        
                except Exception as e:
                    continue
                    
            self.processed_sources.append('pitchero')
            print(f"✅ Pitchero complete: {len(self.clubs)} total clubs")
            
        except Exception as e:
            logging.error(f"Error scraping Pitchero: {e}")
            
        finally:
            driver.quit()

    def deduplicate_clubs(self):
        """Remove duplicate clubs based on name similarity"""
        print("🔄 Deduplicating clubs...")
        
        unique_clubs = []
        seen_names = set()
        
        for club in self.clubs:
            # Normalize name for comparison
            normalized_name = club['name'].lower().strip()
            normalized_name = re.sub(r'\s+', ' ', normalized_name)
            normalized_name = re.sub(r'[^\w\s]', '', normalized_name)
            
            if normalized_name not in seen_names and len(normalized_name) > 2:
                seen_names.add(normalized_name)
                unique_clubs.append(club)
                
        removed_count = len(self.clubs) - len(unique_clubs)
        self.clubs = unique_clubs
        
        print(f"✅ Removed {removed_count} duplicates. {len(self.clubs)} unique clubs remaining.")

    def save_results(self):
        """Save scraped clubs to CSV"""
        if not self.clubs:
            print("❌ No clubs found to save")
            return
            
        df = pd.DataFrame(self.clubs)
        
        # Add metadata
        df['scraped_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        df['has_website'] = df['url'].apply(lambda x: bool(x and x != ''))
        
        # Save comprehensive results
        output_file = 'data/uk_football_clubs.csv'
        df.to_csv(output_file, index=False)
        
        # Create summary statistics
        summary = {
            'total_clubs': len(df),
            'by_country': df['country'].value_counts().to_dict(),
            'by_source': df['source'].value_counts().to_dict(),
            'by_type': df['type'].value_counts().to_dict(),
            'clubs_with_websites': df['has_website'].sum()
        }
        
        # Save summary
        with open('data/uk_football_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"💾 Saved {len(df)} UK football clubs to {output_file}")
        print(f"📊 Summary saved to data/uk_football_summary.json")
        
        # Print summary
        print("\n📈 **SCRAPING SUMMARY**")
        print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 English clubs: {summary['by_country'].get('England', 0)}")
        print(f"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scottish clubs: {summary['by_country'].get('Scotland', 0)}")
        print(f"🇬🇧 UK clubs: {summary['by_country'].get('UK', 0)}")
        print(f"🌐 Clubs with websites: {summary['clubs_with_websites']}")
        
        return output_file

    def run_full_scrape(self):
        """Run the complete UK football club scraping process"""
        print("🚀 Starting comprehensive UK football club scraping...")
        print("This will collect clubs from multiple official sources\n")
        
        # Scrape all sources
        self.scrape_fa_fulltime()
        self.save_progress()
        
        self.scrape_scottish_fa()
        self.save_progress()
        
        self.scrape_non_league_directory()
        self.save_progress()
        
        self.scrape_pitchero_clubs()
        self.save_progress()
        
        # Clean up and save final results
        self.deduplicate_clubs()
        output_file = self.save_results()
        
        print(f"\n🎉 **SCRAPING COMPLETE!**")
        print(f"📁 Results saved to: {output_file}")
        print(f"📊 Total unique clubs: {len(self.clubs)}")
        
        return output_file

if __name__ == "__main__":
    scraper = UKFootballClubScraper()
    scraper.run_full_scrape()