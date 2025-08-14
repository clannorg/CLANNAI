#!/usr/bin/env python3
"""
Clean Contact Data - Remove garbage and create quality contact files
"""

import pandas as pd
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactCleaner:
    def __init__(self):
        self.junk_emails = [
            'user@domain.com', 'example@example.com', 'test@test.com',
            'admin@wordpress.com', 'noreply@', 'donotreply@',
            'hey-logo@2x.png', '@sentry-next.wixpress.com',
            'placeholder@', 'sample@', 'demo@'
        ]
        
        self.junk_domains = [
            'example.com', 'test.com', 'sample.com', 'placeholder.com',
            'wordpress.com', 'wixpress.com', 'sentry.io', 'github.com'
        ]
        
        self.valid_tlds = [
            '.com', '.co.uk', '.org', '.net', '.edu', '.gov', 
            '.ie', '.uk', '.eu', '.fr', '.de', '.es', '.it'
        ]

    def is_valid_email(self, email):
        """Check if email is valid and not junk"""
        if not email or pd.isna(email) or email.strip() == '':
            return False
            
        email = email.strip().lower()
        
        # Check for junk emails
        for junk in self.junk_emails:
            if junk in email:
                return False
        
        # Check for junk domains
        for domain in self.junk_domains:
            if domain in email:
                return False
        
        # Basic email format check
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
        
        # Check for valid TLD
        has_valid_tld = any(email.endswith(tld) for tld in self.valid_tlds)
        if not has_valid_tld:
            return False
            
        return True

    def is_valid_phone(self, phone):
        """Check if phone number is valid"""
        if not phone or pd.isna(phone):
            return False
            
        phone = str(phone).strip()
        
        # Remove .0 from floats
        if phone.endswith('.0'):
            phone = phone[:-2]
        
        # Remove common formatting but keep + for international
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Must have at least 10 digits
        if len(clean_phone) < 10:
            return False
        
        # Check for UK/international format
        uk_patterns = [
            r'^\+44[17]\d{8,9}$',  # +44 mobile/landline
            r'^0[17]\d{8,9}$',     # UK mobile/landline
            r'^\d{10,11}$'         # 10-11 digit numbers
        ]
        
        for pattern in uk_patterns:
            if re.match(pattern, clean_phone):
                return True
                
        return False

    def clean_phone_format(self, phone):
        """Clean phone number format"""
        if not phone or pd.isna(phone):
            return ''
            
        phone = str(phone).strip()
        
        # Remove .0 from floats
        if phone.endswith('.0'):
            phone = phone[:-2]
        
        # If it's a valid UK mobile (starts with 07)
        if phone.startswith('07') and len(phone) == 11:
            return phone
        
        # If it's a valid UK landline (starts with 01 or 02)
        if phone.startswith(('01', '02')) and len(phone) in [10, 11]:
            return phone
        
        # If it's international format
        if phone.startswith('+44'):
            return phone
        
        # If it's 10-11 digits, assume UK format
        clean_phone = re.sub(r'[^\d]', '', phone)
        if len(clean_phone) == 10:
            return '0' + clean_phone  # Add leading 0
        elif len(clean_phone) == 11 and clean_phone.startswith('0'):
            return clean_phone
        
        return phone

    def is_english_club_name(self, club_name):
        """Check if club name is in English (filter out Asian characters)"""
        if not club_name or pd.isna(club_name):
            return False
            
        # Check for non-English characters (Chinese, Japanese, Korean, etc.)
        asian_chars = re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf\uac00-\ud7af]', club_name)
        if asian_chars:
            return False
            
        # Check for obvious junk names
        if club_name.strip() in ['-', '_', '---', '___', '.', '..']:
            return False
            
        return True

    def clean_contacts_data(self, input_file):
        """Clean the contacts data and create filtered files"""
        logger.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)
        
        logger.info(f"Original data: {len(df)} rows")
        
        # Filter out non-English club names
        df['is_english'] = df['Club_Name'].apply(self.is_english_club_name)
        english_df = df[df['is_english']].copy()
        logger.info(f"After English filter: {len(english_df)} rows")
        
        # Clean and validate emails
        english_df['clean_email'] = english_df['Email'].apply(
            lambda x: str(x).strip() if pd.notna(x) and self.is_valid_email(str(x)) else ''
        )
        
        # Clean and validate phones
        english_df['clean_phone'] = english_df['Phone'].apply(
            lambda x: self.clean_phone_format(x) if pd.notna(x) and self.is_valid_phone(x) else ''
        )
        
        # Create quality tiers
        high_quality = english_df[
            (english_df['clean_email'] != '') | 
            (english_df['clean_phone'] != '')
        ].copy()
        
        medium_quality = english_df[
            (english_df['Website'] != '') & 
            (english_df['Website'].notna()) &
            (english_df['clean_email'] == '') &
            (english_df['clean_phone'] == '')
        ].copy()
        
        # Clean column names and prepare final data
        final_columns = ['Club_Name', 'Recordings', 'Website', 'clean_email', 'clean_phone', 'Status']
        
        if len(high_quality) > 0:
            high_quality_clean = high_quality[final_columns].copy()
            high_quality_clean.columns = ['Club_Name', 'Recordings', 'Website', 'Email', 'Phone', 'Status']
            high_quality_clean.to_csv('high_quality_contacts.csv', index=False)
            logger.info(f"High quality contacts: {len(high_quality_clean)} clubs")
        
        if len(medium_quality) > 0:
            medium_quality_clean = medium_quality[final_columns].copy()
            medium_quality_clean.columns = ['Club_Name', 'Recordings', 'Website', 'Email', 'Phone', 'Status']
            medium_quality_clean.to_csv('medium_quality_contacts.csv', index=False)
            logger.info(f"Medium quality contacts: {len(medium_quality_clean)} clubs")
        
        # Create email-only file
        email_only = high_quality[high_quality['clean_email'] != ''][
            ['Club_Name', 'Recordings', 'Website', 'clean_email', 'Status']
        ].copy()
        
        if len(email_only) > 0:
            email_only.columns = ['Club_Name', 'Recordings', 'Website', 'Email', 'Status']
            email_only.to_csv('clean_emails_only.csv', index=False)
            logger.info(f"Clean emails only: {len(email_only)} clubs")
        
        # Create phone-only file
        phone_only = high_quality[high_quality['clean_phone'] != ''][
            ['Club_Name', 'Recordings', 'Website', 'clean_phone', 'Status']
        ].copy()
        
        if len(phone_only) > 0:
            phone_only.columns = ['Club_Name', 'Recordings', 'Website', 'Phone', 'Status']
            phone_only.to_csv('clean_phones_only.csv', index=False)
            logger.info(f"Clean phones only: {len(phone_only)} clubs")
        
        # Create summary report
        summary = {
            'total_rows': len(df),
            'english_clubs': len(english_df),
            'high_quality_contacts': len(high_quality),
            'medium_quality_contacts': len(medium_quality),
            'clean_emails': len(email_only) if len(email_only) > 0 else 0,
            'clean_phones': len(phone_only) if len(phone_only) > 0 else 0,
            'filtered_out': len(df) - len(english_df)
        }
        
        logger.info("\n📊 CLEANING SUMMARY:")
        logger.info(f"   Total rows: {summary['total_rows']:,}")
        logger.info(f"   English clubs: {summary['english_clubs']:,}")
        logger.info(f"   High quality: {summary['high_quality_contacts']:,}")
        logger.info(f"   Medium quality: {summary['medium_quality_contacts']:,}")
        logger.info(f"   Clean emails: {summary['clean_emails']:,}")
        logger.info(f"   Clean phones: {summary['clean_phones']:,}")
        logger.info(f"   Filtered out: {summary['filtered_out']:,}")
        
        return summary

def main():
    """Run the contact cleaning process"""
    cleaner = ContactCleaner()
    
    input_file = 'mega_27k_contacts.csv'
    
    try:
        summary = cleaner.clean_contacts_data(input_file)
        
        print(f"""
🧹 CONTACT CLEANING COMPLETED!

📁 Clean files created:
   - high_quality_contacts.csv ({summary['high_quality_contacts']} clubs)
   - medium_quality_contacts.csv ({summary['medium_quality_contacts']} clubs)
   - clean_emails_only.csv ({summary['clean_emails']} clubs)
   - clean_phones_only.csv ({summary['clean_phones']} clubs)

🎯 Ready for Louis to use!
        """)
        
    except Exception as e:
        logger.error(f"Error cleaning data: {e}")

if __name__ == "__main__":
    main()