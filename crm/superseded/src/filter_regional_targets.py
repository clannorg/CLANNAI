import pandas as pd
import re

def is_uk_club(name):
    uk_indicators = [
        'FC', 'United', 'Town', 'City', 'Athletic', 'Rangers', 'Celtic',
        'AFC', 'Utd', 'Academy', 'School', 'College', 'Ltd', 'Limited',
        'Sheffield', 'Manchester', 'Liverpool', 'London', 'Birmingham',
        'Glasgow', 'Edinburgh', 'Belfast', 'Cardiff'
    ]
    return any(indicator.lower() in name.lower() for indicator in uk_indicators)

def is_us_club(name):
    us_indicators = [
        'Soccer', 'SC', 'High School', 'Academy', 'University', 
        'College', 'Athletics', 'Eagles', 'Hawks', 'Patriots',
        'California', 'Florida', 'Texas', 'New York', 'Chicago',
        'AYSO', 'Club', 'United', 'Force', 'Elite'
    ]
    return any(indicator.lower() in name.lower() for indicator in us_indicators)

def filter_regional_targets():
    # Read the feasible customers
    df = pd.read_csv('data/feasible_customers.csv')
    
    # Create regional segments
    uk_clubs = df[df['Club Name'].apply(is_uk_club)].sort_values('Activity_Score', ascending=False)
    us_clubs = df[df['Club Name'].apply(is_us_club)].sort_values('Activity_Score', ascending=False)
    
    # Save as markdown files
    def save_target_list(data, region):
        markdown = f"# {region} Target Clubs\n\n"
        markdown += "| Club Name | Recordings | Teams | Activity Score |\n"
        markdown += "|-----------|------------|-------|----------------|\n"
        
        for _, row in data.iterrows():
            markdown += f"| {row['Club Name']} | {row['Recordings']} | {row['Teams']} | {row['Activity_Score']} |\n"
        
        with open(f'data/targets_{region.lower()}.md', 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"Found {len(data)} potential {region} targets")
        print(f"Top 5 {region} targets by activity:")
        print(data[['Club Name', 'Activity_Score']].head())
        print("\n")
    
    save_target_list(uk_clubs, "UK")
    save_target_list(us_clubs, "US")

if __name__ == "__main__":
    filter_regional_targets() 