#!/usr/bin/env python3
"""
Improved VEO Scraper - Gets actual club names and all data
Fixed to extract real club names instead of generic placeholders
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import re

def setup_driver():
    """Setup Chrome driver for scraping"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    return webdriver.Chrome(options=options)

def extract_club_data(element):
    """Extract club name, recordings, and teams from a club element"""
    try:
        text = element.text.strip()
        if not text:
            return None
            
        lines = text.split('\n')
        club_name = None
        recordings = 0
        teams = 0
        
        # Look for the club name (usually first non-empty line)
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['recordings', 'teams', 'follow']):
                if not re.match(r'^\d+$', line):  # Skip pure numbers
                    club_name = line
                    break
        
        # Look for recordings and teams info
        for line in lines:
            if 'recording' in line.lower() and 'team' in line.lower():
                # Format: "X recordings, Y teams"
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 2:
                    recordings = int(numbers[0])
                    teams = int(numbers[1])
                    break
            elif 'recording' in line.lower():
                numbers = re.findall(r'\d+', line)
                if numbers:
                    recordings = int(numbers[0])
            elif 'team' in line.lower():
                numbers = re.findall(r'\d+', line)
                if numbers:
                    teams = int(numbers[0])
        
        if club_name:
            return {
                'Club_Name': club_name,
                'Recordings': recordings,
                'Teams': teams
            }
    except Exception as e:
        print(f"Error extracting club data: {e}")
    
    return None

def improved_scrape():
    """Improved scraper to get real club names and data"""
    driver = setup_driver()
    clubs = []
    
    try:
        print("🚀 Improved VEO scraper starting...")
        print("Getting real club names this time!")
        
        # Navigate to VEO clubs page
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(5)
        
        # Wait for content to load
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            print("Page load timeout, continuing anyway...")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        stuck_count = 0
        scroll_attempts = 0
        max_clubs = 100  # Only get the first 100 clubs for testing
        
        while len(clubs) < max_clubs and stuck_count < 30:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(0.8, 1.5))
            
            # Try different selectors to find club elements
            selectors = [
                'div[class*="club"]',
                'div[class*="card"]', 
                'a[href*="club"]',
                'div[data-testid*="club"]',
                'div[class*="item"]'
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        club_data = extract_club_data(element)
                        if club_data:
                            clubs.append(club_data)
                            print(f"Found: {club_data['Club_Name']} ({club_data['Recordings']} recordings, {club_data['Teams']} teams)")
                            if len(clubs) % 10 == 0:
                                df = pd.DataFrame(clubs)
                                df.to_csv('../data/raw/improved_clubs.csv', index=False)
                                print(f"💾 Saved {len(clubs)} clubs to file")
                            if len(clubs) >= max_clubs:
                                break
                except Exception as e:
                    continue
            if len(clubs) >= max_clubs:
                break
            # Also try the original approach for backup
            try:
                all_divs = driver.find_elements(By.TAG_NAME, "div")
                for div in all_divs:
                    club_data = extract_club_data(div)
                    if club_data:
                        clubs.append(club_data)
                        print(f"Found: {club_data['Club_Name']} ({club_data['Recordings']} recordings, {club_data['Teams']} teams)")
                        if len(clubs) % 10 == 0:
                            df = pd.DataFrame(clubs)
                            df.to_csv('../data/raw/improved_clubs.csv', index=False)
                            print(f"💾 Saved {len(clubs)} clubs to file")
                        if len(clubs) >= max_clubs:
                            break
            except:
                pass
            if len(clubs) >= max_clubs:
                break
            # Check if page height changed
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                stuck_count += 1
                print(f"Page stuck at {new_height}px (attempt {stuck_count}/30) - Found {len(clubs)} clubs so far")
            else:
                stuck_count = 0
                last_height = new_height
            
            scroll_attempts += 1
        # Final save
        if clubs:
            df = pd.DataFrame(clubs)
            df.to_csv('../data/raw/improved_clubs.csv', index=False)
            print(f"\n✅ FINAL RESULTS:")
            print(f"📊 Total clubs found: {len(clubs)}")
            print(f"📁 Saved to: ../data/raw/improved_clubs.csv")
            print(f"\n🔥 Top clubs by recordings:")
            df_sorted = df.sort_values('Recordings', ascending=False)
            print(df_sorted.head(10).to_string(index=False))
        else:
            print("❌ No clubs found - might need to adjust selectors")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
        print("🏁 Scraper finished")

if __name__ == "__main__":
    improved_scrape()