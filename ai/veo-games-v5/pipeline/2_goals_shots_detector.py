#!/usr/bin/env python3
"""
2. Goals & Shots Detector
Analyze clip descriptions to identify actual goals and shots, then compare with VEO ground truth
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
        Path(__file__).resolve().parent.parent / '.env',   # ai/veo-games-v5/.env
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

class GoalsShotsDetector:
    def __init__(self):
        """Initialize with Gemini 1.5 Flash for efficient analysis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Use cheaper model for this task
    
    def analyze_clips_for_goals_shots(self, descriptions_text: str, team_config: dict) -> str:
        """Analyze all clip descriptions to identify goals and shots"""
        
        prompt = f"""You are a football analysis expert. Your job is to identify ACTUAL GOALS and SHOTS from detailed clip descriptions.

**TEAMS:**
- **{team_config['team_a']['name']}**: {team_config['team_a']['colors']}
- **{team_config['team_b']['name']}**: {team_config['team_b']['colors']}

**YOUR TASK:**
Analyze these clip descriptions and identify:
1. **ACTUAL GOALS** - Ball clearly crosses the goal line into the net
2. **SHOTS** - Attempts at goal (saved, missed, blocked, hit post/crossbar)

**CRITICAL RULES:**
- **GOAL**: Only when ball clearly goes INTO the goal/net
- **SHOT SAVED**: Goalkeeper saves/catches/blocks the shot
- **SHOT MISSED**: Ball goes wide, over, hits post/crossbar
- **SHOT BLOCKED**: Defender blocks the shot
- **NOT A GOAL**: "Ball retrieved from goal", "goalkeeper has ball", "saved shot"
- **NOT A GOAL**: "Shot goes wide", "hits crossbar", "saved by keeper"

**CLIP DESCRIPTIONS:**
{descriptions_text}

**OUTPUT FORMAT:**
For each GOAL or SHOT you find, output exactly this format:

GOAL|MM:SS|TEAM_NAME|Description of what happened
SHOT|MM:SS|TEAM_NAME|Description (saved/missed/blocked)

**EXAMPLES:**
GOAL|23:45|Dalkey|Player scores from close range, ball clearly crosses goal line
SHOT|15:30|Corduff|Long-range shot saved by goalkeeper
SHOT|45:12|Dalkey|Header hits the crossbar and bounces out

**BE VERY STRICT:**
- Only mark as GOAL if ball definitely goes in the net
- Everything else is a SHOT (saved, missed, blocked)
- Use exact team names: {team_config['team_a']['name']} or {team_config['team_b']['name']}
- Use MM:SS format from the clip timestamps

Analyze the descriptions now:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error analyzing clips: {str(e)}"

    def parse_ai_results(self, ai_output: str) -> dict:
        """Parse AI output into structured data"""
        results = {
            'goals': [],
            'shots': [],
            'errors': []
        }
        
        for line in ai_output.split('\n'):
            line = line.strip()
            if not line or not ('GOAL|' in line or 'SHOT|' in line):
                continue
                
            try:
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    event_type = parts[0].strip()
                    timestamp = parts[1].strip()
                    team = parts[2].strip()
                    description = parts[3].strip()
                    
                    # Convert MM:SS to seconds
                    time_parts = timestamp.split(':')
                    if len(time_parts) == 2:
                        minutes = int(time_parts[0])
                        seconds = int(time_parts[1])
                        total_seconds = minutes * 60 + seconds
                        
                        event = {
                            'timestamp': timestamp,
                            'timestamp_seconds': total_seconds,
                            'team': team,
                            'description': description
                        }
                        
                        if event_type == 'GOAL':
                            results['goals'].append(event)
                        elif event_type == 'SHOT':
                            results['shots'].append(event)
                            
            except Exception as e:
                results['errors'].append(f"Parse error: {line} - {str(e)}")
        
        return results

    def load_veo_ground_truth(self, veo_file: Path) -> dict:
        """Load VEO ground truth data"""
        with open(veo_file, 'r') as f:
            veo_data = json.load(f)
        
        veo_results = {
            'goals': [],
            'shots': []
        }
        
        for event in veo_data.get('events', []):
            event_type = event.get('event_type', '')
            timestamp = event.get('timestamp', '')
            timestamp_seconds = event.get('timestamp_seconds', 0)
            
            veo_event = {
                'timestamp': timestamp,
                'timestamp_seconds': timestamp_seconds,
                'event_type': event_type,
                'event_id': event.get('event_id', '')
            }
            
            if event_type == 'Goal':
                veo_results['goals'].append(veo_event)
            elif event_type == 'Shot on goal':
                veo_results['shots'].append(veo_event)
        
        return veo_results

    def compare_with_veo(self, ai_results: dict, veo_results: dict) -> dict:
        """Compare AI results with VEO ground truth"""
        comparison = {
            'goals': {
                'ai_count': len(ai_results['goals']),
                'veo_count': len(veo_results['goals']),
                'matches': [],
                'ai_only': [],
                'veo_only': []
            },
            'shots': {
                'ai_count': len(ai_results['shots']),
                'veo_count': len(veo_results['shots']),
                'matches': [],
                'ai_only': [],
                'veo_only': []
            }
        }
        
        # Compare goals (within 30 seconds tolerance)
        for ai_goal in ai_results['goals']:
            matched = False
            for veo_goal in veo_results['goals']:
                time_diff = abs(ai_goal['timestamp_seconds'] - veo_goal['timestamp_seconds'])
                if time_diff <= 30:  # 30 second tolerance
                    comparison['goals']['matches'].append({
                        'ai': ai_goal,
                        'veo': veo_goal,
                        'time_diff': time_diff
                    })
                    matched = True
                    break
            
            if not matched:
                comparison['goals']['ai_only'].append(ai_goal)
        
        # Find VEO goals not matched by AI
        for veo_goal in veo_results['goals']:
            matched = False
            for match in comparison['goals']['matches']:
                if match['veo']['event_id'] == veo_goal['event_id']:
                    matched = True
                    break
            
            if not matched:
                comparison['goals']['veo_only'].append(veo_goal)
        
        # Similar comparison for shots (but less strict - just count)
        comparison['shots']['ai_only'] = ai_results['shots']
        comparison['shots']['veo_only'] = veo_results['shots']
        
        return comparison

def main():
    if len(sys.argv) != 2:
        print("Usage: python 2_goals_shots_detector.py <match-id>")
        print("Example: python 2_goals_shots_detector.py 20250427-match-apr-27-2025-9bd1cf29")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Check directories exist
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    descriptions_dir = outputs_dir / 'clip_descriptions'  # Use detailed descriptions
    veo_file = outputs_dir / '1_veo_ground_truth.json'
    
    if not outputs_dir.exists():
        print(f"❌ Error: Match directory not found: {outputs_dir}")
        sys.exit(1)
    
    if not descriptions_dir.exists():
        print(f"❌ Error: Descriptions directory not found: {descriptions_dir}")
        print("Run step 3 first: python 3_analyze_clips.py <match-id>")
        sys.exit(1)
    
    if not veo_file.exists():
        print(f"❌ Error: VEO ground truth not found: {veo_file}")
        print("Run step 1.1 first: python 1.1_fetch_veo.py <veo-url>")
        sys.exit(1)
    
    # Load team configuration
    team_config_file = outputs_dir / 'team_config.json'
    if not team_config_file.exists():
        print(f"❌ Error: Team configuration not found: {team_config_file}")
        sys.exit(1)
    
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    print(f"🎯 Goals & Shots Detection for: {match_id}")
    print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
    print("🔍 Analyzing detailed clip descriptions for goals and shots...")
    print("=" * 60)
    
    # Load all clip descriptions
    description_files = sorted(descriptions_dir.glob("*.txt"))
    if not description_files:
        print(f"❌ No description files found in {descriptions_dir}")
        sys.exit(1)
    
    print(f"📊 Found {len(description_files)} clip descriptions")
    
    # Combine all descriptions with timestamps
    all_descriptions = []
    for desc_file in description_files:
        # Extract timestamp from filename (e.g., clip_23m45s.txt -> 23:45)
        import re
        match = re.search(r'clip_(\d+)m(\d+)s', desc_file.name)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            timestamp = f"{minutes:02d}:{seconds:02d}"
            
            with open(desc_file, 'r') as f:
                content = f.read().strip()
            
            all_descriptions.append(f"[{timestamp}] {content}")
    
    descriptions_text = "\n\n".join(all_descriptions)
    
    # Initialize detector
    detector = GoalsShotsDetector()
    
    # Analyze clips for goals and shots
    print("🤖 Running AI analysis...")
    ai_output = detector.analyze_clips_for_goals_shots(descriptions_text, team_config)
    
    # Parse AI results
    ai_results = detector.parse_ai_results(ai_output)
    
    # Load VEO ground truth
    print("📊 Loading VEO ground truth...")
    veo_results = detector.load_veo_ground_truth(veo_file)
    
    # Compare results
    comparison = detector.compare_with_veo(ai_results, veo_results)
    
    # Save results
    results_file = outputs_dir / '2_goals_shots_analysis.json'
    results_data = {
        'match_id': match_id,
        'ai_analysis': ai_results,
        'veo_ground_truth': veo_results,
        'comparison': comparison,
        'raw_ai_output': ai_output
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    # Print summary
    print(f"\n🎯 GOALS & SHOTS ANALYSIS COMPLETE")
    print("=" * 50)
    
    print(f"\n⚽ GOALS COMPARISON:")
    print(f"   🤖 AI Detected: {comparison['goals']['ai_count']} goals")
    print(f"   📊 VEO Truth: {comparison['goals']['veo_count']} goals")
    print(f"   ✅ Matches: {len(comparison['goals']['matches'])}")
    print(f"   🔍 AI Only: {len(comparison['goals']['ai_only'])}")
    print(f"   📊 VEO Only: {len(comparison['goals']['veo_only'])}")
    
    print(f"\n🎯 SHOTS COMPARISON:")
    print(f"   🤖 AI Detected: {comparison['shots']['ai_count']} shots")
    print(f"   📊 VEO Truth: {comparison['shots']['veo_count']} shots")
    
    # Show details
    if comparison['goals']['matches']:
        print(f"\n✅ MATCHED GOALS:")
        for match in comparison['goals']['matches']:
            ai_goal = match['ai']
            veo_goal = match['veo']
            print(f"   {ai_goal['timestamp']} - {ai_goal['team']}: {ai_goal['description'][:50]}...")
            print(f"     VEO: {veo_goal['timestamp']} (±{match['time_diff']}s)")
    
    if comparison['goals']['ai_only']:
        print(f"\n🤖 AI-ONLY GOALS (possible false positives):")
        for goal in comparison['goals']['ai_only']:
            print(f"   {goal['timestamp']} - {goal['team']}: {goal['description'][:50]}...")
    
    if comparison['goals']['veo_only']:
        print(f"\n📊 VEO-ONLY GOALS (missed by AI):")
        for goal in comparison['goals']['veo_only']:
            print(f"   {goal['timestamp']} - VEO Goal")
    
    print(f"\n📁 Detailed results saved to: {results_file}")
    print(f"\n🎯 Next step: Review results and run tactical analysis")

if __name__ == "__main__":
    main()
