#!/usr/bin/env python3
"""
8_tactical_analyst.py - AI Football Tactical Analyst

Takes validated timeline and goals to provide:
- Team strengths & weaknesses analysis
- Tactical insights and patterns
- Coaching recommendations
- Training drill suggestions
- Performance evidence
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os

class TacticalAnalyst:
    def __init__(self):
        """Initialize the AI Tactical Analyst"""
        load_dotenv()
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def get_tactical_analysis_prompt(self, team_name: str = "Team") -> str:
        """Generate prompt for tactical analysis"""
        return f"""You are an elite football tactical analyst and coach with 20+ years of experience analyzing professional matches. You've been provided with a complete match timeline and validated goals/shots data.

Your task is to provide comprehensive tactical analysis for {team_name}, including:

1. **TACTICAL STRENGTHS** - What this team does well
2. **TACTICAL WEAKNESSES** - Areas needing improvement  
3. **KEY EVIDENCE** - Specific timeline moments supporting your analysis
4. **COACHING RECOMMENDATIONS** - Tactical adjustments for next match
5. **TRAINING DRILLS** - Specific exercises to address weaknesses

## ANALYSIS GUIDELINES:

### ATTACKING ANALYSIS:
- Set piece effectiveness (free kicks, corners, penalties)
- Counter-attacking speed and precision
- Final third creativity and clinical finishing
- Wide play vs central penetration patterns
- Goal-scoring variety (headers, long-range, tap-ins, etc.)

### DEFENSIVE ANALYSIS:
- Pressing intensity and coordination
- Defensive transitions after losing possession
- Set piece defending (walls, marking, clearances)
- Goalkeeper distribution and shot-stopping
- Defensive line organization and offside trap

### TACTICAL PATTERNS:
- Possession-based vs direct play preferences
- Formation changes and positional flexibility
- Key player influences and weak links
- Time periods of dominance vs vulnerability
- Response to going behind/ahead in score

### EVIDENCE REQUIREMENTS:
- Quote specific timestamps and events from the timeline
- Reference goal/shot patterns as proof
- Identify recurring tactical themes
- Note successful and unsuccessful sequences

### COACHING FOCUS:
- Prioritize most impactful improvements
- Suggest realistic training methods
- Address both individual and team tactics
- Consider opponent analysis for next match

## OUTPUT FORMAT:

### 🎯 TACTICAL STRENGTHS
*List 3-5 key strengths with specific evidence*

**1. [Strength Name]**
- **Evidence:** Timeline quotes and goal examples
- **Impact:** How this helps win games
- **Continue Doing:** Specific tactical instructions

### ⚠️ TACTICAL WEAKNESSES  
*List 3-5 key weaknesses with specific evidence*

**1. [Weakness Name]**
- **Evidence:** Timeline quotes showing problems
- **Cost:** How this loses games/chances
- **Improvement Plan:** Specific changes needed

### 📊 KEY PERFORMANCE EVIDENCE
*Statistical and observational evidence*

**Attacking Metrics:**
- Goal variety and timing patterns
- Set piece conversion rates
- Shooting accuracy and decision-making

**Defensive Metrics:**
- Shots conceded and save requirements
- Defensive action success rates
- Transition speed and effectiveness

### 🎯 COACHING RECOMMENDATIONS

**Immediate Tactical Adjustments:**
1. [Specific change for next match]
2. [Formation/personnel recommendation]
3. [Set piece modifications]

**Medium-term Development:**
1. [Tactical system improvements]
2. [Player role clarifications]
3. [Team shape refinements]

### 🏃‍♂️ TRAINING DRILL SUGGESTIONS

**Priority Drill 1: [Weakness-focused]**
- **Objective:** Address main weakness
- **Setup:** Detailed drill description
- **Focus Points:** Key coaching cues
- **Duration:** Recommended training time

