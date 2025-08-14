#!/usr/bin/env python3
"""
MEGA 27K CLUBS SCRAPER - Scale Nick's approach to ALL 27,675 clubs!
Expected results: ~11,000 websites, ~3,000 emails, ~800 phones
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
import signal
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mega_27k_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Mega27KScraper:
    def __init__(self):
        self.results = []
        self.progress_file = 'mega_27k_progress.json'
        self.results_file = 'mega_27k_contacts.csv'
        self.checkpoint_file = 'mega_27k_checkpoint.csv'
        self.lock = threading.Lock()
        self.stop_requested = False
        
        # Optimized for mass processing
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Expanded known domains for better coverage
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
            'celtic': 'https://www.celticfc.com',
            'crusaders': 'https://www.crusadersfc.com',
            'glentoran': 'https://www.glentoran.com',
            'linfield': 'https://www.linfieldfc.com',
            'ballymena': 'https://www.ballymenaunitedfc.com',
            'coleraine': 'https://www.colerainefcchelseafc.com',
            # Add more as we discover them
        }
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        logger.info("🛑 Shutdown signal received. Saving progress...")
        self.stop_requested = True

    def clean_club_name(self, club_name: str) -> str:
        """Clean club name for domain generation"""
        if not club_name or club_name in ['-', '_', '---']:
            return ''
        
        # Remove common suffixes and prefixes
        clean = re.sub(r'\b(fc|football club|f\.c\.|academy|youth|veo\d*|united|rovers|athletic|town|city)\b', '', club_name.lower())
        # Remove special characters and extra spaces
        clean = re.sub(r'[^\w\s]', '', clean).strip()
        # Replace spaces with nothing for domain
        clean = re.sub(r'\s+', '', clean)
        return clean

    def generate_fast_domain_variants(self, club_name: str) -> List[str]:
        """Generate domain variants optimized for speed"""
        if not club_name or club_name in ['-', '_', '---']:
            return []
            
        clean_name = self.clean_club_name(club_name)
        if not clean_name or len(clean_name) < 3:
            return []
        
        # Check known domains first (fastest)
        for known, domain in self.known_domains.items():
            if known in club_name.lower():
                return [domain]
        
        # Generate top variants only (limit to 6 for speed)
        variants = [
            f"https://www.{clean_name}fc.com",
            f"https://www.{clean_name}fc.co.uk",
            f"https://www.{clean_name}.com",
            f"https://www.{clean_name}.co.uk",
            f"https://{clean_name}fc.com",
            f"https://{clean_name}.com"
        ]
        
        return variants

    def fast_extract_contacts(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Fast contact extraction optimized for mass processing"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            # Reduced timeout for speed
            response = requests.get(url, timeout=5, headers=headers, allow_redirects=True)
            
            if response.status_code != 200:
                return None, None
                
            text = response.text.lower()
            
            # Fast email extraction
            email_match = re.search(r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b', text)
            email = email_match.group() if email_match else None
            
            # Filter out junk emails quickly
            if email and any(junk in email for junk in ['noreply', 'donotreply', 'example', 'test', 'wordpress']):
                email = None
            
            # Fast phone extraction (UK only for speed)
            phone_match = re.search(r'\b0[17]\d{8,9}\b', text)
            phone = phone_match.group() if phone_match else None
            
            return email, phone
            
        except Exception:
            return None, None

    def process_club_fast(self, club_data: dict) -> dict:
        """Fast processing for a single club"""
        club_name = club_data.get('Club Name', '')
        recordings = club_data.get('Recordings', 0)
        
        if not club_name or club_name in ['-', '_', '---']:
            return {
                'Club_Name': club_name,
                'Recordings': recordings,
                'Website': '',
                'Email': '',
                'Phone': '',
                'Status': 'Skipped'
            }
        
        domain_variants = self.generate_fast_domain_variants(club_name)
        
        for domain in domain_variants[:4]:  # Only try first 4 for speed
            if self.stop_requested:
                break
                
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = requests.head(domain, timeout=3, headers=headers, allow_redirects=True)
                
                if response.status_code == 200:
                    # Found website, try to extract contacts
                    email, phone = self.fast_extract_contacts(domain)
                    
                    return {
                        'Club_Name': club_name,
                        'Recordings': recordings,
                        'Website': domain,
                        'Email': email or '',
                        'Phone': phone or '',
                        'Status': 'Success'
                    }
                    
            except Exception:
                continue
        
        return {
            'Club_Name': club_name,
            'Recordings': recordings,
            'Website': '',
            'Email': '',
            'Phone': '',
            'Status': 'No Website'
        }

    def save_progress(self, results: List[dict]):
        """Save current results and progress"""
        with self.lock:
            if not results:
                return
                
            # Save to CSV
            df = pd.DataFrame(results)
            df.to_csv(self.results_file, index=False)
            
            # Save checkpoint (last 1000 results for quick recovery)
            if len(results) > 1000:
                checkpoint_df = df.tail(1000)
                checkpoint_df.to_csv(self.checkpoint_file, index=False)
            
            # Save progress metadata
            websites = len([r for r in results if r['Website']])
            emails = len([r for r in results if r['Email']])
            phones = len([r for r in results if r['Phone']])
            
            progress = {
                'total_processed': len(results),
                'clubs_with_websites': websites,
                'clubs_with_emails': emails,
                'clubs_with_phones': phones,
                'website_rate': f"{websites/len(results)*100:.1f}%" if results else "0%",
                'email_rate': f"{emails/len(results)*100:.1f}%" if results else "0%",
                'phone_rate': f"{phones/len(results)*100:.1f}%" if results else "0%",
                'timestamp': time.time()
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress, f, indent=2)

    def process_mega_batch(self, input_csv: str, max_workers: int = 50, start_index: int = 0):
        """Process all 27K clubs with optimized parallel execution"""
        logger.info(f"🚀 MEGA 27K SCRAPER STARTING!")
        logger.info(f"📁 Input file: {input_csv}")
        logger.info(f"⚡ Workers: {max_workers}")
        logger.info(f"🎯 Expected results: ~11K websites, ~3K emails")
        
        # Load clubs data
        df = pd.read_csv(input_csv)
        clubs_data = df.iloc[start_index:].to_dict('records')
        
        logger.info(f"📊 Processing {len(clubs_data)} clubs starting from index {start_index}")
        
        results = []
        batch_size = 1000  # Process in batches of 1000
        
        for batch_start in range(0, len(clubs_data), batch_size):
            if self.stop_requested:
                logger.info("🛑 Stopping due to shutdown request")
                break
                
            batch_end = min(batch_start + batch_size, len(clubs_data))
            batch_clubs = clubs_data[batch_start:batch_end]
            
            logger.info(f"🔄 Processing batch {batch_start//batch_size + 1}: clubs {start_index + batch_start + 1} to {start_index + batch_end}")
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_club = {executor.submit(self.process_club_fast, club): club for club in batch_clubs}
                
                batch_results = []
                for future in as_completed(future_to_club):
                    if self.stop_requested:
                        break
                        
                    try:
                        result = future.result()
                        batch_results.append(result)
                        
                        # Log successful finds
                        if result['Website']:
                            logger.info(f"✅ {result['Club_Name']}: {result['Website']}")
                            if result['Email']:
                                logger.info(f"📧 Email: {result['Email']}")
                            if result['Phone']:
                                logger.info(f"📞 Phone: {result['Phone']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing club: {e}")
                
                # Add batch results
                results.extend(batch_results)
                
                # Save progress after each batch
                self.save_progress(results)
                
                # Print batch summary
                batch_websites = len([r for r in batch_results if r['Website']])
                batch_emails = len([r for r in batch_results if r['Email']])
                batch_phones = len([r for r in batch_results if r['Phone']])
                
                total_websites = len([r for r in results if r['Website']])
                total_emails = len([r for r in results if r['Email']])
                total_phones = len([r for r in results if r['Phone']])
                
                logger.info(f"""
