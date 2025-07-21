import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from googlesearch import search
import time

def extract_contacts(text):
    # Phone patterns - expanded to catch more formats
    phone_patterns = [
        r'\+44\s?\d{4}\s?\d{6}',          # UK +44
        r'0\d{3}\s?\d{3}\s?\d{4}',        # UK local
        r'0\d{4}\s?\d{6}',                # UK local alt
        r'07\d{3}\s?\d{6}',               # UK mobile
        r'\+1\s?\d{3}\s?\d{3}\s?\d{4}',   # US/CA
        r'\(\d{3}\)\s?\d{3}-\d{4}',       # US/CA parentheses
        r'\d{3}[-\.]\d{3}[-\.]\d{4}'      # US/CA dots/dashes
    ]
    
    # Email pattern - improved to catch more valid emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    
    # Find all matches
    phones = []
    for pattern in phone_patterns:
        found = re.findall(pattern, text)
        phones.extend(found)
    
    emails = re.findall(email_pattern, text.lower())  # lowercase to avoid duplicates
    
    # Clean up results
    phones = list(set(phones))  # Remove duplicates
    emails = list(set(emails))  # Remove duplicates
    
    return phones, emails

def find_club_contacts():
    # Read our club list and sort by activity score
    df = pd.read_csv('data/feasible_customers.csv')
    df = df.sort_values('Activity_Score', ascending=False)
    
    # Take only top 20 clubs
    df = df.head(20)
    
    # Create new contacts dataframe
    contacts_df = pd.DataFrame(columns=['Club Name', 'Phones', 'Emails', 'Website'])
    
    total_clubs = len(df)
    found_contacts = 0
    
    for idx, row in df.iterrows():
        club_name = row['Club Name']
        print(f"\n[{idx+1}/20] {club_name}")
        print(f"Activity Score: {row['Activity_Score']}")
        
        try:
            query = f"{club_name} football club contact"
            for url in search(query, num_results=2):
                if any(x in url.lower() for x in ['facebook.com', 'twitter.com', 'instagram.com']):
                    continue
                    
                print(f"Checking {url}")
                response = requests.get(url, timeout=5)
                text = response.text
                
                phones, emails = extract_contacts(text)
                
                if phones or emails:
                    contacts_df.loc[len(contacts_df)] = {
                        'Club Name': club_name,
                        'Phones': '; '.join(phones),
                        'Emails': '; '.join(emails),
                        'Website': url
                    }
                    found_contacts += 1
                    print(f"Found: {len(phones)} phones, {len(emails)} emails")
                    break
            
            time.sleep(1)  # Small delay between searches
            
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
    
    # Save results
    contacts_df.to_csv('data/top20_contacts.csv', index=False)
    print(f"\nComplete! Found contacts for {found_contacts} clubs")
    print("\nResults preview:")
    print(contacts_df)

if __name__ == "__main__":
    find_club_contacts() 