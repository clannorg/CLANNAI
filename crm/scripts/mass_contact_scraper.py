#!/usr/bin/env python3
"""
MASS CONTACT SCRAPER - Based on Nick's winning approach
Scales his direct domain method to process ALL 3,177 clubs
NO search engines = NO blocking!
"""

import csv
import time
import re
import requests
import random
import pandas as pd
from typing import Optional, Tuple, List
import logging
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mass_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MassContactScraper:
    def __init__(self):
        self.results = []
        self.progress_file = 'mass_scraper_progress.json'
        self.results_file = 'mass_contacts_results.csv'
        self.lock = threading.Lock()
        
        # Multiple user agents to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Known club domains (from Nick's data + additions)
        self.known_domains = {
            'chelsea': 'https://www.chelseafc.com',
            'liverpool': 'https://www.liverpoolfc.com', 
            'arsenal': 'https://www.arsenal.com',
            'manchester united': 'https://www.manutd.com',
            'manchester city': 'https://www.mancity.com',
            'tottenham': 'https://www.tottenhamhotspur.com',
            'leicester': 'https://www.lcfc.com',
            'everton': 'https://www.evertonfc.com',
            'aston villa': 'https://www.avfc.co.uk',
            'leeds united': 'https://www.leedsunited.com',
            'burnley': 'https://www.burnleyfootballclub.com',
            'ipswich town': 'https://www.itfc.co.uk',
            'hearts': 'https://www.heartsfc.co.uk',
            'hibs': 'https://www.hibernianfc.co.uk',
            'rangers': 'https://www.rangers.co.uk',
            'celtic': 'https://www.celticfc.com'
        }

    def clean_club_name(self, club_name: str) -> str:
        """Clean club name for domain generation"""
        # Remove common suffixes and prefixes
        clean = re.sub(r'\b(fc|football club|f\.c\.|academy|youth|veo\d*)\b', '', club_name.lower())
        # Remove special characters and extra spaces
        clean = re.sub(r'[^\w\s]', '', clean).strip()
        # Replace spaces with nothing for domain
        clean = re.sub(r'\s+', '', clean)
        return clean

    def generate_domain_variants(self, club_name: str) -> List[str]:
        """Generate multiple domain variants for a club"""
        clean_name = self.clean_club_name(club_name)
        
        # Check known domains first
        for known, domain in self.known_domains.items():
            if known in club_name.lower():
                return [domain]
        
        variants = []
        
        # Standard patterns
        base_patterns = [
            f"https://www.{clean_name}.com",
            f"https://www.{clean_name}.co.uk", 
            f"https://{clean_name}.com",
            f"https://{clean_name}.co.uk",
            f"https://www.{clean_name}fc.com",
            f"https://www.{clean_name}fc.co.uk",
            f"https://www.{clean_name}football.com",
            f"https://www.{clean_name}football.co.uk"
        ]
        
        variants.extend(base_patterns)
        
        # Try with different word combinations if multiple words
        words = club_name.lower().split()
        if len(words) > 1:
            # First word only
            first_word = re.sub(r'[^\w]', '', words[0])
            variants.extend([
                f"https://www.{first_word}fc.com",
                f"https://www.{first_word}fc.co.uk",
                f"https://www.{first_word}.com",
                f"https://www.{first_word}.co.uk"
            ])
            
            # Last word if it's not common
            if words[-1] not in ['fc', 'football', 'club', 'academy', 'youth']:
                last_word = re.sub(r'[^\w]', '', words[-1])
                variants.extend([
                    f"https://www.{last_word}fc.com",
                    f"https://www.{last_word}fc.co.uk"
                ])
        
        return variants

    def extract_contacts_from_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract email and phone from a URL"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
            
            if response.status_code != 200:
                return None, None
                
            text = response.text.lower()
            
            # Extract emails - improved patterns
            email_patterns = [
                r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b',
                r'mailto:([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})'
            ]
            
            emails = set()
            for pattern in email_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    email = match if isinstance(match, str) else match
                    # Filter out junk emails
                    if not any(junk in email for junk in ['noreply', 'donotreply', 'example', 'test', 'sample', 'admin@wordpress']):
                        emails.add(email)
            
            # Extract phone numbers - UK focused
            phone_patterns = [
                r'\+44\s?[17]\d{8,9}',  # UK mobile/landline with +44
                r'\b0[17]\d{8,9}\b',    # UK mobile/landline
                r'\b0[2-9]\d{8,9}\b',   # UK landline
                r'\(0\d{3,4}\)\s?\d{6,7}',  # (01234) 567890 format
            ]
            
            phones = set()
            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # Clean phone number
                    clean_phone = re.sub(r'[^\d+]', '', match)
                    if len(clean_phone) >= 10:
                        phones.add(match.strip())
            
            best_email = list(emails)[0] if emails else None
            best_phone = list(phones)[0] if phones else None
            
            return best_email, best_phone
            
        except Exception as e:
            logger.debug(f"Error extracting from {url}: {e}")
            return None, None

    def find_club_website(self, club_name: str, recordings: int) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Find website and extract contacts for a club"""
        domain_variants = self.generate_domain_variants(club_name)
        
        for domain in domain_variants[:8]:  # Try first 8 variants
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.head(domain, timeout=5, headers=headers, allow_redirects=True)
                
                if response.status_code == 200:
                    logger.info(f"✅ Found website for {club_name}: {domain}")
                    
                    # Extract contacts from this domain
                    email, phone = self.extract_contacts_from_url(domain)
                    return domain, email, phone
                    
            except Exception as e:
                continue
        
        return None, None, None

    def process_club(self, club_data: dict) -> dict:
        """Process a single club"""
        club_name = club_data['Club Name']
        recordings = club_data.get('Recordings', 0)
        country = club_data.get('Country', 'Unknown')
        
        logger.info(f"🔍 Processing: {club_name} ({recordings} recordings)")
        
        website, email, phone = self.find_club_website(club_name, recordings)
        
        result = {
            'Club_Name': club_name,
            'Recordings': recordings,
            'Country': country,
            'Website': website or '',
            'Email': email or '',
            'Phone': phone or '',
            'Contact_Score': sum(1 for x in [website, email, phone] if x),
            'Status': 'Found' if website else 'Not Found'
        }
        
        if website or email or phone:
            logger.info(f"🎯 SUCCESS: {club_name} - Website: {bool(website)}, Email: {bool(email)}, Phone: {bool(phone)}")
        
        # Random delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 2.0))
        
        return result

    def save_progress(self, results: List[dict]):
        """Save current results"""
        with self.lock:
            # Save to CSV
            df = pd.DataFrame(results)
            df.to_csv(self.results_file, index=False)
            
            # Save progress metadata
            progress = {
                'total_processed': len(results),
                'clubs_with_websites': len([r for r in results if r['Website']]),
                'clubs_with_emails': len([r for r in results if r['Email']]),
                'clubs_with_phones': len([r for r in results if r['Phone']]),
                'timestamp': time.time()
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)

    def process_all_clubs(self, input_csv: str, max_workers: int = 10, max_clubs: int = None):
        """Process all clubs with parallel execution"""
        logger.info(f"🚀 Starting mass contact scraping from {input_csv}")
        
        # Load clubs data
        df = pd.read_csv(input_csv)
        clubs_data = df.to_dict('records')
        
        if max_clubs:
            clubs_data = clubs_data[:max_clubs]
        
        logger.info(f"📊 Processing {len(clubs_data)} clubs with {max_workers} workers")
        
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_club = {executor.submit(self.process_club, club): club for club in clubs_data}
            
            for i, future in enumerate(as_completed(future_to_club)):
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Save progress every 50 clubs
                    if len(results) % 50 == 0:
                        self.save_progress(results)
                        logger.info(f"💾 Saved progress: {len(results)}/{len(clubs_data)} clubs processed")
                        
                        # Print current stats
                        websites = len([r for r in results if r['Website']])
                        emails = len([r for r in results if r['Email']])
                        phones = len([r for r in results if r['Phone']])
                        
                        logger.info(f"📈 Current stats: {websites} websites, {emails} emails, {phones} phones")
                    
                except Exception as e:
                    logger.error(f"Error processing club: {e}")
        
        # Final save
        self.save_progress(results)
        
        # Print final summary
        websites = len([r for r in results if r['Website']])
        emails = len([r for r in results if r['Email']])
        phones = len([r for r in results if r['Phone']])
        
        logger.info(f"""
🎉 MASS SCRAPING COMPLETED!
📊 Final Results:
   - Total clubs processed: {len(results)}
   - Websites found: {websites} ({websites/len(results)*100:.1f}%)
   - Emails found: {emails} ({emails/len(results)*100:.1f}%)
   - Phones found: {phones} ({phones/len(results)*100:.1f}%)
   
📁 Results saved to: {self.results_file}
        """)

def main():
    """Run the mass contact scraper"""
    scraper = MassContactScraper()
    
    # Process Scottish and NI clubs first (smaller test)
    input_files = [
        '../data/scotland_clubs.csv',
        '../data/northern_ireland_clubs.csv'
    ]
    
    for input_file in input_files:
        if Path(input_file).exists():
            logger.info(f"Processing {input_file}")
            scraper.process_all_clubs(input_file, max_workers=20, max_clubs=100)  # Test with first 100
        else:
            logger.warning(f"File not found: {input_file}")

if __name__ == "__main__":
    main()