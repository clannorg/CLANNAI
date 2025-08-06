import csv
import os
import requests
import concurrent.futures
from threading import Lock
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config
INPUT_CSV = 'data/1-veo-scraper/veo_clubs.csv'  # 27k clubs
OUTPUT_CSV = 'data/2-by-country/football_clubs_by_country.csv'
PROGRESS_FILE = 'data/2-by-country/gemini_progress.json'
API_KEY = os.getenv('GEMINI_API_KEY')
API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'
BATCH_SIZE = 100    # Smaller batches for better accuracy
MAX_WORKERS = 5     # Conservative parallel processing

headers = {
    'Content-Type': 'application/json',
}

write_lock = Lock()
processed_count = 0

def load_progress():
    """Load processing progress"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"processed_batches": [], "completed_clubs": 0}

def save_progress(progress):
    """Save processing progress"""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def process_batch(clubs_batch, batch_num, progress):
    """Process a batch of clubs with Gemini"""
    global processed_count
    
    # Skip if already processed
    if batch_num in progress["processed_batches"]:
        print(f"⏭️  Batch {batch_num} already processed, skipping...")
        return []
    
    club_list = "\n".join([f"{i+1}. {club['Club Name']}" for i, club in enumerate(clubs_batch)])
    
    prompt = f"""Analyze this list of {len(clubs_batch)} sports clubs and ONLY return football/soccer clubs with their locations.

🚨 CRITICAL REQUIREMENTS:
1. ONLY include actual football/soccer clubs (exclude rugby, GAA, basketball, hockey, etc.)
2. Be very specific about locations: Northern Ireland vs Ireland vs England vs Scotland vs Wales
3. Exclude: schools, colleges, academies unless they are PRIMARILY football clubs
4. Exclude: rugby clubs (RFC), GAA clubs, basketball, hockey, cricket, etc.

For EVERY FOOTBALL CLUB found, provide this exact CSV format:
Club Name,Recordings,Club Identifier,Country,Sport,Additional Info

Countries must be specific:
- Northern Ireland (Belfast, Derry, Lisburn, Armagh areas)
- Ireland (Republic of Ireland only)
- England, Scotland, Wales
- United States, Germany, Japan, etc.

Sport must be: "Football" or "Soccer"

SKIP non-football clubs entirely - do not include them in your response.

Club list:
{club_list}

CSV output (FOOTBALL CLUBS ONLY):"""

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192
        }
    }
    params = {'key': API_KEY}
    
    try:
        print(f"🤖 Processing batch {batch_num} ({len(clubs_batch)} clubs)...")
        response = requests.post(API_URL, headers=headers, params=params, json=data, timeout=180)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Parse CSV response
        batch_results = []
        lines = text.split('\n')
        for line in lines:
            if line.strip() and ',' in line and not line.startswith('Club Name'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:  # Club Name, Recordings, Identifier, Country, Sport
                    club_name = parts[0]
                    # Find matching club from original data
                    for club in clubs_batch:
                        if club['Club Name'].lower() == club_name.lower():
                            batch_results.append({
                                'Club Name': club['Club Name'],
                                'Recordings': club['Recordings'],
                                'Club Identifier': club['Club Identifier'],
                                'Country': parts[3],
                                'Sport': parts[4],
                                'Additional Info': parts[5] if len(parts) > 5 else ''
                            })
                            break
        
        # Update progress
        with write_lock:
            progress["processed_batches"].append(batch_num)
            progress["completed_clubs"] += len(batch_results)
            save_progress(progress)
            processed_count += len(batch_results)
        
        football_count = len(batch_results)
        print(f"✅ Batch {batch_num} complete: {football_count} football clubs found")
        
        # Rate limiting
        time.sleep(1)
        return batch_results
        
    except Exception as e:
        print(f"❌ Error processing batch {batch_num}: {e}")
        return []

def main():
    global processed_count
    
    if not API_KEY:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return
    
    print("🏈 GEMINI FOOTBALL CLUB CATEGORIZER")
    print("=" * 50)
    
    # Load progress
    progress = load_progress()
    print(f"📊 Previous progress: {progress['completed_clubs']} clubs processed")
    
    # Read all clubs
    clubs = []
    print(f"📖 Reading clubs from {INPUT_CSV}...")
    
    try:
        with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                club_name = row['Club Name']
                if club_name and club_name.strip() not in ('-', '.', '---', '------------', '*', '⚽', '—-', '⚽⚽⚽', ''):
                    clubs.append(row)
    except FileNotFoundError:
        print(f"❌ File not found: {INPUT_CSV}")
        return
    
    print(f"📊 Found {len(clubs)} total clubs to process")
    
    # Split into batches
    batches = []
    for i in range(0, len(clubs), BATCH_SIZE):
        batch_clubs = clubs[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        batches.append((batch_clubs, batch_num))
    
    print(f"🔄 Processing {len(batches)} batches with {MAX_WORKERS} workers...")
    
    # Create output directory
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # Process batches in parallel (with limited workers)
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_batch, batch_clubs, batch_num, progress) 
                  for batch_clubs, batch_num in batches]
        
        for future in concurrent.futures.as_completed(futures):
            batch_results = future.result()
            all_results.extend(batch_results)
            print(f"🎯 Total football clubs found so far: {len(all_results)}")
    
    # Write final results
    if all_results:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['Club Name', 'Recordings', 'Club Identifier', 'Country', 'Sport', 'Additional Info']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\n🏆 SUCCESS! Found {len(all_results)} football clubs")
        print(f"📁 Results saved to {OUTPUT_CSV}")
        
        # Summary by country
        countries = {}
        for club in all_results:
            country = club['Country']
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n🌍 Football clubs by country:")
        sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)
        for country, count in sorted_countries:
            print(f"  {country}: {count} clubs")
        
        # UK/Ireland focus
        uk_countries = ['England', 'Scotland', 'Wales', 'Northern Ireland', 'Ireland']
        uk_total = sum(countries.get(country, 0) for country in uk_countries)
        print(f"\n🎯 Total UK/Ireland football clubs: {uk_total}")
        
        # Show top clubs by recordings
        sorted_clubs = sorted(all_results, key=lambda x: int(x['Recordings']), reverse=True)
        print(f"\n🔥 Top 10 most active football clubs:")
        for i, club in enumerate(sorted_clubs[:10], 1):
            print(f"  {i}. {club['Club Name']} ({club['Country']}): {club['Recordings']} recordings")
    
    else:
        print("❌ No football clubs found")

if __name__ == '__main__':
    main()