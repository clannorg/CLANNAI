import csv
import requests
import re
import time
import random
from bs4 import BeautifulSoup
import json
from urllib.parse import unquote, urlparse
import duckduckgo_search as ddgs

# Config  
INPUT_CSV = 'data/contacts/ni_clubs/ni_football_clubs_only.csv'
OUTPUT_CSV = 'data/contacts/ni_clubs/safe_ddg_results.csv'
PROGRESS_FILE = 'data/contacts/ni_clubs/safe_ddg_progress.json'

class SafeDDGScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate user agents
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Enhanced patterns
        self.phone_patterns = [
            r'\b(?:\+44|0044|44)[\s\-\.]?(?:\d{2,4}[\s\-\.]?){2,3}\d{3,4}\b',
            r'\b028[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b',  # NI specific
            r'\b07\d{3}[\s\-\.]?\d{6}\b',  # UK mobile
            r'\b0\d{2,4}[\s\-\.]?\d{6,8}\b',
        ]
        
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
    def get_random_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def extract_contacts_from_text(self, text, club_name):
        """Extract and validate contacts"""
        phones = set()
        emails = set()
        
        # Only proceed if text mentions the club
        club_words = set(club_name.lower().split()) - {'fc', 'football', 'club', 'united'}
        if club_words:
            text_lower = text.lower()
            if not any(word in text_lower for word in club_words if len(word) > 3):
                return [], []  # Text doesn't seem to match club
        
        # Extract phones
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_phone = re.sub(r'[^\d+]', '', match)
                if len(clean_phone) >= 10:
                    phones.add(match.strip())
        
        # Extract emails
        email_matches = re.findall(self.email_pattern, text, re.IGNORECASE)
        for email in email_matches:
            email_clean = email.lower().strip()
            if not any(junk in email_clean for junk in ['example.com', 'test.com', 'noreply']):
                emails.add(email_clean)
        
        return list(phones), list(emails)
    
    def clean_ddg_url(self, ddg_url):
        """Clean DuckDuckGo redirect URLs to get real URLs"""
        if '//duckduckgo.com/l/?uddg=' in ddg_url:
            # Extract the real URL from DDG redirect
            try:
                real_url = ddg_url.split('uddg=')[1].split('&')[0]
                real_url = unquote(real_url)
                return real_url
            except:
                return ddg_url
        return ddg_url
    
    def search_ddg_api(self, query, max_results=5):
        """Use DuckDuckGo API for cleaner results"""
        try:
            print(f"    🦆 DDG API: {query}")
            
            # Use duckduckgo_search library for cleaner results
            with ddgs.DDGS() as ddg:
                results = []
                for result in ddg.text(query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'body': result.get('body', ''),
                        'href': result.get('href', '')
                    })
                return results
                
        except Exception as e:
            print(f"    ⚠️  DDG API error: {e}")
            return []
    
    def search_ddg_html(self, query):
        """Fallback: HTML scraping with URL cleaning"""
        try:
            print(f"    🦆 DDG HTML: {query}")
            
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(search_url, headers=self.get_random_headers(), timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                # Extract search results with cleaned URLs
                for result in soup.find_all('a', {'class': 'result__a'}):
                    href = result.get('href', '')
                    if href:
                        clean_url = self.clean_ddg_url(href)
                        title = result.get_text(strip=True)
                        results.append({
                            'title': title,
                            'href': clean_url,
                            'body': title  # Use title as body for HTML scraping
                        })
                
                return results[:5]  # Limit results
                
        except Exception as e:
            print(f"    ⚠️  DDG HTML error: {e}")
            return []
    
    def scrape_website_safely(self, url, club_name):
        """Safely scrape a website for contacts"""
        contacts = {'phones': [], 'emails': []}
        
        try:
            print(f"    🌐 Checking: {url}")
            
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return contacts
            
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, headers=self.get_random_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                phones, emails = self.extract_contacts_from_text(text, club_name)
                contacts['phones'].extend(phones)
                contacts['emails'].extend(emails)
                
                if phones or emails:
                    print(f"    ✅ Found: {len(phones)} phones, {len(emails)} emails")
            
        except Exception as e:
            print(f"    ⚠️  Website error: {e}")
        
        return contacts
    
    def search_club_comprehensive(self, club_name):
        """Multi-method DDG search with API + HTML fallback"""
        print(f"\n🦆 SAFE DDG SEARCH: {club_name}")
        
        all_contacts = {
            'phones': [],
            'emails': [],
            'websites_found': [],
            'search_methods': [],
            'sources': []
        }
        
        search_queries = [
            f'"{club_name}" contact phone email Northern Ireland',
            f'{club_name} football club contact details',
            f'{club_name} FC official website'
        ]
        
        for query in search_queries[:2]:  # Limit queries
            # Method 1: Try DDG API first (cleaner, no redirects)
            all_contacts['search_methods'].append(f'DDG API: {query}')
            api_results = self.search_ddg_api(query)
            
            # Method 2: Fallback to HTML with URL cleaning
            if not api_results:
                all_contacts['search_methods'].append(f'DDG HTML: {query}')
                api_results = self.search_ddg_html(query)
            
            # Process results
            for result in api_results[:3]:  # Top 3 results per query
                href = result.get('href', '')
                if href and href not in all_contacts['websites_found']:
                    all_contacts['websites_found'].append(href)
                    
                    # Extract from search snippet first
                    snippet = result.get('body', '') + ' ' + result.get('title', '')
                    phones, emails = self.extract_contacts_from_text(snippet, club_name)
                    all_contacts['phones'].extend(phones)
                    all_contacts['emails'].extend(emails)
                    
                    if phones or emails:
                        all_contacts['sources'].append(f'DDG snippet: {query}')
                    
                    # Then try scraping the actual website
                    website_contacts = self.scrape_website_safely(href, club_name)
                    all_contacts['phones'].extend(website_contacts['phones'])
                    all_contacts['emails'].extend(website_contacts['emails'])
                    
                    if website_contacts['phones'] or website_contacts['emails']:
                        all_contacts['sources'].append(f'Website: {href}')
            
            # Be respectful with delays
            time.sleep(random.uniform(3, 6))
        
        # Clean up duplicates
        all_contacts['phones'] = list(set(all_contacts['phones']))
        all_contacts['emails'] = list(set(all_contacts['emails']))
        
        # Report results
        total = len(all_contacts['phones']) + len(all_contacts['emails'])
        if total > 0:
            print(f"  🎉 SUCCESS: {len(all_contacts['phones'])} phones, {len(all_contacts['emails'])} emails")
            if all_contacts['phones']:
                print(f"    📞 {', '.join(all_contacts['phones'][:2])}...")
            if all_contacts['emails']:
                print(f"    📧 {', '.join(all_contacts['emails'][:2])}...")
        else:
            print(f"  ❌ No contacts found")
        
        return all_contacts
    
    def load_progress(self):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_progress(self, progress):
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def scrape_safe_ddg(self, limit=10):
        """Safe DDG scraping that won't get blocked"""
        progress = self.load_progress()
        
        # Read clubs
        clubs = []
        with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                clubs.append(row)
        
        top_clubs = clubs[:limit]
        
        print(f"🦆 SAFE DDG SCRAPER - Anti-Block Design")
        print(f"🎯 Target: Top {limit} clubs")
        print(f"🛡️  Using: DDG API + HTML fallback + URL cleaning")
        print(f"⏱️  Safe delays to avoid blocking")
        
        output_data = []
        
        for i, club in enumerate(top_clubs):
            club_name = club['Club Name']
            recordings = club['Recordings']
            
            print(f"\n{'='*50}")
            print(f"🦆 Processing {i+1}/{len(top_clubs)}: {club_name}")
            
            if club_name in progress:
                print(f"  ✅ Already processed - skipping")
                result = progress[club_name]
            else:
                result = self.search_club_comprehensive(club_name)
                progress[club_name] = result
                self.save_progress(progress)
                
                # Longer delays to be respectful
                time.sleep(random.uniform(8, 12))
            
            # Add to output
            output_row = {
                'Club Name': club_name,
                'Recordings': recordings,
                'Phones_Count': len(result['phones']),
                'Emails_Count': len(result['emails']),
                'Phones': '; '.join(result['phones']),
                'Emails': '; '.join(result['emails']),
                'Websites_Found': '; '.join(result['websites_found']),
                'Sources': '; '.join(result['sources']),
                'Methods_Used': '; '.join(result['search_methods'])
            }
            output_data.append(output_row)
        
        # Write results
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Club Name', 'Recordings', 'Phones_Count', 'Emails_Count', 
                         'Phones', 'Emails', 'Websites_Found', 'Sources', 'Methods_Used']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_data)
        
        print(f"\n{'='*50}")
        print(f"🦆 SAFE DDG SCRAPER COMPLETED!")
        print(f"📁 Results: {OUTPUT_CSV}")
        
        # Analysis
        total_phones = sum(row['Phones_Count'] for row in output_data)
        total_emails = sum(row['Emails_Count'] for row in output_data)
        
        print(f"\n📊 DDG vs Google Comparison:")
        print(f"  📞 Phones: {total_phones} (Google got 29)")
        print(f"  📧 Emails: {total_emails} (Google got 43)")
        print(f"  🛡️  Block risk: MUCH LOWER")

if __name__ == '__main__':
    scraper = SafeDDGScraper()
    scraper.scrape_safe_ddg(limit=5)  # Test with 5 clubs first