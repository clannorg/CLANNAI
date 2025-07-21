import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from googlesearch import search
import time

def find_club_contacts():
    # Read our club list
    df = pd.read_csv('data/feasible_customers.csv')
    
    # Add contact columns
    df['website'] = ''
    df['phone_numbers'] = ''
    df['contact_page'] = ''
    
    def extract_phones(text):
        # Phone patterns for UK/US numbers
        patterns = [
            r'\+44\s?\d{4}\s?\d{6}',  # UK format
            r'0\d{3}\s?\d{3}\s?\d{4}',  # UK local
            r'\+1\s?\d{3}\s?\d{3}\s?\d{4}',  # US format
            r'\(\d{3}\)\s?\d{3}-\d{4}'  # US local
        ]
        phones = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            phones.extend(found)
        return phones
    
    for idx, row in df.iterrows():
        club_name = row['Club Name']
        print(f"\nSearching for {club_name}...")
        
        try:
            # Search for club website
            query = f"{club_name} football club contact"
            search_results = search(query, num_results=3)
            
            for url in search_results:
                if 'facebook' in url or 'twitter' in url:
                    continue
                    
                print(f"Checking {url}")
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for contact page links
                contact_links = soup.find_all('a', text=re.compile('contact|get in touch', re.I))
                
                # Extract all text
                text = soup.get_text()
                phones = extract_phones(text)
                
                if phones:
                    df.at[idx, 'website'] = url
                    df.at[idx, 'phone_numbers'] = ', '.join(phones)
                    print(f"Found numbers: {phones}")
                    break
                    
            time.sleep(2)  # Be nice to servers
            
        except Exception as e:
            print(f"Error with {club_name}: {str(e)}")
            continue
    
    # Save results
    df.to_csv('data/clubs_with_contacts.csv', index=False)
    print("\nSaved results to clubs_with_contacts.csv")

if __name__ == "__main__":
    find_club_contacts() 