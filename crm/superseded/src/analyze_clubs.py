import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_clubs():
    try:
        df = pd.read_csv('data/veo_clubs.csv')
        
        # Basic stats
        print(f"=== Veo Platform Stats ===")
        print(f"Total Clubs: {len(df):,}")
        print(f"Total Recordings: {df['Recordings'].sum():,}")
        print(f"Total Teams: {df['Teams'].sum():,}")
        
        # Activity analysis
        active_clubs = df[df['Recordings'] > 0]
        print(f"\n=== Recording Analysis ===")
        print(f"Active Clubs: {len(active_clubs):,} ({len(active_clubs)/len(df)*100:.1f}%)")
        print(f"Average Recordings per Active Club: {active_clubs['Recordings'].mean():.1f}")
        print(f"Median Recordings per Active Club: {active_clubs['Recordings'].median():.1f}")
        
        # Recording frequency categories
        print(f"\n=== Recording Volume Categories ===")
        recording_cats = pd.cut(active_clubs['Recordings'], 
                              bins=[0, 10, 50, 100, 500, 1000, float('inf')],
                              labels=['1-10', '11-50', '51-100', '101-500', '501-1000', '1000+'])
        volume_stats = recording_cats.value_counts().sort_index()
        for cat, count in volume_stats.items():
            print(f"{cat}: {count:,} clubs ({count/len(active_clubs)*100:.1f}%)")
        
        # Team size analysis for active clubs
        print(f"\n=== Team Size Analysis (Active Clubs) ===")
        teams_with_recordings = active_clubs[active_clubs['Teams'] > 0]
        print(f"Active Clubs with Teams: {len(teams_with_recordings):,}")
        print(f"Average Teams per Active Club: {teams_with_recordings['Teams'].mean():.1f}")
        print(f"Average Recordings per Team: {teams_with_recordings['Recordings'].sum() / teams_with_recordings['Teams'].sum():.1f}")
        
        # High volume users
        print(f"\n=== Power Users (500+ recordings) ===")
        power_users = active_clubs[active_clubs['Recordings'] >= 500]
        print(f"Number of Power Users: {len(power_users)}")
        print("\nTop 10 Most Active Clubs:")
        print(power_users.nlargest(10, 'Recordings')[['Club Name', 'Recordings', 'Teams']])
        
        # Create visualizations
        plt.figure(figsize=(15, 5))
        
        # Recording distribution
        plt.subplot(1, 3, 1)
        sns.histplot(data=active_clubs, x='Recordings', bins=30)
        plt.title('Recording Distribution\n(Active Clubs)')
        plt.yscale('log')
        
        # Teams vs Recordings scatter
        plt.subplot(1, 3, 2)
        sns.scatterplot(data=teams_with_recordings, x='Teams', y='Recordings', alpha=0.5)
        plt.title('Recordings vs Teams\n(Active Clubs)')
        
        # Recording volume categories
        plt.subplot(1, 3, 3)
        volume_stats.plot(kind='bar')
        plt.title('Recording Volume Categories')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('data/veo_analysis.png')
        print("\nDetailed analysis plots saved to data/veo_analysis.png")
        
    except ImportError as e:
        print(f"Error: Missing required package. Please install with: pip install pandas matplotlib seaborn\n{str(e)}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    analyze_clubs() 