#!/usr/bin/env python3
"""
STAGE 2: Location Sorter
Categorizes clubs by country/region and calculates activity scores
Input: data/1-veo-scraper/veo_clubs.csv
Output: data/2-by-country/clubs_*.csv
"""

import pandas as pd
import re
from pathlib import Path
import logging

class LocationSorter:
    def __init__(self):
        self.setup_logging()
        
        # Location keywords for classification
        self.location_patterns = {
            'Northern Ireland': [
                'belfast', 'derry', 'lisburn', 'newry', 'armagh', 'omagh', 'craigavon',
                'ballymena', 'newtownabbey', 'carrickfergus', 'coleraine', 'antrim',
                'larne', 'magherafelt', 'dungannon', 'limavady', 'cookstown', 'ni fc',
                'northern ireland', 'ulster'
            ],
            'Ireland': [
                'dublin', 'cork', 'galway', 'waterford', 'limerick', 'kilkenny',
                'wexford', 'sligo', 'drogheda', 'dundalk', 'bray', 'navan',
                'republic of ireland', 'eire', 'irish'
            ],
            'Scotland': [
                'glasgow', 'edinburgh', 'aberdeen', 'dundee', 'stirling', 'perth',
                'inverness', 'falkirk', 'hamilton', 'ayr', 'kilmarnock', 'paisley',
                'scotland', 'scottish', 'highland', 'rangers', 'celtic'
            ],
            'Wales': [
                'cardiff', 'swansea', 'newport', 'wrexham', 'barry', 'rhondda',
                'caerphilly', 'bridgend', 'neath', 'port talbot', 'llanelli',
                'wales', 'welsh', 'cymru'
            ],
            'England': [
                'london', 'manchester', 'liverpool', 'birmingham', 'leeds', 'sheffield',
                'bristol', 'leicester', 'coventry', 'bradford', 'stoke', 'wolverhampton',
                'plymouth', 'derby', 'southampton', 'portsmouth', 'norwich', 'luton',
                'english', 'england'
            ],
            'United States': [
                'fc', 'soccer club', 'united states', 'usa', 'california', 'texas',
                'florida', 'new york', 'illinois', 'pennsylvania', 'ohio', 'georgia',
                'michigan', 'virginia', 'washington', 'arizona', 'massachusetts'
            ]
        }
        
    def setup_logging(self):
        """Setup logging"""
        Path('data/2-by-country').mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler('data/2-by-country/location_sorter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def classify_location(self, club_name):
        """
        Classify club location based on name patterns
        Returns: country name or 'Unknown'
        """
        if not club_name or club_name in ['-', '_', '']:
            return 'Unknown'
            
        club_lower = club_name.lower()
        
        # Check each location pattern
        for country, keywords in self.location_patterns.items():
            for keyword in keywords:
                if keyword in club_lower:
                    return country
                    
        # Default classification logic
        if any(word in club_lower for word in ['fc', 'united', 'city', 'rovers', 'town']):
            return 'England'  # Most common for these patterns
            
        return 'Unknown'
        
    def add_location_scores(self, df):
        """Add activity and location scores to dataframe"""
        # Handle missing Teams column
        if 'Teams' not in df.columns:
            df['Teams'] = 0  # Default to 0 if no teams data
            
        # Calculate activity score (100% recordings if no teams data, otherwise 70/30 split)
        if df['Teams'].sum() == 0:
            df['Activity_Score'] = df['Recordings'].astype(float).round(2)
        else:
            df['Activity_Score'] = (
                df['Recordings'] * 0.7 + 
                df['Teams'] * 0.3
            ).round(2)
        
        # Add location classification
        df['Country'] = df['Club Name'].apply(self.classify_location)
        
        return df
        
    def sort_by_location(self, input_file='data/1-veo-scraper/veo_clubs.csv', output_file='data/2-by-country/clubs_by_location.csv'):
        """
        Sort clubs by location and add scores
        """
        self.logger.info(f"🌍 STAGE 2: Sorting {input_file} by location...")
        
        try:
            # Read input file
            df = pd.read_csv(input_file)
            self.logger.info(f"📚 Loaded {len(df)} clubs from {input_file}")
            
            # Clean up club names
            df = df[df['Club Name'].notna()]  # Remove NaN club names
            df = df[~df['Club Name'].isin(['-', '_', ''])]  # Remove placeholder names
            
            # Add location and scoring
            df = self.add_location_scores(df)
            
            # Sort by activity score (highest first within each country)
            df = df.sort_values(['Country', 'Activity_Score'], ascending=[True, False])
            
            # Save results
            df.to_csv(output_file, index=False)
            
            # Generate summary
            summary = df.groupby('Country').agg({
                'Club Name': 'count',
                'Recordings': 'sum',
                'Activity_Score': 'mean'
            }).round(2)
            
            if 'Teams' in df.columns:
                summary['Total_Teams'] = df.groupby('Country')['Teams'].sum()
            
            summary.columns = ['Total_Clubs', 'Total_Recordings', 'Avg_Activity_Score'] + (['Total_Teams'] if 'Teams' in df.columns else [])
            
            self.logger.info(f"✅ Saved {len(df)} clubs to {output_file}")
            print("\n📊 STAGE 2 RESULTS - Country Summary:")
            print(summary.to_string())
            
            return output_file, summary
            
        except Exception as e:
            self.logger.error(f"Location sorting failed: {e}")
            return None, None
            
    def create_country_files(self, input_file='data/2-by-country/clubs_by_location.csv'):
        """Create separate files for each country"""
        try:
            df = pd.read_csv(input_file)
            
            output_files = {}
            for country in df['Country'].unique():
                if country != 'Unknown':
                    country_df = df[df['Country'] == country]
                    filename = f"data/2-by-country/clubs_{country.lower().replace(' ', '_')}.csv"
                    country_df.to_csv(filename, index=False)
                    output_files[country] = filename
                    self.logger.info(f"📁 Created {filename} with {len(country_df)} clubs")
                    
            return output_files
            
        except Exception as e:
            self.logger.error(f"Failed to create country files: {e}")
            return {}

def main():
    """Run the location sorter"""
    print("🎯 STAGE 2: LOCATION SORTER")
    print("=" * 40)
    print("This will sort clubs by country and calculate activity scores")
    print("Input: data/1-veo-scraper/veo_clubs.csv")
    print("Output: data/2-by-country/clubs_*.csv")
    print()
    
    sorter = LocationSorter()
    
    # Check if input file exists
    input_file = 'data/1-veo-scraper/veo_clubs.csv'
    if not Path(input_file).exists():
        print(f"❌ Input file {input_file} not found!")
        print("Run '1-veo-scraper.py' first to generate club data")
        return
        
    # Sort by location
    output_file, summary = sorter.sort_by_location()
    
    if output_file:
        print(f"\n✅ STAGE 2 COMPLETE!")
        print(f"📊 Main file: {output_file}")
        
        # Create individual country files
        country_files = sorter.create_country_files(output_file)
        if country_files:
            print(f"\n📁 Created {len(country_files)} country-specific files:")
            for country, filename in country_files.items():
                print(f"  • {country}: {filename}")
        
        print(f"\n➡️  Next: Run '3-contact-finder.py'")
    else:
        print("❌ Location sorting failed")

if __name__ == "__main__":
    main()