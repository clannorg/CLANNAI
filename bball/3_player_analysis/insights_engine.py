#!/usr/bin/env python3
"""
Player Insights Engine - Aesthetic Analysis
Generates beautiful ASCII insights from player tracking timeline
"""

import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PlayerInsightsEngine:
    def __init__(self, target_player: str = "Player_31"):
        """Initialize the insights engine with Gemini 2.5"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.target_player = target_player
        
    def load_timeline(self) -> str:
        """Load the player timeline from synthesis output"""
        synthesis_dir = Path(__file__).parent / "synthesis_output"
        timeline_file = synthesis_dir / f"{self.target_player.lower()}_timeline.txt"
        
        if not timeline_file.exists():
            raise FileNotFoundError(f"Timeline file not found: {timeline_file}")
        
        with open(timeline_file, 'r') as f:
            return f.read()
    
    def get_insights_prompt(self, timeline: str) -> str:
        """Generate prompt for concise, stats-focused insights analysis with ASCII art"""
        return f"""
🏀 BASKETBALL PLAYER INSIGHTS (CONCISE)
=======================================

You are a professional basketball analyst. Analyze this player's timeline and provide a report that is:
- CONCISE but includes ASCII art layout
- Focused on HARD STATS (percentages, counts, rates, efficiency)
- Only the most insightful, actionable findings
- Include a player rating (1-10 scale)
- Use ASCII boxes for section headers

PLAYER: {self.target_player}
TIMELINE DATA:
{timeline}

FORMAT:
- Start with a brief player overview in an ASCII box
- List only the most important stats (shooting %, rebounds, assists, turnovers, defensive stats)
- List only the most insightful findings (e.g., "Most effective in transition", "Struggles with contested shots")
- End with a player rating (1-10 scale) and brief verdict
- Use ASCII boxes for section headers, but keep content concise
- NO FLUFF, NO GENERIC PRAISE, JUST HARD INSIGHTS
"""

    def generate_insights(self, timeline: str) -> str:
        """Generate aesthetic insights from timeline"""
        print(f"🎯 Generating insights for {self.target_player}...")
        
        prompt = self.get_insights_prompt(timeline)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
            return f"Error generating insights: {e}"
    
    def save_insights(self, insights: str):
        """Save insights to insights_output directory"""
        output_dir = Path(__file__).parent / "insights_output"
        output_dir.mkdir(exist_ok=True)
        
        insights_file = output_dir / f"{self.target_player.lower()}_insights.txt"
        with open(insights_file, 'w') as f:
            f.write(insights)
        
        print(f"📁 Insights saved to: {output_dir}")
        print(f"   🎯 Insights: {self.target_player.lower()}_insights.txt")

def main():
    """Run aesthetic player insights analysis"""
    print("🎯 PLAYER INSIGHTS ENGINE")
    print("=" * 40)
    print("🏀 Generating aesthetic basketball analysis")
    print()
    
    # Get target player from the tracking script
    from tracking_clip_analyzer import TARGET_PLAYER
    
    engine = PlayerInsightsEngine(target_player=TARGET_PLAYER)
    
    try:
        # Load timeline
        print("📂 Loading player timeline...")
        timeline = engine.load_timeline()
        
        # Generate insights
        print("🧠 Analyzing player performance...")
        insights = engine.generate_insights(timeline)
        
        # Print insights to console
        print("\n" + "="*60)
        print(insights)
        print("="*60)
        
        # Save insights
        engine.save_insights(insights)
        
        print(f"\n✅ Insights generation complete!")
        print(f"   🎯 Created aesthetic analysis for {engine.target_player}")
        
    except Exception as e:
        print(f"❌ Error in insights generation: {e}")

if __name__ == "__main__":
    main() 