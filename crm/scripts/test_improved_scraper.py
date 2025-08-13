#!/usr/bin/env python3
"""
Test script for improved DuckDuckGo scraper
Tests the improved error handling and rate limiting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from duckduckgo_ni_scraper import DuckDuckGoNIScraper
import requests

def test_network():
    """Test basic network connectivity"""
    print("🌐 Testing network connectivity...")
    
    try:
        # Test basic connectivity
        response = requests.get("https://www.google.com", timeout=10)
        print(f"✅ Google connectivity: {response.status_code}")
        
        # Test DuckDuckGo specifically
        response = requests.get("https://duckduckgo.com", timeout=10)
        print(f"✅ DuckDuckGo connectivity: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return False

def test_scraper():
    """Test the improved scraper with a single club"""
    print("\n🧪 Testing improved DuckDuckGo scraper...")
    
    if not test_network():
        print("❌ Network issues detected - skipping scraper test")
        return
    
    scraper = DuckDuckGoNIScraper()
    
    # Test with just one club
    club_name = "Linfield FC"
    print(f"\n[1/1] Testing: {club_name}")
    
    try:
        result = scraper.search_club_online(club_name, "Northern Ireland")
        
        if result['phones'] or result['emails']:
            print(f"  ✅ SUCCESS: {len(result['phones'])} phones, {len(result['emails'])} emails")
            if result['phones']:
                print(f"    📞 Phones: {', '.join(result['phones'][:2])}")
            if result['emails']:
                print(f"    📧 Emails: {', '.join(result['emails'][:2])}")
        else:
            print(f"  ⚠️  No contacts found (this is normal for some clubs)")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_scraper() 