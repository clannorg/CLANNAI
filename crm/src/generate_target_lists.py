import pandas as pd

def generate_target_lists():
    # Read the CSV
    df = pd.read_csv('data/feasible_customers.csv')
    
    # Create different target segments
    
    # 1. Enterprise Targets (High volume, many teams)
    enterprise = df[
        (df['Recordings'] >= 1000) | 
        (df['Teams'] >= 30)
    ].sort_values('Activity_Score', ascending=False)
    
    # 2. Growth Potential (Medium recordings, growing team count)
    growth = df[
        (df['Recordings'].between(500, 999)) & 
        (df['Teams'] >= 10)
    ].sort_values('Activity_Score', ascending=False)
    
    # 3. Active Users (Regular recording activity)
    active = df[
        (df['Recordings'].between(200, 499)) & 
        (df['Teams'] >= 5)
    ].sort_values('Activity_Score', ascending=False)
    
    # Save target lists
    def save_target_list(data, name, description):
        markdown = f"# {name}\n\n{description}\n\n"
        markdown += "| Club Name | Recordings | Teams | Activity Score |\n"
        markdown += "|-----------|------------|-------|----------------|\n"
        
        for _, row in data.iterrows():
            markdown += f"| {row['Club Name']} | {row['Recordings']} | {row['Teams']} | {row['Activity_Score']} |\n"
        
        with open(f'data/targets_{name.lower().replace(" ", "_")}.md', 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        print(f"Generated {name} list with {len(data)} targets")
    
    # Generate the lists
    save_target_list(
        enterprise,
        "Enterprise Targets",
        "High-value targets with large recording volumes or team counts. Priority accounts for AI analysis offering."
    )
    
    save_target_list(
        growth,
        "Growth Potential",
        "Medium-sized clubs showing strong growth and regular platform usage. Good candidates for expanded services."
    )
    
    save_target_list(
        active,
        "Active Users",
        "Consistently active clubs that could benefit from advanced features and increased usage."
    )

if __name__ == "__main__":
    generate_target_lists() 