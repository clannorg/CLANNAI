from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

def debug_veo_page():
    """Debug what's actually on the Veo page"""
    
    # Setup driver
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument(f'--user-data-dir=/tmp/debug-{random.randint(1000,9999)}')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Loading Veo page...")
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(10)  # Wait longer for full load
        
        print("\n=== PAGE ANALYSIS ===")
        
        # Get page title
        title = driver.title
        print(f"Page title: {title}")
        
        # Get page source length
        source = driver.page_source
        print(f"Page source length: {len(source)} characters")
        
        # Get all text content
        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = body_text.split('\n')
        print(f"Total text lines: {len(lines)}")
        
        # Look for club patterns
        club_lines = []
        for i, line in enumerate(lines):
            if 'recordings' in line.lower() or 'teams' in line.lower():
                club_lines.append((i, line))
                if i > 0:
                    club_lines.append((i-1, lines[i-1]))  # Club name is usually above
        
        print(f"\nFound {len(club_lines)} potential club lines:")
        for line_num, line in club_lines[:20]:  # Show first 20
            print(f"Line {line_num}: {line}")
        
        # Check for pagination or load more buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nFound {len(buttons)} buttons:")
        for btn in buttons[:10]:
            print(f"Button text: '{btn.text}'")
        
        # Check for any divs with club-related classes
        divs = driver.find_elements(By.TAG_NAME, "div")
        club_divs = []
        for div in divs:
            class_name = div.get_attribute("class") or ""
            if any(keyword in class_name.lower() for keyword in ['club', 'team', 'recording']):
                club_divs.append(div)
        
        print(f"\nFound {len(club_divs)} divs with club-related classes")
        
        # Save page source for manual inspection
        with open('data/veo_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\nSaved page source to data/veo_page_debug.html")
        
        # Save text content
        with open('data/veo_page_debug.txt', 'w', encoding='utf-8') as f:
            f.write(body_text)
        print(f"Saved text content to data/veo_page_debug.txt")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_veo_page() 