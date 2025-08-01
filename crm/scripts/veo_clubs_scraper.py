from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

def get_all_clubs():
    driver = webdriver.Chrome()
    try:
        print("Opening page...")
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(5)
        
        # Find the main scrollable container
        main_content = driver.find_element(By.CSS_SELECTOR, "main")
        
        last_height = driver.execute_script("return arguments[0].scrollHeight", main_content)
        clubs_found = 0
        
        while True:
            # Scroll down inside the main content
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", main_content)
            time.sleep(2)  # Wait for content to load
            
            # Get current content
            content = driver.find_element(By.TAG_NAME, "body").text
            lines = content.split('\n')
            
            # Count current clubs
            current_clubs = sum(1 for line in lines if 'recordings' in line and 'teams' in line)
            print(f"Found {current_clubs} clubs... (Height: {last_height}px)")
            
            # Check if we found more clubs
            if current_clubs > clubs_found:
                clubs_found = current_clubs
                time.sleep(1)  # Give more time for loading
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return arguments[0].scrollHeight", main_content)
            if new_height == last_height:
                # Try one more scroll to be sure
                time.sleep(2)
                driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", main_content)
                if new_height == last_height:
                    break
            last_height = new_height
        
        # Now process all clubs we found
        clubs = []
        for i in range(len(lines)):
            line = lines[i]
            if 'recordings' in line and 'teams' in line:
                club_name = lines[i-1] if i > 0 else "Unknown"
                if club_name not in ['Login', 'Clubs']:
                    stats = line.split(',')
                    recordings = int(stats[0].split()[0])
                    teams = int(stats[1].split()[0])
                    
                    if club_name in ['>', 'µ', '_', '__', '-']:
                        club_name = f"Unnamed Club ({club_name})"
                    
                    clubs.append({
                        'Club Name': club_name,
                        'Recordings': recordings,
                        'Teams': teams
                    })
        
        # Create and save DataFrame
        df = pd.DataFrame(clubs)
        df = df.sort_values(['Teams', 'Recordings'], ascending=[False, False])
        df.to_csv('data/veo_clubs.csv', index=False)
        
        print(f"\nSaved {len(clubs)} clubs to data/veo_clubs.csv")
        print("\nSample of the data:")
        print(df.head())
        
        print(f"\nTotal recordings across all clubs: {df['Recordings'].sum():,}")
        print(f"Total teams across all clubs: {df['Teams'].sum():,}")
        print(f"Average recordings per club: {df['Recordings'].mean():.1f}")
        print(f"Clubs with no teams: {len(df[df['Teams'] == 0])}")
        
    finally:
        driver.quit()

def test_scroll():
    driver = webdriver.Chrome()
    try:
        print("Opening page...")
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(5)
        
        # Find the main content area that scrolls
        scroll_attempts = 0
        last_count = 0
        
        while scroll_attempts < 20:  # Try up to 20 scrolls
            # Scroll in smaller increments
            driver.execute_script("window.scrollBy(0, 500);")  # Scroll by 500px
            time.sleep(2)  # Wait for content to load
            
            # Count clubs
            lines = driver.find_element(By.TAG_NAME, "body").text.split('\n')
            current_count = sum(1 for line in lines if 'recordings' in line and 'teams' in line)
            
            scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
            scroll_position = driver.execute_script("return window.pageYOffset")
            
            print(f"Found {current_count} clubs (Scroll position: {scroll_position}/{scroll_height}px)")
            
            if current_count > last_count:
                last_count = current_count
                scroll_attempts = 0  # Reset attempts when we find more clubs
            else:
                scroll_attempts += 1
            
    finally:
        driver.quit()

if __name__ == "__main__":
    get_all_clubs()
    test_scroll()