**Priority Drill 2: [Strength-enhancement]**
- **Objective:** Maximize existing strength
- **Setup:** Detailed drill description
- **Focus Points:** Key coaching cues
- **Duration:** Recommended training time

**Priority Drill 3: [Tactical-specific]**
- **Objective:** Address tactical pattern
- **Setup:** Detailed drill description
- **Focus Points:** Key coaching cues
- **Duration:** Recommended training time

### 🔍 OPPONENT PREPARATION
*How to prepare for teams that play similarly*

**Expected Opponent Tactics:**
- Likely formation and style
- Key threats to watch
- Vulnerability areas to exploit

**Counter-Strategy:**
- Tactical setup recommendations
- Player instructions
- Set piece plans

---

**CRITICAL:** Base ALL analysis on the actual timeline evidence provided. Do not make generic football observations - everything must be supported by specific events, timestamps, and patterns from this match data.

Be specific, actionable, and evidence-based. Think like you're preparing a detailed tactical report for the coaching staff."""

    def analyze_match_tactics(self, match_id: str) -> bool:
        """Perform comprehensive tactical analysis"""
        print(f"🧠 AI Tactical Analysis for {match_id}")
        print("🎯 Analyzing team performance with coaching insights...")
        
        # Load match data
        data_dir = Path("../outputs") / match_id
        
        # Read validated timeline
        timeline_path = data_dir / "6_validated_timeline.txt"
        if not timeline_path.exists():
            print(f"❌ Validated timeline not found: {timeline_path}")
            return False
            
        # Read complete timeline for context
        complete_timeline_path = data_dir / "5_complete_timeline.txt"
        if not complete_timeline_path.exists():
            print(f"❌ Complete timeline not found: {complete_timeline_path}")
            return False
        
        # Read ground truth for additional context
        ground_truth_path = data_dir / "1_veo_ground_truth.json"
        ground_truth_data = {}
        if ground_truth_path.exists():
            with open(ground_truth_path, 'r') as f:
                ground_truth_data = json.load(f)
        
        # Load timeline data
        with open(timeline_path, 'r') as f:
            validated_timeline = f.read()
            
        with open(complete_timeline_path, 'r') as f:
            complete_timeline = f.read()
        
        print("📊 Processing match data with Gemini 2.5 Pro...")
        
        # Analyze both teams separately
        for team_name in ["Red Team", "Yellow Team"]:
            print(f"🔍 Analyzing {team_name}...")
            
            # Create comprehensive prompt
            analysis_prompt = f"""
MATCH DATA FOR TACTICAL ANALYSIS:

## VALIDATED GOALS & SHOTS ANALYSIS:
{validated_timeline}

## COMPLETE MATCH TIMELINE:
{complete_timeline[:8000]}  # Truncate for token limits

## GROUND TRUTH CONTEXT:
Total Events: {len(ground_truth_data.get('events', []))}
Match Duration: {ground_truth_data.get('duration', 'Unknown')}

---

{self.get_tactical_analysis_prompt(team_name)}
"""
            
            try:
                # Generate tactical analysis
                response = self.model.generate_content(analysis_prompt)
                
                if response and response.text:
                    # Save analysis
                    output_path = data_dir / f"8_tactical_analysis_{team_name.lower().replace(' ', '_')}.txt"
                    
                    with open(output_path, 'w') as f:
                        f.write(f"# Tactical Analysis - {team_name}\n")
                        f.write(f"# Match: {match_id}\n")
                        f.write(f"# Generated: {datetime.now().isoformat()}\n")
                        f.write(f"# Method: Gemini 2.5 Pro tactical analysis\n")
                        f.write(f"# Context: AI-powered coaching insights\n\n")
                        f.write(response.text)
                    
                    print(f"✅ {team_name} analysis saved to: {output_path}")
                    
                    # Print summary
                    lines = response.text.split('\n')
                    print(f"\n🎯 {team_name.upper()} TACTICAL SUMMARY:")
                    in_strengths = False
                    in_weaknesses = False
                    strength_count = 0
                    weakness_count = 0
                    
                    for line in lines:
                        if "TACTICAL STRENGTHS" in line:
                            in_strengths = True
                            in_weaknesses = False
                        elif "TACTICAL WEAKNESSES" in line:
                            in_strengths = False
                            in_weaknesses = True
                        elif in_strengths and line.strip().startswith("**") and strength_count < 2:
                            print(f"✅ {line.strip()}")
                            strength_count += 1
                        elif in_weaknesses and line.strip().startswith("**") and weakness_count < 2:
                            print(f"⚠️  {line.strip()}")
                            weakness_count += 1
                    print()
                    
                else:
                    print(f"❌ No response from Gemini for {team_name}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error analyzing {team_name}: {str(e)}")
                return False
        
        # Create combined summary
        print("📋 Creating combined tactical summary...")
        self.create_match_summary(match_id, data_dir)
        
        return True
    
    def create_match_summary(self, match_id: str, data_dir: Path):
        """Create a combined tactical summary"""
        
        red_analysis_path = data_dir / "8_tactical_analysis_red_team.txt"
        yellow_analysis_path = data_dir / "8_tactical_analysis_yellow_team.txt"
        
        if not (red_analysis_path.exists() and yellow_analysis_path.exists()):
            print("⚠️ Individual team analyses not found for summary")
            return
        
        # Read both analyses
        with open(red_analysis_path, 'r') as f:
            red_analysis = f.read()
        with open(yellow_analysis_path, 'r') as f:
            yellow_analysis = f.read()
        
        # Create summary prompt
        summary_prompt = f"""Based on the detailed tactical analyses of both teams, create a concise match summary focusing on:

1. **MATCH OVERVIEW** - Key tactical battle and outcome
2. **WINNING FACTORS** - Why the winning team succeeded  
3. **KEY TACTICAL MOMENTS** - Turning points in the match
4. **COACHING LESSONS** - Main takeaways for both teams
5. **NEXT MATCH PREPARATION** - Priority areas for each team

RED TEAM ANALYSIS:
{red_analysis[:4000]}

YELLOW TEAM ANALYSIS:  
{yellow_analysis[:4000]}

Provide a professional match report suitable for coaching staff review."""

        try:
            response = self.model.generate_content(summary_prompt)
            
            if response and response.text:
                summary_path = data_dir / "8_tactical_match_summary.txt"
                
                with open(summary_path, 'w') as f:
                    f.write(f"# Tactical Match Summary\n")
                    f.write(f"# Match: {match_id}\n") 
                    f.write(f"# Generated: {datetime.now().isoformat()}\n")
                    f.write(f"# Method: Combined tactical analysis summary\n\n")
                    f.write(response.text)
                
                print(f"✅ Match summary saved to: {summary_path}")
                
                # Print key insights
                lines = response.text.split('\n')
                print("\n📋 MATCH TACTICAL SUMMARY:")
                for line in lines[:10]:  # First 10 lines
                    if line.strip() and not line.startswith('#'):
                        print(f"   {line.strip()}")
                print("   ...")
                        
        except Exception as e:
            print(f"❌ Error creating match summary: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python 8_tactical_analyst.py <match-id>")
        print("Example: python 8_tactical_analyst.py f323-527e6a4e")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    print("============================================================")
    print("🧠 AI TACTICAL ANALYST")
    print("============================================================")
    
    analyst = TacticalAnalyst()
    success = analyst.analyze_match_tactics(match_id)
    
    if success:
        print("============================================================")
        print("🎯 Tactical Analysis Complete!")
        print(f"📁 All reports saved in data/{match_id}/")
        print("   - 8_tactical_analysis_red_team.txt")
        print("   - 8_tactical_analysis_yellow_team.txt") 
        print("   - 8_tactical_match_summary.txt")
        print("============================================================")
    else:
        print("❌ Tactical analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main()