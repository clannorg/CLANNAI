#!/usr/bin/env python3
"""
FOCUSED EVENTS ANALYZER - v5 Pipeline
Same as 2.5 mega analyzer but focuses ONLY on 7 high-value event types

Inputs:
- 1.6_complete_timeline.txt (complete match timeline)
- 1_veo_ground_truth.json (VEO verified events)
- 1_team_config.json (team names and colors)

Outputs:
- 2.6_focused_events.txt (clean list of 7 event types only)
- 2.6_focused_summary.txt (match summary with focused events)
"""

import sys
import os
import json
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_paths = [
    Path('.env'),
    Path('../.env'), 
    Path('../../.env'),
    Path('/home/ubuntu/CLANNAI/.env'),
    Path('/home/ubuntu/CLANNAI/ai/.env')
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"🔑 Loaded environment from: {env_path}")
        break

class FocusedEventsAnalyzer:
    def __init__(self):
        """Initialize the focused analyzer with Gemini"""
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("🎯 Focused Events Analyzer initialized with Gemini 2.5 Flash")
        
        # Our 7 target event types
        self.TARGET_EVENTS = [
            'Goals', 'Shots', 'Fouls', 'Corners', 'Free kicks', 'Goal kicks', 'Turnovers'
        ]
        print(f"📋 Target events: {', '.join(self.TARGET_EVENTS)}")
    
    def load_team_config(self, match_id: str) -> dict:
        """Load team configuration for consistent naming"""
        config_path = Path(f"../outputs/{match_id}/1_team_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to generic names if config missing
            return {
                'team_a': {'name': 'Team A', 'jersey': 'first team colors'},
                'team_b': {'name': 'Team B', 'jersey': 'second team colors'}
            }

    def load_match_data(self, match_id: str):
        """Load all input data for analysis"""
        base_path = Path(f"../outputs/{match_id}")
        
        print(f"📖 Loading match data for: {match_id}")
        
        # Load timeline
        timeline_path = base_path / "1.6_complete_timeline.txt"
        if not timeline_path.exists():
            raise FileNotFoundError(f"Timeline not found: {timeline_path}")
        
        with open(timeline_path, 'r') as f:
            timeline = f.read()
        
        # Load VEO ground truth
        veo_path = base_path / "1_veo_ground_truth.json"
        if not veo_path.exists():
            raise FileNotFoundError(f"VEO ground truth not found: {veo_path}")
            
        with open(veo_path, 'r') as f:
            veo_data = json.load(f)
        
        print(f"✅ Loaded timeline: {len(timeline)} chars")
        print(f"✅ Loaded VEO data: {veo_data['total_events']} events") 
        
        return {
            'timeline': timeline,
            'veo_data': veo_data,
            'match_id': match_id
        }

    def create_focused_prompt(self, data):
        """Create the focused analysis prompt - ONLY 7 event types"""
        
        # Extract VEO goals and shots (same system as 2.5)
        veo_goals = []
        veo_shots = []
        
        for event in data['veo_data']['events']:
            event_info = {
                'time': event['timestamp'],
                'seconds': event['timestamp_seconds'],
                'type': event['event_type']
            }
            
            if event['event_type'] == 'Goal':
                veo_goals.append(event_info)
            elif event['event_type'] == 'Shot on goal':
                veo_shots.append(event_info)
        
        # Truncate timeline if too long (Gemini limits)
        timeline = data['timeline']
        if len(timeline) > 100000:
            timeline = timeline[:100000] + "\n... (timeline truncated for analysis)"
        
        # Load team config for actual names
        team_config = self.load_team_config(data['match_id'])
        team_a_name = team_config['team_a']['name']
        team_b_name = team_config['team_b']['name']
        
        prompt = f"""You are analyzing a 90-minute football match. Focus ONLY on 7 high-value event types.

INPUTS:
1. AI TIMELINE: Descriptions of 370+ clips covering the entire match
2. VEO GROUND TRUTH: {data['veo_data']['total_events']} verified events including {len(veo_goals)} goals and {len(veo_shots)} shots
3. TEAMS: {team_a_name} vs {team_b_name} (use actual team names consistently)

VEO VERIFIED GOALS ({len(veo_goals)} total):
{json.dumps(veo_goals, indent=2)}

VEO VERIFIED SHOTS ({len(veo_shots)} total):
{json.dumps(veo_shots, indent=2)}

AI TIMELINE:
{timeline}

OUTPUT 3 SECTIONS - FOCUS ONLY ON THESE 7 EVENT TYPES:
1. Goals (use VEO verification system)
2. Shots (including penalties, headers, volleys)
3. Fouls (including cards, bookings)
4. Corners (corner kicks)
5. Free kicks (direct and indirect)
6. Goal kicks
7. Turnovers (interceptions, tackles, possession changes)

=== FOCUSED_EVENTS.TXT ===
List ONLY the 7 event types above in chronological order, one per line:
Format: MM:SS - TYPE: Team - Description → OUTCOME: [what happened next]

CRITICAL RULES FOR VEO GOAL MATCHING:
- VEO goals are the ONLY goals that count - use exactly {len(veo_goals)} goals from VEO data
- VEO timestamps mark the START of attacking plays that led to goals
- For each VEO goal timestamp, look 15-30 seconds AFTER in the AI timeline to find the actual goal moment
- Use the AI's precise timestamp when the ball actually went in, not VEO's start-of-attack time
- Extract which team scored from the AI description (look for jersey colors/team names)
- NEVER output "Unidentified Team" - always find the team from AI timeline
- Use "{team_a_name}" and "{team_b_name}" consistently
- IGNORE ALL OTHER "goal" mentions in AI timeline - only VEO goals count

OUTCOME TRACKING:
- SHOT → "Goal scored" / "Saved by goalkeeper" / "Shot missed" / "Shot blocked"
- FOUL → "Free kick awarded" / "Penalty awarded" / "Card shown" / "Play stopped"
- CORNER → "Goal from corner" / "Corner cleared" / "Shot from corner"
- FREE KICK → "Direct goal" / "Shot blocked" / "Cross delivered"
- TURNOVER → "Counter-attack started" / "Possession regained"

**VEO GOAL MATCHING EXAMPLE:**
- VEO says: Goal at 36:29 (start of attack)
- AI timeline at 36:45: "red and black jerseys player scores into top corner"
- Output: "36:45 - GOAL: {team_b_name} - Ball travels into top right corner of net → OUTCOME: Goal scored"

**MANDATORY GOAL VERIFICATION:**
- You MUST output exactly {len(veo_goals)} goals and NO MORE
- Each goal MUST correspond to a VEO timestamp: {[g['time'] for g in veo_goals]}
- If AI timeline mentions other "goals", they are NOT real goals - ignore them completely
- Only goals that match VEO verification timestamps are valid

Example output:
30:50 - GOAL: {team_a_name} - Header from corner kick, player #10 scores → OUTCOME: Goal scored
31:31 - SHOT: {team_b_name} - Long range effort from 25 yards → OUTCOME: Saved by goalkeeper
32:15 - FOUL: {team_a_name} - Defender tackles striker in penalty area → OUTCOME: Penalty awarded
70:15 - CORNER: {team_a_name} - Corner kick from right side → OUTCOME: Corner cleared by defense
75:22 - TURNOVER: {team_b_name} - Midfielder intercepts pass in center circle → OUTCOME: Counter-attack started

IGNORE ALL OTHER EVENTS: No throw-ins, substitutions, warm-ups, pre-match activities, general possession play, etc.

**CRITICAL WARNING ABOUT FAKE GOALS:**
- AI timeline may mention many "goals" that are NOT real goals
- These could be: warm-up shots, practice goals, celebration descriptions, or AI mistakes
- ONLY the {len(veo_goals)} VEO-verified goals at timestamps {[g['time'] for g in veo_goals]} are real
- All other "goal" mentions in AI timeline must be classified as SHOTS instead

=== FOCUSED_SUMMARY.TXT ===
Match summary focusing on the 7 event types:

Match: {team_a_name} vs {team_b_name}
Final Score: [X-Y based on VEO goals ONLY]

=== {team_a_name.upper()} STATISTICS ===
- Goals: [count for {team_a_name}]
- Shots: [count for {team_a_name}]
- Fouls: [count for {team_a_name}]
- Corners: [count for {team_a_name}]
- Free kicks: [count for {team_a_name}]
- Goal kicks: [count for {team_a_name}]
- Turnovers: [count for {team_a_name}]

=== {team_b_name.upper()} STATISTICS ===
- Goals: [count for {team_b_name}]
- Shots: [count for {team_b_name}]
- Fouls: [count for {team_b_name}]
- Corners: [count for {team_b_name}]
- Free kicks: [count for {team_b_name}]
- Goal kicks: [count for {team_b_name}]
- Turnovers: [count for {team_b_name}]

Match Flow (Key Moments Only):
[2-3 paragraphs focusing ONLY on goals, major shots, key fouls/cards, and game-changing turnovers]

=== FOCUSED_TACTICAL.TXT ===
Tactical analysis focusing on the 7 event types:

=== {team_a_name.upper()} ===
Strengths:
- [List 3-4 strengths based on focused events evidence]

Weaknesses:
- [List 2-3 weaknesses based on focused events evidence]

Key Moments:
- [Key plays involving {team_a_name} from the 7 event types]

=== {team_b_name.upper()} ===
Strengths:
- [List 3-4 strengths based on focused events evidence]

Weaknesses:
- [List 2-3 weaknesses based on focused events evidence]

Key Moments:
- [Key plays involving {team_b_name} from the 7 event types]

Generate these 3 sections now - IGNORE everything except the 7 event types:"""

        return prompt

    def analyze_match(self, match_id: str):
        """Run focused match analysis"""
        print(f"🎯 Starting focused analysis for: {match_id}")
        
        # Load all data
        data = self.load_match_data(match_id)
        
        # Create focused prompt  
        prompt = self.create_focused_prompt(data)
        
        print(f"🧠 Calling Gemini with {len(prompt)} char prompt...")
        print("🎯 Focusing on 7 event types only...")
        
        # Get analysis from Gemini and save as text files
        try:
            print("🧠 Generating focused analysis...")
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            print("✅ Analysis generated")
            print(f"📊 Generated {len(analysis_text)} characters")
            
            # Parse the 2 sections and save as separate files
            self.save_focused_outputs(analysis_text, match_id)
            
            print("✅ Focused analysis complete")
            return True
            
        except Exception as e:
            print(f"❌ Analysis generation failed: {e}")
            raise

    def save_focused_outputs(self, analysis_text: str, match_id: str):
        """Parse analysis text and save as 3 focused text files"""
        base_path = Path(f"../outputs/{match_id}")
        
        try:
            # Find all section markers
            events_start = analysis_text.find("=== FOCUSED_EVENTS.TXT ===")
            summary_start = analysis_text.find("=== FOCUSED_SUMMARY.TXT ===")
            tactical_start = analysis_text.find("=== FOCUSED_TACTICAL.TXT ===")
            
            if events_start == -1 or summary_start == -1 or tactical_start == -1:
                raise Exception("Could not find all required sections in Gemini response")
            
            # Extract events text (between FOCUSED_EVENTS and FOCUSED_SUMMARY)
            events_text = analysis_text[events_start + len("=== FOCUSED_EVENTS.TXT ==="):summary_start].strip()
            
            # Extract summary text (between FOCUSED_SUMMARY and FOCUSED_TACTICAL)
            summary_text = analysis_text[summary_start + len("=== FOCUSED_SUMMARY.TXT ==="):tactical_start].strip()
            
            # Extract tactical text (everything after FOCUSED_TACTICAL)
            tactical_text = analysis_text[tactical_start + len("=== FOCUSED_TACTICAL.TXT ==="):].strip()
            
            # Save focused_events.txt
            events_path = base_path / "2.6_focused_events.txt"
            with open(events_path, 'w') as f:
                f.write(events_text)
            print(f"✅ Saved events: {events_path}")
            
            # Save focused_summary.txt
            summary_path = base_path / "2.6_focused_summary.txt"
            with open(summary_path, 'w') as f:
                f.write(summary_text)
            print(f"✅ Saved summary: {summary_path}")
            
            # Save focused_tactical.txt
            tactical_path = base_path / "2.6_focused_tactical.txt"
            with open(tactical_path, 'w') as f:
                f.write(tactical_text)
            print(f"✅ Saved tactical: {tactical_path}")
            
        except Exception as e:
            print(f"❌ Failed to parse sections: {e}")
            # Save raw text for debugging
            raw_path = base_path / "2.6_focused_analysis_raw.txt" 
            with open(raw_path, 'w') as f:
                f.write(analysis_text)
            print(f"💾 Raw analysis saved for debugging: {raw_path}")
            raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python 2.6_focused_events.py <match-id>")
        print("Example: python 2.6_focused_events.py 20250427-match-apr-27-2025-9bd1cf29")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        analyzer = FocusedEventsAnalyzer()
        # Run focused analysis (saves text files directly)
        analyzer.analyze_match(match_id)
        
        print(f"\n🎉 FOCUSED ANALYSIS COMPLETE!")
        print(f"📁 3 files created:")
        print(f"   📄 2.6_focused_events.txt - All events chronologically")  
        print(f"   📊 2.6_focused_summary.txt - Team stats & match summary")
        print(f"   🎯 2.6_focused_tactical.txt - Team tactical analysis")
        print(f"🎯 Only 7 event types included")
        print(f"✅ VEO goal correction system applied")
        print(f"🔄 Complete replacement for 2.5 mega analyzer")
        
    except Exception as e:
        print(f"❌ Focused analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()