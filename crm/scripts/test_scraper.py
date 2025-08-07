#!/usr/bin/env python3
"""
Quick Test Scraper - Just get 100 clubs and stop
Avoid premature optimization, just test the basic concept
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random

def setup_driver():
    """Setup Chrome driver for scraping"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def quick_test_scrape():
    """Quick test scrape - just get 100 clubs"""
    driver = setup_driver()
    clubs = []
    
    try:
        print("🚀 Quick test scraper starting...")
        print("Target: 100 clubs, then stop")
        
        # Navigate to VEO clubs page
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(3)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        stuck_count = 0
        
        while len(clubs) < 100 and stuck_count < 20:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(0.5, 1.0))
            
            # Extract clubs from current view
            try:
                elements = driver.find_elements(By.TAG_NAME, "div")
                for element in elements:
                    text = element.text.strip()
                    if text and 'recordings' in text.lower() and 'teams' in text.lower():
                        lines = text.split('\n')
                        for line in lines:
                            if 'recordings' in line.lower() and 'teams' in line.lower():
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    club_name = f"Club_{len(clubs)+1}"  # Simple naming for test
                                    recordings = ''.join(filter(str.isdigit, parts[0]))
                                    teams = ''.join(filter(str.isdigit, parts[1]))
                                    
                                    if recordings and teams:
                                        club_data = {
                                            'Club_Name': club_name,
                                            'Recordings': int(recordings),
                                            'Teams': int(teams)
                                        }
                                        clubs.append(club_data)
                                        print(f"Found club {len(clubs)}: {recordings} recordings, {teams} teams")
            except Exception as e:
                print(f"Error extracting: {e}")
            
            # Check if page height changed
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                stuck_count += 1
                print(f"Height stuck at {new_height}px (attempt {stuck_count}/20)")
            else:
                stuck_count = 0
                last_height = new_height
            
            # Save progress every 10 clubs
            if len(clubs) % 10 == 0 and len(clubs) > 0:
                df = pd.DataFrame(clubs)
                df.to_csv('../data/raw/test_clubs.csv', index=False)
                print(f"💾 Saved {len(clubs)} clubs to file")
        
        # Final save
        if clubs:
            df = pd.DataFrame(clubs)
            df.to_csv('../data/raw/test_clubs.csv', index=False)
            print(f"✅ Final save: {len(clubs)} clubs")
            print(f"📊 Sample data:")
            print(df.head())
        else:
            print("❌ No clubs found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        print("🏁 Test scraper finished")

if __name__ == "__main__":
    quick_test_scrape()