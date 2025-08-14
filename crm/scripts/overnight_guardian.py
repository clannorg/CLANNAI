#!/usr/bin/env python3
"""
Overnight Guardian - Ensures the mega scraper keeps running all night
Monitors, restarts if needed, and sends status updates
"""

import subprocess
import time
import json
import os
from pathlib import Path
import datetime

class OvernightGuardian:
    def __init__(self):
        self.scraper_script = 'mega_27k_scraper.py'
        self.progress_file = 'mega_27k_progress.json'
        self.guardian_log = 'overnight_guardian.log'
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.guardian_log, 'a') as f:
            f.write(log_msg + '\n')
    
    def is_scraper_running(self):
        """Check if mega scraper is still running"""
        try:
            result = subprocess.run(['pgrep', '-f', self.scraper_script], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_progress(self):
        """Get current scraping progress"""
        try:
            if Path(self.progress_file).exists():
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                return progress
        except:
            pass
        return None
    
    def restart_scraper(self):
        """Restart the mega scraper if it died"""
        self.log("🔄 Restarting mega scraper...")
        try:
            subprocess.Popen(['nohup', 'python3', self.scraper_script], 
                           stdout=open('mega_27k_restart.out', 'w'),
                           stderr=subprocess.STDOUT)
            time.sleep(10)  # Give it time to start
            
            if self.is_scraper_running():
                self.log("✅ Mega scraper restarted successfully")
                return True
            else:
                self.log("❌ Failed to restart mega scraper")
                return False
        except Exception as e:
            self.log(f"❌ Error restarting scraper: {e}")
            return False
    
    def get_system_status(self):
        """Get system resource status"""
        try:
            # Get memory usage
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            memory_lines = result.stdout.split('\n')[1:3]
            
            # Get disk usage
            result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
            disk_line = result.stdout.split('\n')[1]
            
            return {
                'memory': memory_lines,
                'disk': disk_line
            }
        except:
            return None
    
    def monitor_overnight(self):
        """Main overnight monitoring loop"""
        self.log("🌙 Overnight Guardian started - watching mega scraper")
        
        check_interval = 300  # Check every 5 minutes
        last_progress_check = time.time()
        last_processed = 0
        stall_count = 0
        
        while True:
            try:
                # Check if scraper is running
                if not self.is_scraper_running():
                    self.log("⚠️ Mega scraper not running!")
                    if self.restart_scraper():
                        stall_count = 0
                    else:
                        self.log("💀 Could not restart scraper - sleeping 30 mins")
                        time.sleep(1800)  # Wait 30 minutes before trying again
                        continue
                
                # Check progress
                progress = self.get_progress()
                if progress:
                    processed = progress.get('total_processed', 0)
                    websites = progress.get('clubs_with_websites', 0)
                    emails = progress.get('clubs_with_emails', 0)
                    phones = progress.get('clubs_with_phones', 0)
                    
                    # Check if progress is stalled
                    if processed == last_processed:
                        stall_count += 1
                        if stall_count >= 3:  # Stalled for 15+ minutes
                            self.log(f"⚠️ Scraper appears stalled at {processed} clubs")
                            self.log("🔄 Attempting restart...")
                            self.restart_scraper()
                            stall_count = 0
                    else:
                        stall_count = 0
                        last_processed = processed
                    
                    # Log progress every hour
                    if time.time() - last_progress_check > 3600:
                        completion_pct = (processed / 27675 * 100) if processed > 0 else 0
                        self.log(f"""
📊 Hourly Progress Report:
   🔄 Processed: {processed:,}/27,675 ({completion_pct:.1f}%)
   🌐 Websites: {websites:,} ({websites/processed*100:.1f}% if processed > 0 else 0)
   📧 Emails: {emails:,} ({emails/processed*100:.1f}% if processed > 0 else 0)
   📞 Phones: {phones:,} ({phones/processed*100:.1f}% if processed > 0 else 0)
                        """)
                        last_progress_check = time.time()
                
                # Check system resources
                system = self.get_system_status()
                if system:
                    # Check if disk is getting full (warn at 90%)
                    disk_usage = system['disk'].split()[4].replace('%', '')
                    if int(disk_usage) > 90:
                        self.log(f"⚠️ Disk usage high: {disk_usage}%")
                
                # Sleep until next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.log("🛑 Guardian stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Guardian error: {e}")
                time.sleep(check_interval)
        
        self.log("🌅 Guardian monitoring ended")

def main():
    """Run the overnight guardian"""
    guardian = OvernightGuardian()
    guardian.monitor_overnight()

if __name__ == "__main__":
    main()