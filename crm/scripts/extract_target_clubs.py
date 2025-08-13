#!/usr/bin/env python3
"""
Extract clubs from England, Scotland, Northern Ireland
Creates organized lists with recording counts and activity data
"""

import csv
import pandas as pd

def extract_target_clubs():
    """Extract clubs from target countries and organize by activity"""
    
    # Read the processed data
    df = pd.read_csv('data/processed/all_clubs_by_country.csv')
    
    # Filter for target countries
    target_countries = ['England', 'Scotland', 'Northern Ireland']
    target_df = df[df['Country'].isin(target_countries)].copy()
    
    # Convert recordings to numeric, handle errors
    target_df['Recordings'] = pd.to_numeric(target_df['Recordings'], errors='coerce').fillna(0)
    
    # Sort by recordings (most active first)
    target_df = target_df.sort_values('Recordings', ascending=False)
    
    print(f"📊 Found clubs:")
    for country in target_countries:
        count = len(target_df[target_df['Country'] == country])
        total_recordings = target_df[target_df['Country'] == country]['Recordings'].sum()
        print(f"  {country}: {count} clubs, {total_recordings:,} total recordings")
    
    # Save comprehensive list
    target_df.to_csv('data/target_clubs_comprehensive.csv', index=False)
    print(f"\n💾 Saved comprehensive list: {len(target_df)} clubs")
    
    # Create country-specific files
    for country in target_countries:
        country_df = target_df[target_df['Country'] == country].copy()
        filename = f'data/{country.lower().replace(" ", "_")}_clubs.csv'
        country_df.to_csv(filename, index=False)
        print(f"  📁 {country}: {len(country_df)} clubs saved to {filename}")
    
    # Show top clubs by activity
    print(f"\n🏆 Top 10 Most Active Clubs:")
    top_clubs = target_df.head(10)
    for _, club in top_clubs.iterrows():
        print(f"  {club['Club Name']} ({club['Country']}) - {club['Recordings']} recordings")
    
    # Activity statistics
    print(f"\n📈 Activity Statistics:")
    for country in target_countries:
        country_data = target_df[target_df['Country'] == country]
        avg_recordings = country_data['Recordings'].mean()
        median_recordings = country_data['Recordings'].median()
        print(f"  {country}:")
        print(f"    Average recordings: {avg_recordings:.1f}")
        print(f"    Median recordings: {median_recordings:.1f}")
        print(f"    Clubs with 100+ recordings: {len(country_data[country_data['Recordings'] >= 100])}")
    
    return target_df

def create_priority_lists():
    """Create priority lists for contact scraping"""
    
    df = pd.read_csv('data/target_clubs_comprehensive.csv')
    
    # High priority: 100+ recordings
    high_priority = df[df['Recordings'] >= 100].copy()
    high_priority.to_csv('data/high_priority_clubs.csv', index=False)
    print(f"🎯 High priority clubs (100+ recordings): {len(high_priority)}")
    
    # Medium priority: 50-99 recordings
    medium_priority = df[(df['Recordings'] >= 50) & (df['Recordings'] < 100)].copy()
    medium_priority.to_csv('data/medium_priority_clubs.csv', index=False)
    print(f"📊 Medium priority clubs (50-99 recordings): {len(medium_priority)}")
    
    # Low priority: 10-49 recordings
    low_priority = df[(df['Recordings'] >= 10) & (df['Recordings'] < 50)].copy()
    low_priority.to_csv('data/low_priority_clubs.csv', index=False)
    print(f"📋 Low priority clubs (10-49 recordings): {len(low_priority)}")
    
    # Summary
    print(f"\n📊 Priority Summary:")
    print(f"  High Priority: {len(high_priority)} clubs")
    print(f"  Medium Priority: {len(medium_priority)} clubs") 
    print(f"  Low Priority: {len(low_priority)} clubs")
    print(f"  Total Target: {len(high_priority) + len(medium_priority) + len(low_priority)} clubs")

def main():
    print("🎯 Extracting target clubs from England, Scotland, Northern Ireland...")
    
    # Extract and organize clubs
    target_df = extract_target_clubs()
    
    # Create priority lists
    create_priority_lists()
    
    print(f"\n✅ Complete! Ready for contact scraping.")

if __name__ == "__main__":
    main() 