#!/usr/bin/env python3
"""
Fast Multi-Strategy Contact Scraper
Goal: Get 15-25 contacts from 91 clubs in ~20 minutes
"""

import pandas as pd
import requests
from duckduckgo_search import DDGS
import re
import time
import random
from bs4 import BeautifulSoup
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastContactScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Contact patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_patterns = [
            r'\+44\s*\d{4}\s*\d{6}',  # UK +44
            r'0\d{4}\s*\d{6}',        # UK landline
            r'07\d{3}\s*\d{6}',       # UK mobile
            r'\(\d{3,4}\)\s*\d{6,7}', # (0123) 456789
            r'\d{4}\s*\d{6}',         # 0123 456789
            r'\d{11}',                # 01234567890
        ]
        
        self.results = []
        
    def random_delay(self, min_sec=1, max_sec=3):
        """Random delay to avoid rate limiting"""
        time.sleep(random.uniform(min_sec, max_sec))
        
    def extract_contacts_from_text(self, text):
        """Extract emails and phones from text"""
        emails = re.findall(self.email_pattern, text, re.IGNORECASE)
        
        phones = []
        for pattern in self.phone_patterns:
            phones.extend(re.findall(pattern, text))
            
        # Clean and dedupe
        emails = list(set([email.lower() for email in emails if not any(skip in email.lower() for skip in ['@example', '@test', 'noreply', 'no-reply'])]))
        phones = list(set([re.sub(r'\s+', ' ', phone.strip()) for phone in phones]))
        
        return emails, phones
        
    def ddg_search_club(self, club_name):
        """Search DuckDuckGo for club contact info"""
        try:
            ddgs = DDGS()
            search_queries = [
                f'"{club_name}" contact email phone',
                f'"{club_name}" secretary manager coach contact',
                f'"{club_name}" football club contact details'
            ]
            
            all_emails = []
            all_phones = []
            websites = []
            
            for query in search_queries:
                try:
                    results = ddgs.text(query, max_results=5)
                    for result in results:
                        # Extract from title and snippet
                        text = f"{result.get('title', '')} {result.get('body', '')}"
                        emails, phones = self.extract_contacts_from_text(text)
                        all_emails.extend(emails)
                        all_phones.extend(phones)
                        
                        # Collect websites
                        if result.get('href'):
                            websites.append(result['href'])
                            
                    self.random_delay(0.5, 1.5)  # Short delay between searches
                except Exception as e:
                    logger.warning(f"DDG search failed for {query}: {e}")
                    continue
                    
            return list(set(all_emails)), list(set(all_phones)), websites[:3]
            
        except Exception as e:
            logger.error(f"DDG search failed for {club_name}: {e}")
            return [], [], []
            
    def scrape_website(self, url):
        """Scrape contact info from website"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for contact pages
            contact_links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.text.lower()
                if any(word in href or word in text for word in ['contact', 'about', 'staff', 'committee']):
                    full_url = urljoin(url, link['href'])
                    contact_links.append(full_url)
                    
            # Extract from main page
            page_text = soup.get_text()
            emails, phones = self.extract_contacts_from_text(page_text)
            
            # Check contact pages (first 2 only)
            for contact_url in contact_links[:2]:
                try:
                    contact_response = self.session.get(contact_url, timeout=8)
                    contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                    contact_text = contact_soup.get_text()
                    
                    contact_emails, contact_phones = self.extract_contacts_from_text(contact_text)
                    emails.extend(contact_emails)
                    phones.extend(contact_phones)
                    
                    self.random_delay(0.5, 1)
                except Exception as e:
                    logger.warning(f"Failed to scrape contact page {contact_url}: {e}")
                    continue
                    
            return list(set(emails)), list(set(phones))
            
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return [], []
            
    def process_club(self, club_name, club_id, country):
        """Process a single club through all strategies"""
        logger.info(f"Processing: {club_name} ({country})")
        
        result = {
            'club_name': club_name,
            'club_id': club_id,
            'country': country,
            'emails': [],
            'phones': [],
            'websites': [],
            'contact_found': False
        }
        
        try:
            # Strategy 1: DuckDuckGo search
            ddg_emails, ddg_phones, websites = self.ddg_search_club(club_name)
            result['emails'].extend(ddg_emails)
            result['phones'].extend(ddg_phones)
            result['websites'].extend(websites)
            
            # Strategy 2: Website scraping (if we found websites)
            for website in websites[:2]:  # Only check first 2 websites
                try:
                    web_emails, web_phones = self.scrape_website(website)
                    result['emails'].extend(web_emails)
                    result['phones'].extend(web_phones)
                    self.random_delay(1, 2)
                except Exception as e:
                    logger.warning(f"Website scraping failed for {website}: {e}")
                    continue
                    
            # Clean and dedupe final results
            result['emails'] = list(set(result['emails']))
            result['phones'] = list(set(result['phones']))
            result['websites'] = list(set(result['websites']))
            
            # Mark as successful if we found any contact info
            result['contact_found'] = len(result['emails']) > 0 or len(result['phones']) > 0
            
            if result['contact_found']:
                logger.info(f"✅ Found contacts for {club_name}: {len(result['emails'])} emails, {len(result['phones'])} phones")
            else:
                logger.info(f"❌ No contacts found for {club_name}")
                
        except Exception as e:
            logger.error(f"Failed to process {club_name}: {e}")
            
        return result
        
    def run_scraper(self, input_file='data/scotland_ni_ireland_targets.csv', output_file='data/fast_scraper_results.csv'):
        """Run the scraper on all clubs"""
        logger.info("🚀 Starting Fast Contact Scraper")
        
        # Load clubs
        df = pd.read_csv(input_file)
        total_clubs = len(df)
        logger.info(f"📊 Processing {total_clubs} clubs")
        
        start_time = time.time()
        
        for idx, row in df.iterrows():
            club_name = row['Club Name']
            club_id = row['Club Identifier']
            country = row['Country']
            
            result = self.process_club(club_name, club_id, country)
            self.results.append(result)
            
            # Progress update
            progress = (idx + 1) / total_clubs * 100
            elapsed = time.time() - start_time
            eta = elapsed / (idx + 1) * (total_clubs - idx - 1)
            
            logger.info(f"Progress: {idx + 1}/{total_clubs} ({progress:.1f}%) - ETA: {eta/60:.1f} min")
            
            # Save progress every 10 clubs
            if (idx + 1) % 10 == 0:
                self.save_results(output_file)
                
            # Random delay between clubs
            self.random_delay(2, 4)
            
        # Final save
        self.save_results(output_file)
        
        # Summary
        total_time = time.time() - start_time
        contacts_found = sum(1 for r in self.results if r['contact_found'])
        
        logger.info(f"🎯 SCRAPER COMPLETE!")
        logger.info(f"⏱️  Total time: {total_time/60:.1f} minutes")
        logger.info(f"📞 Contacts found: {contacts_found}/{total_clubs} ({contacts_found/total_clubs*100:.1f}%)")
        logger.info(f"💾 Results saved to: {output_file}")
        
        return self.results
        
    def save_results(self, output_file):
        """Save results to CSV"""
        if not self.results:
            return
            
        # Convert to DataFrame
        df_results = pd.DataFrame(self.results)
        
        # Create readable format
        df_export = pd.DataFrame({
            'Club Name': df_results['club_name'],
            'Country': df_results['country'],
            'Emails': df_results['emails'].apply(lambda x: '; '.join(x) if x else ''),
            'Phones': df_results['phones'].apply(lambda x: '; '.join(x) if x else ''),
            'Websites': df_results['websites'].apply(lambda x: '; '.join(x) if x else ''),
            'Contact Found': df_results['contact_found']
        })
        
        df_export.to_csv(output_file, index=False)
        logger.info(f"💾 Saved {len(df_export)} results to {output_file}")

def main():
    scraper = FastContactScraper()
    results = scraper.run_scraper()
    
    # Print summary
    contacts_found = sum(1 for r in results if r['contact_found'])
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"📞 Contacts found: {contacts_found}/{len(results)}")
    print(f"📊 Success rate: {contacts_found/len(results)*100:.1f}%")

if __name__ == "__main__":
    main()