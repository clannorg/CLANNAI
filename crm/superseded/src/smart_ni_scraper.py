import csv
import requests
import re
import time
import random
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

# Config
INPUT_CSV = 'data/contacts/ni_clubs/ni_football_clubs_only.csv'
OUTPUT_CSV = 'data/contacts/ni_clubs/smart_scraper_results.csv'
PROGRESS_FILE = 'data/contacts/ni_clubs/smart_progress.json'

class SmartNIScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
        ]
        
        # Enhanced phone patterns for UK/NI
        self.phone_patterns = [
            r'\b(?:\+44|0044|44)[\s\-\.]?(?:\d{2,4}[\s\-\.]?){2,3}\d{3,4}\b',  # International format
            r'\b028[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b',  # NI landline specific
            r'\b07\d{3}[\s\-\.]?\d{6}\b',  # UK mobile
            r'\b0\d{2,4}[\s\-\.]?\d{6,8}\b',  # UK landline general
            r'\b\d{11}\b'  # Plain 11-digit numbers
        ]
        
        # Email pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Common contact page URLs to try
        self.contact_paths = [
            '/contact', '/contact-us', '/contacts', '/contact.html', '/contact.php',
            '/about/contact', '/club/contact', '/contact-details', '/get-in-touch',
            '/contact-info', '/contact-information'
        ]
        
    def get_random_headers(self):
        """Get randomized headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def extract_contacts_from_text(self, text):
        """Extract phone numbers and emails from text with validation"""
        phones = set()
        emails = set()
        
        # Find phone numbers
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean and validate phone number
                clean_phone = re.sub(r'[^\d+]', '', match)
                if len(clean_phone) >= 10 and len(clean_phone) <= 15:
                    # Format nicely
                    if clean_phone.startswith('44'):
                        formatted = '+44 ' + clean_phone[2:]
                    elif clean_phone.startswith('0'):
                        formatted = clean_phone
                    else:
                        formatted = match.strip()
                    phones.add(formatted)
        
        # Find emails
        email_matches = re.findall(self.email_pattern, text, re.IGNORECASE)
        for email in email_matches:
            email_clean = email.lower().strip()
            # Filter out obvious junk emails
            if not any(junk in email_clean for junk in ['example.com', 'test.com', 'noreply', 'donotreply']):
                emails.add(email_clean)
        
        return list(phones), list(emails)
    
    def validate_club_match(self, club_name, content):
        """Check if the content actually relates to the club"""
        club_words = set(club_name.lower().split())
        content_lower = content.lower()
        
        # Remove common words
        ignore_words = {'fc', 'football', 'club', 'united', 'city', 'town', 'academy'}
        club_words = club_words - ignore_words
        
        if not club_words:
            return True  # If only common words, assume it matches
        
        # Check if at least one significant club word appears
        matches = sum(1 for word in club_words if len(word) > 3 and word in content_lower)
        return matches > 0
    
    def find_official_website(self, club_name):
        """Try to find the official club website"""
        print(f"    🔍 Searching for official website...")
        
        # Try Google search for official site
        search_queries = [
            f'"{club_name}" official website Northern Ireland',
            f'{club_name} football club official site',
            f'{club_name} FC website'
        ]
        
        for query in search_queries[:2]:  # Limit searches
            try:
                # Google search
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                
                time.sleep(random.uniform(1, 3))
                response = self.session.get(search_url, headers=self.get_random_headers(), timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for official-looking URLs in search results
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '')
                        if '/url?q=' in href:
                            # Extract real URL from Google redirect
                            real_url = href.split('/url?q=')[1].split('&')[0]
                            
                            # Check if this looks like an official club website
                            if any(indicator in real_url.lower() for indicator in [
                                club_name.lower().replace(' ', ''), 'fc.', 'football', '.com', '.co.uk'
                            ]):
                                print(f"    ✅ Found potential website: {real_url}")
                                return real_url
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"    ⚠️  Website search error: {e}")
                continue
        
        return None
    
    def scrape_website_contacts(self, url, club_name):
        """Scrape contacts from a specific website"""
        contacts = {'phones': [], 'emails': [], 'sources': []}
        
        try:
            print(f"    🌐 Scraping website: {url}")
            
            # First try the main page
            response = self.session.get(url, headers=self.get_random_headers(), timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                if self.validate_club_match(club_name, text):
                    phones, emails = self.extract_contacts_from_text(text)
                    contacts['phones'].extend(phones)
                    contacts['emails'].extend(emails)
                    if phones or emails:
                        contacts['sources'].append(f"{url} (main page)")
            
            # Try contact pages
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            for path in self.contact_paths[:3]:  # Try first 3 contact paths
                try:
                    contact_url = urljoin(base_url, path)
                    time.sleep(random.uniform(1, 2))
                    
                    response = self.session.get(contact_url, headers=self.get_random_headers(), timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        
                        phones, emails = self.extract_contacts_from_text(text)
                        if phones or emails:
                            contacts['phones'].extend(phones)
                            contacts['emails'].extend(emails)
                            contacts['sources'].append(f"{contact_url}")
                            print(f"    💎 Contact page found: {len(phones)} phones, {len(emails)} emails")
                            break  # Found good contact page, stop trying others
                
                except:
                    continue
        
        except Exception as e:
            print(f"    ❌ Website scraping error: {e}")
        
        # Remove duplicates
        contacts['phones'] = list(set(contacts['phones']))
        contacts['emails'] = list(set(contacts['emails']))
        
        return contacts
    
    def search_facebook(self, club_name):
        """Search for club's Facebook page"""
        contacts = {'phones': [], 'emails': [], 'sources': []}
        
        try:
            print(f"    📘 Searching Facebook...")
            
            # Search for Facebook page
            search_query = f'{club_name} facebook Northern Ireland'
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
            time.sleep(random.uniform(1, 3))
            response = self.session.get(search_url, headers=self.get_random_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for Facebook URLs
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'facebook.com' in href and club_name.lower() in href.lower():
                        print(f"    ✅ Found Facebook page: {href}")
                        contacts['sources'].append(f"Facebook: {href}")
                        break
        
        except Exception as e:
            print(f"    ⚠️  Facebook search error: {e}")
        
        return contacts
    
    def search_comprehensive(self, club_name):
        """Comprehensive multi-strategy search for club contacts"""
        print(f"\n🎯 SMART SEARCH: {club_name}")
        
        all_contacts = {
            'phones': [],
            'emails': [],
            'website': '',
            'facebook': '',
            'sources': [],
            'search_strategies': []
        }
        
        # Strategy 1: Find and scrape official website
        all_contacts['search_strategies'].append('Official Website Search')
        website_url = self.find_official_website(club_name)
        if website_url:
            all_contacts['website'] = website_url
            website_contacts = self.scrape_website_contacts(website_url, club_name)
            all_contacts['phones'].extend(website_contacts['phones'])
            all_contacts['emails'].extend(website_contacts['emails'])
            all_contacts['sources'].extend(website_contacts['sources'])
        
        # Strategy 2: Facebook search
        all_contacts['search_strategies'].append('Facebook Search')
        fb_contacts = self.search_facebook(club_name)
        all_contacts['sources'].extend(fb_contacts['sources'])
        
        # Strategy 3: Enhanced Google search with validation
        all_contacts['search_strategies'].append('Validated Google Search')
        google_contacts = self.enhanced_google_search(club_name)
        all_contacts['phones'].extend(google_contacts['phones'])
        all_contacts['emails'].extend(google_contacts['emails'])
        all_contacts['sources'].extend(google_contacts['sources'])
        
        # Remove duplicates and clean up
        all_contacts['phones'] = list(set(all_contacts['phones']))
        all_contacts['emails'] = list(set(all_contacts['emails']))
        
        # Report results
        total_contacts = len(all_contacts['phones']) + len(all_contacts['emails'])
        if total_contacts > 0:
            print(f"  🎉 SUCCESS: {len(all_contacts['phones'])} phones, {len(all_contacts['emails'])} emails")
            if all_contacts['phones']:
                print(f"    📞 Phones: {', '.join(all_contacts['phones'][:3])}...")
            if all_contacts['emails']:
                print(f"    📧 Emails: {', '.join(all_contacts['emails'][:3])}...")
        else:
            print(f"  ❌ No contacts found")
        
        return all_contacts
    
    def enhanced_google_search(self, club_name):
        """Enhanced Google search with better validation"""
        contacts = {'phones': [], 'emails': [], 'sources': []}
        
        search_queries = [
            f'"{club_name}" phone email contact Northern Ireland',
            f'{club_name} football club contact details phone',
        ]
        
        for query in search_queries[:2]:
            try:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(search_url, headers=self.get_random_headers(), timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    # Only extract if content seems to match the club
                    if self.validate_club_match(club_name, text):
                        phones, emails = self.extract_contacts_from_text(text)
                        contacts['phones'].extend(phones)
                        contacts['emails'].extend(emails)
                        if phones or emails:
                            contacts['sources'].append(f"Google search: {query}")
            
            except Exception as e:
                print(f"    ⚠️  Google search error: {e}")
                continue
        
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
    
    def scrape_top_clubs(self, limit=10):
        """Scrape the top N clubs using smart strategies"""
        progress = self.load_progress()
        
        # Read clubs
        clubs = []
        with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                clubs.append(row)
        
        # Take only top clubs
        top_clubs = clubs[:limit]
        
        print(f"🧠 SMART NI SCRAPER - Multi-Strategy Contact Hunter")
        print(f"🎯 Target: Top {limit} clubs (aiming for 5 phones + 3 emails each)")
        print(f"📈 Using: Website scraping + Facebook + Validated searches")
        
        # Prepare output data
        output_data = []
        
        for i, club in enumerate(top_clubs):
            club_name = club['Club Name']
            recordings = club['Recordings']
            
            print(f"\n{'='*60}")
            print(f"📞 Processing {i+1}/{len(top_clubs)}: {club_name} ({recordings} recordings)")
            
            # Skip if already processed
            if club_name in progress:
                print(f"  ✅ Already processed - skipping")
                result = progress[club_name]
            else:
                # Smart comprehensive search
                result = self.search_comprehensive(club_name)
                progress[club_name] = result
                self.save_progress(progress)
                
                # Longer delay between clubs to be respectful
                time.sleep(random.uniform(5, 8))
            
            # Add to output
            output_row = {
                'Club Name': club_name,
                'Recordings': recordings,
                'Phones_Count': len(result['phones']),
                'Emails_Count': len(result['emails']),
                'Phones': '; '.join(result['phones']),
                'Emails': '; '.join(result['emails']),
                'Website': result['website'],
                'Facebook': result.get('facebook', ''),
                'Sources': '; '.join(result['sources']),
                'Strategies_Used': '; '.join(result['search_strategies'])
            }
            output_data.append(output_row)
        
        # Write results
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Club Name', 'Recordings', 'Phones_Count', 'Emails_Count', 
                         'Phones', 'Emails', 'Website', 'Facebook', 'Sources', 'Strategies_Used']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_data)
        
        print(f"\n{'='*60}")
        print(f"🏆 SMART SCRAPER COMPLETED!")
        print(f"📁 Results saved to: {OUTPUT_CSV}")
        
        # Detailed analysis
        total_phones = sum(row['Phones_Count'] for row in output_data)
        total_emails = sum(row['Emails_Count'] for row in output_data)
        clubs_with_contacts = len([row for row in output_data if row['Phones_Count'] > 0 or row['Emails_Count'] > 0])
        
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print(f"  📞 Total phones found: {total_phones}")
        print(f"  📧 Total emails found: {total_emails}")
        print(f"  🎯 Clubs with contacts: {clubs_with_contacts}/{len(output_data)}")
        print(f"  📈 Average contacts per club: {(total_phones + total_emails) / len(output_data):.1f}")
        
        # Show best results
        best_clubs = sorted(output_data, key=lambda x: x['Phones_Count'] + x['Emails_Count'], reverse=True)
        print(f"\n🔥 TOP CONTACT HUNTERS:")
        for i, club in enumerate(best_clubs[:5], 1):
            total_contacts = club['Phones_Count'] + club['Emails_Count']
            print(f"  {i}. {club['Club Name']}: {club['Phones_Count']} phones + {club['Emails_Count']} emails = {total_contacts} total")
        
        # Goal assessment
        target_phones = 5 * len(output_data)
        target_emails = 3 * len(output_data)
        print(f"\n🎯 GOAL ASSESSMENT:")
        print(f"  📞 Phone goal: {total_phones}/{target_phones} ({total_phones/target_phones*100:.1f}%)")
        print(f"  📧 Email goal: {total_emails}/{target_emails} ({total_emails/target_emails*100:.1f}%)")

if __name__ == '__main__':
    scraper = SmartNIScraper()
    scraper.scrape_top_clubs(limit=10)