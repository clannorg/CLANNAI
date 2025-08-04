#!/usr/bin/env python3
"""
Game Events Insights Engine - Comprehensive Basketball Analysis
Generates beautiful ASCII insights from game events timeline
"""

import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GameEventsInsightsEngine:
    def __init__(self):
        """Initialize the insights engine with Gemini 2.5 Pro"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def load_events_timeline(self) -> str:
        """Load the events timeline from synthesis output"""
        synthesis_dir = Path(__file__).parent / "synthesis_output"
        timeline_file = synthesis_dir / "events_timeline.txt"
        
        if not timeline_file.exists():
            raise FileNotFoundError(f"Events timeline not found: {timeline_file}")
        
        with open(timeline_file, 'r') as f:
            timeline = f.read()
        
        print(f"📂 Loaded events timeline: {timeline_file}")
        return timeline
    
    def get_insights_prompt(self, timeline: str) -> str:
        """Generate prompt for comprehensive game insights analysis"""
        return f"""
🏀 BASKETBALL GAME INSIGHTS ANALYSIS
====================================

You are a professional basketball analyst. Analyze this game events timeline and provide a report with TWO SECTIONS:

**SECTION 1: SIMPLE GAME SUMMARY (FIRST)**
Write a clear, simple summary like this:
- Who won and by how much?
- Who were the top 3 scorers with their points?
- What was the key moment that decided the game?
- What type of game was this (pickup, scrimmage, etc.)?
- Keep this section under 150 words, simple language

**SECTION 2: COMPREHENSIVE ANALYSIS (SECOND)**
Then provide detailed analysis with:
- Final score breakdown and shooting percentages
- Player performance ratings (1-10 scale)
- Game flow and momentum shifts
- Tactical insights and patterns
- Clutch moments and key plays
- ASCII charts and visual stats
- **Team analysis by basket + jersey color**

**PLAYER CLASSIFICATION:**
Classify players by BOTH their jersey color AND which basket they're shooting at:
- **LEFT BASKET TEAM:** Players shooting at LEFT basket (jersey color + "LEFT")
- **RIGHT BASKET TEAM:** Players shooting at RIGHT basket (jersey color + "RIGHT")
- Track which players switch baskets during the game
- Analyze team performance by basket + color combinations

**BASKET ANALYSIS:**
- **LEFT BASKET:** One team's offensive basket
- **RIGHT BASKET:** Other team's offensive basket
- Teams switch baskets at halftime or when possession changes
- Track which team is shooting at which basket

**FORMAT:**
1. Start with "🏀 GAME SUMMARY" (simple and clear)
2. Then "📊 DETAILED ANALYSIS" (complex and fancy)
3. Use ASCII boxes and visual elements in the detailed section
4. Include player ratings and charts
5. **Classify players as "Blue-LEFT", "White-RIGHT", etc.**

**GAME EVENTS DATA:**
{timeline}

Generate a professional report that's both clear AND comprehensive.
"""

    def generate_insights(self, timeline: str) -> str:
        """Generate comprehensive game insights using Gemini 2.5 Pro"""
        print("🎯 Generating comprehensive game insights...")
        
        prompt = self.get_insights_prompt(timeline)
        
        try:
            response = self.model.generate_content(prompt)
            insights = response.text.strip()
            
            print("✅ Insights generated successfully")
            return insights
            
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
            return f"Error generating insights: {e}"
    
    def save_insights(self, insights: str):
        """Save insights to insights_output directory"""
        insights_dir = Path(__file__).parent / "insights_output"
        insights_dir.mkdir(exist_ok=True)
        
        insights_file = insights_dir / "game_insights.txt"
        with open(insights_file, 'w') as f:
            f.write(insights)
        
        print(f"📁 Insights saved to: {insights_dir}")
        print(f"   📊 Analysis: game_insights.txt")
    
    def run_analysis(self):
        """Run the complete insights analysis"""
        print("🏀 GAME EVENTS INSIGHTS ENGINE")
        print("=" * 40)
        print("📊 Generating comprehensive basketball analysis")
        print()
        
        try:
            # Load events timeline
            timeline = self.load_events_timeline()
            
            # Generate insights
            insights = self.generate_insights(timeline)
            
            # Print insights to console
            print("\n" + "=" * 60)
            print("🎯 GAME INSIGHTS ANALYSIS")
            print("=" * 60)
            print(insights)
            print("=" * 60)
            
            # Save insights
            self.save_insights(insights)
            
            print(f"\n✅ Game insights analysis complete!")
            print(f"   📊 Comprehensive basketball analysis generated")
            print(f"   🎯 Visual stats and insights created")
            
        except Exception as e:
            print(f"❌ Error in insights analysis: {e}")

def main():
    """Run the game events insights engine"""
    engine = GameEventsInsightsEngine()
    engine.run_analysis()

if __name__ == "__main__":
    main() 