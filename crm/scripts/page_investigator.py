from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def setup_driver():
    """Setup Chrome driver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    return webdriver.Chrome(options=chrome_options)

def investigate_page_structure():
    """Investigate the VEO page structure to understand how to get all clubs"""
    driver = setup_driver()
    
    try:
        print("🔍 Investigating VEO page structure...")
        
        # Navigate to VEO clubs page
        driver.get("https://app.veo.co/all-clubs/")
        time.sleep(8)
        
        print("📄 Page loaded, analyzing structure...")
        
        # 1. Check page title and basic info
        print(f"📋 Page title: {driver.title}")
        print(f"🌐 Current URL: {driver.current_url}")
        
        # 2. Check for any API endpoints or data sources
        print("\n🔍 Looking for API calls or data sources...")
        logs = driver.get_log('performance')
        api_calls = []
        for log in logs:
            if 'message' in log:
                message = json.loads(log['message'])
                if 'message' in message and 'method' in message['message']:
                    if message['message']['method'] == 'Network.requestWillBeSent':
                        url = message['message']['params']['request']['url']
                        if 'api' in url or 'clubs' in url or 'data' in url:
                            api_calls.append(url)
        
        print(f"📡 Found {len(api_calls)} potential API calls:")
        for call in api_calls[:10]:  # Show first 10
            print(f"  - {call}")
        
        # 3. Check for pagination elements
        print("\n🔍 Looking for pagination elements...")
        pagination_selectors = [
            'button[class*="load"]',
            'button[class*="more"]',
            'button[class*="next"]',
            'a[class*="load"]',
            'a[class*="more"]',
            'a[class*="next"]',
            '[class*="pagination"]',
            '[class*="load-more"]',
            '[class*="show-more"]'
        ]
        
        for selector in pagination_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for elem in elements[:3]:  # Show first 3
                        print(f"  - Text: '{elem.text}' | Visible: {elem.is_displayed()}")
            except:
                continue
        
        # 4. Check for infinite scroll triggers
        print("\n🔍 Looking for scroll containers and triggers...")
        scroll_containers = driver.find_elements(By.CSS_SELECTOR, '[class*="scroll"], [class*="container"], main, [class*="content"]')
        print(f"📦 Found {len(scroll_containers)} potential scroll containers")
        
        for i, container in enumerate(scroll_containers[:5]):  # Check first 5
            try:
                print(f"  Container {i+1}: {container.tag_name} | Class: {container.get_attribute('class')}")
                print(f"    Scroll height: {driver.execute_script('return arguments[0].scrollHeight', container)}")
                print(f"    Client height: {driver.execute_script('return arguments[0].clientHeight', container)}")
            except:
                continue
        
        # 5. Check for hidden elements or lazy loading
        print("\n🔍 Checking for hidden elements...")
        all_elements = driver.find_elements(By.CSS_SELECTOR, '*')
        hidden_elements = []
        
        for elem in all_elements[:1000]:  # Check first 1000 elements
            try:
                if not elem.is_displayed():
                    text = elem.text.strip()
                    if text and len(text) > 3:
                        hidden_elements.append(text[:50])
            except:
                continue
        
        print(f"👻 Found {len(hidden_elements)} hidden elements with text")
        for text in hidden_elements[:10]:
            print(f"  - {text}")
        
        # 6. Check for data attributes or scripts
        print("\n🔍 Looking for data attributes and scripts...")
        scripts = driver.find_elements(By.TAG_NAME, 'script')
        print(f"📜 Found {len(scripts)} script tags")
        
        for script in scripts[:5]:  # Check first 5
            try:
                src = script.get_attribute('src')
                if src:
                    print(f"  - Script src: {src}")
            except:
                continue
        
        # 7. Try to find the actual club data structure
        print("\n🔍 Analyzing club data structure...")
        club_elements = driver.find_elements(By.CSS_SELECTOR, '*')
        club_data = []
        
        for elem in club_elements[:500]:  # Check first 500
            try:
                text = elem.text.strip()
                if text and ('recording' in text.lower() or 'team' in text.lower()):
                    club_data.append({
                        'text': text[:100],
                        'tag': elem.tag_name,
                        'class': elem.get_attribute('class'),
                        'visible': elem.is_displayed()
                    })
            except:
                continue
        
        print(f"🏟️ Found {len(club_data)} potential club data elements")
        for data in club_data[:10]:
            print(f"  - {data['tag']} | Class: {data['class']} | Visible: {data['visible']}")
            print(f"    Text: {data['text']}")
        
        # 8. Check for any network requests that might load more data
        print("\n🔍 Checking for dynamic content loading...")
        
        # Scroll a bit and check for new network requests
        initial_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"📏 Height before scroll: {initial_height}px")
        print(f"📏 Height after scroll: {new_height}px")
        print(f"📈 Height change: {new_height - initial_height}px")
        
        # 9. Look for any JavaScript variables or data
        print("\n🔍 Checking for JavaScript data...")
        js_data = driver.execute_script("""
            // Look for any global variables that might contain club data
            let data = {};
            for (let key in window) {
                if (typeof window[key] === 'object' && window[key] !== null) {
                    if (key.toLowerCase().includes('club') || 
                        key.toLowerCase().includes('data') ||
                        key.toLowerCase().includes('veo')) {
                        data[key] = typeof window[key];
                    }
                }
            }
            return data;
        """)
        
        print(f"💾 Found {len(js_data)} potential data objects:")
        for key, value_type in js_data.items():
            print(f"  - {key}: {value_type}")
        
        # 10. Check for any localStorage or sessionStorage
        print("\n🔍 Checking browser storage...")
        local_storage = driver.execute_script("return Object.keys(localStorage);")
        session_storage = driver.execute_script("return Object.keys(sessionStorage);")
        
        print(f"💾 localStorage keys: {local_storage}")
        print(f"💾 sessionStorage keys: {session_storage}")
        
        # 11. Final summary
        print("\n📊 INVESTIGATION SUMMARY:")
        print(f"  - API calls found: {len(api_calls)}")
        print(f"  - Pagination elements: {len([s for s in pagination_selectors if driver.find_elements(By.CSS_SELECTOR, s)])}")
        print(f"  - Scroll containers: {len(scroll_containers)}")
        print(f"  - Hidden elements: {len(hidden_elements)}")
        print(f"  - Club data elements: {len(club_data)}")
        print(f"  - JavaScript data objects: {len(js_data)}")
        print(f"  - Height change on scroll: {new_height - initial_height}px")
        
        return {
            'api_calls': api_calls,
            'pagination_elements': pagination_selectors,
            'scroll_containers': len(scroll_containers),
            'hidden_elements': len(hidden_elements),
            'club_data': len(club_data),
            'js_data': js_data,
            'height_change': new_height - initial_height
        }
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    results = investigate_page_structure()
    if results:
        print("\n🎯 RECOMMENDATIONS:")
        if results['api_calls']:
            print("  - Try to reverse engineer the API calls to get all clubs")
        if results['height_change'] > 0:
            print("  - Page does load more content on scroll, but may be limited")
        if results['js_data']:
            print("  - JavaScript data objects found - may contain all club data")
        if results['hidden_elements'] > 0:
            print("  - Hidden elements found - may contain more club data") 