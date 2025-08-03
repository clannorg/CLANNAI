#!/usr/bin/env python3
"""
Master script to run comprehensive UK football club scraping
Combines results from multiple scrapers for maximum coverage
"""

import pandas as pd
import json
from pathlib import Path
import sys
import time
from datetime import datetime

# Import our scrapers
from uk_football_scraper import UKFootballClubScraper
from football_db_scraper import FootballDatabaseScraper

def run_comprehensive_scraping():
    """Run all UK football club scrapers and combine results"""
    
    print("🚀 COMPREHENSIVE UK FOOTBALL CLUB SCRAPING")
    print("=" * 50)
    print("This will scrape clubs from multiple sources:")
    print("• FA Full-Time (official FA directory)")
    print("• Scottish FA (official Scottish directory)")
    print("• Non-League Directory (grassroots clubs)")
    print("• Pitchero (club management platform)")
    print("• EFL/Premier League (professional clubs)")
    print("• County FAs (regional associations)")
    print("• Scottish leagues (regional leagues)")
    print("• Football APIs (structured data)")
    print()
    
    start_time = time.time()
    all_clubs = []
    
    # Run Selenium-based scraper
    print("🎯 PHASE 1: Dynamic Website Scraping (Selenium)")
    print("-" * 45)
    try:
        selenium_scraper = UKFootballClubScraper()
        selenium_file = selenium_scraper.run_full_scrape()
        
        if Path(selenium_file).exists():
            selenium_df = pd.read_csv(selenium_file)
            selenium_clubs = selenium_df.to_dict('records')
            all_clubs.extend(selenium_clubs)
            print(f"✅ Selenium scraper: {len(selenium_clubs)} clubs")
        else:
            print("⚠️  Selenium scraper: No results file found")
            
    except Exception as e:
        print(f"❌ Selenium scraper failed: {e}")
    
    print()
    
    # Run requests-based scraper  
    print("🎯 PHASE 2: Database & API Scraping (Requests)")
    print("-" * 42)
    try:
        db_scraper = FootballDatabaseScraper()
        db_file = db_scraper.run_scrape()
        
        if Path(db_file).exists():
            db_df = pd.read_csv(db_file)
            db_clubs = db_df.to_dict('records')
            all_clubs.extend(db_clubs)
            print(f"✅ Database scraper: {len(db_clubs)} clubs")
        else:
            print("⚠️  Database scraper: No results file found")
            
    except Exception as e:
        print(f"❌ Database scraper failed: {e}")
    
    print()
    
    # Combine and deduplicate results
    print("🎯 PHASE 3: Combining & Deduplicating Results")
    print("-" * 40)
    
    if not all_clubs:
        print("❌ No clubs found from any scraper!")
        return None
        
    # Convert to DataFrame for easier processing
    combined_df = pd.DataFrame(all_clubs)
    
    print(f"📊 Total clubs before deduplication: {len(combined_df)}")
    
    # Enhanced deduplication
    combined_df['normalized_name'] = combined_df['name'].str.lower().str.strip()
    combined_df['normalized_name'] = combined_df['normalized_name'].str.replace(r'[^\w\s]', '', regex=True)
    combined_df['normalized_name'] = combined_df['normalized_name'].str.replace(r'\s+', ' ', regex=True)
    
    # Keep the entry with the most information (prefer entries with URLs, etc.)
    combined_df['info_score'] = (
        combined_df['url'].fillna('').str.len() + 
        combined_df.get('country', '').fillna('').str.len() +
        combined_df.get('type', '').fillna('').str.len()
    )
    
    # Drop duplicates keeping the one with highest info score
    deduplicated_df = combined_df.sort_values('info_score', ascending=False).drop_duplicates(
        subset=['normalized_name'], keep='first'
    )
    
    # Clean up temporary columns
    deduplicated_df = deduplicated_df.drop(['normalized_name', 'info_score'], axis=1)
    
    print(f"✅ Unique clubs after deduplication: {len(deduplicated_df)}")
    print(f"🗑️  Removed {len(combined_df) - len(deduplicated_df)} duplicates")
    
    # Add metadata
    deduplicated_df['combined_scrape_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    deduplicated_df['total_sources_checked'] = len(set(deduplicated_df['source']))
    
    # Save combined results
    output_file = 'data/comprehensive_uk_football_clubs.csv'
    deduplicated_df.to_csv(output_file, index=False)
    
    # Create comprehensive summary
    summary = create_comprehensive_summary(deduplicated_df)
    
    with open('data/comprehensive_uk_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print final results
    elapsed_time = time.time() - start_time
    print_final_summary(summary, output_file, elapsed_time)
    
    return output_file

def create_comprehensive_summary(df):
    """Create detailed summary of scraping results"""
    summary = {
        'scraping_metadata': {
            'total_clubs': len(df),
            'scraping_date': datetime.now().isoformat(),
            'sources_used': list(df['source'].unique()),
            'total_sources': len(df['source'].unique())
        },
        'geographic_breakdown': {
            'by_country': df['country'].value_counts().to_dict() if 'country' in df.columns else {},
            'england_clubs': len(df[df.get('country', '') == 'England']) if 'country' in df.columns else 0,
            'scotland_clubs': len(df[df.get('country', '') == 'Scotland']) if 'country' in df.columns else 0,
            'uk_clubs': len(df[df.get('country', '') == 'UK']) if 'country' in df.columns else 0
        },
        'club_types': {
            'by_type': df['type'].value_counts().to_dict() if 'type' in df.columns else {},
            'by_level': df['level'].value_counts().to_dict() if 'level' in df.columns else {}
        },
        'data_quality': {
            'clubs_with_urls': len(df[df['url'].fillna('') != '']),
            'clubs_with_country': len(df[df.get('country', '').fillna('') != '']),
            'clubs_with_type': len(df[df.get('type', '').fillna('') != ''])
        },
        'source_breakdown': df['source'].value_counts().to_dict()
    }
    
    return summary

def print_final_summary(summary, output_file, elapsed_time):
    """Print comprehensive final summary"""
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE SCRAPING COMPLETE!")
    print("=" * 60)
    
    meta = summary['scraping_metadata']
    geo = summary['geographic_breakdown']
    quality = summary['data_quality']
    
    print(f"📁 Output file: {output_file}")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print(f"📊 Total clubs: {meta['total_clubs']:,}")
    print(f"🗂️  Sources used: {meta['total_sources']}")
    
    print(f"\n🌍 GEOGRAPHIC BREAKDOWN:")
    print(f"🏴󠁧󠁢󠁥󠁮󠁧󠁿 English clubs: {geo['england_clubs']:,}")
    print(f"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scottish clubs: {geo['scotland_clubs']:,}")
    print(f"🇬🇧 UK clubs: {geo['uk_clubs']:,}")
    
    print(f"\n📈 DATA QUALITY:")
    print(f"🌐 Clubs with websites: {quality['clubs_with_urls']:,}")
    print(f"🗺️  Clubs with country: {quality['clubs_with_country']:,}")
    print(f"🏷️  Clubs with type: {quality['clubs_with_type']:,}")
    
    print(f"\n📋 TOP SOURCES:")
    for source, count in list(summary['source_breakdown'].items())[:5]:
        print(f"   • {source}: {count:,} clubs")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   • Review data: head {output_file}")
    print(f"   • Filter by region: grep 'England' {output_file}")
    print(f"   • Analyze by type: python src/analyze_uk_clubs.py")
    print(f"   • Find contacts: python src/find_uk_contacts.py")

def main():
    """Main execution function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("UK Football Club Scraper")
        print("Usage: python3 src/run_uk_club_scraping.py")
        print("\nThis script will:")
        print("1. Scrape FA Full-Time, Scottish FA, Non-League Directory")
        print("2. Scrape EFL, Premier League, County FAs")
        print("3. Combine and deduplicate all results")
        print("4. Save comprehensive CSV with all UK football clubs")
        return
    
    try:
        output_file = run_comprehensive_scraping()
        if output_file:
            print(f"\n✅ Success! Check {output_file} for all UK football clubs")
        else:
            print("\n❌ Scraping failed - check logs for details")
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Check logs in data/ directory for details")

if __name__ == "__main__":
    main()