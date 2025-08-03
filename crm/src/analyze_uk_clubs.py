#!/usr/bin/env python3
"""
Quick analysis script for UK football club scraping results
"""

import pandas as pd
import json
from pathlib import Path

def analyze_uk_clubs():
    """Analyze the comprehensive UK football club results"""
    
    # Check for results file
    results_file = Path('data/comprehensive_uk_football_clubs.csv')
    summary_file = Path('data/comprehensive_uk_summary.json')
    
    if not results_file.exists():
        print("❌ No results file found!")
        print("Run: python3 src/run_uk_club_scraping.py first")
        return
    
    # Load data
    df = pd.read_csv(results_file)
    
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            summary = json.load(f)
    else:
        summary = {}
    
    print("🏴󠁧󠁢󠁥󠁮󠁧󠁿🏴󠁧󠁢󠁳󠁣󠁴󠁿 UK FOOTBALL CLUB ANALYSIS")
    print("=" * 50)
    
    # Basic stats
    print(f"📊 Total clubs scraped: {len(df):,}")
    print(f"🗂️  Data sources used: {len(df['source'].unique())}")
    
    # Geographic breakdown
    if 'country' in df.columns:
        print(f"\n🌍 GEOGRAPHIC DISTRIBUTION:")
        country_counts = df['country'].value_counts()
        for country, count in country_counts.items():
            flag = "🏴󠁧󠁢󠁥󠁮󠁧󠁿" if country == "England" else "🏴󠁧󠁢󠁳󠁣󠁴󠁿" if country == "Scotland" else "🇬🇧"
            print(f"   {flag} {country}: {count:,} clubs")
    
    # Source breakdown
    print(f"\n📋 SOURCE BREAKDOWN:")
    source_counts = df['source'].value_counts()
    for source, count in source_counts.head(8).items():
        print(f"   • {source}: {count:,} clubs")
    
    # Club type analysis
    if 'type' in df.columns:
        print(f"\n🏷️  CLUB TYPES:")
        type_counts = df['type'].value_counts()
        for club_type, count in type_counts.items():
            print(f"   • {club_type}: {count:,} clubs")
    
    # Data quality
    print(f"\n📈 DATA QUALITY:")
    total_clubs = len(df)
    clubs_with_urls = len(df[df['url'].fillna('') != ''])
    clubs_with_country = len(df[df.get('country', '').fillna('') != ''])
    
    print(f"   🌐 Clubs with websites: {clubs_with_urls:,} ({clubs_with_urls/total_clubs*100:.1f}%)")
    print(f"   🗺️  Clubs with country data: {clubs_with_country:,} ({clubs_with_country/total_clubs*100:.1f}%)")
    
    # Sample clubs
    print(f"\n🎯 SAMPLE CLUBS:")
    sample_clubs = df.head(10)
    for _, club in sample_clubs.iterrows():
        country_flag = "🏴󠁧󠁢󠁥󠁮󠁧󠁿" if club.get('country') == "England" else "🏴󠁧󠁢󠁳󠁣󠁴󠁿" if club.get('country') == "Scotland" else "🇬🇧"
        website = "🌐" if club.get('url', '') else "📝"
        print(f"   {country_flag} {website} {club['name']} ({club['source']})")
    
    # Professional clubs found
    if 'level' in df.columns:
        professional_clubs = df[df['level'].isin(['premier', 'professional'])]['name'].tolist()
        if professional_clubs:
            print(f"\n⚽ PROFESSIONAL CLUBS FOUND ({len(professional_clubs)}):")
            for club in professional_clubs[:15]:  # Show first 15
                print(f"   • {club}")
            if len(professional_clubs) > 15:
                print(f"   ... and {len(professional_clubs) - 15} more")
    
    # Regional analysis for England
    english_clubs = df[df.get('country', '') == 'England'] if 'country' in df.columns else df
    if len(english_clubs) > 0:
        print(f"\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLISH REGIONS DETECTED:")
        
        # Try to detect regions from club names
        regions = {
            'London': ['London', 'Chelsea', 'Arsenal', 'Tottenham', 'West Ham', 'Crystal Palace', 'Fulham', 'Brentford'],
            'Manchester': ['Manchester', 'United', 'City'],
            'Liverpool': ['Liverpool', 'Everton', 'Liverpool FC'],
            'Birmingham': ['Birmingham', 'Aston Villa', 'West Bromwich'],
            'Sheffield': ['Sheffield', 'United', 'Wednesday'],
            'Newcastle': ['Newcastle', 'Sunderland'],
            'Leeds': ['Leeds', 'United']
        }
        
        for region, keywords in regions.items():
            region_clubs = english_clubs[
                english_clubs['name'].str.contains('|'.join(keywords), case=False, na=False)
            ]
            if len(region_clubs) > 0:
                print(f"   📍 {region} area: {len(region_clubs)} clubs")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   • Export by country: df[df['country']=='England'].to_csv('english_clubs.csv')")
    print(f"   • Find professional clubs: df[df['level']=='professional']")
    print(f"   • Search by name: df[df['name'].str.contains('United')]")
    print(f"   • Find contact info: python src/find_uk_contacts.py")

if __name__ == "__main__":
    analyze_uk_clubs()