📊 Batch {batch_start//batch_size + 1} completed:
   Batch: {batch_websites} websites, {batch_emails} emails, {batch_phones} phones
   Total: {total_websites} websites ({total_websites/len(results)*100:.1f}%), {total_emails} emails ({total_emails/len(results)*100:.1f}%), {total_phones} phones ({total_phones/len(results)*100:.1f}%)
   Progress: {len(results)}/{len(clubs_data)} clubs ({len(results)/len(clubs_data)*100:.1f}%)
                """)
                
                # Small delay between batches
                if not self.stop_requested:
                    time.sleep(2)
        
        # Final save and summary
        self.save_progress(results)
        
        total_websites = len([r for r in results if r['Website']])
        total_emails = len([r for r in results if r['Email']])
        total_phones = len([r for r in results if r['Phone']])
        
        logger.info(f"""
🎉 MEGA 27K SCRAPING COMPLETED!
📊 Final Results:
   - Total clubs processed: {len(results)}
   - Websites found: {total_websites} ({total_websites/len(results)*100:.1f}%)
   - Emails found: {total_emails} ({total_emails/len(results)*100:.1f}%)
   - Phones found: {total_phones} ({total_phones/len(results)*100:.1f}%)
   
📁 Results saved to: {self.results_file}
📁 Progress log: {self.progress_file}
🔥 Estimated final totals if this rate continues:
   - ~{int(total_websites/len(results)*27000)} total websites
   - ~{int(total_emails/len(results)*27000)} total emails
   - ~{int(total_phones/len(results)*27000)} total phones
        """)

def main():
    """Run the mega 27K scraper"""
    scraper = Mega27KScraper()
    
    input_file = '../data/raw/veo_clubs_27k.csv'
    
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        return
    
    # Start processing all 27K clubs
    scraper.process_mega_batch(
        input_csv=input_file,
        max_workers=50,  # Aggressive parallel processing
        start_index=0
    )

if __name__ == "__main__":
    main()