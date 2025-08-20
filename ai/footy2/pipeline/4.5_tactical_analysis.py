#!/usr/bin/env python3
"""
4.5. Tactical Analysis
Analyze tactical patterns using full game timeline + highlights overview
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

class TacticalAnalyst:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for tactical analysis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def get_tactical_analysis_prompt(self, team_config: dict) -> str:
        """Generate comprehensive tactical analysis prompt"""
        team_a_name = team_config['team_a']['name']
        team_a_colors = team_config['team_a']['colors']
        team_b_name = team_config['team_b']['name'] 
        team_b_colors = team_config['team_b']['colors']
        
        return f"""You are an elite 5-a-side football tactical analyst with 20+ years of experience. You have access to:

1. **COMPLETE GAME TIMELINE** - Every 15-second segment described in detail
2. **HIGHLIGHTS OVERVIEW** - Key events, final score, match summary
3. **TEAM IDENTIFICATION** - Visual appearance and names

**TEAMS:**
- **{team_a_name}** ({team_a_colors})
- **{team_b_name}** ({team_b_colors})

**YOUR MISSION:** Provide deep tactical insights that only someone who watched EVERY second could give.

**5-A-SIDE TACTICAL FOCUS:**
- **Individual Brilliance** vs **Team Coordination**
- **Pressing Triggers** - When/how teams press
- **Transition Speed** - Defense to attack timing
- **Goalkeeper Distribution** - Short vs long, accuracy
- **Space Exploitation** - Wide areas, through balls
- **Fatigue Patterns** - Performance drops over time
- **Set Piece Execution** - Corners, free kicks, throw-ins
- **1v1 Duels** - Success rates, key matchups

**EVIDENCE REQUIREMENTS:**
- Quote specific timestamps from timeline
- Reference multiple examples of patterns
- Identify tactical shifts during the game
- Note individual player impacts by description
- Connect timeline details to goal/highlight outcomes

**OUTPUT FORMAT:**

# 🎯 TACTICAL ANALYSIS: {team_a_name} vs {team_b_name}

## 📊 MATCH OVERVIEW
[Brief tactical summary of how the game unfolded]

## 🔥 {team_a_name.upper()} ANALYSIS

### ⚡ TACTICAL STRENGTHS
**1. [Strength Name]**
- **Evidence:** [Specific timeline quotes with timestamps]
- **Pattern:** [How often this happened]
- **Impact:** [How this contributed to goals/chances]

**2. [Strength Name]**
- **Evidence:** [Timeline examples]
- **Pattern:** [Frequency/timing]
- **Impact:** [Game influence]

### ⚠️ TACTICAL WEAKNESSES
**1. [Weakness Name]**
- **Evidence:** [Timeline quotes showing problems]
- **Cost:** [Goals conceded/chances missed because of this]
- **Pattern:** [When this weakness appeared]

### 🎯 KEY PLAYERS (by description)
**[Player Description]** (e.g., "Tall player", "Bearded player")
- **Role:** [Tactical position/responsibility]
- **Impact:** [Specific contributions with timestamps]
- **Effectiveness:** [Success rate in key actions]

## 🔥 {team_b_name.upper()} ANALYSIS

### ⚡ TACTICAL STRENGTHS
[Same format as above]

### ⚠️ TACTICAL WEAKNESSES
[Same format as above]

### 🎯 KEY PLAYERS (by description)
[Same format as above]

## 🧠 TACTICAL BATTLE ANALYSIS

### 🔄 GAME PHASES
**Early Game (0-15 mins):**
- [Tactical approach, tempo, key events]

**Mid Game (15-35 mins):**
- [Tactical adjustments, momentum shifts]

**Late Game (35+ mins):**
- [Fatigue impact, desperation tactics, game management]

### ⚔️ KEY TACTICAL DUELS
**1. [Tactical Matchup]**
- **Timeline Evidence:** [Specific examples]
- **Winner:** [Which approach succeeded]
- **Impact:** [How this affected the game]

### 🎯 TURNING POINTS
**[Timestamp] - [Event]**
- **Tactical Significance:** [Why this changed the game]
- **Evidence:** [Timeline details before/after]

## 🏆 COACHING INSIGHTS

### 📈 WHAT WORKED
- [Successful tactical approaches with evidence]

### 📉 WHAT FAILED  
- [Failed tactical approaches with evidence]

### 🎯 NEXT MATCH RECOMMENDATIONS
**For {team_a_name}:**
- [Specific tactical adjustments]

**For {team_b_name}:**
- [Specific tactical adjustments]

**WILD INSIGHTS ONLY POSSIBLE WITH FULL GAME DATA:**
[Unique observations that require seeing every moment - patterns, subtle tactical shifts, individual player evolution during the game, etc.]

Analyze the complete game data and provide this comprehensive tactical breakdown:"""

    def analyze_tactics(self, full_timeline: str, highlights: str, team_config: dict) -> str:
        """Generate tactical analysis using full timeline and highlights"""
        try:
            prompt = self.get_tactical_analysis_prompt(team_config)
            
            # Combine all data for analysis
            analysis_input = f"""
{prompt}

**HIGHLIGHTS OVERVIEW:**
{highlights}

**COMPLETE GAME TIMELINE:**
{full_timeline}
"""
            
            print("🧠 Generating tactical analysis...")
            print("📊 Processing full game timeline + highlights...")
            
            response = self.model.generate_content(analysis_input)
            return response.text.strip()
            
        except Exception as e:
            return f"Error generating tactical analysis: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4.5_tactical_analysis.py <match-id>")
        print("Example: python 4.5_tactical_analysis.py leo1")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        print("Run previous steps first")
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
    print(f"🧠 Tactical Analysis for: {match_id}")
    print("=" * 50)
    
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
    analyzer = TacticalAnalyst()
    
    # Generate tactical analysis
    print("\n🧠 Analyzing tactical patterns...")
    print("⏳ This may take 30-60 seconds due to large data volume...")
    
    tactical_analysis = analyzer.analyze_tactics(full_timeline, highlights, team_config)
    
    # Save analysis
    tactical_file = outputs_dir / 'tactical_analysis.txt'
    with open(tactical_file, 'w') as f:
        f.write(tactical_analysis)
    
    print(f"\n✅ Tactical analysis complete!")
    print(f"📁 Analysis saved to: {tactical_file}")
    print(f"📊 Analysis length: {len(tactical_analysis):,} characters")
    
    # Show preview
    lines = tactical_analysis.split('\n')
    preview_lines = lines[:20] if len(lines) > 20 else lines
    print(f"\n🔍 PREVIEW:")
    print("-" * 50)
    for line in preview_lines:
        print(line)
    if len(lines) > 20:
        print(f"... ({len(lines) - 20} more lines)")
    
    print(f"\n🎯 Ready for step 5: python 5_format_webapp.py {match_id}")

if __name__ == "__main__":
    main()