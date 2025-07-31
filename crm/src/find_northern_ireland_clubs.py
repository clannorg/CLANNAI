import csv
import os
import requests
import time

# Config
INPUT_CSV = 'data/veo_clubs_2.csv'
OUTPUT_CSV = 'data/northern_ireland_clubs.csv'
API_KEY = os.getenv('GEMINI_API_KEY')
API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent'

if not API_KEY:
    API_KEY = input('Enter your GEMINI_API_KEY: ').strip()

headers = {
    'Content-Type': 'application/json',
}

def is_northern_ireland_club(club_name):
    prompt = f"Is the following football club based in Northern Ireland? Only answer 'Yes' or 'No'. Club: {club_name}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {'key': API_KEY}
    try:
        response = requests.post(API_URL, headers=headers, params=params, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text'].strip().lower()
        return text.startswith('yes')
    except Exception as e:
        print(f"Error for club '{club_name}': {e}")
        return False

def main():
    with open(INPUT_CSV, newline='', encoding='utf-8') as infile, \
         open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        count = 0
        for row in reader:
            club_name = row['Club Name']
            if not club_name or club_name.strip() in ('-', '.', '---', '------------', '*', '⚽', '—-', '⚽⚽⚽'):
                continue  # skip empty or placeholder names
            if is_northern_ireland_club(club_name):
                writer.writerow(row)
                print(f"Northern Ireland club found: {club_name}")
            count += 1
            if count % 10 == 0:
                print(f"Processed {count} clubs...")
            time.sleep(1.2)  # avoid rate limits
    print(f"Done. Results saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    main()