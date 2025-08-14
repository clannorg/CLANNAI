#!/usr/bin/env python3
"""
Enhanced Contact Scraper for England, Scotland, Northern Ireland
Gets phone numbers, emails, websites, social media for clubs
"""

import csv
import requests
import re
import time
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import os

class EnhancedContactScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Enhanced phone patterns for UK
        self.phone_patterns = [
            r'\b(?:0|44|\+44)[\s\-\.]?(?:\d{2,4}[\s\-\.]?){2,3}\d{3,4}\b',
            r'\b01\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b',  # UK landline
            r'\b02\d{1}[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b',  # UK landline
            r'\b07\d{3}[\s\-\.]?\d{6}\b',  # UK mobile
            r'\b028[\s\-\.]?\d{4}[\s\-\.]?\d{4}\b',  # NI specific
            r'\b0131[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b',  # Edinburgh
            r'\b0141[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b',  # Glasgow
            r'\b\d{5}\s?\d{6}\b',  # Standard UK format
            r'\b\d{4}\s?\d{3}\s?\d{3}\b'
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
                # Clean phone number
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
    
    def search_google(self, query):
        """Search Google for the given query"""
        try:
            # Use DuckDuckGo as Google alternative
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"  ⚠️  Search returned status {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"  ❌ Error searching: {e}")
            return ""
    
    def search_club_online(self, club_name, country, location=None):
        """Search for club contact information"""
        contacts = {
            'phones': [],
            'emails': [],
            'websites': [],
            'facebook': '',
            'search_queries': []
        }
        
        # Build search queries based on country
        if country == "Northern Ireland":
            search_terms = [
                f'{club_name} Northern Ireland contact phone email',
                f'{club_name} football club Belfast contact',
                f'{club_name} NI contact details',
            ]
        elif country == "Scotland":
            search_terms = [
                f'{club_name} Scotland contact phone email',
                f'{club_name} football club Scotland contact',
                f'{club_name} Scottish football contact',
            ]
        elif country == "England":
            search_terms = [
                f'{club_name} England contact phone email',
                f'{club_name} football club contact',
                f'{club_name} UK contact details',
            ]
        else:
            search_terms = [
                f'{club_name} contact phone email',
                f'{club_name} football club contact',
            ]
        
        if location:
            search_terms.append(f'{club_name} {location} contact')
        
        # Search and extract contacts
        for search_term in search_terms[:3]:  # Limit to 3 searches per club
            try:
                contacts['search_queries'].append(search_term)
                print(f"    🔍 Searching: {search_term}")
                
                html_content = self.search_google(search_term)
                if html_content:
                    phones, emails, websites = self.extract_contacts(html_content)
                    
                    # Add new contacts
                    for phone in phones:
                        if phone not in contacts['phones']:
                            contacts['phones'].append(phone)
                    
                    for email in emails:
                        if email not in contacts['emails']:
                            contacts['emails'].append(email)
                    
                    for website in websites:
                        if website not in contacts['websites']:
                            contacts['websites'].append(website)
                    
                    # Look for Facebook
                    if 'facebook.com' in html_content.lower():
                        contacts['facebook'] = 'Found'
                
            except Exception as e:
                print(f"    ❌ Error processing search: {e}")
                continue
        
        return contacts
    
    def process_clubs(self, input_csv, output_csv, country_filter=None, max_clubs=None):
        """Process clubs and find contact information"""
        clubs = []
        
        # Read clubs
        with open(input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if country_filter and row.get('Country') != country_filter:
                    continue
                clubs.append(row)
        
        if max_clubs:
            clubs = clubs[:max_clubs]
        
        print(f"🎯 Processing {len(clubs)} clubs for {country_filter or 'all countries'}")
        
        results = []
        for i, club in enumerate(clubs):
            print(f"\n[{i+1}/{len(clubs)}] Processing: {club['Club Name']} ({club.get('Country', 'Unknown')})")
            
            contacts = self.search_club_online(
                club['Club Name'], 
                club.get('Country', 'Unknown'),
                club.get('Additional Info', '')
            )
            
            # Create result row
            result = {
                'Club Name': club['Club Name'],
                'Recordings': club['Recordings'],
                'Country': club.get('Country', 'Unknown'),
                'Location': club.get('Additional Info', ''),
                'Phones': '; '.join(contacts['phones']),
                'Emails': '; '.join(contacts['emails']),
                'Websites': '; '.join(contacts['websites']),
                'Facebook': contacts['facebook'],
                'Search Queries': '; '.join(contacts['search_queries'])
            }
            
            results.append(result)
            
            # Save progress every 10 clubs
            if (i + 1) % 10 == 0:
                self.save_results(results, output_csv)
                print(f"💾 Saved progress: {len(results)} clubs processed")
            
            # Rate limiting
            time.sleep(random.uniform(3, 6))
        
        # Final save
        self.save_results(results, output_csv)
        print(f"\n✅ Complete! Processed {len(results)} clubs")
        
        return results
    
    def save_results(self, results, output_csv):
        """Save results to CSV"""
        if not results:
            return
            
        fieldnames = ['Club Name', 'Recordings', 'Country', 'Location', 'Phones', 'Emails', 'Websites', 'Facebook', 'Search Queries']
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

def main():
    scraper = EnhancedContactScraper()
    
    # Updated to use our current data files
    countries_files = {
        'Scotland': '../data/scotland_clubs.csv',
        'Northern Ireland': '../data/northern_ireland_clubs.csv'
    }
    
    for country, input_file in countries_files.items():
        print(f"\n🚀 Processing {country} clubs...")
        
        output_file = f'../data/contacts/{country.lower().replace(" ", "_")}_clubs_with_contacts_FULL.csv'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Process ALL clubs for these countries (no limit)
        results = scraper.process_clubs(
            input_csv=input_file,
            output_csv=output_file,
            country_filter=country,
            max_clubs=None  # Process ALL clubs
        )
        
        print(f"📊 {country}: {len(results)} clubs processed")

if __name__ == "__main__":
    main() 