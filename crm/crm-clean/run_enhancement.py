#!/usr/bin/env python3
"""
Runner script for the clubs enhancement process
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the enhancement process"""
    try:
        from enhance_clubs_data import ClubDataEnhancer
        
        print("Starting clubs data enhancement process...")
        print("This will enhance the enhanced_clubs_england.csv file with:")
        print("- Website URLs")
        print("- Contact email addresses")
        print("- Contact phone numbers")
        print("- Proper football tier categorization")
        print()
        
        # Check if CSV file exists
        csv_file = 'data/enhanced_clubs_england.csv'
        if not os.path.exists(csv_file):
            print(f"Error: CSV file not found at {csv_file}")
            print("Please ensure the file exists in the data directory.")
            return
        
        print(f"Found CSV file: {csv_file}")
        print(f"Starting enhancement process...")
        print()
        
        # Initialize enhancer
        enhancer = ClubDataEnhancer(csv_file)
        
        # Process all clubs
        enhancer.process_all_clubs(start_index=0, batch_size=50)
        
        # Generate summary report
        summary = enhancer.generate_summary_report()
        if summary:
            print("\n" + "="*50)
            print("ENHANCEMENT COMPLETED SUCCESSFULLY!")
            print("="*50)
            print(f"Total clubs processed: {summary['total_clubs']}")
            print(f"Clubs with websites: {summary['clubs_with_website']} ({summary['website_coverage']})")
            print(f"Clubs with emails: {summary['clubs_with_email']} ({summary['email_coverage']})")
            print(f"Clubs with phones: {summary['clubs_with_phone']} ({summary['phone_coverage']})")
            print("\nTier distribution:")
            for tier, count in summary['tier_distribution'].items():
                print(f"  {tier}: {count} clubs")
            print("\nCheck the following files for results:")
            print(f"- Enhanced CSV: {csv_file}")
            print(f"- Backup: {csv_file.replace('.csv', '_backup.csv')}")
            print(f"- Enhanced version: {csv_file.replace('.csv', '_enhanced.csv')}")
            print(f"- Summary report: enhancement_summary.json")
            print(f"- Log file: clubs_enhancement.log")
        
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Please ensure you have activated the virtual environment:")
        print("  source venv_enhancement/bin/activate")
        print("And installed the requirements:")
        print("  pip install -r requirements_enhancement.txt")
    except Exception as e:
        print(f"Error during enhancement process: {e}")
        print("Check the log file for more details.")

if __name__ == "__main__":
    main()

