#!/usr/bin/env python3
"""
Monitor the mass contact scraper progress
"""

import json
import time
import pandas as pd
from pathlib import Path

def monitor_progress():
    """Monitor scraper progress"""
    progress_file = 'mass_scraper_progress.json'
    results_file = 'mass_contacts_results.csv'
    
    while True:
        try:
            # Check if progress file exists
            if Path(progress_file).exists():
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                
                print(f"\n📊 SCRAPER PROGRESS UPDATE:")
                print(f"   Clubs processed: {progress.get('total_processed', 0)}")
                print(f"   Websites found: {progress.get('clubs_with_websites', 0)}")
                print(f"   Emails found: {progress.get('clubs_with_emails', 0)}")
                print(f"   Phones found: {progress.get('clubs_with_phones', 0)}")
                
                # Show latest results if available
                if Path(results_file).exists():
                    df = pd.read_csv(results_file)
                    if len(df) > 0:
                        recent = df.tail(5)
                        print(f"\n🎯 Latest 5 results:")
                        for _, row in recent.iterrows():
                            status = "✅" if row['Website'] or row['Email'] or row['Phone'] else "❌"
                            print(f"   {status} {row['Club_Name']} - W:{bool(row['Website'])} E:{bool(row['Email'])} P:{bool(row['Phone'])}")
                
            else:
                print("⏳ Waiting for scraper to start...")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_progress()