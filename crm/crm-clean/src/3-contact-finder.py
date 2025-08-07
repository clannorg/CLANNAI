import pandas as pd
import requests
from googlesearch import search
import re
import time
from bs4 import BeautifulSoup
import logging
import json
from pathlib import Path
from urllib.parse import urljoin

class ContactFinder:
    def __init__(self):
        self.phone_patterns = [
            r'\+44\s?\d{4}\s?\d{6}',  # UK format
            r'0\d{3}\s?\d{3}\s?\d{4}',  # UK local
            r'0\d{4}\s?\d{6}',  # UK local alt
            r'07\d{3}\s?\d{6}',  # UK mobile
            r'\+1\s?\d{3}\s?\d{3}\s?\d{4}',  # US format
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # US local
            r'[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{4}'  # Generic
        ]
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.social_domains = {
            'facebook.com': 'Facebook',
            'twitter.com': 'Twitter',
            'instagram.com': 'Instagram',
            'youtube.com': 'YouTube'
        }
        self.contact_keywords = ['contact', 'get in touch', 'reach us', 'talk to us', 'connect']
        self.setup_logging()
        
        # Add progress tracking
        self.progress_file = Path('data/contact_finder_progress.json')
        self.processed_clubs = self.load_progress()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def setup_logging(self):
        logging.basicConfig(
            filename='data/contact_finder.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return set(json.load(f))
        return set()

    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(list(self.processed_clubs), f)

    def get_phone_context(self, soup, phone):
        # Find the element containing the phone number
        for element in soup.find_all(text=re.compile(phone)):
            # Get parent element
            parent = element.parent
            
            # Look for labels or headers nearby
            context = []
            
            # Check previous siblings for labels
            prev_sib = parent.find_previous_sibling()
            if prev_sib:
                if prev_sib.string:
                    context.append(prev_sib.string.strip())
                elif prev_sib.find('label'):
                    context.append(prev_sib.find('label').text.strip())
            
            # Check for containing div class names that might indicate purpose
            containing_div = parent.find_parent('div', class_=re.compile('contact|phone|tel|support|office|staff|coach|manager', re.I))
            if containing_div and containing_div.get('class'):
                context.extend(containing_div['class'])
            
            # Look for nearby text that might indicate the phone's purpose
            nearby_text = []
            for tag in parent.find_all_previous(text=True, limit=3):
                text = tag.strip()
                if text and len(text) < 50:  # Avoid long paragraphs
                    nearby_text.append(text)
            
            context.extend(nearby_text)
            
            # Clean and join context
            context = [c for c in context if c and not phone in c]
            if context:
                return ' | '.join(context)
        
        return 'General'

    def find_contact_page(self, soup, base_url):
        # Look for contact page links
        for keyword in self.contact_keywords:
            for link in soup.find_all('a', href=True, text=re.compile(keyword, re.I)):
                contact_url = urljoin(base_url, link['href'])
                try:
                    response = self.session.get(contact_url, timeout=10)
                    if response.ok:
                        return BeautifulSoup(response.text, 'html.parser')
                except:
                    continue
        return None

    def extract_contacts(self, soup, url):
        phones_with_context = []
        emails = set()
        
        # Get text content
        text = soup.get_text()
        
        # Look for structured contact info (common patterns)
        contact_sections = soup.find_all(['div', 'section'], class_=re.compile('contact|footer|address', re.I))
        
        for section in contact_sections:
            # Extract phones with context
            section_text = section.get_text()
            for pattern in self.phone_patterns:
                found = re.findall(pattern, section_text)
                for phone in found:
                    context = self.get_phone_context(section, phone)
                    if context:
                        phones_with_context.append(f"{phone} ({context})")
            
            # Extract emails from structured sections
            found_emails = re.findall(self.email_pattern, section_text)
            emails.update(found_emails)
        
        # Also check full page for any missed contacts
        for pattern in self.phone_patterns:
            found = re.findall(pattern, text)
            for phone in found:
                if not any(phone in p for p in phones_with_context):
                    phones_with_context.append(phone)
        
        page_emails = set(re.findall(self.email_pattern, text))
        emails.update(page_emails)
        
        # Filter out system emails
        emails = {e for e in emails if not any(x in e.lower() for x in ['sentry.io', 'wixpress.com', 'noreply', 'donotreply'])}
        
        return phones_with_context, list(emails)

    def find_club_contacts(self, club_name):
        try:
            social_links = {}
            contact_info = None
            
            queries = [
                f"{club_name} football club contact",
                f"{club_name} soccer club contact us",
                f"{club_name} club staff contacts"
            ]
            
            for query in queries:
                for url in search(query, num_results=5):  # Increased to catch more results
                    # Check if it's a social media link
                    for domain, platform in self.social_domains.items():
                        if domain in url.lower():
                            social_links[platform] = url
                            continue
                    
                    # If not social media, check for contact info
                    if not any(domain in url.lower() for domain in self.social_domains):
                        print(f"Checking {url}")
                        response = self.session.get(url, timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        phones, emails = self.extract_contacts(soup, url)
                        
                        contact_soup = self.find_contact_page(soup, url)
                        if contact_soup:
                            contact_phones, contact_emails = self.extract_contacts(contact_soup, url)
                            phones.extend(contact_phones)
                            emails.extend(contact_emails)
                        
                        if phones or emails:
                            contact_info = {
                                'Club Name': club_name,
                                'Phones': '; '.join(set(phones)),
                                'Emails': '; '.join(set(emails)),
                                'Website': url,
                                'Facebook': social_links.get('Facebook', ''),
                                'Twitter': social_links.get('Twitter', ''),
                                'Instagram': social_links.get('Instagram', ''),
                                'YouTube': social_links.get('YouTube', '')
                            }
                            break
                    
                    time.sleep(2)
                
                if contact_info:
                    break
            
            return contact_info
            
        except Exception as e:
            logging.error(f"Error processing {club_name}: {str(e)}")
        
        return None

def main():
    # Read feasible customers
    df = pd.read_csv('data/feasible_customers.csv')
    
    # Create data directory if it doesn't exist
    Path('data').mkdir(exist_ok=True)
    
    finder = ContactFinder()
    results = []
    
    # Load any existing results
    output_file = Path('data/all_club_contacts.csv')
    if output_file.exists():
        existing_results = pd.read_csv(output_file)
        results = existing_results.to_dict('records')
        print(f"Loaded {len(results)} existing results")
    
    # Filter for unprocessed clubs
    unprocessed_df = df[~df['Club Name'].isin(finder.processed_clubs)]
    print(f"Found {len(unprocessed_df)} clubs to process")
    
    try:
        # Process in batches of 50
        batch_size = 50
        for i in range(0, len(unprocessed_df), batch_size):
            batch = unprocessed_df.iloc[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({i}-{i+len(batch)})")
            
            for _, row in batch.iterrows():
                club_name = row['Club Name']
                print(f"Finding contacts for {club_name}...")
                
                result = finder.find_club_contacts(club_name)
                if result:
                    results.append(result)
                    print(f"Found contacts: {result['Phones']}")
                
                # Mark as processed and save progress
                finder.processed_clubs.add(club_name)
                finder.save_progress()
                
                # Save results after each club
                pd.DataFrame(results).to_csv('data/all_club_contacts.csv', index=False)
                
                time.sleep(1)
            
            print(f"Completed {len(finder.processed_clubs)} of {len(df)} clubs")
    
    except KeyboardInterrupt:
        print("\nScript interrupted! Progress saved.")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Progress has been saved.")
    finally:
        # Final save of results
        if results:
            pd.DataFrame(results).to_csv('data/all_club_contacts.csv', index=False)
            print(f"\nSaved results for {len(results)} clubs")

if __name__ == "__main__":
    main() 