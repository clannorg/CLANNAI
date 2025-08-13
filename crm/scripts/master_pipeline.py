#!/usr/bin/env python3
"""
Master Pipeline for England, Scotland, Northern Ireland Club Contact Scraping
Runs the complete process from data extraction to contact details
"""

import os
import sys
import time
from datetime import datetime

def run_step(step_name, script_path, description):
    """Run a pipeline step with error handling"""
    print(f"\n{'='*60}")
    print(f"🚀 STEP: {step_name}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run the script
        result = os.system(f"python3 {script_path}")
        
        if result == 0:
            elapsed = time.time() - start_time
            print(f"✅ {step_name} completed successfully in {elapsed:.1f}s")
            return True
        else:
            print(f"❌ {step_name} failed with exit code {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {step_name}: {e}")
        return False

def main():
    print("🎯 MASTER PIPELINE: England, Scotland, Northern Ireland Club Contacts")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create necessary directories
    os.makedirs('data/contacts', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Step 1: Extract target clubs
    success = run_step(
        "Data Extraction",
        "extract_target_clubs.py",
        "Extract clubs from England, Scotland, Northern Ireland and organize by activity"
    )
    
    if not success:
        print("❌ Pipeline failed at data extraction step")
        return
    
    # Step 2: Contact scraping for each country
    countries = ['England', 'Scotland', 'Northern Ireland']
    
    for country in countries:
        print(f"\n🎯 Processing {country} clubs...")
        
        success = run_step(
            f"Contact Scraping - {country}",
            "enhanced_contact_scraper.py",
            f"Find contact details for {country} clubs"
        )
        
        if not success:
            print(f"⚠️  {country} contact scraping had issues, continuing...")
    
    # Step 3: Generate summary report
    print(f"\n{'='*60}")
    print("📊 GENERATING SUMMARY REPORT")
    print(f"{'='*60}")
    
    try:
        # Count results
        total_clubs = 0
        total_with_contacts = 0
        
        for country in countries:
            filename = f'data/contacts/{country.lower().replace(" ", "_")}_clubs_with_contacts.csv'
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    club_count = len(lines) - 1  # Subtract header
                    total_clubs += club_count
                    
                    # Count clubs with contact info
                    with_contacts = 0
                    for line in lines[1:]:  # Skip header
                        if any(field.strip() for field in line.split(',')[4:7]):  # Phones, Emails, Websites
                            with_contacts += 1
                    
                    total_with_contacts += with_contacts
                    print(f"  {country}: {club_count} clubs, {with_contacts} with contacts")
        
        print(f"\n📈 FINAL SUMMARY:")
        print(f"  Total clubs processed: {total_clubs}")
        print(f"  Clubs with contact details: {total_with_contacts}")
        print(f"  Success rate: {(total_with_contacts/total_clubs*100):.1f}%" if total_clubs > 0 else "  Success rate: 0%")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
    
    print(f"\n✅ Pipeline completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 