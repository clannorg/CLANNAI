import csv

# Config
INPUT_CSV = 'data/ni_clubs/ni_clubs_with_recordings.csv'
OUTPUT_CSV = 'data/ni_clubs/ni_football_clubs_only.csv'

def is_football_club(club_name, additional_info):
    """Determine if a club is a football/soccer club"""
    
    # Convert to lowercase for easier matching
    name_lower = club_name.lower()
    info_lower = additional_info.lower() if additional_info else ""
    
    # Exclude non-football clubs
    exclude_keywords = [
        'rugby', 'rfc', 'gaa', 'gac', 'gaelic', 'hockey', 'grammar school', 
        'high school', 'college', 'academy', 'school', 'camogie', 'hurling',
        'volleyball', 'cricket', 'athletics', 'golf', 'tennis', 'basketball'
    ]
    
    for keyword in exclude_keywords:
        if keyword in name_lower or keyword in info_lower:
            return False
    
    # Include obvious football clubs
    football_keywords = [
        'fc', 'football club', 'soccer', 'united', 'city fc', 'town fc', 
        'rangers fc', 'wanderers', 'athletic fc', 'celtic fc'
    ]
    
    for keyword in football_keywords:
        if keyword in name_lower:
            return True
    
    # Include clubs with football-related additional info
    if 'football' in info_lower and 'rugby' not in info_lower:
        return True
    
    # Manual inclusions for known football clubs
    known_football_clubs = [
        'crusaders', 'glenavon', 'cliftonville', 'glentoran', 'linfield',
        'coleraine', 'ballymena', 'carrick rangers', 'larne', 'newry',
        'portadown', 'dungannon swifts', 'warrenpoint', 'institute',
        'dergview', 'knockbreda', 'annagh', 'dollingstown', 'limavady',
        'armagh city', 'bangor', 'lisburn distillery', 'moyola park',
        'comber rec', 'greenisland', 'lurgan celtic', 'dundela',
        'banbridge town', 'ballinamallard', 'fivemiletown'
    ]
    
    for known_club in known_football_clubs:
        if known_club in name_lower:
            return True
    
    # Default to False if unsure
    return False

def filter_football_clubs():
    """Filter the CSV to only include football clubs"""
    
    football_clubs = []
    
    with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        for row in reader:
            club_name = row['Club Name']
            additional_info = row.get('Additional Info', '')
            
            if is_football_club(club_name, additional_info):
                football_clubs.append(row)
                print(f"✓ {club_name}")
            else:
                print(f"✗ {club_name} (excluded - not football)")
    
    # Write filtered results
    if football_clubs:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['Club Name', 'Recordings', 'Club Identifier', 'Country', 'Additional Info']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(football_clubs)
        
        print(f"\n✅ Filtered {len(football_clubs)} football clubs")
        print(f"📁 Saved to: {OUTPUT_CSV}")
        
        # Show top clubs by recordings
        football_clubs.sort(key=lambda x: int(x['Recordings']), reverse=True)
        print(f"\n🔥 Top 10 football clubs by recordings:")
        for i, club in enumerate(football_clubs[:10], 1):
            print(f"  {i}. {club['Club Name']}: {club['Recordings']} recordings")
    
    else:
        print("❌ No football clubs found")

if __name__ == '__main__':
    filter_football_clubs()