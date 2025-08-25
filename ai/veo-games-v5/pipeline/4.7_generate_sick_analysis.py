#!/usr/bin/env python3
"""
4.7. Generate Sick Analysis
Create absolutely mental tactical analysis with interactive elements, player cards, 
clickable moments, and rich data that pushes the webapp to its limits
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

class SickAnalysisGenerator:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for sick analysis generation"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def get_sick_analysis_prompt(self, team_config: dict) -> str:
        """Generate prompt for absolutely mental tactical analysis"""
        team_a_name = team_config['team_a']['name']
        team_a_colors = team_config['team_a']['colors']
        team_b_name = team_config['team_b']['name'] 
        team_b_colors = team_config['team_b']['colors']
        
        return f"""You are creating the most INSANE tactical analysis ever generated. You have access to:

1. **COMPLETE GAME TIMELINE** - Every 15-second segment described in detail
2. **HIGHLIGHTS OVERVIEW** - Key events, final score, match summary  
3. **TEAM DATA** - Visual appearance and names

**TEAMS:**
- **{team_a_name}** ({team_a_colors})
- **{team_b_name}** ({team_b_colors})

**YOUR MISSION:** Create tactical analysis that's so detailed and interactive it breaks the webapp in the best way possible.

**SICK ANALYSIS REQUIREMENTS:**

### 🔥 PLAYER ANALYSIS (Individual Cards)
For each key player, create detailed profiles with:
- **Physical Description** (from timeline observations)
- **Tactical Role** (position, responsibilities)  
- **Performance Stats** (goals, shots, key actions)
- **Timeline Moments** (specific timestamps of key actions)
- **Impact Rating** (1-10 based on influence)
- **Signature Moves** (what they do best)
- **Weaknesses** (what they struggle with)

### ⚡ TACTICAL MOMENTS (Interactive Timeline)
Create clickable moments with:
- **Exact Timestamps** (MM:SS format)
- **Tactical Significance** (why this moment mattered)
- **Before/After Analysis** (how the game changed)
- **Player Involvement** (who was key)
- **Tactical Lesson** (what coaches can learn)

### 🧠 ADVANCED INSIGHTS
Generate insights that only someone with COMPLETE game data could know:
- **Fatigue Patterns** (performance drops over time)
- **Tactical Evolution** (how strategies changed mid-game)
- **Micro-Battles** (individual duels that decided the game)
- **Psychological Warfare** (momentum shifts, confidence impacts)
- **Hidden Patterns** (things only visible with full timeline)

### 📊 PERFORMANCE METRICS
Calculate detailed stats from timeline:
- **Shot Accuracy** (successful vs attempted)
- **Possession Phases** (how long each team held the ball)
- **Pressing Success** (turnovers forced)
- **Transition Speed** (defense to attack timing)
- **Set Piece Effectiveness** (corners, free kicks success rate)

### 🎯 COACHING GOLDMINE
Provide actionable insights:
- **Training Drills** (specific exercises to improve weaknesses)
- **Tactical Adjustments** (formation/approach changes)
- **Player Development** (individual improvement areas)
- **Opposition Analysis** (how to beat similar teams)

**OUTPUT FORMAT:**

# 🔥 SICK TACTICAL ANALYSIS: {team_a_name} vs {team_b_name}

## 🎮 MATCH OVERVIEW
[Epic narrative of how the game unfolded with specific details only possible with full timeline]

## 👑 PLAYER SPOTLIGHT CARDS

### {team_a_name.upper()} PLAYERS
**[Player Description] - "The [Nickname]"**
- **Role:** [Tactical position and responsibilities]
- **Physical:** [Height, build, distinctive features from timeline]
- **Performance Stats:**
  - Goals: X (timestamps: MM:SS, MM:SS)
  - Shots: X (accuracy: X%)
  - Key Actions: X (passes, tackles, saves)
- **Timeline Moments:**
  - MM:SS: [Specific action with impact]
  - MM:SS: [Another key moment]
- **Impact Rating:** X/10
- **Signature Move:** [What they do best]
- **Weakness:** [What they struggle with]
- **Coach Notes:** [Specific development advice]

[Repeat for each key player]

### {team_b_name.upper()} PLAYERS
[Same format for opposition players]

## ⚡ TACTICAL TIMELINE (Interactive Moments)

**MM:SS - [Event Title]**
- **What Happened:** [Detailed description]
- **Tactical Significance:** [Why this mattered]
- **Players Involved:** [Key participants]
- **Game Impact:** [How this changed things]
- **Coaching Point:** [What to learn]

[Multiple interactive moments throughout the game]

## 🧠 ADVANCED TACTICAL INSIGHTS

### 🔄 GAME PHASES BREAKDOWN
**Phase 1 (0-15 mins): [Title]**
- **Tactical Approach:** [How each team played]
- **Key Battles:** [Individual duels]
- **Momentum:** [Who controlled the game]
- **Turning Points:** [Critical moments]

**Phase 2 (15-30 mins): [Title]**
[Same format]

**Phase 3 (30+ mins): [Title]**
[Same format]

### 🎯 MICRO-BATTLES ANALYSIS
**Battle 1: [Player A] vs [Player B]**
- **Duel Type:** [Attacking vs Defending, etc.]
- **Winner:** [Who came out on top]
- **Key Moments:** [Specific timestamps]
- **Impact:** [How this affected the game]

