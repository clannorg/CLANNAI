#!/usr/bin/env python3
"""
Alternative Scraper - Uses Google search instead of DuckDuckGo
Since DuckDuckGo appears to be blocked on this server
"""

import csv
import requests
import re
import time
import random
from bs4 import BeautifulSoup
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Config
INPUT_CSV = 'data/ni_clubs/ni_football_clubs_only.csv'
OUTPUT_CSV = 'data/ni_clubs/google_contacts.csv'
PROGRESS_FILE = 'data/ni_clubs/google_progress.json'

class GoogleScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Google-friendly headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Enhanced phone patterns for UK/NI
        self.phone_patterns = [
            r'\b(?:0|44|\+44)[\s\-\.]?(?:\d{2,4}[\s\-\.]?){2,3}\d{3,4}\b',
            r'\b028[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b',  # NI specific
            r'\b07\d{3}[\s\-\.]?\d{6}\b',  # UK mobile
            r'\b\d{5}\s?\d{6}\b',  # Standard UK format
            r'\b\d{4}\s?\d{3}\s?\d{3}\b'
        ]
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
    def extract_contacts(self, text):
        """Extract phone numbers and emails from text"""
        phones = set()
        emails = set()
        
        # Find phone numbers
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean phone number
                clean_phone = re.sub(r'[^\d+]', '', match)
                if len(clean_phone) >= 10:
                    phones.add(match.strip())
        
        # Find emails
        email_matches = re.findall(self.email_pattern, text, re.IGNORECASE)
        for email in email_matches:
            emails.add(email.lower())
            
        return list(phones), list(emails)
    
    def search_google(self, query):
        """Search Google for the given query"""
        try:
            # Google search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            # Add random delay
            time.sleep(random.uniform(3, 6))
            
            response = self.session.get(search_url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print(f"  ⚠️  Rate limited by Google - waiting 60 seconds...")
                time.sleep(60)
                return ""
            else:
                print(f"  ⚠️  Google returned status {response.status_code}")
                return ""
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ Request timeout - will retry later")
            return ""
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection error - will retry later")
            return ""
        except Exception as e:
            print(f"  ❌ Error searching Google: {e}")
            return ""
    
    def search_club_online(self, club_name, location=None):
        """Search for club contact information using Google"""
        contacts = {
            'phones': [],
            'emails': [],
            'website': '',
            'facebook': '',
            'search_queries': []
        }
        
        # Build search queries
        search_terms = [
            f'{club_name} Northern Ireland contact phone email',
            f'{club_name} football club contact details',
        ]
        
        if location:
            search_terms.append(f'{club_name} {location} contact')
        
        # Only try the first search term to reduce load
        for search_term in search_terms[:1]:
            try:
                contacts['search_queries'].append(search_term)
                
                print(f"    🔍 Searching: {search_term}")
                
                # Search Google
                html_content = self.search_google(search_term)
                
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    text = soup.get_text()
                    
                    phones, emails = self.extract_contacts(text)
                    contacts['phones'].extend(phones)
                    contacts['emails'].extend(emails)
                    
                    # Look for website links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'facebook.com' in href and not contacts['facebook']:
                            contacts['facebook'] = href
                        elif any(term in href.lower() for term in ['fc.', 'football', 'club']) and not contacts['website']:
                            contacts['website'] = href
                
                # Delay between searches
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                print(f"  ❌ Error searching for {club_name}: {e}")
                continue
        
        # Remove duplicates
        contacts['phones'] = list(set(contacts['phones']))
        contacts['emails'] = list(set(contacts['emails']))
        
        return contacts
    
    def load_progress(self):
        """Load previous progress"""
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_progress(self, progress):
        """Save current progress"""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def scrape_contacts(self):
        """Main scraping function using Google"""
        progress = self.load_progress()
        
        # Read clubs
        clubs = []
        try:
            with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    clubs.append(row)
        except FileNotFoundError:
            print(f"❌ Input file {INPUT_CSV} not found!")
            return
        
        print(f"🔍 Found {len(clubs)} Northern Ireland football clubs to process")
        print("🔍 Using Google search engine (DuckDuckGo was blocked)")
        
        # Prepare output data
        output_data = []
        
        for i, club in enumerate(clubs):
            club_name = club['Club Name']
            recordings = club['Recordings']
            location = club.get('Additional Info', '')
            
            print(f"\n[{i+1}/{len(clubs)}] Processing: {club_name}")
            
            # Skip if already processed
            if club_name in progress:
                print(f"  ✅ Already processed - skipping")
                result = progress[club_name]
            else:
                # Search for contacts
                try:
                    result = self.search_club_online(club_name, location)
                    progress[club_name] = result
                    self.save_progress(progress)
                except Exception as e:
                    print(f"  ❌ Error processing {club_name}: {e}")
                    result = {'phones': [], 'emails': [], 'website': '', 'facebook': '', 'search_queries': []}
                    progress[club_name] = result
                    self.save_progress(progress)
                
                if result['phones'] or result['emails']:
                    print(f"  🎉 SUCCESS: {len(result['phones'])} phones, {len(result['emails'])} emails")
                    if result['phones']:
                        print(f"    📞 Phones: {', '.join(result['phones'][:2])}...")
                    if result['emails']:
                        print(f"    📧 Emails: {', '.join(result['emails'][:2])}...")
                else:
                    print(f"  ❌ No contacts found")
                
                # Longer delay between clubs to avoid rate limiting
                time.sleep(random.uniform(15, 25))
                
                # Periodic save every 10 clubs
                if (i + 1) % 10 == 0:
                    print(f"💾 Saved progress: {i + 1} clubs processed")
            
            # Add to output
            output_row = {
                'Club Name': club_name,
                'Recordings': recordings,
                'Location': location,
                'Phones': '; '.join(result['phones']),
                'Emails': '; '.join(result['emails']),
                'Website': result['website'],
                'Facebook': result['facebook'],
                'Search Queries': '; '.join(result['search_queries'])
            }
            output_data.append(output_row)
        
        # Write results
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Club Name', 'Recordings', 'Location', 'Phones', 'Emails', 'Website', 'Facebook', 'Search Queries']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_data)
        
        print(f"\n🏆 Completed! Results saved to {OUTPUT_CSV}")
        
        # Summary
        total_phones = sum(1 for row in output_data if row['Phones'])
        total_emails = sum(1 for row in output_data if row['Emails'])
        total_contacts = len([row for row in output_data if row['Phones'] or row['Emails']])
        success_rate = round(total_contacts / len(output_data) * 100, 1)
        
        print(f"📊 Summary:")
        print(f"  📞 {total_phones} clubs with phone numbers")
        print(f"  📧 {total_emails} clubs with email addresses")  
        print(f"  🎯 {total_contacts}/{len(output_data)} clubs with contacts ({success_rate}% success rate)")

if __name__ == '__main__':
    scraper = GoogleScraper()
    scraper.scrape_contacts() 