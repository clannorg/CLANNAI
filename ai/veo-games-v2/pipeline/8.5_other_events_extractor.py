#!/usr/bin/env python3
"""
8.5 Other Events Extractor
Extracts fouls, cards, corners, substitutions and other events from the complete timeline
Uses intelligent analysis to identify significant non-goal/shot events
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class OtherEventsExtractor:
    def __init__(self):
        """Initialize with Gemini for intelligent event extraction"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("📋 Other Events Extractor initialized with Gemini AI")

    def get_extraction_prompt(self, complete_timeline: str) -> str:
        """Create prompt for extracting other football events"""
        return f"""You are an expert football analyst tasked with extracting significant non-goal/shot events from a match timeline.

COMPLETE MATCH TIMELINE:
{complete_timeline}

TASK: Extract and categorize significant football events beyond goals and shots.

TARGET EVENTS TO FIND:
1. **Fouls** - Including free kicks awarded, tackles, challenges
2. **Cards** - Yellow cards, red cards (look for referee decisions)
3. **Corners** - Corner kicks taken by either team
4. **Substitutions** - Player changes (in/out)
5. **Offsides** - Offside calls and decisions
6. **Penalties** - Penalty awards (separate from goals)
7. **Throw-ins** - Significant throw-in situations
8. **Restarts** - Free kicks, goal kicks that create opportunities
9. **Turnovers** - Possession changes, interceptions, recoveries

ANALYSIS GUIDELINES:
- Look for referee decisions and stoppages
- Identify set-piece situations
- Note disciplinary actions
- Track game flow disruptions
- Include tactical changes (substitutions)
- Focus on events that affect match dynamics
- Detect possession changes (wins/loses possession, interceptions, recoveries)

OUTPUT FORMAT:
=== FOULS & FREE KICKS ===
Timestamp: XX:XX (XXXX seconds)
Type: [Foul/Free kick/Tackle]
Team: [Fouling team]
Description: [Context and location]
Significance: [Impact on match flow]

=== CARDS & DISCIPLINE ===
Timestamp: XX:XX (XXXX seconds)  
Type: [Yellow card/Red card/Warning]
Team: [Player's team]
Description: [Reason and context]
Impact: [Effect on team/match]

=== CORNERS & SET PIECES ===
Timestamp: XX:XX (XXXX seconds)
Type: [Corner kick/Free kick/Throw-in]
Team: [Taking team]
Description: [Situation and outcome]
Danger Level: [High/Medium/Low threat]

=== SUBSTITUTIONS ===
Timestamp: XX:XX (XXXX seconds)
Team: [Team making change]
Change: [Player out → Player in]
Tactical Reason: [Why substitution made]

=== TURNOVERS & POSSESSION CHANGES ===
Timestamp: XX:XX (XXXX seconds)
Type: [Turnover/Interception/Recovery]
Team: [Team that GAINS possession]
Description: [How possession was won - tackle, interception, loose ball, etc.]
Context: [Situation - throw-in, midfield, defensive third, counter-attack opportunity]
Impact: [Immediate result - counter-attack, build-up, defensive action]

=== OFFSIDE & DECISIONS ===
Timestamp: XX:XX (XXXX seconds)
Type: [Offside/VAR decision/Referee call]
Team: [Affected team]
Description: [Situation details]
Impact: [Match flow effect]

=== OTHER SIGNIFICANT EVENTS ===
[Any other notable match events that affect flow or tactics]

QUALITY CRITERIA:
- Only include events clearly described in timeline
- Provide context for why each event matters
- Estimate impact on match dynamics
- Use exact timestamps from timeline
- Be specific about teams and situations

Focus on events that coaches would want to review or that significantly affected the match flow."""

    def extract_other_events(self, match_id: str) -> bool:
        """Extract other events using Gemini analysis"""
        print(f"📋 Extracting other events for {match_id}")
        
        data_dir = Path("../data") / match_id
        timeline_path = data_dir / "5_complete_timeline.txt"
        output_path = data_dir / "8.5_other_events.txt"
        
        # Check input file exists
        if not timeline_path.exists():
            print(f"❌ Complete timeline file not found: {timeline_path}")
            return False
        
        # Read complete timeline
        print("📥 Reading complete match timeline...")
        with open(timeline_path, 'r') as f:
            complete_timeline = f.read()
        
        # Generate other events analysis
        print("🧠 Analyzing timeline for other significant events...")
        extraction_prompt = self.get_extraction_prompt(complete_timeline)
        
        try:
            response = self.model.generate_content(extraction_prompt)
            other_events_content = response.text
            
            # Save other events
            print(f"💾 Saving other events to: {output_path}")
            with open(output_path, 'w') as f:
                f.write(f"# Other Events - {match_id}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Method: Gemini intelligent event extraction\n")
                f.write(f"# Source: Complete timeline analysis\n")
                f.write(f"# Focus: Fouls, cards, corners, substitutions, turnovers, decisions\n\n")
                f.write(other_events_content)
            
            print("✅ Other events extracted successfully!")
            print(f"📊 Output: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during event extraction: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 8.5_other_events_extractor.py <match_id>")
        print("Example: python 8.5_other_events_extractor.py newmills-20250222")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    extractor = OtherEventsExtractor()
    success = extractor.extract_other_events(match_id)
    
    if success:
        print(f"\n📋 Other events extracted for {match_id}!")
        print("🎯 Contains fouls, cards, corners, substitutions, turnovers, and decisions")
        print("🔄 Next: Run 9_convert_to_web_format.py for final JSON conversion")
    else:
        print(f"\n❌ Failed to extract other events for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()