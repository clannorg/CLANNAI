#!/usr/bin/env python3
"""
Consolidated Team Intelligence Report Generator
Combines all tactical insights into frontend-ready team reports.
"""

import json
import os
import sys
from pathlib import Path
import google.generativeai as genai
from datetime import datetime

class TeamIntelligenceConsolidator:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def get_consolidation_prompt(self, team_name: str) -> str:
        return f"""You are an elite football analytics expert creating a comprehensive Team Intelligence Report for frontend display.

Create a structured, comprehensive report that consolidates ALL tactical insights for {team_name}.

## OUTPUT FORMAT (STRICT JSON):

```json
{{
  "team_name": "{team_name}",
  "match_id": "match-identifier",
  "generated_at": "ISO timestamp",
  "summary": {{
    "overall_rating": "A-F grade",
    "key_identity": "Primary tactical identity in 1 sentence",
    "match_outcome_assessment": "Win/Loss/Draw assessment with key factors"
  }},
  "strengths": [
    {{
      "title": "Strength Name",
      "description": "Detailed explanation",
      "evidence_timestamps": ["22:04", "86:39", "129:08"],
      "impact_score": 85,
      "key_evidence": "Specific match evidence"
    }}
  ],
  "weaknesses": [
    {{
      "title": "Weakness Name", 
      "description": "Detailed explanation",
      "evidence_timestamps": ["44:04", "132:13"],
      "severity_score": 75,
      "cost_analysis": "What this weakness costs the team"
    }}
  ],
  "training_drills": [
    {{
      "focus_area": "Area to improve",
      "drill_name": "Specific drill name",
      "description": "How to execute the drill",
      "duration": "15-30 minutes",
      "equipment": "Required equipment",
      "success_metrics": "How to measure improvement"
    }}
  ],
  "key_moments": [
    {{
      "timestamp": "86:39",
      "event_type": "goal",
      "description": "What happened",
      "tactical_significance": "Why this moment matters tactically",
      "learning_point": "What can be learned"
    }}
  ],
  "performance_metrics": {{
    "attacking": {{
      "goals_scored": 3,
      "shots_total": 15,
      "conversion_rate": "20%",
      "set_piece_threat": "High"
    }},
    "defending": {{
      "goals_conceded": 2,
      "saves_required": 17,
      "defensive_actions": "High pressure",
      "set_piece_vulnerability": "Medium"
    }}
  }},
  "next_match_focus": [
    {{
      "priority": "High",
      "area": "Defensive Set Pieces",
      "action": "Wall positioning drills",
      "expected_improvement": "Reduce free kick goals conceded"
    }}
  ]
}}
```

## GUIDELINES:
- Use ONLY the provided match data
- Include specific timestamps as evidence
- Rate strengths (0-100) and weaknesses by severity (0-100)  
- Provide actionable, specific training drills
- Focus on tactical insights that help coaches make decisions
- Extract clear patterns from the timeline data
- Be precise about what the evidence shows

Create a comprehensive report that a coach can immediately use for team development and tactical planning."""

    def consolidate_team_intelligence(self, match_id: str, team_name: str) -> dict:
        """Generate consolidated team intelligence report"""
        print(f"🧠 Generating consolidated intelligence for {team_name}")
        
        # Get base directory
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / match_id
        
        # Read all source data
        timeline_path = data_dir / "6_validated_timeline.txt"
        complete_timeline_path = data_dir / "5_complete_timeline.txt"
        ground_truth_path = data_dir / "1_veo_ground_truth.json"
        
        if not all([timeline_path.exists(), complete_timeline_path.exists(), ground_truth_path.exists()]):
            raise FileNotFoundError("Required source files not found")
        
        # Load data
        with open(timeline_path, 'r') as f:
            validated_timeline = f.read()
        
        with open(complete_timeline_path, 'r') as f:
            complete_timeline = f.read()[:12000]  # Limit for token constraints
        
        with open(ground_truth_path, 'r') as f:
            ground_truth = json.load(f)
        
        # Create comprehensive analysis prompt
        analysis_prompt = f"""
TEAM INTELLIGENCE CONSOLIDATION REQUEST

## MATCH DATA:

### VALIDATED TIMELINE (Goals & Shots):
{validated_timeline}

### COMPLETE MATCH TIMELINE (First 12k chars):
{complete_timeline}

### GROUND TRUTH CONTEXT:
- Total Events: {len(ground_truth.get('events', []))}
- Match Duration: {ground_truth.get('duration', 'Unknown')}
- Match Date: {ground_truth.get('date', 'Unknown')}

---

{self.get_consolidation_prompt(team_name)}
"""
        
        print(f"📊 Processing tactical intelligence for {team_name}...")
        response = self.model.generate_content(analysis_prompt)
        
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Find JSON block
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            team_intelligence = json.loads(json_text)
            
            # Add metadata
            team_intelligence['match_id'] = match_id
            team_intelligence['generated_at'] = datetime.now().isoformat()
            
            return team_intelligence
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"🔍 Raw response: {response.text[:500]}...")
            
            # Fallback: create basic structure
            return {
                "team_name": team_name,
                "match_id": match_id,
                "generated_at": datetime.now().isoformat(),
                "error": "Failed to parse AI response",
                "raw_response": response.text[:1000]
            }

    def generate_team_reports(self, match_id: str):
        """Generate consolidated reports for both teams"""
        print(f"🚀 GENERATING CONSOLIDATED TEAM INTELLIGENCE - {match_id}")
        
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / match_id
        
        # Generate reports for both teams
        teams = [
            {"name": "Red Team", "filename": "13_team_intelligence_red.json"},
            {"name": "Yellow Team", "filename": "13_team_intelligence_yellow.json"}
        ]
        
        generated_files = []
        
        for team in teams:
            try:
                print(f"\n📋 Processing {team['name']}...")
                
                intelligence = self.consolidate_team_intelligence(match_id, team['name'])
                
                # Save consolidated report
                output_path = data_dir / team['filename']
                with open(output_path, 'w') as f:
                    json.dump(intelligence, f, indent=2, ensure_ascii=False)
                
                generated_files.append(output_path)
                print(f"✅ {team['name']} intelligence saved: {output_path}")
                
            except Exception as e:
                print(f"❌ Error generating {team['name']} report: {e}")
                continue
        
        # Generate summary
        print(f"\n🎯 TEAM INTELLIGENCE CONSOLIDATION COMPLETE")
        print(f"📁 Match: {match_id}")
        print(f"📄 Files generated: {len(generated_files)}")
        
        for file_path in generated_files:
            file_size = file_path.stat().st_size / 1024  # KB
            print(f"   📋 {file_path.name} ({file_size:.1f}KB)")
        
        return generated_files

def main():
    if len(sys.argv) != 2:
        print("Usage: python 13_team_intelligence_consolidator.py <match_id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        consolidator = TeamIntelligenceConsolidator()
        consolidator.generate_team_reports(match_id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()