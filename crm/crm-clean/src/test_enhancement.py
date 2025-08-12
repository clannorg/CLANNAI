#!/usr/bin/env python3
"""
Test script for the clubs enhancement functionality
This script tests the enhancement on a small subset of clubs first
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhance_clubs_data import ClubDataEnhancer
import pandas as pd

def test_enhancement():
    """Test the enhancement on a small subset"""
    
    # Create a test CSV with just a few clubs
    test_data = {
        'Club Name': [
            'Arsenal Football Club PLC',
            'Chelsea Academy VEO',
            'Manchester City FC',
            'Blackburn Rovers',
            'Ipswich Town FC',
            'Test Club Unknown'
        ],
        'Recordings': [1229, 2466, 1626, 787, 3663, 100],
        'Club Identifier': ['arsenal-fc', 'chelsea-academy', 'manchester-city', 'blackburn-rovers', 'ipswich-town', 'test-club'],
        'Country': ['England'] * 6,
        'Confidence': [0.9, 0.7, 0.9, 0.9, 0.9, 0.5],
        'Reason': ['English place + football indicators'] * 6,
        'Website': [''] * 6,
        'Emails': [''] * 6,
        'Phone Numbers': [''] * 6,
        'Contact_Quality': [0] * 6,
        'Football_Tier': ['Unknown'] * 6,
        'Tier_Number': [0] * 6,
        'Tier_Confidence': [0.3] * 6
    }
    
    # Create test CSV
    test_df = pd.DataFrame(test_data)
    test_csv_path = 'test_clubs.csv'
    test_df.to_csv(test_csv_path, index=False)
    
    print(f"Created test CSV with {len(test_df)} clubs")
    
    try:
        # Initialize enhancer with test data
        enhancer = ClubDataEnhancer(test_csv_path)
        
        # Process just the first 3 clubs as a test
        print("\nTesting enhancement on first 3 clubs...")
        enhancer.process_all_clubs(start_index=0, batch_size=3)
        
        # Show results
        print("\nEnhanced data:")
        enhanced_df = pd.read_csv(test_csv_path)
        for _, row in enhanced_df.head(3).iterrows():
            print(f"\nClub: {row['Club Name']}")
            print(f"  Website: {row['Website']}")
            print(f"  Email: {row['Emails']}")
            print(f"  Phone: {row['Phone Numbers']}")
            print(f"  Football Tier: {row['Football_Tier']} (Tier {row['Tier_Number']})")
            print(f"  Contact Quality: {row['Contact_Quality']}")
        
        # Generate summary
        summary = enhancer.generate_summary_report()
        print(f"\nSummary: {summary}")
        
        # Clean up test file
        os.remove(test_csv_path)
        print(f"\nCleaned up test file: {test_csv_path}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        # Clean up on error
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)

if __name__ == "__main__":
    test_enhancement()

