#!/usr/bin/env python3
"""
MEGA GEMINI ANALYZER - v2 Pipeline
Replaces steps 4-11 with single context-aware Gemini call

Inputs:
- 5_complete_timeline.txt (AI timeline from 600 clips)
- 1_veo_ground_truth.json (VEO verified events)
- meta/match_meta.json (match metadata)

Outputs:
- mega_analysis.json (complete analysis)
- web_events_array.json (webapp format)
- 11_tactical_analysis.json (tactical insights)
- accuracy_report.json (precision/recall metrics)
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

class MegaAnalyzer:
    def __init__(self):
        """Initialize the mega analyzer with Gemini"""
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("🧠 Mega Analyzer initialized with Gemini 2.5 Flash")
    
    def load_team_config(self, match_id: str) -> dict:
        """Load team configuration for consistent naming"""
        config_path = Path(f"../outputs/{match_id}/match_config.json")
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
        timeline_path = base_path / "5_complete_timeline.txt"
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
        
        # Load match metadata (optional)
        meta_path = base_path / "meta" / "match_meta.json"
        meta_data = {}
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                meta_data = json.load(f)
        
        print(f"✅ Loaded timeline: {len(timeline)} chars")
        print(f"✅ Loaded VEO data: {veo_data['total_events']} events") 
        print(f"✅ Loaded metadata: {len(meta_data)} fields")
        
        return {
            'timeline': timeline,
            'veo_data': veo_data,
            'metadata': meta_data,
            'match_id': match_id
        }

    def create_mega_prompt(self, data):
        """Create the comprehensive analysis prompt for plain text output"""
        
        # Extract VEO goals and shots
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
        
        prompt = f"""You are analyzing a 90-minute football match. You will create 3 separate plain text files:

INPUTS:
1. AI TIMELINE: Descriptions of 416x15-second clips covering the entire match
2. VEO GROUND TRUTH: {data['veo_data']['total_events']} verified events including {len(veo_goals)} goals and {len(veo_shots)} shots
3. TEAMS: {team_a_name} vs {team_b_name} (use actual team names consistently)

VEO VERIFIED GOALS ({len(veo_goals)} total):
{json.dumps(veo_goals, indent=2)}

VEO VERIFIED SHOTS ({len(veo_shots)} total):
{json.dumps(veo_shots, indent=2)}

AI TIMELINE:
{timeline}

OUTPUT 3 SEPARATE SECTIONS:

=== MEGA_EVENTS.TXT ===
List all significant events in chronological order, one per line:
Format: MM:SS - TYPE: Team - Description

CRITICAL RULES:
- VEO goals are the ONLY goals that count - use exactly {len(veo_goals)} goals from VEO data
- Use AI timeline to add DETAILS to VEO goals (who scored, how, from where, etc.)
- Add other events from AI timeline: fouls, corners, cards, substitutions, throw-ins, free kicks
- NEVER add AI-detected goals that aren't in VEO data
- Use "{team_a_name}" and "{team_b_name}" consistently

Example:
30:50 - GOAL: {team_a_name} - Header from corner kick, player #10 scores with powerful header
31:31 - SHOT: {team_b_name} - Long range effort from 25 yards, saved by goalkeeper
70:15 - PENALTY: {team_a_name} - Penalty awarded after defender handball in box

=== MEGA_TACTICAL.TXT ===
Team analysis in plain text sections:

=== {team_a_name.upper()} ===
Strengths:
- [List 3-4 strengths based on timeline evidence]

Weaknesses:
- [List 2-3 weaknesses]

Key Moments:
- [Key plays involving {team_a_name}]

=== {team_b_name.upper()} ===
Strengths:
- [List 3-4 strengths]

Weaknesses:
- [List 2-3 weaknesses]

Key Moments:
- [Key plays involving {team_b_name}]

=== MEGA_SUMMARY.TXT ===
Match overview:

Match: {team_a_name} vs {team_b_name}
Final Score: [X-Y based on VEO goals ONLY]
Duration: 104 minutes (including stoppage)

Key Statistics:
- Goals: {len(veo_goals)} (VEO Verified - 100% accurate)
- Shots: {len(veo_shots)} (VEO Verified - 100% accurate)
- [Other stats from AI timeline: fouls, corners, cards, throw-ins, free kicks]

Match Narrative:
[2-3 paragraph summary of match flow, using VEO goals as the definitive scoring record]

