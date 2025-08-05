#!/usr/bin/env python3
"""
Claret Team Specific Insights Generator
"""

import sys
import os
import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

def generate_claret_insights(match_id):
    """Generate insights specifically for the claret team"""
    
    # Load enhanced events
    data_dir = Path("../data") / match_id
    events_path = data_dir / "enhanced_events.json"
    
    with open(events_path, 'r') as f:
        all_events = json.load(f)
    
    # Extract claret team events
    claret_events = []
    claret_mentioned = []
    
    for event in all_events:
        team = event.get('team', '').lower()
        description = event.get('description', '').lower()
        
        if 'claret' in team or 'claret' in description:
            claret_events.append(event)
        
        # Also look for claret team interactions (saves by claret keeper, etc.)
        if 'claret' in description:
            claret_mentioned.append(event)
    
    print("🎯 CLARET TEAM ANALYSIS")
    print("=" * 50)
    print(f"📊 Direct Claret Events: {len(claret_events)}")
    print(f"📋 Claret Mentions: {len(claret_mentioned)}")
    
    # Initialize Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""Generate specific tactical insights for the CLARET TEAM based on their match events.

CLARET TEAM EVENTS:
{json.dumps(claret_events, indent=2)}

EVENTS MENTIONING CLARET:
{json.dumps(claret_mentioned, indent=2)}

TASK: Provide comprehensive analysis of the Claret team's performance.

ANALYSIS AREAS:
1. **Defensive Performance** - How did they defend?
2. **Goalkeeping** - Goalkeeper performance and saves
3. **Discipline** - Cards, fouls, referee decisions
4. **Tactical Changes** - Substitutions and adjustments
5. **Key Moments** - Critical events involving Claret team

OUTPUT:
Provide a detailed tactical report focusing ONLY on the Claret team's performance, strengths, weaknesses, and key moments from the match.
"""

    try:
        response = model.generate_content(prompt)
        insights = response.text.strip()
        
        print("\n🏈 CLARET TEAM TACTICAL REPORT:")
        print("=" * 50)
        print(insights)
        print("=" * 50)
        
        # Save insights
        output_path = data_dir / "claret_team_insights.txt"
        with open(output_path, 'w') as f:
            f.write("CLARET TEAM TACTICAL ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            f.write(insights)
        
        print(f"📁 Claret insights saved to: {output_path}")
        
        # Show specific events
        print(f"\n📋 CLARET TEAM EVENTS BREAKDOWN:")
        for i, event in enumerate(claret_events, 1):
            timestamp = event.get('timestamp', 0)
            minutes = timestamp // 60
            seconds = timestamp % 60
            event_type = event.get('type', 'unknown').upper()
            description = event.get('description', '')[:80]
            
            print(f"   {i}. {minutes:02d}:{seconds:02d} - {event_type} - {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python claret_team_insights.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = generate_claret_insights(match_id)
    
    if success:
        print("\n🎉 Claret team analysis complete!")
    else:
        sys.exit(1)