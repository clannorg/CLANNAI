#!/usr/bin/env python3
"""
Veo Browser Extractor - Automated network capture to find event data
Uses Selenium to replicate browser behavior and capture all network requests
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests

class VeoBrowserExtractor:
    def __init__(self):
        self.match_url = "https://app.veo.co/matches/20250111-ballyclare-425e4c3f/"
        self.captured_requests = []
        
    def setup_driver(self):
        """Setup Chrome driver with network logging enabled"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=1")
        # Enable performance logging to capture network requests
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        return webdriver.Chrome(options=chrome_options)
    
    def capture_network_requests(self):
        """Load the Veo page and capture all network requests"""
        driver = self.setup_driver()
        
        try:
            print(f"Loading {self.match_url}")
            driver.get(self.match_url)
            
            # Wait for page to load and events to appear
            print("Waiting for page to load...")
            time.sleep(10)
            
            # Try to find event elements in DOM
            try:
                events = driver.find_elements(By.XPATH, "//*[contains(text(), 'Shot on goal') or contains(text(), '36:39') or contains(text(), '66:26')]")
                if events:
                    print(f"✅ Found {len(events)} event elements in DOM!")
                    for event in events[:3]:
                        print(f"  - {event.text}")
            except Exception as e:
                print(f"No events found in DOM: {e}")
            
            # Capture network logs
            logs = driver.get_log('performance')
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    if 'veo.co' in url and any(keyword in url for keyword in ['match', 'event', 'highlight', 'stats']):
                        self.captured_requests.append({
                            'url': url,
                            'status': message['message']['params']['response']['status'],
                            'timestamp': datetime.now().isoformat()
                        })
            
            return True
            
        except Exception as e:
            print(f"Error during capture: {e}")
            return False
        finally:
            driver.quit()
    
    def test_captured_requests(self):
        """Test each captured request to find the one with event data"""
        print(f"\n🔍 Testing {len(self.captured_requests)} captured requests...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': self.match_url,
            'Origin': 'https://app.veo.co'
        }
        
        for i, req in enumerate(self.captured_requests):
            print(f"\n{i+1}. Testing: {req['url']}")
            try:
                response = requests.get(req['url'], headers=headers, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    # Check if this contains our event data
                    if any(keyword in content for keyword in ['36:39', '66:26', 'Shot on goal']):
                        print(f"🎯 FOUND EVENT DATA! Status: {response.status_code}")
                        print(f"Content preview: {content[:500]}...")
                        return req['url'], content
                    elif 'event' in content.lower() or 'goal' in content.lower():
                        print(f"📝 Contains event keywords. Size: {len(content)} chars")
                else:
                    print(f"❌ Status: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return None, None
    
    def extract_events(self):
        """Main method to extract events"""
        print("🚀 Starting Veo Browser Event Extraction...")
        
        if self.capture_network_requests():
            print(f"\n📊 Captured {len(self.captured_requests)} relevant requests")
            
            # Save captured requests for reference
            with open('captured_requests.json', 'w') as f:
                json.dump(self.captured_requests, f, indent=2)
            
            # Test each request
            event_url, event_data = self.test_captured_requests()
            
            if event_url:
                print(f"\n🎉 SUCCESS! Found event data at: {event_url}")
                # Save the event data
                with open('veo_events_found.json', 'w') as f:
                    json.dump({'url': event_url, 'data': event_data}, f, indent=2)
                return event_url, event_data
            else:
                print("\n❌ No event data found in captured requests")
                return None, None
        else:
            print("❌ Failed to capture network requests")
            return None, None

if __name__ == "__main__":
    extractor = VeoBrowserExtractor()
    extractor.extract_events() 