#!/usr/bin/env python3
"""
4.8. Convert Sick Analysis to Interactive JSON
Convert our absolutely mental tactical analysis to webapp-compatible JSON 
with interactive elements, player cards, clickable moments, and rich data
"""

import sys
import os
import json
import time
import re
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

def load_env_multisource() -> None:
    """Load environment variables from multiple likely locations"""
    load_dotenv()  # Keep shell environment
    
    candidates = [
        Path(__file__).resolve().parent.parent / '.env',  # ai/footy2/.env
        Path(__file__).resolve().parents[2] / '.env',     # ai/.env
        Path(__file__).resolve().parents[3] / '.env',     # repo root .env
    ]
    
    for env_path in candidates:
        try:
            if env_path.exists():
                load_dotenv(env_path, override=False)
        except Exception:
            pass

load_env_multisource()

class SickJSONConverter:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for sick JSON conversion"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def get_sick_conversion_prompt(self, team_config: dict) -> str:
        """Generate prompt to convert sick analysis to interactive JSON"""
        team_a_name = team_config['team_a']['name']
        team_b_name = team_config['team_b']['name']
        
        return f"""Convert this absolutely MENTAL tactical analysis into the most interactive JSON format possible for the ClannAI webapp.

**TEAM MAPPING:**
- Team A: {team_a_name} → "red_team" in JSON
- Team B: {team_b_name} → "blue_team" in JSON

**REQUIRED SICK JSON STRUCTURE:**
```json
{{
  "tactical_analysis": {{
    "red_team": {{
      "team_name": "{team_a_name}",
      "strengths": [
        "🔥 STRENGTH TITLE (9/10): Detailed explanation with evidence from 05:30, 12:15 - This tactical approach dominated the game",
        "⚡ ANOTHER STRENGTH (8/10): More detailed analysis with specific examples and impact"
      ],
      "weaknesses": [
        "⚠️ WEAKNESS TITLE (7/10 severity): Detailed explanation with evidence from 08:45 - Cost them 2 goals",
        "🚨 CRITICAL WEAKNESS (9/10): Another weakness with specific impact and timestamps"
      ],
      "key_players": [
        "👑 THE [NICKNAME] (9.2/10): Physical description - Tactical position. Stats: 4 goals, 12 shots (75% accuracy). Key moments: 05:30 (scored brilliant goal), 12:15 (game-changing assist). Signature: What they do best. Weakness: What they struggle with. Coach notes: Development advice",
        "⚡ ANOTHER PLAYER (8.5/10): Player description with stats, key moments, and coaching insights all in one detailed string"
      ],
      "tactical_setup": "Formation and approach",
      "performance_summary": "Overall performance",
      "performance_metrics": {{
        "shot_accuracy": "75%",
        "possession_quality": "High",
        "pressing_success": "12 turnovers",
        "transition_speed": "3.2 seconds avg"
      }}
    }},
    "blue_team": {{
      "team_name": "{team_b_name}",
      "strengths": [...],
      "weaknesses": [...],
      "key_players": [...],
      "tactical_setup": "...",
      "performance_summary": "...",
      "performance_metrics": {{...}}
    }}
  }},
  "match_overview": {{
    "final_score": "Team A X - Y Team B",
    "key_tactical_story": "Epic narrative",
    "game_phases": [
      {{
        "phase": "Early Game (0-15 mins)",
        "title": "Phase Title",
        "description": "What happened",
        "key_battles": ["Player A vs Player B"],
        "momentum": "Who controlled",
        "turning_points": ["MM:SS: Event description"]
      }}
    ]
  }},
  "analysis": {{
    "key_moments": [
      {{
        "timestamp": 330,
        "description": "🔥 FOUR-GOAL BARRAGE BEGINS: Tactical turning point where Player A's shot changed everything",
        "tactical_significance": "Before: Game was competitive. After: Complete domination. Coaching point: When momentum shifts, capitalize immediately"
      }},
      {{
        "timestamp": 735,
        "description": "⚡ THE SPIRIT BREAKER: Crossbar hit that demoralized opposition",
        "tactical_significance": "Psychological warfare at its finest - the sound of the crossbar broke their spirit"
      }},
      {{
        "timestamp": 1125,
        "description": "🎯 TACTICAL MASTERCLASS: Perfect example of pressing trigger execution",
        "tactical_significance": "This moment showed how to turn defense into attack in seconds"
      }}
    ]
  }},
  "micro_battles": [
    {{
      "title": "Player A vs Player B",
      "duel_type": "Attacking vs Defending",
      "winner": "Player A",
      "key_moments": ["05:30", "12:15"],
      "impact": "How this affected the game",
      "stats": {{
        "duels_won": "7/10",
        "success_rate": "70%"
      }}
    }}
  ],
  "performance_evolution": {{
    "fatigue_analysis": [
      {{
        "period": "Early Game (0-20 mins)",
        "intensity": "High",
        "key_actions": "Specific examples",
        "performance_level": 9
      }},
      {{
        "period": "Mid Game (20-40 mins)", 
        "intensity": "Medium",
        "tactical_adjustments": "Changes made",
        "performance_level": 7
      }},
      {{
        "period": "Late Game (40+ mins)",
        "intensity": "Low",
        "fatigue_impact": "How tiredness affected play",
        "performance_level": 5
      }}
    ]
  }},
  "coaching_goldmine": {{
    "training_drills": [
      {{
        "team": "red_team",
        "drill_name": "Specific Exercise Name",
        "purpose": "What it improves",
        "description": "How to do it",
        "frequency": "How often to practice"
      }}
    ],
    "tactical_adjustments": [
      {{
        "team": "red_team",
        "adjustment": "Formation change",
        "reason": "Why needed",
        "implementation": "How to do it"
      }}
    ]
  }},
  "wild_insights": [
    {{
      "title": "Insight Title",
      "description": "Something only visible with full timeline",
      "evidence": "Specific examples",
      "significance": "Why this matters",
      "rarity": "How unique this insight is"
    }}
  ],
  "manager_recommendations": {{
    "red_team": [
      "🎯 HIGH PRIORITY: Recommendation title - Detailed advice with specific implementation steps and expected impact",
      "⚡ MEDIUM PRIORITY: Another recommendation with tactical reasoning and training drill suggestions",
      "💡 LOW PRIORITY: Third recommendation focusing on long-term development and skill building"
    ],
    "blue_team": [
      "🚨 CRITICAL: Most important recommendation with immediate action required",
      "🔧 TACTICAL FIX: Formation adjustment needed with specific positioning changes",
      "📈 DEVELOPMENT: Player improvement focus with targeted training approach"
    ]
  }}
}}
```

**CONVERSION RULES:**
1. **Detailed String Format**: Convert all insights to rich, detailed strings with emojis and ratings
2. **Include Evidence**: Add timestamps and specific examples in string descriptions
3. **Priority/Impact Ratings**: Include numerical ratings (X/10) in string format
4. **Key Moments**: Create detailed timeline strings with tactical significance
5. **Player Analysis**: Combine stats, moments, and insights into comprehensive player strings
6. **Manager Recommendations**: Use priority emojis (🎯🚨⚡💡) with detailed advice
7. **Strengths/Weaknesses**: Include impact ratings and evidence timestamps in strings
8. **Performance Metrics**: Keep as simple key-value pairs for webapp display
9. **Wild Insights**: Convert to engaging strings that highlight uniqueness

**IMPORTANT:**
- Make timestamps clickable by converting MM:SS to seconds
- Add impact ratings (1-10) for players and tactical elements
- Include evidence timestamps for all claims
- Create rich objects instead of simple strings
- Extract specific stats and metrics from the analysis

Convert the following sick tactical analysis to interactive JSON:"""

    def convert_to_sick_json(self, sick_analysis: str, team_config: dict) -> dict:
        """Convert sick analysis to interactive JSON"""
        try:
            prompt = self.get_sick_conversion_prompt(team_config)
            
            conversion_input = f"""
{prompt}

**SICK TACTICAL ANALYSIS TO CONVERT:**
{sick_analysis}

Convert this to the interactive JSON format specified above:"""
            
            print("🔄 Converting sick analysis to interactive JSON...")
            print("⚡ Creating player cards, clickable moments, and rich data...")
            
            response = self.model.generate_content(conversion_input)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Find JSON in the response (sometimes wrapped in markdown)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            
            # Parse and validate JSON
            sick_json = json.loads(json_text)
            
            return sick_json
            
        except Exception as e:
            return {"error": f"Failed to convert sick analysis: {str(e)}"}

    def enhance_json_with_timestamps(self, sick_json: dict) -> dict:
        """Enhance JSON by converting timestamps to seconds for video seeking"""
        def convert_timestamp(timestamp_str):
            """Convert MM:SS to seconds"""
            if isinstance(timestamp_str, str) and ':' in timestamp_str:
                try:
                    parts = timestamp_str.split(':')
                    if len(parts) == 2:
                        minutes = int(parts[0])
                        seconds = int(parts[1])
                        return minutes * 60 + seconds
                except:
                    pass
            return None
        
        def process_timestamps(obj):
            """Recursively process timestamps in the JSON"""
            if isinstance(obj, dict):
                # Add video_seek field for timestamps
                if 'timestamp' in obj and isinstance(obj['timestamp'], str):
                    seek_seconds = convert_timestamp(obj['timestamp'])
                    if seek_seconds is not None:
                        obj['video_seek'] = seek_seconds
                        obj['clickable'] = True
                
                # Process all values recursively
                for key, value in obj.items():
                    obj[key] = process_timestamps(value)
                    
            elif isinstance(obj, list):
                return [process_timestamps(item) for item in obj]
                
            return obj
        
        return process_timestamps(sick_json)

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4.8_convert_sick_to_json.py <match-id>")
        print("Example: python 4.8_convert_sick_to_json.py leo1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    # Check required files exist
    sick_analysis_file = outputs_dir / 'sick_tactical_analysis.txt'
    team_config_file = outputs_dir / 'team_config.json'
    
    if not sick_analysis_file.exists():
        print(f"❌ Error: Sick analysis file not found: {sick_analysis_file}")
        print("Run step 4.7 first: python 4.7_generate_sick_analysis.py <match-id>")
        sys.exit(1)
    
    if not team_config_file.exists():
        print(f"❌ Error: Team config not found: {team_config_file}")
        sys.exit(1)
    
    # Load data
    print(f"🔄 Converting sick analysis to interactive JSON for: {match_id}")
    print("=" * 60)
    
    with open(sick_analysis_file, 'r') as f:
        sick_analysis = f.read()
    
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    print(f"📊 Input analysis: {len(sick_analysis):,} characters")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    
    # Initialize converter
    converter = SickJSONConverter()
    
    # Convert to JSON
    print("\n🔄 Converting to interactive JSON...")
    print("⏳ This may take 60-90 seconds for complex analysis...")
    
    sick_json = converter.convert_to_sick_json(sick_analysis, team_config)
    
    if "error" in sick_json:
        print(f"❌ Conversion failed: {sick_json['error']}")
        sys.exit(1)
    
    # Enhance with clickable timestamps
    print("⚡ Adding interactive elements and clickable timestamps...")
    sick_json = converter.enhance_json_with_timestamps(sick_json)
    
    # Save JSON
    json_file = outputs_dir / 'sick_tactical_analysis.json'
    with open(json_file, 'w') as f:
        json.dump(sick_json, f, indent=2)
    
    print(f"\n🔥 SICK JSON conversion complete!")
    print(f"📁 JSON saved to: {json_file}")
    print(f"📊 JSON structure: {list(sick_json.keys())}")
    
    # Show stats
    stats = []
    if 'tactical_analysis' in sick_json:
        if 'red_team' in sick_json['tactical_analysis']:
            red_team = sick_json['tactical_analysis']['red_team']
            stats.append(f"🔴 Red team players: {len(red_team.get('key_players', []))}")
            stats.append(f"🔴 Red team strengths: {len(red_team.get('strengths', []))}")
        
        if 'blue_team' in sick_json['tactical_analysis']:
            blue_team = sick_json['tactical_analysis']['blue_team']
            stats.append(f"🔵 Blue team players: {len(blue_team.get('key_players', []))}")
    
    if 'interactive_moments' in sick_json:
        stats.append(f"⚡ Interactive moments: {len(sick_json['interactive_moments'])}")
    
    if 'micro_battles' in sick_json:
        stats.append(f"⚔️ Micro battles: {len(sick_json['micro_battles'])}")
    
    if 'wild_insights' in sick_json:
        stats.append(f"🤯 Wild insights: {len(sick_json['wild_insights'])}")
    
    print(f"\n🔍 SICK ANALYSIS STATS:")
    for stat in stats:
        print(f"   {stat}")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 READY FOR WEBAPP!")
    print(f"📋 This JSON will push the webapp to its limits with:")
    print(f"   • Interactive player cards with stats")
    print(f"   • Clickable timeline moments")
    print(f"   • Rich tactical insights")
    print(f"   • Performance evolution tracking")
    print(f"   • Micro-battle analysis")
    print(f"   • Wild insights only possible with full data")
    print("=" * 60)

if __name__ == "__main__":
    main()