Generate these 3 sections now:"""

        return prompt

    def analyze_match(self, match_id: str):
        """Run complete match analysis"""
        print(f"🎯 Starting mega-analysis for: {match_id}")
        self.current_match_id = match_id  # Store for debug purposes
        
        # Load all data
        data = self.load_match_data(match_id)
        
        # Create mega prompt  
        prompt = self.create_mega_prompt(data)
        
        print(f"🧠 Calling Gemini with {len(prompt)} char prompt...")
        
        # Get analysis from Gemini and save as text files
        try:
            print("🧠 Generating comprehensive analysis...")
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            print("✅ Analysis generated")
            print(f"📊 Generated {len(analysis_text)} characters")
            
            # Parse the 3 sections and save as separate files
            self.save_text_outputs(analysis_text, match_id)
            
            print("✅ Mega-analysis complete")
            return True
            
        except Exception as e:
            print(f"❌ Analysis generation failed: {e}")
            raise
    def save_text_outputs(self, analysis_text: str, match_id: str):
        """Parse analysis text and save as 3 separate text files"""
        base_path = Path(f"../outputs/{match_id}")
        
        try:
            # Split the analysis into sections
            sections = analysis_text.split("=== ")
            
            events_text = ""
            tactical_text = ""
            summary_text = ""
            
            for section in sections:
                if section.startswith("MEGA_EVENTS.TXT"):
                    events_text = section.replace("MEGA_EVENTS.TXT ===", "").strip()
                elif section.startswith("MEGA_TACTICAL.TXT"):
                    tactical_text = "=== " + section.strip()
                elif section.startswith("MEGA_SUMMARY.TXT"):
                    summary_text = section.replace("MEGA_SUMMARY.TXT ===", "").strip()
            
            # Save mega_events.txt
            events_path = base_path / "mega_events.txt"
            with open(events_path, 'w') as f:
                f.write(events_text)
            print(f"✅ Saved: {events_path}")
            
            # Save mega_tactical.txt  
            tactical_path = base_path / "mega_tactical.txt"
            with open(tactical_path, 'w') as f:
                f.write(tactical_text)
            print(f"✅ Saved: {tactical_path}")
            
            # Save mega_summary.txt
            summary_path = base_path / "mega_summary.txt"
            with open(summary_path, 'w') as f:
                f.write(summary_text)
            print(f"✅ Saved: {summary_path}")
            
            # Also save the full analysis for debugging
            full_path = base_path / "mega_analysis_full.txt"
            with open(full_path, 'w') as f:
                f.write(analysis_text)
            print(f"📄 Full analysis saved: {full_path}")
            
        except Exception as e:
            print(f"❌ Failed to parse text sections: {e}")
            # Save raw text for debugging
            raw_path = base_path / "mega_analysis_raw.txt" 
            with open(raw_path, 'w') as f:
                f.write(analysis_text)
            print(f"💾 Raw analysis saved: {raw_path}")
            raise

    def save_outputs(self, analysis, match_id: str):
        """Save all output files"""
        base_path = Path(f"../outputs/{match_id}")
        
        print("💾 Saving analysis outputs...")
        
        # Save complete analysis
        mega_path = base_path / "mega_analysis.json" 
        with open(mega_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✅ Saved: {mega_path}")
        
        # Extract nested match analysis
        match_analysis = analysis.get('match_analysis', {})
        
        # Save web events array
        web_events = match_analysis.get('web_events_array', [])
        web_path = base_path / "web_events_array.json"
        with open(web_path, 'w') as f:
            json.dump(web_events, f, indent=2)
        print(f"✅ Saved: {web_path}")
        
        # Save tactical analysis
        tactical = match_analysis.get('tactical_analysis', {})
        tactical_path = base_path / "11_tactical_analysis.json"
        with open(tactical_path, 'w') as f:
            json.dump(tactical, f, indent=2)
        print(f"✅ Saved: {tactical_path}")
        
        # Save accuracy report
        accuracy = match_analysis.get('accuracy_metrics', {})
        accuracy_path = base_path / "accuracy_report.json"
        with open(accuracy_path, 'w') as f:
            json.dump(accuracy, f, indent=2)
        print(f"✅ Saved: {accuracy_path}")
        
        # Also save legacy web events format 
        web_events_legacy = {"events": web_events}
        legacy_path = base_path / "web_events.json"
        with open(legacy_path, 'w') as f:
            json.dump(web_events_legacy, f, indent=2)
        print(f"✅ Saved: {legacy_path}")
        
        # Save match metadata
        metadata = match_analysis.get('match_metadata', {})
        metadata_path = base_path / "match_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved: {metadata_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python mega_analyzer.py <match-id>")
        print("Example: python mega_analyzer.py 20250523-match-23-may-2025-3fc1de88")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        analyzer = MegaAnalyzer()
        # Run analysis (saves text files directly)
        analyzer.analyze_match(match_id)
        
        print(f"\n🎉 MEGA ANALYSIS COMPLETE!")
        print(f"📁 Text files saved to: ../outputs/{match_id}/")
        print(f"🎯 Ready for webapp formatting")
        
    except Exception as e:
        print(f"❌ Mega-analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()