#!/usr/bin/env python3
"""
Enhanced Clubs Data Enrichment Script

This script enhances the enhanced_clubs_england.csv file by:
1. Searching for club websites
2. Extracting contact email addresses and phone numbers
3. Properly categorizing football tiers (1=Premier League, 2=Championship, etc.)
4. Updating the original CSV file with new data

Author: AI Assistant
Date: 2024
"""

import csv
import time
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import json
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clubs_enhancement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ClubDataEnhancer:
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.backup_file_path = csv_file_path.replace('.csv', '_backup.csv')
        self.enhanced_file_path = csv_file_path.replace('.csv', '_enhanced.csv')
        
        # User agents for web scraping
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Football tier mapping
        self.football_tiers = {
            'Premier League': 1,
            'Championship': 2,
            'League One': 3,
            'League Two': 4,
            'National League': 5,
            'National League North': 5,
            'National League South': 5,
            'Isthmian League': 6,
            'Northern Premier League': 6,
            'Southern League': 6,
            'Unknown': 0
        }
        
        # Known club websites (to avoid unnecessary searches)
        self.known_clubs = {
            'Arsenal': 'https://www.arsenal.com',
            'Chelsea': 'https://www.chelseafc.com',
            'Manchester United': 'https://www.manutd.com',
            'Manchester City': 'https://www.mancity.com',
            'Liverpool': 'https://www.liverpoolfc.com',
            'Tottenham Hotspur': 'https://www.tottenhamhotspur.com',
            'Crystal Palace': 'https://www.cpfc.co.uk',
            'Burnley': 'https://www.burnleyfootballclub.com',
            'Blackburn Rovers': 'https://www.rovers.co.uk',
            'Ipswich Town': 'https://www.itfc.co.uk',
            'Fleetwood Town': 'https://www.fleetwoodtownfc.com',
            'Burton Albion': 'https://www.burtonalbionfc.co.uk',
            'Cheltenham Town': 'https://www.ctfc.com',
            'Mansfield Town': 'https://www.mansfieldtown.net',
            'Lincoln City': 'https://www.weareimps.com',
            'Exeter City': 'https://www.exetercityfc.co.uk',
            'Chatham Town': 'https://www.chathamtownfc.com',
            'Ilkley Town': 'https://www.ilkleytownafc.com'
        }
        
        # Load existing data
        self.load_data()
    
    def load_data(self):
        """Load the existing CSV data"""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            logger.info(f"Loaded {len(self.df)} clubs from {self.csv_file_path}")
            
            # Ensure text columns are properly typed as strings
            text_columns = ['Website', 'Emails', 'Phone Numbers', 'Football_Tier']
            for col in text_columns:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str)
                    # Replace 'nan' strings with empty strings
                    self.df[col] = self.df[col].replace('nan', '')
            
            # Create backup
            self.df.to_csv(self.backup_file_path, index=False)
            logger.info(f"Created backup at {self.backup_file_path}")
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            raise
    
    def search_club_website(self, club_name: str) -> Optional[str]:
        """Search for a club's website using various methods"""
        try:
            # First check known clubs
            for known_name, website in self.known_clubs.items():
                if known_name.lower() in club_name.lower():
                    return website
            
            # Try direct domain search
            clean_name = re.sub(r'[^\w\s]', '', club_name).lower()
            clean_name = re.sub(r'\s+', '', clean_name)
            
            potential_domains = [
                f"https://www.{clean_name}.com",
                f"https://www.{clean_name}.co.uk",
                f"https://{clean_name}.com",
                f"https://{clean_name}.co.uk",
                f"https://www.{clean_name}fc.com",
                f"https://www.{clean_name}fc.co.uk"
            ]
            
            for domain in potential_domains:
                try:
                    response = requests.get(domain, timeout=10, headers={'User-Agent': random.choice(self.user_agents)})
                    if response.status_code == 200:
                        logger.info(f"Found website for {club_name}: {domain}")
                        return domain
                except:
                    continue
            
            # Try Google search (simplified approach)
            search_query = f"{club_name} official website football club"
            # Note: In production, you'd use a proper search API
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for website for {club_name}: {e}")
            return None
    
    def extract_contact_info(self, website: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract email and phone from a website"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = requests.get(website, timeout=15, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, response.text)
            
            # Filter out common non-contact emails
            filtered_emails = []
            for email in emails:
                if not any(exclude in email.lower() for exclude in ['noreply', 'donotreply', 'example', 'test']):
                    filtered_emails.append(email)
            
            # Extract phone numbers
            phone_patterns = [
                r'(\+44\s?1\d{3}\s?\d{3}\s?\d{4})',  # UK mobile
                r'(\+44\s?\d{4}\s?\d{3}\s?\d{3})',   # UK landline
                r'(0\d{4}\s?\d{3}\s?\d{3})',          # UK landline without country code
                r'(0\d{3}\s?\d{3}\s?\d{4})',          # UK mobile without country code
            ]
            
            phones = []
            for pattern in phone_patterns:
                phones.extend(re.findall(pattern, response.text))
            
            # Clean up phone numbers
            cleaned_phones = []
            for phone in phones:
                cleaned = re.sub(r'\s+', '', phone)
                if len(cleaned) >= 10:
                    cleaned_phones.append(cleaned)
            
            email = filtered_emails[0] if filtered_emails else ''
            phone = cleaned_phones[0] if cleaned_phones else ''
            
            if email or phone:
                logger.info(f"Extracted contact info from {website}: email={email}, phone={phone}")
            
            return email, phone
            
        except Exception as e:
            logger.error(f"Error extracting contact info from {website}: {e}")
            return '', ''
    
    def categorize_football_tier(self, club_name: str, existing_tier: str) -> Tuple[str, int, float]:
        """Categorize the football tier of a club"""
        try:
            # If we already have a good tier, use it
            if existing_tier in self.football_tiers and existing_tier != 'Unknown':
                tier_number = self.football_tiers[existing_tier]
                return existing_tier, tier_number, 0.9
            
            # Try to categorize based on club name patterns
            club_lower = club_name.lower()
            
            # Premier League clubs (current and recent)
            premier_league_clubs = [
                'arsenal', 'chelsea', 'manchester united', 'manchester city', 'liverpool',
                'tottenham', 'crystal palace', 'burnley', 'newcastle', 'everton',
                'west ham', 'brighton', 'wolves', 'aston villa', 'leeds', 'southampton',
                'fulham', 'brentford', 'bournemouth', 'nottingham forest', 'leicester'
            ]
            
            # Championship clubs
            championship_clubs = [
                'blackburn rovers', 'ipswich town', 'fleetwood town', 'burton albion',
                'cheltenham town', 'mansfield town', 'lincoln city', 'exeter city',
                'bristol city', 'cardiff city', 'swansea city', 'hull city',
                'middlesbrough', 'stoke city', 'birmingham city', 'huddersfield'
            ]
            
            # League One clubs
            league_one_clubs = [
                'chatham town', 'ilkley town', 'bradford city', 'bristol rovers',
                'burton albion', 'carlisle united', 'charlton athletic', 'cheltenham town',
                'derby county', 'exeter city', 'fleetwood town', 'lincoln city'
            ]
            
            # Check against known tiers
            for club in premier_league_clubs:
                if club in club_lower:
                    return 'Premier League', 1, 0.9
            
            for club in championship_clubs:
                if club in club_lower:
                    return 'Championship', 2, 0.9
            
            for club in league_one_clubs:
                if club in club_lower:
                    return 'League One', 3, 0.9
            
            # Check for academy/youth indicators
            if any(indicator in club_lower for indicator in ['academy', 'youth', 'under', 'u18', 'u21']):
                return 'Academy/Youth', 0, 0.7
            
            # Check for non-league indicators
            if any(indicator in club_lower for indicator in ['town', 'united', 'rovers', 'athletic']):
                return 'Non-League', 6, 0.6
            
            return 'Unknown', 0, 0.3
            
        except Exception as e:
            logger.error(f"Error categorizing tier for {club_name}: {e}")
            return 'Unknown', 0, 0.3
    
    def enhance_club_data(self, club_name: str, existing_data: Dict) -> Dict:
        """Enhance data for a single club"""
        enhanced_data = existing_data.copy()
        
        try:
            # Search for website
            website = self.search_club_website(club_name)
            if website:
                enhanced_data['Website'] = website
                
                # Extract contact information
                email, phone = self.extract_contact_info(website)
                if email:
                    enhanced_data['Emails'] = email
                if phone:
                    enhanced_data['Phone Numbers'] = phone
                
                # Update contact quality
                contact_quality = 0
                if website:
                    contact_quality += 1
                if email:
                    contact_quality += 1
                if phone:
                    contact_quality += 1
                enhanced_data['Contact_Quality'] = contact_quality
            
            # Categorize football tier
            tier_name, tier_number, tier_confidence = self.categorize_football_tier(
                club_name, 
                existing_data.get('Football_Tier', 'Unknown')
            )
            
            enhanced_data['Football_Tier'] = tier_name
            enhanced_data['Tier_Number'] = tier_number
            enhanced_data['Tier_Confidence'] = tier_confidence
            
            logger.info(f"Enhanced data for {club_name}: website={website}, tier={tier_name}")
            
        except Exception as e:
            logger.error(f"Error enhancing data for {club_name}: {e}")
        
        return enhanced_data
    
    def process_all_clubs(self, start_index: int = 0, batch_size: int = 50):
        """Process all clubs in batches"""
        total_clubs = len(self.df)
        logger.info(f"Starting enhancement of {total_clubs} clubs from index {start_index}")
        
        for i in range(start_index, total_clubs, batch_size):
            end_index = min(i + batch_size, total_clubs)
            logger.info(f"Processing batch {i//batch_size + 1}: clubs {i+1} to {end_index}")
            
            for j in range(i, end_index):
                club_name = self.df.iloc[j]['Club Name']
                existing_data = self.df.iloc[j].to_dict()
                
                # Skip if already enhanced
                if existing_data.get('Website') and existing_data.get('Contact_Quality', 0) > 0:
                    logger.info(f"Skipping {club_name} - already enhanced")
                    continue
                
                enhanced_data = self.enhance_club_data(club_name, existing_data)
                
                # Update the dataframe
                for key, value in enhanced_data.items():
                    if key in self.df.columns:
                        self.df.at[j, key] = value
                
                # Save progress every 10 clubs
                if (j - i + 1) % 10 == 0:
                    self.save_progress()
                
                # Rate limiting
                time.sleep(random.uniform(1, 3))
            
            # Save batch progress
            self.save_progress()
            logger.info(f"Completed batch {i//batch_size + 1}")
            
            # Save enhanced version
            self.df.to_csv(self.enhanced_file_path, index=False)
            logger.info(f"Saved enhanced data to {self.enhanced_file_path}")
    
    def save_progress(self):
        """Save current progress"""
        try:
            self.df.to_csv(self.csv_file_path, index=False)
            logger.info("Progress saved")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def generate_summary_report(self):
        """Generate a summary report of the enhancement"""
        try:
            total_clubs = len(self.df)
            clubs_with_website = len(self.df[self.df['Website'].notna() & (self.df['Website'] != '')])
            clubs_with_email = len(self.df[self.df['Emails'].notna() & (self.df['Emails'] != '')])
            clubs_with_phone = len(self.df[self.df['Phone Numbers'].notna() & (self.df['Phone Numbers'] != '')])
            
            # Tier distribution
            tier_counts = self.df['Football_Tier'].value_counts()
            
            report = {
                'total_clubs': total_clubs,
                'clubs_with_website': clubs_with_website,
                'clubs_with_email': clubs_with_email,
                'clubs_with_phone': clubs_with_phone,
                'website_coverage': f"{(clubs_with_website/total_clubs)*100:.1f}%",
                'email_coverage': f"{(clubs_with_email/total_clubs)*100:.1f}%",
                'phone_coverage': f"{(clubs_with_phone/total_clubs)*100:.1f}%",
                'tier_distribution': tier_counts.to_dict()
            }
            
            # Save report
            with open('enhancement_summary.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("Enhancement summary report generated")
            return report
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return None

def main():
    """Main function to run the enhancement process"""
    try:
        # Initialize enhancer
        enhancer = ClubDataEnhancer('enhanced_clubs_england.csv')
        
        # Process all clubs
        enhancer.process_all_clubs(start_index=0, batch_size=50)
        
        # Generate summary report
        summary = enhancer.generate_summary_report()
        if summary:
            logger.info("Enhancement completed successfully!")
            logger.info(f"Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Enhancement process failed: {e}")
        raise

if __name__ == "__main__":
    main()
