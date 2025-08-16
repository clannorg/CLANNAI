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
        """Create the comprehensive analysis prompt"""
        
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
        
        prompt = f"""You are analyzing a 90-minute football match with complete context. You have:

1. COMPLETE AI TIMELINE: Descriptions of 600x15-second clips covering the entire match
2. VEO GROUND TRUTH: {data['veo_data']['total_events']} verified events including {len(veo_goals)} goals and {len(veo_shots)} shots
3. TEAMS: Blue team (blue jerseys) vs Black/White team (black and white striped jerseys)

⚫⚪ PRIMARY FOCUS: BLACK/WHITE TEAM ANALYSIS ⚪⚫
Pay special attention to the Black/White team's performance, tactics, and key moments throughout the match.

VEO VERIFIED GOALS ({len(veo_goals)} total):
{json.dumps(veo_goals, indent=2)}

VEO VERIFIED SHOTS ({len(veo_shots)} total):
{json.dumps(veo_shots, indent=2)}

AI TIMELINE:
{timeline}

YOUR TASK: Produce comprehensive match analysis by cross-referencing AI timeline against VEO ground truth.

CRITICAL INSTRUCTIONS:
1. Every VEO goal/shot MUST appear in your analysis (they are 100% verified)
2. For each VEO event, find supporting evidence in the AI timeline around that timestamp
3. Add other significant events from timeline (fouls, cards, corners, substitutions, turnovers)
4. Generate tactical insights based on validated events only
5. Calculate accuracy metrics comparing AI detection vs VEO truth
6. ⚫⚪ PRIORITIZE BLACK/WHITE TEAM: Focus extra attention on their attacking patterns, defensive actions, set pieces, and overall team dynamics

Write a comprehensive analysis in natural text covering:
- All validated goals and shots with timeline evidence
- Other significant events (fouls, cards, corners, etc.)
- Detailed tactical analysis for both teams (especially Black/White team)
- Match statistics and accuracy metrics
- Team metadata and match info

Be thorough and detailed. Don't worry about JSON formatting - just write a complete analysis:

EXAMPLE STRUCTURE (but write naturally):
Goals Analysis: [List each VEO goal with timeline evidence]
Shots Analysis: [List validated shots]
Other Events: [Fouls, cards, corners, turnovers, etc.]
Black/White Team Tactical Analysis: [Detailed analysis - strengths, weaknesses, key moments]
Blue Team Analysis: [Basic analysis]
Match Statistics: [Goals, shots, score, etc.]
Accuracy Metrics: [AI vs VEO comparison]
Match Metadata: [Teams, colors, date, etc.]

Generate this analysis now:"""

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
        
        # STEP 1: Get natural text analysis from Gemini
        try:
            print("🧠 Step 1: Getting text analysis from Gemini...")
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            print("✅ Step 1 complete: Got text analysis")
            print(f"📝 Analysis length: {len(analysis_text)} characters")
            
            # Save raw text analysis for debugging
            debug_path = f"../outputs/{self.current_match_id}/raw_analysis.txt"
            with open(debug_path, 'w') as f:
                f.write(analysis_text)
            print(f"💾 Raw analysis saved to: {debug_path}")
            
        except Exception as e:
            print(f"❌ Step 1 failed - Gemini text analysis: {e}")
            raise
        
        # STEP 2: Convert text to JSON format
        try:
            print("🧠 Step 2: Converting text to structured JSON...")
            json_prompt = f"""Convert this football match analysis into the exact JSON structure requested.

ORIGINAL ANALYSIS:
{analysis_text}

Convert this into the exact JSON format that was requested in the original prompt. Extract all events, stats, tactical analysis, and metadata. Ensure valid JSON syntax with proper commas and brackets.

Output ONLY the JSON, no other text:"""

            json_response = self.model.generate_content(json_prompt)
            json_text = json_response.text
            
            # Clean up JSON formatting
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]
            
            json_text = json_text.strip()
            
            # Try to parse
            analysis = json.loads(json_text)
            
            print("✅ Step 2 complete: Converted to JSON")
            print("✅ Mega-analysis complete")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ Step 2 failed - JSON conversion: {e}")
            # Save failed JSON for debugging
            debug_json_path = f"../outputs/{self.current_match_id}/failed_json.txt"
            with open(debug_json_path, 'w') as f:
                f.write(json_text)
            print(f"💾 Failed JSON saved to: {debug_json_path}")
            raise
        except Exception as e:
            print(f"❌ Step 2 failed: {e}")
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
        analysis = analyzer.analyze_match(match_id)
        analyzer.save_outputs(analysis, match_id)
        
        # Print summary
        match_analysis = analysis.get('match_analysis', {})
        goals = match_analysis.get('goals_analysis', {}).get('total_veo_verified_goals', 0)
        shots = match_analysis.get('shots_analysis', {}).get('total_veo_verified_shots', 0)
        events = len(match_analysis.get('web_events_array', []))
        
        print(f"\n🎉 MEGA-ANALYSIS COMPLETE!")
        print(f"📊 Goals detected: {goals}")
        print(f"🎯 Shots detected: {shots}")
        print(f"📋 Total events: {events}")
        print(f"💾 Outputs saved to: ../outputs/{match_id}/")
        
    except Exception as e:
        print(f"❌ Mega-analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()