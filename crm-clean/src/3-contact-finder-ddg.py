#!/usr/bin/env python3
"""
STAGE 3: Contact Finder (DuckDuckGo Version)
Finds phone numbers and emails for clubs using DuckDuckGo search
Input: data/2-by-country/clubs_by_location.csv
Output: data/3-contact-details/club_contacts.csv
"""

import pandas as pd
import requests
from duckduckgo_search import DDGS
import re
import time
from bs4 import BeautifulSoup
import logging
import json
from pathlib import Path

class ContactFinderDDG:
    def __init__(self):
        self.setup_logging()
        self.setup_session()
        
        # Contact patterns
        self.phone_patterns = [
            r'\+44\s?\d{4}\s?\d{6}',      # UK international
            r'0\d{3}\s?\d{3}\s?\d{4}',    # UK landline
            r'07\d{3}\s?\d{6}',           # UK mobile
            r'\+1\s?\d{3}\s?\d{3}\s?\d{4}', # US format
            r'\(\d{3}\)\s?\d{3}-\d{4}'    # US local
        ]
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Progress tracking
        self.progress_file = Path('data/3-contact-details/ddg_contact_progress.json')
        self.processed_clubs = self.load_progress()
        
    def setup_logging(self):
        """Setup logging"""
        Path('data/3-contact-details').mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler('data/3-contact-details/ddg_contact_finder.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_session(self):
        """Setup requests session with headers"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def load_progress(self):
        """Load processed clubs from progress file"""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                data = json.load(f)
                return set(data.get('processed_clubs', []))
        return set()
        
    def save_progress(self):
        """Save progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump({
                'processed_clubs': list(self.processed_clubs),
                'total_processed': len(self.processed_clubs)
            }, f, indent=2)
            
    def extract_contacts(self, text):
        """Extract phone numbers and emails from text"""
        phones = []
        emails = []
        
        # Find phone numbers
        for pattern in self.phone_patterns:
            phones.extend(re.findall(pattern, text))
            
        # Find emails
        emails.extend(re.findall(self.email_pattern, text))
        
        # Clean and deduplicate
        phones = list(set([phone.strip() for phone in phones]))
        emails = list(set([email.strip().lower() for email in emails]))
        
        return phones, emails
        
    def search_club_website_ddg(self, club_name, country):
        """Search for club website using DuckDuckGo and extract contacts"""
        try:
            # DuckDuckGo search
            search_query = f'"{club_name}" football club {country} contact website'
            
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=3))
                
            for result in results:
                url = result.get('href', '')
                
                try:
                    # Skip social media and directory sites
                    skip_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'veo.co', 'youtube.com']
                    if any(domain in url for domain in skip_domains):
                        continue
                        
                    # Fetch page content
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    # Parse content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Extract contacts
                    phones, emails = self.extract_contacts(text)
                    
                    if phones or emails:
                        return {
                            'phones': phones,
                            'emails': emails,
                            'website': url,
                            'search_engine': 'DuckDuckGo'
                        }
                        
                except Exception as e:
                    self.logger.debug(f"Failed to process {url}: {e}")
                    continue
                    
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            self.logger.warning(f"DuckDuckGo search failed for {club_name}: {e}")
            
        return None
        
    def find_club_contacts(self, club_name, country, activity_score):
        """Find contacts for a specific club"""
        if club_name in self.processed_clubs:
            return None
            
        self.logger.info(f"🦆 [{activity_score:.0f}] DDG Search: {club_name} ({country})")
        
        # Search for contacts
        contact_info = self.search_club_website_ddg(club_name, country)
        
        result = {
            'Club Name': club_name,
            'Country': country,
            'Activity_Score': activity_score,
            'Phones': [],
            'Emails': [],
            'Website': '',
            'Contact_Found': False,
            'Search_Engine': 'DuckDuckGo',
            'Searched_At': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if contact_info:
            result.update({
                'Phones': contact_info.get('phones', []),
                'Emails': contact_info.get('emails', []),
                'Website': contact_info.get('website', ''),
                'Contact_Found': bool(contact_info.get('phones') or contact_info.get('emails'))
            })
            
        # Mark as processed
        self.processed_clubs.add(club_name)
        
        return result
        
    def process_clubs(self, input_file='data/3-contact-details/target_prospects.csv', max_clubs=None):
        """Process clubs to find contacts using DuckDuckGo"""
        self.logger.info(f"🦆 STAGE 3: Starting DuckDuckGo contact search...")
        
        try:
            # Read clubs file
            df = pd.read_csv(input_file)
            
            # Sort by activity score (highest first)
            df = df.sort_values('Activity_Score', ascending=False)
                
            # Limit processing if specified
            if max_clubs:
                df = df.head(max_clubs)
                
            self.logger.info(f"📊 Processing {len(df)} clubs using DuckDuckGo...")
            
            results = []
            
            # Load existing results
            output_file = Path('data/3-contact-details/club_contacts_ddg.csv')
            if output_file.exists():
                existing_df = pd.read_csv(output_file)
                results = existing_df.to_dict('records')
                self.logger.info(f"📚 Loaded {len(results)} existing DDG results")
            
            # Process clubs
            for i, (_, row) in enumerate(df.iterrows(), 1):
                club_name = row['Club Name']
                country = row.get('Country', 'Unknown')
                activity_score = row.get('Activity_Score', 0)
                
                if club_name in self.processed_clubs:
                    self.logger.info(f"[{i}/{len(df)}] ⏭️  {club_name} - Already processed")
                    continue
                    
                self.logger.info(f"[{i}/{len(df)}] Processing: {club_name}")
                
                # Find contacts
                contact_result = self.find_club_contacts(club_name, country, activity_score)
                if contact_result:
                    results.append(contact_result)
                    
                    if contact_result['Contact_Found']:
                        self.logger.info(f"✅ Found contacts: {len(contact_result['Emails'])} emails, {len(contact_result['Phones'])} phones")
                    else:
                        self.logger.info(f"❌ No contacts found")
                    
                # Save progress every 5 clubs (more frequent due to DDG being faster)
                if i % 5 == 0:
                    self.save_progress()
                    pd.DataFrame(results).to_csv('data/3-contact-details/club_contacts_ddg.csv', index=False)
                    self.logger.info(f"💾 Progress saved - {len(results)} results so far")
                    
                time.sleep(2)  # Conservative rate limiting
                
            # Final save
            self.save_progress()
            if results:
                final_df = pd.DataFrame(results)
                final_df.to_csv('data/3-contact-details/club_contacts_ddg.csv', index=False)
                
                # Summary
                found_contacts = final_df[final_df['Contact_Found'] == True]
                self.logger.info(f"🦆 DDG CONTACT SEARCH COMPLETE!")
                self.logger.info(f"📊 Total processed: {len(final_df)}")
                self.logger.info(f"📞 Contacts found: {len(found_contacts)}")
                
                return 'data/3-contact-details/club_contacts_ddg.csv'
                
        except Exception as e:
            self.logger.error(f"DDG Contact finding failed: {e}")
            
        return None

def main():
    """Run the DuckDuckGo contact finder"""
    print("🦆 STAGE 3: DUCKDUCKGO CONTACT FINDER")
    print("=" * 45)
    print("This will find phone numbers and emails using DuckDuckGo")
    print("Input: data/3-contact-details/target_prospects.csv")
    print("Output: data/3-contact-details/club_contacts_ddg.csv")
    print()
    
    finder = ContactFinderDDG()
    
    # Check if input file exists
    input_file = 'data/3-contact-details/target_prospects.csv'
    if not Path(input_file).exists():
        print(f"❌ Input file {input_file} not found!")
        print("Run '2-location-sorter.py' first to generate target prospects")
        return
        
    # Ask user how many clubs to process
    try:
        max_clubs = input("How many clubs to process with DuckDuckGo? (Enter for 20): ").strip()
        max_clubs = int(max_clubs) if max_clubs else 20
    except ValueError:
        max_clubs = 20
        
    # Process clubs
    output_file = finder.process_clubs(input_file, max_clubs)
    
    if output_file:
        print(f"\n🦆 DDG CONTACT SEARCH COMPLETE!")
        print(f"📊 Results saved to: {output_file}")
        print(f"🎯 Ready for sales outreach!")
    else:
        print("❌ DDG Contact search failed")

if __name__ == "__main__":
    main()