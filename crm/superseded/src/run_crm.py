#!/usr/bin/env python3
"""
CRM Pipeline Runner
Runs the complete CRM workflow: scrape clubs → sort by location → find contacts
"""

import sys
from pathlib import Path
import logging

# Import our essential modules
from club_scraper import ClubScraper
from location_sorter import LocationSorter
from contact_finder import ContactFinder

def setup_logging():
    """Setup logging for the pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler('data/crm_pipeline.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_full_pipeline():
    """Run the complete CRM pipeline"""
    logger = setup_logging()
    
    print("🚀 CLANNAI CRM PIPELINE")
    print("=" * 40)
    print("This will run the complete workflow:")
    print("1. 📊 Scrape VEO clubs")
    print("2. 📍 Sort by location")
    print("3. 📞 Find contact details")
    print()
    
    # Create data directory
    Path('data').mkdir(exist_ok=True)
    
    # Step 1: Scrape clubs
    print("🎯 STEP 1: Scraping VEO clubs...")
    print("-" * 30)
    
    scraper = ClubScraper()
    clubs = scraper.scrape_clubs()
    
    if not clubs:
        logger.error("❌ No clubs found! Pipeline stopped.")
        return False
        
    club_file = scraper.save_to_csv()
    print(f"✅ Step 1 complete: {len(clubs)} clubs saved to {club_file}")
    print()
    
    # Step 2: Sort by location
    print("🎯 STEP 2: Sorting by location...")
    print("-" * 30)
    
    sorter = LocationSorter()
    location_file, summary = sorter.sort_by_location(club_file)
    
    if not location_file:
        logger.error("❌ Location sorting failed! Pipeline stopped.")
        return False
        
    # Create country-specific files
    country_files = sorter.create_country_files(location_file)
    print(f"✅ Step 2 complete: Clubs sorted by location")
    print()
    
    # Step 3: Find contacts
    print("🎯 STEP 3: Finding contact details...")
    print("-" * 30)
    
    # Ask user how many contacts to find
    try:
        max_contacts = input("How many clubs to find contacts for? (50 recommended): ").strip()
        max_contacts = int(max_contacts) if max_contacts else 50
    except ValueError:
        max_contacts = 50
        
    finder = ContactFinder()
    contact_file = finder.process_clubs(location_file, max_contacts)
    
    if not contact_file:
        logger.error("❌ Contact finding failed!")
        return False
        
    print(f"✅ Step 3 complete: Contacts saved to {contact_file}")
    print()
    
    # Pipeline summary
    print("🎉 CRM PIPELINE COMPLETE!")
    print("=" * 40)
    print(f"📊 Clubs scraped: {len(clubs)}")
    print(f"📍 Location file: {location_file}")
    print(f"📞 Contact file: {contact_file}")
    print(f"📁 Country files: {len(country_files)}")
    print()
    print("🎯 Next steps:")
    print("• Review contact data in data/club_contacts.csv")
    print("• Use country-specific files for targeted outreach")
    print("• Import contacts into your email marketing tool")
    
    return True

def run_single_step():
    """Run individual pipeline steps"""
    print("📋 SELECT STEP TO RUN:")
    print("1. 📊 Scrape clubs only")
    print("2. 📍 Sort by location only")
    print("3. 📞 Find contacts only")
    print("4. 🚀 Run full pipeline")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        scraper = ClubScraper()
        clubs = scraper.scrape_clubs()
        if clubs:
            scraper.save_to_csv()
            print(f"✅ Scraped {len(clubs)} clubs")
            
    elif choice == "2":
        sorter = LocationSorter()
        output_file, summary = sorter.sort_by_location()
        if output_file:
            sorter.create_country_files(output_file)
            print("✅ Location sorting complete")
            
    elif choice == "3":
        finder = ContactFinder()
        max_clubs = input("How many clubs to process? (Enter for 50): ").strip()
        max_clubs = int(max_clubs) if max_clubs else 50
        output_file = finder.process_clubs(max_clubs=max_clubs)
        if output_file:
            print(f"✅ Contact finding complete: {output_file}")
            
    elif choice == "4":
        run_full_pipeline()
        
    else:
        print("❌ Invalid choice")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            run_full_pipeline()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_crm.py           # Interactive mode")
            print("  python run_crm.py --full    # Run full pipeline")
            print("  python run_crm.py --help    # Show this help")
        else:
            print("Unknown option. Use --help for usage.")
    else:
        run_single_step()

if __name__ == "__main__":
    main()