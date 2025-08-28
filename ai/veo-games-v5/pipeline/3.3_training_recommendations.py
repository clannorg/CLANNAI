#!/usr/bin/env python3
"""
Step 3.3: Generate Training Drill Recommendations
Analyzes tactical insights and recommends specific training drills with YouTube videos.
"""

import json
import sys
import os
from pathlib import Path
import google.generativeai as genai
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

# Configure Gemini
api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Training Drill Database with YouTube links
DRILL_DATABASE = {
    "defensive_transitions": {
        "name": "4v2 Defensive Transition Drill",
        "youtube_id": "dQw4w9WgXcQ",  # Replace with actual drill video
        "description": "Improve defensive shape and pressing after losing possession",
        "focus": "Quick transition from attack to defense, compact shape"
    },
    "attacking_transitions": {
        "name": "3v2 Counter Attack Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Develop quick attacking transitions and decision making",
        "focus": "Speed of play, forward passing, clinical finishing"
    },
    "set_piece_defending": {
        "name": "Zonal Marking Corner Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Organize defensive set piece structure and communication",
        "focus": "Zonal positioning, aerial duels, clearing techniques"
    },
    "possession_retention": {
        "name": "Rondo Possession Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Improve passing accuracy and ball retention under pressure",
        "focus": "Quick passing, movement off the ball, press resistance"
    },
    "finishing": {
        "name": "1v1 Finishing Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Improve clinical finishing in one-on-one situations",
        "focus": "Composure, shot placement, beating the goalkeeper"
    },
    "crossing_delivery": {
        "name": "Wide Play Crossing Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Develop accurate crossing and attacking movement in the box",
        "focus": "Cross quality, timing of runs, aerial finishing"
    },
    "pressing": {
        "name": "High Press Trigger Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Coordinate team pressing and win ball in final third",
        "focus": "Press triggers, compactness, ball recovery"
    },
    "build_up_play": {
        "name": "Playing Out From Back Drill",
        "youtube_id": "dQw4w9WgXcQ",
        "description": "Improve ball progression from defensive third",
        "focus": "Passing angles, press resistance, progressive passing"
    }
}

def load_tactical_analysis(match_id):
    """Load tactical analysis JSON"""
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    tactical_file = base_path / "3.2_tactical_analysis.json"
    
    if not tactical_file.exists():
        print(f"❌ Tactical analysis not found: {tactical_file}")
        print("Run step 3.2 first: python 3.2_tactical_formatter.py <match-id>")
        return None
    
    with open(tactical_file, 'r') as f:
        return json.load(f)

def load_match_summary(match_id):
    """Load match summary for additional context"""
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    summary_file = base_path / "2.6_focused_summary.txt"
    
    if not summary_file.exists():
        return "No match summary available"
    
    return summary_file.read_text()

def analyze_training_needs(tactical_analysis, match_summary):
    """Use Gemini to analyze tactical weaknesses and recommend training areas"""
    
    prompt = f"""
Analyze this football match tactical analysis and identify the TOP 3 training priorities.

TACTICAL ANALYSIS:
{json.dumps(tactical_analysis, indent=2)}

MATCH SUMMARY:
{match_summary}

Based on the tactical analysis, identify the 3 most important training areas from these options:
- defensive_transitions
- attacking_transitions  
- set_piece_defending
- possession_retention
- finishing
- crossing_delivery
- pressing
- build_up_play

For each training area, provide:
1. The training area name (from the list above)
2. Specific evidence from the match (goals conceded, missed chances, etc.)
3. Why this training would help (1-2 sentences)

Respond in this exact JSON format:
{{
  "training_priorities": [
    {{
      "area": "defensive_transitions",
      "evidence": "Team conceded 2 goals from counter-attacks in minutes 23 and 67",
      "reasoning": "Poor defensive shape after losing possession led to dangerous counter-attacks"
    }},
    {{
      "area": "finishing", 
      "evidence": "Created 8 chances but only scored 1 goal, conversion rate of 12.5%",
      "reasoning": "Clinical finishing training would improve goal conversion rate"
    }},
    {{
      "area": "set_piece_defending",
      "evidence": "Conceded from corner kick, poor zonal marking organization",
      "reasoning": "Better set piece structure would prevent defensive lapses"
    }}
  ]
}}

Focus on areas where the team showed clear weaknesses with specific match evidence.
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        
        return json.loads(response_text)
        
    except Exception as e:
        print(f"❌ Error analyzing training needs: {e}")
        return None

def generate_training_recommendations(match_id):
    """Generate complete training recommendations"""
    print(f"🏋️ Generating training recommendations for: {match_id}")
    
    # Load tactical analysis
    tactical_analysis = load_tactical_analysis(match_id)
    if not tactical_analysis:
        return False
    
    # Load match summary
    match_summary = load_match_summary(match_id)
    
    # Analyze training needs with Gemini
    print("🧠 Analyzing tactical weaknesses...")
    training_needs = analyze_training_needs(tactical_analysis, match_summary)
    if not training_needs:
        return False
    
    # Build recommendations with drill details
    recommendations = {
        "match_id": match_id,
        "generated_at": datetime.now().isoformat(),
        "training_recommendations": []
    }
    
    for priority in training_needs.get("training_priorities", []):
        area = priority["area"]
        if area in DRILL_DATABASE:
            drill = DRILL_DATABASE[area]
            recommendation = {
                "drill_name": drill["name"],
                "youtube_url": f"https://www.youtube.com/watch?v={drill['youtube_id']}",
                "youtube_embed": f"https://www.youtube.com/embed/{drill['youtube_id']}",
                "description": drill["description"],
                "focus_areas": drill["focus"],
                "match_evidence": priority["evidence"],
                "why_needed": priority["reasoning"],
                "priority": len(recommendations["training_recommendations"]) + 1
            }
            recommendations["training_recommendations"].append(recommendation)
    
    # Save recommendations
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    output_file = base_path / "3.3_training_recommendations.json"
    
    with open(output_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"✅ Training recommendations saved: {output_file}")
    print(f"📊 Generated {len(recommendations['training_recommendations'])} drill recommendations")
    
    # Print summary
    print("\n🏋️ TRAINING RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations["training_recommendations"], 1):
        print(f"\n{i}. {rec['drill_name']}")
        print(f"   Evidence: {rec['match_evidence']}")
        print(f"   Focus: {rec['focus_areas']}")
        print(f"   Video: {rec['youtube_url']}")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 3.3_training_recommendations.py <match-id>")
        print("Example: python 3.3_training_recommendations.py 20250427-match-apr-27-2025-9bd1cf29")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    success = generate_training_recommendations(match_id)
    if not success:
        sys.exit(1)
    
    print("\n🎯 Training recommendations complete!")
    print("Next step: Upload to website with 3.5_s3_uploader.py")

if __name__ == "__main__":
    main()
