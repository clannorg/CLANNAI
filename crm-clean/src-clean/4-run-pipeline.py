#!/usr/bin/env python3
"""
STAGE 4: Complete CRM Pipeline Runner
Runs all stages in sequence: scrape → sort → find contacts
"""

import sys
from pathlib import Path
import logging
import subprocess
import time

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

def run_stage(stage_script, stage_name):
    """Run a single pipeline stage"""
    print(f"\n🎯 RUNNING {stage_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, f"src-clean/{stage_script}"], 
                              capture_output=False, text=True, cwd=".")
        
        if result.returncode == 0:
            print(f"✅ {stage_name} completed successfully!")
            return True
        else:
            print(f"❌ {stage_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ {stage_name} failed with error: {e}")
        return False

def run_full_pipeline():
    """Run the complete CRM pipeline"""
    logger = setup_logging()
    
    print("🚀 CLANNAI CRM PIPELINE")
    print("=" * 50)
    print("This will run the complete 3-stage workflow:")
    print("📊 Stage 1: Scrape VEO clubs")
    print("🌍 Stage 2: Sort by location & score")
    print("📞 Stage 3: Find contact details")
    print()
    
    start_time = time.time()
    
    # Create all data directories
    Path('data/1-veo-scraper').mkdir(parents=True, exist_ok=True)
    Path('data/2-by-country').mkdir(parents=True, exist_ok=True)
    Path('data/3-contact-details').mkdir(parents=True, exist_ok=True)
    
    # Stage 1: Scrape clubs
    if not run_stage("1-veo-scraper.py", "STAGE 1: VEO SCRAPER"):
        logger.error("❌ Pipeline stopped at Stage 1")
        return False
    
    # Stage 2: Sort by location
    if not run_stage("2-location-sorter.py", "STAGE 2: LOCATION SORTER"):
        logger.error("❌ Pipeline stopped at Stage 2")
        return False
    
    # Stage 3: Find contacts
    print(f"\n🎯 RUNNING STAGE 3: CONTACT FINDER")
    print("=" * 50)
    
    # Ask user how many contacts to find
    try:
        max_contacts = input("How many clubs to find contacts for? (50 recommended): ").strip()
        max_contacts = int(max_contacts) if max_contacts else 50
    except ValueError:
        max_contacts = 50
    
    # Modify the contact finder call to use the max_contacts
    print(f"Finding contacts for {max_contacts} clubs...")
    
    try:
        # Run contact finder with input
        process = subprocess.Popen([sys.executable, "src-clean/3-contact-finder.py"], 
                                 stdin=subprocess.PIPE, text=True, cwd=".")
        process.communicate(input=str(max_contacts))
        
        if process.returncode == 0:
            print(f"✅ STAGE 3: CONTACT FINDER completed successfully!")
        else:
            print(f"❌ STAGE 3 failed")
            return False
            
    except Exception as e:
        print(f"❌ STAGE 3 failed with error: {e}")
        return False
    
    # Pipeline summary
    elapsed_time = time.time() - start_time
    print("\n🎉 CRM PIPELINE COMPLETE!")
    print("=" * 50)
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print()
    print("📁 Generated Files:")
    print("├── data/1-veo-scraper/veo_clubs.csv")
    print("├── data/2-by-country/clubs_by_location.csv")
    print("├── data/2-by-country/clubs_[country].csv")
    print("└── data/3-contact-details/club_contacts.csv")
    print()
    print("🎯 Next steps:")
    print("• Review contacts in data/3-contact-details/club_contacts.csv")
    print("• Use country files for targeted outreach")
    print("• Import contacts into your email system")
    print("• Start reaching out to prospects!")
    
    return True

def run_single_stage():
    """Run individual pipeline stages"""
    print("📋 SELECT STAGE TO RUN:")
    print("1. 📊 Stage 1: Scrape VEO clubs")
    print("2. 🌍 Stage 2: Sort by location")
    print("3. 📞 Stage 3: Find contacts")
    print("4. 🚀 Run full pipeline")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        run_stage("1-veo-scraper.py", "STAGE 1: VEO SCRAPER")
        
    elif choice == "2":
        run_stage("2-location-sorter.py", "STAGE 2: LOCATION SORTER")
        
    elif choice == "3":
        max_clubs = input("How many clubs to process? (Enter for 50): ").strip()
        max_clubs = int(max_clubs) if max_clubs else 50
        
        try:
            process = subprocess.Popen([sys.executable, "src-clean/3-contact-finder.py"], 
                                     stdin=subprocess.PIPE, text=True, cwd=".")
            process.communicate(input=str(max_clubs))
            
            if process.returncode == 0:
                print(f"✅ STAGE 3 complete")
            else:
                print(f"❌ STAGE 3 failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    elif choice == "4":
        run_full_pipeline()
        
    else:
        print("❌ Invalid choice")

def show_status():
    """Show current pipeline status"""
    print("📊 CRM PIPELINE STATUS")
    print("=" * 30)
    
    stages = [
        ("Stage 1", "data/1-veo-scraper/veo_clubs.csv", "VEO clubs scraped"),
        ("Stage 2", "data/2-by-country/clubs_by_location.csv", "Clubs sorted by location"),
        ("Stage 3", "data/3-contact-details/club_contacts.csv", "Contact details found")
    ]
    
    for stage, file_path, description in stages:
        if Path(file_path).exists():
            print(f"✅ {stage}: {description}")
        else:
            print(f"❌ {stage}: Not completed")
    
    print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            run_full_pipeline()
        elif sys.argv[1] == "--status":
            show_status()
        elif sys.argv[1] == "--help":
            print("ClannAI CRM Pipeline")
            print("Usage:")
            print("  python 4-run-pipeline.py           # Interactive mode")
            print("  python 4-run-pipeline.py --full    # Run full pipeline")
            print("  python 4-run-pipeline.py --status  # Show pipeline status")
            print("  python 4-run-pipeline.py --help    # Show this help")
        else:
            print("Unknown option. Use --help for usage.")
    else:
        show_status()
        run_single_stage()

if __name__ == "__main__":
    main()