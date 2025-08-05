#!/usr/bin/env python3
import pandas as pd
import requests
from duckduckgo_search import DDGS
import re
import time
from bs4 import BeautifulSoup
import json
from pathlib import Path

print("🦆 DUCKDUCKGO CONTACT FINDER")
print("=" * 35)

# Load target prospects
input_file = "../data/3-contact-details/target_prospects.csv"
df = pd.read_csv(input_file)
print(f"📊 Loaded {len(df)} prospects")

# Process top 5 clubs to test
top_clubs = df.head(5)
print(f"🎯 Testing DDG search on TOP 5 clubs...")
print()

results = []
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
phone_patterns = [
    r"\+44\s?\d{4}\s?\d{6}",
    r"0\d{3}\s?\d{3}\s?\d{4}",
    r"07\d{3}\s?\d{6}",
    r"\+1\s?\d{3}\s?\d{3}\s?\d{4}",
    r"\(\d{3}\)\s?\d{3}-\d{4}"
]

for i, (_, row) in enumerate(top_clubs.iterrows(), 1):
    club_name = row["Club Name"]
    country = row["Country"]
    activity = row["Activity_Score"]
    
    print(f"[{i}/5] 🦆 {club_name} ({country}) - Activity: {activity:.0f}")
    
    result = {
        "Club Name": club_name,
        "Country": country,
        "Activity_Score": activity,
        "Phones": [],
        "Emails": [],
        "Website": "",
        "Contact_Found": False
    }
    
    try:
        # DuckDuckGo search
        search_query = f"\"{club_name}\" football club {country} contact"
        
        with DDGS() as ddgs:
            search_results = list(ddgs.text(search_query, max_results=2))
            
        for search_result in search_results:
            url = search_result.get("href", "")
            
            try:
                # Skip social media
                if any(domain in url for domain in ["facebook.com", "twitter.com", "veo.co"]):
                    continue
                    
                response = session.get(url, timeout=8)
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text()
                
                # Extract contacts
                emails = list(set(re.findall(email_pattern, text)))
                phones = []
                for pattern in phone_patterns:
                    phones.extend(re.findall(pattern, text))
                phones = list(set(phones))
                
                if emails or phones:
                    result.update({
                        "Phones": phones,
                        "Emails": emails,
                        "Website": url,
                        "Contact_Found": True
                    })
                    print(f"    ✅ Found: {len(emails)} emails, {len(phones)} phones")
                    break
                    
            except Exception as e:
                continue
                
        if not result["Contact_Found"]:
            print(f"    ❌ No contacts found")
            
    except Exception as e:
        print(f"    ❌ DDG search failed: {str(e)[:30]}")
    
    results.append(result)
    time.sleep(2)  # Rate limiting

# Save results
Path("../data/3-contact-details").mkdir(parents=True, exist_ok=True)
results_df = pd.DataFrame(results)
results_df.to_csv("../data/3-contact-details/club_contacts_ddg.csv", index=False)

found_contacts = results_df[results_df["Contact_Found"] == True]
print(f"
🦆 DDG CONTACT SEARCH COMPLETE!")
print(f"📊 Processed: {len(results)} clubs")
print(f"📞 Contacts found: {len(found_contacts)} clubs")
print(f"💾 Saved to: data/3-contact-details/club_contacts_ddg.csv")

if len(found_contacts) > 0:
    print(f"
🎯 SUCCESS STORIES:")
    for _, contact in found_contacts.iterrows():
        emails = eval(contact["Emails"]) if isinstance(contact["Emails"], str) else contact["Emails"]
        phones = eval(contact["Phones"]) if isinstance(contact["Phones"], str) else contact["Phones"]
        print(f"• {contact[\"Club Name\"]}: {len(emails)} emails, {len(phones)} phones")

