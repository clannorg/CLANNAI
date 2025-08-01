import json
import csv

# Load the progress data that contains all the contacts we found
progress_file = 'data/ni_clubs/scraper_progress.json'
clubs_file = 'data/ni_clubs/ni_clubs_with_recordings.csv'
output_file = 'data/ni_clubs/ni_clubs_contacts_extracted.csv'

def extract_contacts():
    # Load progress data
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    # Load clubs data
    clubs = []
    with open(clubs_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clubs.append(row)
    
    print(f"Found contact data for {len(progress)} clubs")
    
    # Extract contacts for each club
    output_data = []
    for club in clubs:
        club_name = club['Club Name']
        recordings = club['Recordings']
        location = club.get('Additional Info', '')
        
        if club_name in progress:
            contact_data = progress[club_name]
            phones = '; '.join(contact_data.get('phones', []))
            emails = '; '.join(contact_data.get('emails', []))
            website = contact_data.get('website', '')
            facebook = contact_data.get('facebook', '')
        else:
            phones = ''
            emails = ''
            website = ''
            facebook = ''
        
        output_row = {
            'Club Name': club_name,
            'Recordings': recordings,
            'Location': location,
            'Phones': phones,
            'Emails': emails,
            'Website': website,
            'Facebook': facebook,
            'Contact Status': 'Found' if (phones or emails) else 'No contacts'
        }
        output_data.append(output_row)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Club Name', 'Recordings', 'Location', 'Phones', 'Emails', 'Website', 'Facebook', 'Contact Status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)
    
    # Show summary
    clubs_with_contacts = sum(1 for row in output_data if row['Contact Status'] == 'Found')
    total_phones = sum(1 for row in output_data if row['Phones'])
    total_emails = sum(1 for row in output_data if row['Emails'])
    
    print(f"\nResults saved to {output_file}")
    print(f"Summary:")
    print(f"  - {clubs_with_contacts}/{len(output_data)} clubs have contact information")
    print(f"  - {total_phones} clubs have phone numbers")
    print(f"  - {total_emails} clubs have email addresses")
    
    # Show top clubs with contacts
    print(f"\nTop clubs with contacts (by recordings):")
    with_contacts = [row for row in output_data if row['Contact Status'] == 'Found']
    with_contacts.sort(key=lambda x: int(x['Recordings']), reverse=True)
    
    for i, club in enumerate(with_contacts[:10]):
        phones_count = len(club['Phones'].split('; ')) if club['Phones'] else 0
        emails_count = len(club['Emails'].split('; ')) if club['Emails'] else 0
        print(f"  {i+1}. {club['Club Name']} ({club['Recordings']} recordings) - {phones_count} phones, {emails_count} emails")

if __name__ == '__main__':
    extract_contacts()