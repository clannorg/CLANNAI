#!/usr/bin/env python3
"""
4. Synthesize Highlights
Use Gemini 2.5 Pro to identify the most important moments from all clip descriptions
"""

import sys
import os
import json
import time
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

def load_env_multisource() -> None:
    """Load environment variables from multiple likely locations"""
    load_dotenv()  # Keep shell environment
    
    candidates = [
        Path(__file__).resolve().parent.parent / '.env',   # ai/footy1/.env
        Path(__file__).resolve().parents[2] / '.env',      # ai/.env
        Path(__file__).resolve().parents[3] / '.env',      # repo root .env
    ]
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            pass

load_env_multisource()

class HighlightSynthesizer:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for synthesis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
    
    def synthesize_highlights(self, all_descriptions: str, team_config: dict) -> str:
        """Synthesize highlights from all clip descriptions as plain text"""
        
        prompt = f"""You are analyzing a 5-a-side football game between teams identified by their visual appearance:
- **{team_config['team_a']['colors']}** (Team A)
- **{team_config['team_b']['colors']}** (Team B)

Below are descriptions of every 15-second clip from the match. Each clip description starts with [MM:SS] showing the clip start time, then contains detailed timing like "At 3 seconds:", "At 8 seconds:" etc.

**YOUR JOB:** Calculate EXACT timestamps by adding clip start time + internal timing.

**TIMESTAMP CALCULATION:**
- Clip starts at [05:30] and event happens "At 8 seconds:" = 05:38 total
- Clip starts at [12:15] and event happens "At 3 seconds:" = 12:18 total
- Always calculate: Clip Start Time + Internal Event Time = Exact Timestamp

**STRICT CRITERIA:**
🥅 **ONLY THE MOST OBVIOUS GOALS** - Only the clearest, most definite goals
🚫 **BE SELECTIVE** - Quality over quantity

**IMPORTANT:** 
- Use EXACT visual identifiers from descriptions (e.g., "Orange bibs", "Non-bibs")
- Only count events that seem completely certain
- Be conservative - when in doubt, exclude it
- **CALCULATE EXACT TIMESTAMPS** - don't just use clip start times

**FORMAT YOUR RESPONSE AS PLAIN TEXT:**

MATCH SUMMARY:
[Brief 2-3 sentence summary using visual identifiers]

FINAL SCORE:
[Visual Team A] X - Y [Visual Team B]

HIGHLIGHTS:
MM:SS - GOAL - [Team]: [Description]
MM:SS - GOAL - [Team]: [Description]
[etc.]

**EXAMPLE:**
MATCH SUMMARY:
A high-scoring match where Non-bibs team dominated with clinical finishing. Orange bibs fought hard but couldn't match the attacking prowess of their opponents.

FINAL SCORE:
Non-bibs 12 - 8 Orange bibs

HIGHLIGHTS:
02:38 - GOAL - Non-bibs: Tall player shoots from close range, ball clearly in net
05:48 - GOAL - Orange bibs: Quick counter-attack finished by bearded player
08:15 - GOAL - Non-bibs: Goalkeeper beaten by low shot from edge of area

**CLIP DESCRIPTIONS:**
{all_descriptions}

Analyze these descriptions and create a plain text summary with EXACT calculated timestamps:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
                
        except Exception as e:
            return f"Error: Failed to synthesize highlights: {str(e)}"

def extract_timestamp_from_filename(filename: str) -> str:
    """Extract timestamp from filename like clip_05m30s.txt -> 05:30"""
    try:
        # Remove .txt and clip_ prefix
        time_part = filename.replace('.txt', '').replace('clip_', '')
        
        # Extract minutes and seconds (e.g., "05m30s" -> "05:30")
        import re
        match = re.match(r'(\d+)m(\d+)s', time_part)
        if match:
            minutes = match.group(1)
            seconds = match.group(2)
            return f"{minutes}:{seconds}"
        else:
            return "00:00"
    except:
        return "00:00"

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4_synthesize_highlights.py <match-id>")
        print("Example: python 4_synthesize_highlights.py sunday-league-game-1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    descriptions_dir = outputs_dir / 'clip_descriptions'
    
    if not descriptions_dir.exists():
        print(f"❌ Error: Descriptions directory not found: {descriptions_dir}")
        print("Run step 3 first: python 3_analyze_clips.py <match-id>")
        sys.exit(1)
    
    # Load team configuration
    team_config_file = outputs_dir / 'team_config.json'
    if not team_config_file.exists():
        print(f"❌ Error: Team configuration not found: {team_config_file}")
        sys.exit(1)
    
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    print(f"🧠 Synthesizing highlights for: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print("🎯 Focus: Goals and cool moments")
    print("=" * 50)
    
    # Collect all clip descriptions
    description_files = sorted(descriptions_dir.glob('*.txt'))
    
    if not description_files:
        print(f"❌ Error: No description files found in {descriptions_dir}")
        sys.exit(1)
    
    print(f"📊 Found {len(description_files)} clip descriptions")
    
    # Build combined timeline
    all_descriptions = []
    
    for desc_file in description_files:
        timestamp = extract_timestamp_from_filename(desc_file.name)
        
        try:
            with open(desc_file, 'r') as f:
                description = f.read().strip()
            
            all_descriptions.append(f"[{timestamp}] {description}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not read {desc_file.name}: {e}")
    
    if not all_descriptions:
        print("❌ Error: No valid descriptions found")
        sys.exit(1)
    
    # Combine all descriptions
    combined_descriptions = "\n\n".join(all_descriptions)
    
    print("🔍 Analyzing all descriptions for highlights...")
    
    # Initialize synthesizer and analyze
    synthesizer = HighlightSynthesizer()
    highlights_text = synthesizer.synthesize_highlights(combined_descriptions, team_config)
    
    # Save results as plain text
    highlights_file = outputs_dir / 'highlights.txt'
    with open(highlights_file, 'w') as f:
        f.write(highlights_text)
    
    # Also save the full timeline for reference
    timeline_file = outputs_dir / 'full_timeline.txt'
    with open(timeline_file, 'w') as f:
        f.write(f"Full Timeline - {team_config['team_a']['name']} vs {team_config['team_b']['name']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(combined_descriptions)
    
    print(f"\n✅ Highlight synthesis complete!")
    print(f"📄 Results saved to: {highlights_file}")
    print(f"📄 Full timeline saved to: {timeline_file}")
    
    # Show preview of results
    print(f"\n🎯 Highlights Summary:")
    print("=" * 50)
    # Show first few lines of the highlights
    lines = highlights_text.split('\n')
    for line in lines[:10]:  # Show first 10 lines
        if line.strip():
            print(f"   {line}")
    
    if len(lines) > 10:
        print(f"   ... and {len(lines) - 10} more lines")
    
    print(f"\n🎯 Ready for step 5: python 5_format_webapp.py {match_id}")

if __name__ == "__main__":
    main()