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
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def synthesize_highlights(self, all_descriptions: str, team_config: dict) -> dict:
        """Synthesize highlights from all clip descriptions"""
        
        prompt = f"""You are analyzing a 5-a-side football game between {team_config['team_a']['name']} and {team_config['team_b']['name']}.

Below are descriptions of every 15-second clip from the match. Your job is to identify the HIGHLIGHTS - the most important and exciting moments.

**FOCUS ON:**
🥅 **GOALS** - All goals scored (most important!)
⚡ **COOL MOMENTS** - Great skills, saves, near-misses, tackles
🎯 **KEY EVENTS** - Important plays that shaped the game

**IGNORE:**
- Routine passing
- Normal possession changes
- Boring moments

**FORMAT YOUR RESPONSE AS JSON:**
```json
{{
  "match_summary": "Brief 2-3 sentence summary of the game",
  "final_score": "Team A X - Y Team B (if determinable, otherwise 'Unknown')",
  "highlights": [
    {{
      "timestamp": "MM:SS",
      "type": "goal|skill|save|near_miss|key_moment",
      "team": "Team A|Team B",
      "description": "What happened",
      "excitement_level": 1-10
    }}
  ],
  "top_moments": [
    "The 3 most exciting moments as brief descriptions"
  ]
}}
```

**CLIP DESCRIPTIONS:**
{all_descriptions}

Analyze these descriptions and extract only the most exciting highlights. Be selective - quality over quantity!"""

        try:
            response = self.model.generate_content(prompt)
            
            # Try to parse as JSON
            response_text = response.text.strip()
            
            # Extract JSON from response (might have markdown formatting)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                # Fallback to text format if JSON parsing fails
                return {
                    "match_summary": "Analysis completed but JSON parsing failed",
                    "final_score": "Unknown",
                    "highlights": [],
                    "top_moments": [],
                    "raw_response": response_text
                }
                
        except Exception as e:
            return {
                "error": f"Failed to synthesize highlights: {str(e)}",
                "match_summary": "Analysis failed",
                "final_score": "Unknown",
                "highlights": [],
                "top_moments": []
            }

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
    highlights_data = synthesizer.synthesize_highlights(combined_descriptions, team_config)
    
    # Save results
    highlights_file = outputs_dir / 'highlights.json'
    with open(highlights_file, 'w') as f:
        json.dump(highlights_data, f, indent=2)
    
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
    if 'highlights' in highlights_data and highlights_data['highlights']:
        print(f"\n🎯 Found {len(highlights_data['highlights'])} highlights:")
        for highlight in highlights_data['highlights'][:5]:  # Show first 5
            print(f"   {highlight.get('timestamp', '??:??')} - {highlight.get('type', 'moment').upper()}: {highlight.get('description', 'No description')}")
        
        if len(highlights_data['highlights']) > 5:
            print(f"   ... and {len(highlights_data['highlights']) - 5} more")
    
    if 'match_summary' in highlights_data:
        print(f"\n📋 Match Summary:")
        print(f"   {highlights_data['match_summary']}")
    
    if 'final_score' in highlights_data and highlights_data['final_score'] != 'Unknown':
        print(f"⚽ Final Score: {highlights_data['final_score']}")
    
    print(f"\n🎯 Ready for step 5: python 5_format_webapp.py {match_id}")

if __name__ == "__main__":
    main()