#!/usr/bin/env python3
"""
Quick Contact Lookup - Get contacts for top clubs
Focuses on most active clubs with better success rate
"""

import csv
import requests
import re
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import os

class QuickContactLookup:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # UK phone patterns
        self.phone_patterns = [
            r'\b(?:0|44|\+44)[\s\-\.]?(?:\d{2,4}[\s\-\.]?){2,3}\d{3,4}\b',
            r'\b01\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b',
            r'\b02\d{1}[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b',
            r'\b07\d{3}[\s\-\.]?\d{6}\b',
            r'\b\d{5}\s?\d{6}\b',
        ]
        
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.website_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        
    def extract_contacts(self, text):
        """Extract phone numbers, emails, and websites from text"""
        phones = set()
        emails = set()
        websites = set()
        
        # Find phone numbers
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean_phone = re.sub(r'[^\d+]', '', match)
                if len(clean_phone) >= 10:
                    phones.add(match.strip())
        
        # Find emails
        email_matches = re.findall(self.email_pattern, text, re.IGNORECASE)
        for email in email_matches:
            emails.add(email.lower())
            
        # Find websites
        website_matches = re.findall(self.website_pattern, text, re.IGNORECASE)
        for website in website_matches:
            if 'facebook.com' not in website.lower():
                websites.add(website.lower())
            
        return list(phones), list(emails), list(websites)
    
    def search_with_retry(self, query, max_retries=3):
        """Search with retry logic"""
        engines = [
            ('duckduckgo', f"https://duckduckgo.com/html/?q={quote_plus(query)}"),
            ('bing', f"https://www.bing.com/search?q={quote_plus(query)}"),
        ]
        
        for attempt in range(max_retries):
            for engine_name, url in engines:
                try:
                    time.sleep(random.uniform(5, 8))  # Longer delays
                    
                    response = self.session.get(url, headers=self.headers, timeout=25)
                    
                    if response.status_code == 200:
                        return response.text
                    else:
                        print(f"  ⚠️  {engine_name} returned status {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Error with {engine_name} (attempt {attempt+1}): {str(e)[:50]}")
                    continue
                    
        return ""
    
    def search_club_contacts(self, club_name, country):
        """Search for club contact information with better queries"""
        # More specific queries for better results
        queries = [
            f'"{club_name}" {country} contact phone email',
            f'"{club_name}" football club contact details',
            f'"{club_name}" {country} phone number',
            f'"{club_name}" official website contact',
        ]
        
        all_phones = set()
        all_emails = set()
        all_websites = set()
        
        for query in queries:
            print(f"    🔍 Searching: {query}")
            html_content = self.search_with_retry(query)
            
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                text = soup.get_text()
                
                phones, emails, websites = self.extract_contacts(text)
                all_phones.update(phones)
                all_emails.update(emails)
                all_websites.update(websites)
        
        return {
            'phones': list(all_phones)[:3],
            'emails': list(all_emails)[:3],
            'websites': list(all_websites)[:3],
        }
    
    def process_top_clubs(self, input_csv, output_csv, country, max_clubs=50):
        """Process top clubs for a specific country"""
        print(f"🚀 Processing top {country} clubs...")
        print(f"🎯 Target: {max_clubs} clubs with contacts")
        
        # Read and sort clubs by recordings
        clubs = []
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Country'] == country:
                    try:
                        recordings = int(row['Recordings'])
                        clubs.append((recordings, row))
                    except:
                        clubs.append((0, row))
        
        # Sort by recordings (highest first)
        clubs.sort(key=lambda x: x[0], reverse=True)
        clubs = [club[1] for club in clubs[:max_clubs]]
        
        print(f"📊 Found {len(clubs)} top {country} clubs to process")
        
        # Process clubs
        results = []
        processed = 0
        found_contacts = 0
        
        for i, club in enumerate(clubs):
            print(f"\n[{i+1}/{len(clubs)}] Processing: {club['Club Name']} ({club['Recordings']} recordings)")
            
            contacts = self.search_club_contacts(club['Club Name'], country)
            
            # Only save if we found some contacts
            if contacts['phones'] or contacts['emails'] or contacts['websites']:
                found_contacts += 1
                print(f"  ✅ Found contacts!")
                if contacts['phones']:
                    print(f"     📞 Phones: {', '.join(contacts['phones'][:2])}")
                if contacts['emails']:
                    print(f"     📧 Emails: {', '.join(contacts['emails'][:2])}")
                if contacts['websites']:
                    print(f"     🌐 Websites: {', '.join(contacts['websites'][:2])}")
            else:
                print(f"  ❌ No contacts found")
            
            # Save result
            result = {
                'Club_Name': club['Club Name'],
                'Recordings': club['Recordings'],
                'Country': country,
                'Location': club.get('Additional Info', ''),
                'Phones': '; '.join(contacts['phones']),
                'Emails': '; '.join(contacts['emails']),
                'Websites': '; '.join(contacts['websites']),
            }
            results.append(result)
            processed += 1
            
            # Save progress every 5 clubs
            if processed % 5 == 0:
                self.save_results(results, output_csv)
                print(f"💾 Saved progress: {processed} clubs processed, {found_contacts} with contacts")
        
        # Final save
        self.save_results(results, output_csv)
        
        print(f"\n✅ {country} Complete!")
        print(f"📊 Processed: {processed} clubs")
        print(f"📞 Found contacts: {found_contacts} clubs")
        print(f"📁 Saved to: {output_csv}")
        
        return found_contacts
    
    def save_results(self, results, output_csv):
        """Save results to CSV"""
        if not results:
            return
            
        fieldnames = ['Club_Name', 'Recordings', 'Country', 'Location', 'Phones', 'Emails', 'Websites']
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

def main():
    """Main function to process top clubs from each country"""
    lookup = QuickContactLookup()
    
    # Ensure output directory exists
    os.makedirs('data/contacts', exist_ok=True)
    
    countries = [
        ('England', 'data/england_clubs.csv', 'data/contacts/england_top_contacts.csv'),
        ('Scotland', 'data/scotland_clubs.csv', 'data/contacts/scotland_top_contacts.csv'),
        ('Northern Ireland', 'data/northern_ireland_clubs.csv', 'data/contacts/ni_top_contacts.csv'),
    ]
    
    total_found = 0
    
    for country, input_file, output_file in countries:
        if os.path.exists(input_file):
            found = lookup.process_top_clubs(input_file, output_file, country, max_clubs=50)
            total_found += found
        else:
            print(f"❌ Input file not found: {input_file}")
    
    print(f"\n🎯 Total contacts found: {total_found}")
    print("✅ All countries processed!")

if __name__ == "__main__":
    main() 