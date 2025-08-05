import csv
import re

# This script creates the missing NI clubs input file from the veo data
INPUT_CSV = 'data/veo_clubs_2.csv'
OUTPUT_CSV = 'data/contacts/ni_clubs/ni_football_clubs_only.csv'

def is_ni_football_club(club_name):
    """Identify Northern Ireland football clubs"""
    
    name_lower = club_name.lower()
    
    # Known NI football clubs (from NIFL and other leagues)
    ni_clubs = [
        'crusaders', 'linfield', 'glentoran', 'cliftonville', 'glenavon',
        'ballymena united', 'coleraine', 'larne', 'portadown', 'dungannon',
        'newry', 'carrick rangers', 'warrenpoint', 'institute', 'dergview',
        'knockbreda', 'annagh', 'dollingstown', 'limavady', 'armagh city',
        'bangor', 'lisburn distillery', 'moyola park', 'comber rec',
        'greenisland', 'lurgan celtic', 'dundela', 'banbridge town',
        'ballinamallard', 'fivemiletown'
    ]
    
    # Check for known clubs
    for ni_club in ni_clubs:
        if ni_club in name_lower:
            return True
    
    # Check for NI location indicators
    ni_locations = [
        'belfast', 'derry', 'lisburn', 'antrim', 'down', 'armagh',
        'fermanagh', 'tyrone', 'londonderry', 'northern ireland'
    ]
    
    for location in ni_locations:
        if location in name_lower and ('fc' in name_lower or 'football' in name_lower):
            return True
    
    return False

def create_ni_input_file():
    """Extract NI football clubs from veo data"""
    
    ni_clubs = []
    
    print("🔍 Scanning veo clubs for Northern Ireland football clubs...")
    
    with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            club_name = row['Club Name']
            recordings = int(row['Recordings'])
            
            # Only include clubs with good data and 10+ recordings
            if recordings >= 10 and is_ni_football_club(club_name):
                ni_clubs.append({
                    'Club Name': club_name,
                    'Recordings': recordings,
                    'Club Identifier': row.get('Club Identifier', ''),
                    'Country': 'Northern Ireland',
                    'Additional Info': ''
                })
                print(f"✅ Found: {club_name} ({recordings} recordings)")
    
    # Sort by recordings (most active first)
    ni_clubs.sort(key=lambda x: x['Recordings'], reverse=True)
    
    # Write the filtered NI clubs
    if ni_clubs:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Club Name', 'Recordings', 'Club Identifier', 'Country', 'Additional Info']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ni_clubs)
        
        print(f"\n🏆 Success! Found {len(ni_clubs)} Northern Ireland football clubs")
        print(f"📁 Saved to: {OUTPUT_CSV}")
        
        print(f"\n🔥 Top NI clubs by recordings:")
        for i, club in enumerate(ni_clubs[:10], 1):
            print(f"  {i}. {club['Club Name']}: {club['Recordings']} recordings")
    
    else:
        print("❌ No Northern Ireland football clubs found")

if __name__ == '__main__':
    create_ni_input_file()