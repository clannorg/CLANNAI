#!/usr/bin/env python3
"""
Create a simple contact file with just: Club, Games, Phone, Email
"""

import pandas as pd

def create_simple_contacts():
    """Create a simple contacts file"""
    
    # Load the raw data
    df = pd.read_csv('mega_27k_contacts.csv')
    
    print(f"Loading {len(df)} rows...")
    
    # Filter for clubs that have either email OR phone
    has_contact = df[
        (df['Email'].notna() & (df['Email'] != '')) |
        (df['Phone'].notna() & (df['Phone'] != ''))
    ].copy()
    
    print(f"Found {len(has_contact)} clubs with contacts...")
    
    # Clean up the data
    simple_df = pd.DataFrame()
    simple_df['Club'] = has_contact['Club_Name']
    simple_df['Games'] = has_contact['Recordings']
    simple_df['Phone'] = has_contact['Phone'].fillna('')
    simple_df['Email'] = has_contact['Email'].fillna('')
    
    # Clean phone numbers (remove .0)
    simple_df['Phone'] = simple_df['Phone'].astype(str).str.replace('.0', '', regex=False)
    simple_df['Phone'] = simple_df['Phone'].str.replace('nan', '', regex=False)
    
    # Clean emails
    simple_df['Email'] = simple_df['Email'].astype(str).str.replace('nan', '', regex=False)
    
    # Sort by number of games (highest first)
    simple_df = simple_df.sort_values('Games', ascending=False)
    
    # Save to file
    simple_df.to_csv('simple_contacts.csv', index=False)
    
    print(f"✅ Created simple_contacts.csv with {len(simple_df)} clubs")
    print(f"   Emails: {len(simple_df[simple_df['Email'] != ''])}")
    print(f"   Phones: {len(simple_df[simple_df['Phone'] != ''])}")

if __name__ == "__main__":
    create_simple_contacts()