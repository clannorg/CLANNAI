#!/usr/bin/env python3
"""
Monitor the MEGA 27K scraper progress
"""

import json
import time
import pandas as pd
from pathlib import Path
import datetime

def format_time_remaining(processed, total, start_time):
    """Estimate time remaining"""
    if processed == 0:
        return "Calculating..."
    
    elapsed = time.time() - start_time
    rate = processed / elapsed
    remaining = (total - processed) / rate if rate > 0 else 0
    
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    
    return f"{hours}h {minutes}m"

def monitor_mega_progress():
    """Monitor mega scraper progress"""
    progress_file = 'mega_27k_progress.json'
    results_file = 'mega_27k_contacts.csv'
    total_clubs = 27675
    start_time = time.time()
    
    print(f"""
🚀 MEGA 27K SCRAPER MONITOR STARTED
📊 Target: {total_clubs:,} clubs
⏰ Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Expected: ~11,000 websites, ~3,000 emails, ~800 phones
    """)
    
    while True:
        try:
            # Check if progress file exists
            if Path(progress_file).exists():
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                
                processed = progress.get('total_processed', 0)
                websites = progress.get('clubs_with_websites', 0)
                emails = progress.get('clubs_with_emails', 0)
                phones = progress.get('clubs_with_phones', 0)
                
                # Calculate rates and projections
                completion_pct = (processed / total_clubs * 100) if processed > 0 else 0
                website_rate = (websites / processed * 100) if processed > 0 else 0
                email_rate = (emails / processed * 100) if processed > 0 else 0
                phone_rate = (phones / processed * 100) if processed > 0 else 0
                
                # Project final numbers
                projected_websites = int(website_rate / 100 * total_clubs)
                projected_emails = int(email_rate / 100 * total_clubs)
                projected_phones = int(phone_rate / 100 * total_clubs)
                
                time_remaining = format_time_remaining(processed, total_clubs, start_time)
                
                print(f"""
📊 MEGA SCRAPER PROGRESS:
   🔄 Processed: {processed:,}/{total_clubs:,} ({completion_pct:.1f}%)
   ⏱️  Time remaining: {time_remaining}
   
🎯 Current Results:
   🌐 Websites: {websites:,} ({website_rate:.1f}%)
   📧 Emails: {emails:,} ({email_rate:.1f}%)  
   📞 Phones: {phones:,} ({phone_rate:.1f}%)
   
🔮 Projected Final Results:
   🌐 Websites: ~{projected_websites:,}
   📧 Emails: ~{projected_emails:,}
   📞 Phones: ~{projected_phones:,}
                """)
                
                # Show latest successful finds if available
                if Path(results_file).exists():
                    df = pd.read_csv(results_file)
                    if len(df) > 0:
                        # Get recent successful finds
                        successful = df[df['Website'] != ''].tail(5)
                        if len(successful) > 0:
                            print(f"🎯 Latest successful finds:")
                            for _, row in successful.iterrows():
                                email_icon = "📧" if row['Email'] else "  "
                                phone_icon = "📞" if row['Phone'] else "  "
                                print(f"   ✅ {row['Club_Name']} {email_icon} {phone_icon}")
                
                # Check if we're done
                if processed >= total_clubs:
                    print(f"\n🎉 MEGA SCRAPING COMPLETED!")
                    print(f"🎯 Final totals: {websites:,} websites, {emails:,} emails, {phones:,} phones")
                    break
                
            else:
                print("⏳ Waiting for mega scraper to start...")
            
            print("-" * 60)
            time.sleep(60)  # Check every minute for 27K run
            
        except KeyboardInterrupt:
            print(f"\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_mega_progress()