### 📊 PERFORMANCE METRICS
**{team_a_name} Stats:**
- Shot Accuracy: X% (X/X shots)
- Possession Quality: [Analysis of ball retention]
- Pressing Success: X turnovers forced
- Transition Speed: Average X seconds defense→attack
- Set Piece Conversion: X% (X/X attempts)

**{team_b_name} Stats:**
[Same format]

### 🔥 FATIGUE ANALYSIS
**Early Game (0-20 mins):**
- [Performance levels, intensity, key actions]

**Mid Game (20-40 mins):**
- [Changes in performance, tactical adjustments]

**Late Game (40+ mins):**
- [Fatigue impact, desperation tactics, game management]

## 🏆 COACHING GOLDMINE

### 📈 WHAT WORKED BRILLIANTLY
**{team_a_name}:**
- [Specific tactical successes with evidence]

**{team_b_name}:**
- [Specific tactical successes with evidence]

### 📉 WHAT FAILED SPECTACULARLY
**{team_a_name}:**
- [Tactical failures with specific examples]

**{team_b_name}:**
- [Tactical failures with specific examples]

### 🎯 TRAINING RECOMMENDATIONS
**For {team_a_name}:**
1. **[Drill Name]:** [Specific exercise to address weakness]
2. **[Drill Name]:** [Another targeted improvement]

**For {team_b_name}:**
1. **[Drill Name]:** [Specific exercise]
2. **[Drill Name]:** [Another improvement area]

### 🧠 TACTICAL EVOLUTION INSIGHTS
**How {team_a_name} Adapted:**
- [Mid-game tactical changes with timestamps]

**How {team_b_name} Responded:**
- [Counter-adaptations and adjustments]

## 🤯 WILD INSIGHTS ONLY POSSIBLE WITH FULL GAME DATA
- **[Insight 1]:** [Something only visible with complete timeline]
- **[Insight 2]:** [Another hidden pattern]
- **[Insight 3]:** [Psychological/momentum insight]
- **[Insight 4]:** [Technical detail only pros would notice]

Analyze the complete game data and create this absolutely mental tactical breakdown:"""

    def generate_sick_analysis(self, full_timeline: str, highlights: str, team_config: dict) -> str:
        """Generate absolutely mental tactical analysis"""
        try:
            prompt = self.get_sick_analysis_prompt(team_config)
            
            # Combine all data for analysis
            analysis_input = f"""
{prompt}

**HIGHLIGHTS OVERVIEW:**
{highlights}

**COMPLETE GAME TIMELINE:**
{full_timeline}
"""
            
            print("🔥 Generating absolutely SICK tactical analysis...")
            print("🧠 Processing full game data with advanced AI...")
            print("⚡ Creating interactive elements and player cards...")
            
            response = self.model.generate_content(analysis_input)
            return response.text.strip()
            
        except Exception as e:
            return f"Error generating sick analysis: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4.7_generate_sick_analysis.py <match-id>")
        print("Example: python 4.7_generate_sick_analysis.py leo1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    # Check required files exist
    full_timeline_file = outputs_dir / 'full_timeline.txt'
    highlights_file = outputs_dir / 'highlights.txt'
    team_config_file = outputs_dir / 'team_config.json'
    
    missing_files = []
    if not full_timeline_file.exists():
        missing_files.append('full_timeline.txt')
    if not highlights_file.exists():
        missing_files.append('highlights.txt')
    if not team_config_file.exists():
        missing_files.append('team_config.json')
    
    if missing_files:
        print(f"❌ Error: Missing required files: {', '.join(missing_files)}")
        print("Run previous pipeline steps first")
        sys.exit(1)
    
    # Load data
    print(f"🔥 Generating SICK analysis for: {match_id}")
    print("=" * 60)
    
    with open(full_timeline_file, 'r') as f:
        full_timeline = f.read()
    
    with open(highlights_file, 'r') as f:
        highlights = f.read()
    
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    print(f"📊 Full timeline: {len(full_timeline):,} characters")
    print(f"🎯 Highlights: {len(highlights):,} characters")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    
    # Initialize analyzer
    analyzer = SickAnalysisGenerator()
    
    # Generate sick analysis
    print("\n🔥 Creating absolutely MENTAL tactical analysis...")
    print("⏳ This will take 60-90 seconds due to advanced processing...")
    print("🧠 Generating player cards, interactive moments, and wild insights...")
    
    sick_analysis = analyzer.generate_sick_analysis(full_timeline, highlights, team_config)
    
    # Save analysis
    sick_file = outputs_dir / 'sick_tactical_analysis.txt'
    with open(sick_file, 'w') as f:
        f.write(sick_analysis)
    
    print(f"\n🔥 SICK analysis complete!")
    print(f"📁 Analysis saved to: {sick_file}")
    print(f"📊 Analysis length: {len(sick_analysis):,} characters")
    
    # Show preview
    lines = sick_analysis.split('\n')
    preview_lines = lines[:25] if len(lines) > 25 else lines
    print(f"\n🔍 PREVIEW:")
    print("=" * 60)
    for line in preview_lines:
        print(line)
    if len(lines) > 25:
        print(f"... ({len(lines) - 25} more lines)")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 NEXT STEP: Convert to interactive JSON format")
    print(f"📋 RUN THIS COMMAND:")
    print(f"   python 4.8_convert_sick_to_json.py {match_id}")
    print("=" * 60)

if __name__ == "__main__":
    main()