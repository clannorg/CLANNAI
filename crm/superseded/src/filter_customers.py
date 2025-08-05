import pandas as pd

def filter_feasible_customers():
    # Read the full dataset
    df = pd.read_csv('data/veo_clubs.csv')
    
    # Filter for feasible customers:
    # 1. Has a proper name (not unnamed/symbols)
    # 2. Has at least 1 recording or team
    feasible = df[
        # Remove unnamed clubs and pure symbols
        (~df['Club Name'].str.contains(r'^[\_\-\>\µ\⚽]+$', regex=True)) &
        (~df['Club Name'].str.contains('Unnamed Club')) &
        # Must have recordings or teams
        ((df['Recordings'] > 0) | (df['Teams'] > 0))
    ]
    
    # Sort by activity level (recordings + teams)
    feasible['Activity_Score'] = feasible['Recordings'] + (feasible['Teams'] * 10)
    feasible = feasible.sort_values('Activity_Score', ascending=False)
    
    # Save filtered dataset
    feasible.to_csv('data/feasible_customers.csv', index=False)
    
    print(f"=== Feasible Customer Analysis ===")
    print(f"Total Feasible Customers: {len(feasible):,}")
    print(f"With Recordings: {len(feasible[feasible['Recordings'] > 0]):,}")
    print(f"With Teams: {len(feasible[feasible['Teams'] > 0]):,}")
    print(f"\nTop 10 Most Active Feasible Customers:")
    print(feasible[['Club Name', 'Recordings', 'Teams']].head(10))

if __name__ == "__main__":
    filter_feasible_customers() 