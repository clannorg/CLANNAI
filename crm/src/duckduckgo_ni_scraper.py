import csv
import requests
import re
import time
import random
from bs4 import BeautifulSoup
import json

# Config
INPUT_CSV = 'data/ni_clubs/ni_football_clubs_only.csv'
OUTPUT_CSV = 'data/ni_clubs/duckduckgo_contacts.csv'
PROGRESS_FILE = 'data/ni_clubs/ddg_progress.json'

class DuckDuckGoNIScraper:
    def __init__(self):
        self.session = requests.Session()
        # DuckDuckGo-friendly headers
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
    
    def search_duckduckgo(self, query):
        """Search DuckDuckGo for the given query"""
        try:
            # DuckDuckGo search URL
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            # Add random delay
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"  ⚠️  DuckDuckGo returned status {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"  ❌ Error searching DuckDuckGo: {e}")
            return ""
    
    def search_club_online(self, club_name, location=None):
        """Search for club contact information using DuckDuckGo"""
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
        
        for search_term in search_terms[:2]:  # Limit to 2 searches per club
            try:
                contacts['search_queries'].append(search_term)
                
                print(f"    🔍 Searching: {search_term}")
                
                # Search DuckDuckGo
                html_content = self.search_duckduckgo(search_term)
                
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
                time.sleep(random.uniform(2, 4))
                
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
        """Main scraping function using DuckDuckGo"""
        progress = self.load_progress()
        
        # Read clubs
        clubs = []
        with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                clubs.append(row)
        
        print(f"🦆 Found {len(clubs)} Northern Ireland football clubs to process")
        print("🔍 Using DuckDuckGo search engine (no blocking!)")
        
        # Prepare output data
        output_data = []
        
        for i, club in enumerate(clubs):
            club_name = club['Club Name']
            recordings = club['Recordings']
            location = club.get('Additional Info', '')
            
            print(f"\n📞 Processing {i+1}/{len(clubs)}: {club_name}")
            
            # Skip if already processed
            if club_name in progress:
                print(f"  ✅ Already processed - skipping")
                result = progress[club_name]
            else:
                # Search for contacts
                result = self.search_club_online(club_name, location)
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
                
                # Random delay between clubs
                time.sleep(random.uniform(3, 6))
            
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
        
        # Show top results
        successful_clubs = [row for row in output_data if row['Phones'] or row['Emails']]
        if successful_clubs:
            print(f"\n🔥 Top contacts found:")
            for club in successful_clubs[:5]:
                print(f"  • {club['Club Name']}: {club['Recordings']} recordings")
                if club['Phones']:
                    print(f"    📞 {club['Phones']}")
                if club['Emails']:
                    print(f"    📧 {club['Emails']}")

if __name__ == '__main__':
    scraper = DuckDuckGoNIScraper()
    scraper.scrape_contacts()