#!/usr/bin/env python3
"""
Step 5: Goal Performance Summary
Extracts goal-related actions from detailed player tracking data.
"""

import os
import sys
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / 'ai' / '.env')

class GoalSummaryExtractor:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        print("🤖 Goal summary extractor initialized with Gemini 2.5 Pro")

    def get_goal_summary_prompt(self, tracking_data: str) -> str:
        """Generate prompt for goal summary extraction."""
        return f"""You are analyzing detailed player tracking data from a football game.

TARGET PLAYER: White guy with grey t-shirt under orange bib

TASK: Extract ONLY goal-related actions and create a comprehensive summary.

ANALYSIS DATA:
{tracking_data}

INSTRUCTIONS:
1. Look for any mentions of:
   - Goals scored by the target player
   - Goals conceded (if player is goalkeeper)
   - Shots taken by the target player
   - Saves made (if goalkeeper)
   - Goal attempts
   - Goal-scoring opportunities

2. Create a summary with:
   - Total goals scored (if any)
   - Total goals conceded (if goalkeeper)
   - Shots taken
   - Saves made
   - Key goal-scoring moments with timestamps
   - Overall goal performance rating

3. Format as:
   "GOAL PERFORMANCE SUMMARY
   [Player Name/Description]
   
   GOALS SCORED: [number]
   GOALS CONCEDED: [number] (if goalkeeper)
   SHOTS TAKEN: [number]
   SAVES MADE: [number] (if goalkeeper)
   
   KEY MOMENTS:
   [timestamp] - [description of goal-related action]
   
   OVERALL PERFORMANCE: [rating and brief summary]"

Focus ONLY on goal-related actions. Ignore other activities like passing, running, etc."""

    def extract_goal_summary(self, game_id: str) -> bool:
        """Extract goal summary from detailed tracking data."""
        print(f"🎯 Step 5: Goal Performance Summary for {game_id}")
        
        # Load detailed tracking data
        output_dir = Path(f"../output/{game_id}")
        detailed_data_path = output_dir / "detailed_player_analyses_parallel.json"
        
        if not detailed_data_path.exists():
            print(f"❌ Detailed tracking data not found: {detailed_data_path}")
            return False
        
        with open(detailed_data_path, 'r') as f:
            tracking_data = json.load(f)
        
        print(f"📊 Loaded {len(tracking_data)} clip analyses")
        
        # Convert to text format for Gemini
        tracking_text = "CLIP-BY-CLIP ANALYSIS:\n\n"
        for analysis in tracking_data:
            if analysis['player_found']:
                tracking_text += f"🕐 {analysis['clip_timestamp']}:\n"
                tracking_text += f"{analysis['analysis']}\n\n"
        
        # Generate goal summary
        prompt = self.get_goal_summary_prompt(tracking_text)
        
        print("🔍 Analyzing goal-related actions...")
        
        try:
            response = self.model.generate_content(prompt)
            goal_summary = response.text.strip()
            
            # Save goal summary
            goal_summary_path = output_dir / "goal_performance_summary.txt"
            with open(goal_summary_path, 'w') as f:
                f.write(goal_summary)
            
            print(f"✅ Goal summary extracted!")
            print(f"📁 Saved to: {goal_summary_path}")
            print(f"\n📊 GOAL PERFORMANCE SUMMARY:")
            print("=" * 50)
            print(goal_summary)
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting goal summary: {e}")
            return False

def main():
    """Main function to extract goal summary."""
    if len(sys.argv) != 2:
        print("Usage: python 5_goal_summary.py <game-id>")
        print("Example: python 5_goal_summary.py brixton5s-20240807")
        sys.exit(1)
    
    game_id = sys.argv[1]
    
    extractor = GoalSummaryExtractor()
    success = extractor.extract_goal_summary(game_id)
    
    if success:
        print(f"🎯 Goal performance analysis complete!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 