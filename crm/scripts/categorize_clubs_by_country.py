import csv
import os
import requests
import concurrent.futures
from threading import Lock

# Config
INPUT_CSV = 'data/veo_clubs_2.csv'

OUTPUT_CSV = 'data/all_clubs_by_country.csv'
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDyQMe6inPpyQuYXNFir-lHMsukARGqqJc')
API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
TOTAL_CLUBS = 27676  # Process all clubs
BATCH_SIZE = 500    # 500 clubs per call

headers = {
    'Content-Type': 'application/json',
}

def process_batch(clubs_batch, batch_num):
    """Process a batch of clubs"""
    club_list = "\n".join([f"{i+1}. {club['Club Name']}" for i, club in enumerate(clubs_batch)])
    
    prompt = f"""Analyze this list of {len(clubs_batch)} football clubs and identify the specific location where each club is based.

IMPORTANT: Be very specific about Northern Ireland vs Ireland vs England vs Scotland vs Wales. These are separate countries/regions.

For EVERY club in the list, provide the information in this exact CSV format:
Club Name,Recordings,Club Identifier,Country,Additional Info

Where Country should be the specific country/region:
- Northern Ireland (for clubs in Northern Ireland specifically)
- Ireland (for Republic of Ireland only)
- England (for English clubs)
- Scotland (for Scottish clubs) 
- Wales (for Welsh clubs)
- United States, Germany, Japan, etc. (for other countries)

Additional Info can include city, league, or other relevant details you can infer from the name.

Pay special attention to identifying Northern Ireland clubs - look for club names mentioning Belfast, Derry, Lisburn, Armagh, or other Northern Ireland locations.

Include ALL clubs in your response - don't skip any.

Club list:
{club_list}

CSV output:"""

    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {'key': API_KEY}
    
    try:
        print(f"Processing batch {batch_num} ({len(clubs_batch)} clubs)...")
        response = requests.post(API_URL, headers=headers, params=params, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Parse CSV response
        batch_results = []
        lines = text.split('\n')
        for line in lines:
            if line.strip() and ',' in line and not line.startswith('Club Name'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    # Find matching club from original data
                    club_name = parts[0]
                    for club in clubs_batch:
                        if club['Club Name'] == club_name:
                            batch_results.append({
                                'Club Name': club['Club Name'],
                                'Recordings': club['Recordings'],
                                'Club Identifier': club['Club Identifier'],
                                'Country': parts[3],
                                'Additional Info': parts[4] if len(parts) > 4 else ''
                            })
                            break
        
        print(f"Batch {batch_num} complete: {len(batch_results)} clubs categorized")
        return batch_results
        
    except Exception as e:
        print(f"Error processing batch {batch_num}: {e}")
        return []

def main():
    # Read clubs (limit to first 5000)
    clubs = []
    with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader):
            if i >= TOTAL_CLUBS:
                break
            club_name = row['Club Name']
            if club_name and club_name.strip() not in ('-', '.', '---', '------------', '*', '⚽', '—-', '⚽⚽⚽'):
                clubs.append(row)
    
    print(f"Processing {len(clubs)} clubs in batches of {BATCH_SIZE}...")
    
    # Split into batches and process in parallel
    batches = []
    for i in range(0, len(clubs), BATCH_SIZE):
        batch_clubs = clubs[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        batches.append((batch_clubs, batch_num))
    
    print(f"Launching {len(batches)} batches in parallel...")
    
    # Process all batches in parallel
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(batches)) as executor:
        futures = [executor.submit(process_batch, batch_clubs, batch_num) for batch_clubs, batch_num in batches]
        
        for future in concurrent.futures.as_completed(futures):
            batch_results = future.result()
            all_results.extend(batch_results)
            print(f"Batch completed: {len(batch_results)} clubs categorized")
    
    # Write results to CSV
    if all_results:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['Club Name', 'Recordings', 'Club Identifier', 'Country', 'Additional Info']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\nSuccess! Categorized {len(all_results)} clubs by country")
        print(f"Results saved to {OUTPUT_CSV}")
        
        # Print summary by country
        countries = {}
        for club in all_results:
            country = club['Country']
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\nBreakdown by country (top 20):")
        sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)
        for country, count in sorted_countries[:20]:
            print(f"  {country}: {count} clubs")
        
        if len(sorted_countries) > 20:
            print(f"  ... and {len(sorted_countries) - 20} more countries")
            
        # Show UK/Ireland totals
        uk_countries = ['England', 'Scotland', 'Wales', 'Northern Ireland', 'Ireland', 'United Kingdom']
        uk_total = sum(countries.get(country, 0) for country in uk_countries)
        print(f"\nTotal UK/Ireland clubs: {uk_total}")
    else:
        print("No clubs categorized")

if __name__ == '__main__':
    main()