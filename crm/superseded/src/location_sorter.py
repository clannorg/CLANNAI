#!/usr/bin/env python3
"""
Essential Location Sorter
Categorizes clubs by country/region using simple text analysis
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
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler('data/location_sorter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def classify_location(self, club_name):
        """
        Classify club location based on name patterns
        Returns: country name or 'Unknown'
        """
        if not club_name:
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
        # Calculate activity score
        df['Activity_Score'] = (
            df['Recordings'] * 0.7 + 
            df['Teams'] * 0.3
        ).round(2)
        
        # Add location classification
        df['Country'] = df['Club Name'].apply(self.classify_location)
        
        return df
        
    def sort_by_location(self, input_file='data/veo_clubs.csv', output_file='data/clubs_by_location.csv'):
        """
        Sort clubs by location and add scores
        """
        self.logger.info(f"📍 Sorting clubs by location...")
        
        try:
            # Read input file
            df = pd.read_csv(input_file)
            self.logger.info(f"Loaded {len(df)} clubs from {input_file}")
            
            # Add location and scoring
            df = self.add_location_scores(df)
            
            # Sort by activity score (highest first)
            df = df.sort_values(['Country', 'Activity_Score'], ascending=[True, False])
            
            # Save results
            df.to_csv(output_file, index=False)
            
            # Generate summary
            summary = df.groupby('Country').agg({
                'Club Name': 'count',
                'Recordings': 'sum',
                'Teams': 'sum',
                'Activity_Score': 'mean'
            }).round(2)
            
            summary.columns = ['Total_Clubs', 'Total_Recordings', 'Total_Teams', 'Avg_Activity_Score']
            
            self.logger.info(f"✅ Saved {len(df)} clubs to {output_file}")
            print("\n📊 Location Summary:")
            print(summary.to_string())
            
            return output_file, summary
            
        except Exception as e:
            self.logger.error(f"Location sorting failed: {e}")
            return None, None
            
    def create_country_files(self, input_file='data/clubs_by_location.csv'):
        """Create separate files for each country"""
        try:
            df = pd.read_csv(input_file)
            
            output_files = {}
            for country in df['Country'].unique():
                if country != 'Unknown':
                    country_df = df[df['Country'] == country]
                    filename = f"data/clubs_{country.lower().replace(' ', '_')}.csv"
                    country_df.to_csv(filename, index=False)
                    output_files[country] = filename
                    self.logger.info(f"Created {filename} with {len(country_df)} clubs")
                    
            return output_files
            
        except Exception as e:
            self.logger.error(f"Failed to create country files: {e}")
            return {}

def main():
    """Run the location sorter"""
    # Create data directory
    Path('data').mkdir(exist_ok=True)
    
    sorter = LocationSorter()
    
    # Check if input file exists
    input_file = 'data/veo_clubs.csv'
    if not Path(input_file).exists():
        print(f"❌ Input file {input_file} not found!")
        print("Run club_scraper.py first to generate club data")
        return
        
    # Sort by location
    output_file, summary = sorter.sort_by_location()
    
    if output_file:
        print(f"\n🎯 Location sorting complete!")
        print(f"📊 Clubs sorted by location: {output_file}")
        
        # Create individual country files
        country_files = sorter.create_country_files(output_file)
        if country_files:
            print(f"\n📁 Created {len(country_files)} country-specific files:")
            for country, filename in country_files.items():
                print(f"  • {country}: {filename}")
    else:
        print("❌ Location sorting failed")

if __name__ == "__main__":
    main()