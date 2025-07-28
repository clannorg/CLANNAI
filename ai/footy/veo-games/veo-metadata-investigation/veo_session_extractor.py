#!/usr/bin/env python3
"""
Veo Session Extractor - Better session handling to mimic browser behavior
"""

import requests
import json
from datetime import datetime

class VeoSessionExtractor:
    def __init__(self):
        self.match_url = "https://app.veo.co/matches/20250111-ballyclare-425e4c3f/"
        self.match_id = "ballyclare-425e4c3f"
        self.uuid_match_id = "ec3ca4f8-1934-4861-b6fa-0a02b7564a0e"  # Real UUID from page source
        self.session = requests.Session()
        
        # Set browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def load_initial_page(self):
        """Load the match page to establish session/cookies"""
        print(f"🌐 Loading initial page: {self.match_url}")
        try:
            response = self.session.get(self.match_url)
            print(f"✅ Page loaded: {response.status_code}")
            print(f"📝 Cookies set: {len(self.session.cookies)} cookies")
            
            # Look for any embedded event data
            if '36:39' in response.text or '66:26' in response.text:
                print("🎯 FOUND TIMESTAMPS IN HTML!")
                return True
            else:
                print("❌ No timestamps found in HTML")
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return False
    
    def test_api_endpoints_with_session(self):
        """Test API endpoints with established session"""
        endpoints = [
            # Original match ID patterns
            f"https://app.veo.co/api/app/matches/{self.match_id}",
            f"https://app.veo.co/api/app/matches/{self.match_id}/highlights", 
            f"https://app.veo.co/api/app/matches/{self.match_id}/events",
            f"https://app.veo.co/api/app/matches/{self.match_id}/stats",
            # UUID-based patterns (REAL match ID)
            f"https://app.veo.co/api/app/matches/{self.uuid_match_id}",
            f"https://app.veo.co/api/app/matches/{self.uuid_match_id}/highlights",
            f"https://app.veo.co/api/app/matches/{self.uuid_match_id}/events", 
            f"https://app.veo.co/api/app/matches/{self.uuid_match_id}/stats",
            f"https://app.veo.co/api/app/matches/{self.uuid_match_id}/timeline",
            f"https://app.veo.co/api/app/matches/{self.uuid_match_id}/moments",
            # Service URLs found in page source (might need tokens)
            f"https://dt3kfuz4eo879.cloudfront.net/matches/{self.uuid_match_id}",
            f"https://dt3kfuz4eo879.cloudfront.net/matches/{self.uuid_match_id}/events",
            f"https://d3g8j1j1rf6msg.cloudfront.net/matches/{self.uuid_match_id}",
            f"https://d3g8j1j1rf6msg.cloudfront.net/matches/{self.uuid_match_id}/events",
        ]
        
        # Update headers for API requests
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Referer': self.match_url,
            'X-Requested-With': 'XMLHttpRequest',
        })
        
        for endpoint in endpoints:
            print(f"\n🔍 Testing: {endpoint}")
            try:
                response = self.session.get(endpoint, timeout=10)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text
                    if any(keyword in content for keyword in ['36:39', '66:26', 'Shot on goal']):
                        print(f"🎯 FOUND EVENT DATA!")
                        print(f"📝 Content preview: {content[:300]}...")
                        return endpoint, content
                    elif 'event' in content.lower() or 'goal' in content.lower():
                        print(f"📋 Contains event keywords. Size: {len(content)} chars")
                        try:
                            data = response.json()
                            print(f"🔧 JSON keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                            # Save the successful response for analysis
                            if 'has_events_enabled' in data:
                                print(f"🎯 SAVING SUCCESSFUL RESPONSE - has_events_enabled: {data.get('has_events_enabled')}")
                                with open(f'successful_response_{endpoint.split("/")[-1]}.json', 'w') as f:
                                    json.dump(data, f, indent=2)
                                # Look for any event-related fields
                                event_fields = [k for k in data.keys() if 'event' in k.lower()]
                                if event_fields:
                                    print(f"🔍 Event-related fields: {event_fields}")
                                    for field in event_fields:
                                        print(f"   {field}: {data[field]}")
                        except:
                            print("📄 Non-JSON response")
                    else:
                        print(f"📄 Response size: {len(content)} chars, no event keywords")
                else:
                    print(f"❌ Error: {response.status_code}")
                    if response.status_code == 403:
                        print("🔒 Forbidden - might need specific session state")
                    elif response.status_code == 404:
                        print("🚫 Not Found - endpoint doesn't exist")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
        return None, None
    
    def extract_events(self):
        """Main extraction method"""
        print("🚀 Starting Veo Session-Based Extraction...\n")
        
        # Step 1: Load page to establish session
        if not self.load_initial_page():
            print("❌ Failed to load initial page")
            return None, None
        
        # Step 2: Test API endpoints with session
        event_url, event_data = self.test_api_endpoints_with_session()
        
        if event_url:
            print(f"\n🎉 SUCCESS! Found events at: {event_url}")
            # Save the results
            result = {
                'url': event_url,
                'data': event_data,
                'timestamp': datetime.now().isoformat(),
                'method': 'session_based'
            }
            with open('veo_events_session.json', 'w') as f:
                json.dump(result, f, indent=2)
            return event_url, event_data
        else:
            print("\n❌ No event data found with session approach")
            return None, None

if __name__ == "__main__":
    extractor = VeoSessionExtractor()
    extractor.extract_events() 