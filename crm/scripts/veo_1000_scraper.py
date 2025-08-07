#!/usr/bin/env python3
"""
VEO 1000 Club Scraper - Aggressive scraping to get 1000 real clubs with all info
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
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    return webdriver.Chrome(options=options)

def extract_club_info(text_content):
    """Extract club info from text content"""
    if not text_content or len(text_content.strip()) < 2:
        return None
    
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    
    # Skip obviously bad data
    bad_patterns = ['login', 'help', 'survey', 'future', 'feedback', 'take', 'start', 'explore']
    if any(bad in text_content.lower() for bad in bad_patterns):
        return None
    
    club_name = None
    recordings = 0
    teams = 0
    
    # Try to find club name and stats
    for i, line in enumerate(lines):
        # Look for recording/team patterns
        if 'recording' in line.lower() and 'team' in line.lower():
            # "X recordings, Y teams" or "X recording, Y team"
            numbers = re.findall(r'(\d+)', line)
            if len(numbers) >= 2:
                recordings = int(numbers[0])
                teams = int(numbers[1])
                # Club name might be in previous lines
                if i > 0:
                    potential_name = lines[i-1]
                    if len(potential_name) > 1 and not re.match(r'^[\d\s\-_\.]+$', potential_name):
                        club_name = potential_name
                break
        elif 'recording' in line.lower():
            numbers = re.findall(r'(\d+)', line)
            if numbers:
                recordings = int(numbers[0])
        elif 'team' in line.lower():
            numbers = re.findall(r'(\d+)', line)
            if numbers:
                teams = int(numbers[0])
    
    # If no club name found yet, try first substantial line
    if not club_name:
        for line in lines:
            if (len(line) > 2 and 
                not re.match(r'^[\d\s\-_\.><µ´]+$', line) and
                'recording' not in line.lower() and
                'team' not in line.lower() and
                line not in ['>', '<', '-', '--', '---', '_', '__', '___']):
                club_name = line
                break
    
    if club_name and len(club_name) > 1:
        return {
            'Club_Name': club_name.strip(),
            'Recordings': recordings,
            'Teams': teams,
            'Raw_Text': text_content[:100]  # Keep sample for debugging
        }
    
    return None

def aggressive_scroll_and_scrape():
    """Aggressively scroll and scrape 1000 clubs"""
    driver = setup_driver()
    clubs = []
    
    try:
        print("🚀 VEO 1000 Club Scraper starting...")
        
        # Navigate to VEO clubs page
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(8)  # Longer wait for page load
        
        print("Page loaded, starting to scroll and extract...")
        
        last_height = 0
        stuck_count = 0
        max_stuck = 50  # Allow more stuck attempts
        scroll_count = 0
        
        while len(clubs) < 1000 and stuck_count < max_stuck:
            # More aggressive scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.0, 2.0))  # Longer waits
            
            # Try multiple approaches to find elements
            all_elements = []
            
            # Try various selectors
            selectors = [
                '*[class*="club"]',
                '*[class*="card"]',
                '*[class*="item"]',
                'div',
                'a',
                'span',
                'li'
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    all_elements.extend(elements)
                except:
                    continue
            
            # Process all elements
            clubs_found_this_round = 0
            for element in all_elements:
                try:
                    text = element.text.strip()
                    if text:
                        club_info = extract_club_info(text)
                        if club_info:
                            # Check for exact duplicates
                            is_duplicate = False
                            for existing in clubs:
                                if (existing['Club_Name'] == club_info['Club_Name'] and 
                                    existing['Recordings'] == club_info['Recordings'] and
                                    existing['Teams'] == club_info['Teams']):
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate:
                                clubs.append(club_info)
                                clubs_found_this_round += 1
                                print(f"#{len(clubs)}: {club_info['Club_Name']} ({club_info['Recordings']} rec, {club_info['Teams']} teams)")
                                
                                # Save every 100 clubs
                                if len(clubs) % 100 == 0:
                                    df = pd.DataFrame(clubs)
                                    df.to_csv('../data/raw/veo_1000_clubs.csv', index=False)
                                    print(f"💾 Saved {len(clubs)} clubs to file")
                                
                                if len(clubs) >= 1000:
                                    break
                except:
                    continue
            
            # Check scroll progress
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                stuck_count += 1
                if clubs_found_this_round == 0:
                    print(f"🔄 Scroll stuck {stuck_count}/{max_stuck}, found 0 new clubs")
                else:
                    print(f"🔄 Scroll stuck {stuck_count}/{max_stuck}, but found {clubs_found_this_round} clubs")
                    stuck_count = max(0, stuck_count - 5)  # Reset counter if we found clubs
            else:
                stuck_count = 0
                last_height = new_height
                print(f"📜 Scrolled to {new_height}px, found {clubs_found_this_round} clubs this round")
            
            scroll_count += 1
            if scroll_count % 10 == 0:
                print(f"📊 Status: {len(clubs)} clubs after {scroll_count} scrolls")
        
        # Final save
        if clubs:
            df = pd.DataFrame(clubs)
            df.to_csv('../data/raw/veo_1000_clubs.csv', index=False)
            
            print(f"\n✅ SCRAPING COMPLETE!")
            print(f"📊 Total clubs: {len(clubs)}")
            print(f"📜 Total scrolls: {scroll_count}")
            print(f"📁 Saved to: ../data/raw/veo_1000_clubs.csv")
            
            # Show stats
            total_recordings = df['Recordings'].sum()
            avg_recordings = df['Recordings'].mean()
            clubs_with_recordings = len(df[df['Recordings'] > 0])
            
            print(f"\n📈 STATS:")
            print(f"Total recordings: {total_recordings:,}")
            print(f"Average recordings per club: {avg_recordings:.1f}")
            print(f"Clubs with recordings: {clubs_with_recordings}")
            print(f"Clubs with teams: {len(df[df['Teams'] > 0])}")
            
            print(f"\n🔥 TOP CLUBS BY RECORDINGS:")
            top_clubs = df.sort_values('Recordings', ascending=False).head(10)
            for _, club in top_clubs.iterrows():
                print(f"{club['Club_Name']}: {club['Recordings']} recordings, {club['Teams']} teams")
        else:
            print("❌ No clubs found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if clubs:
            df = pd.DataFrame(clubs)
            df.to_csv('../data/raw/veo_1000_clubs.csv', index=False)
            print(f"💾 Emergency save: {len(clubs)} clubs")
    finally:
        driver.quit()
        print("🏁 Scraper finished")

if __name__ == "__main__":
    aggressive_scroll_and_scrape()