#!/usr/bin/env python3
"""
1.7. Accuracy Evaluator (V3)
AI-powered comparison between our validator results and VEO ground truth
Uses Gemini 2.5 Pro for intelligent analysis
Ported from V2 with improvements for V3 pipeline
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

class AccuracyEvaluator:
    def __init__(self):
        """Initialize the AI-powered accuracy evaluator"""
        
        # Load environment variables from multiple locations
        env_paths = [
            Path(__file__).parent / '.env',
            Path(__file__).parent.parent / '.env', 
            Path(__file__).parent.parent.parent / '.env'
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"🔑 Loaded environment from: {env_path}")
                break
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        print("🤖 AI-powered accuracy evaluator initialized with Gemini 2.5 Pro")

    def load_team_config(self, match_id: str) -> dict:
        """Load team configuration from match setup"""
        config_path = Path(f"../outputs/{match_id}/match_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return {
                'team_a': {'name': 'Team A', 'jersey': 'first team colors'},
                'team_b': {'name': 'Team B', 'jersey': 'second team colors'}
            }

    def get_comparison_prompt(self, our_analysis: str, veo_ground_truth: str, team_config: dict) -> str:
        """Create prompt for AI-powered accuracy comparison"""
        team_a_name = team_config['team_a']['name']
        team_b_name = team_config['team_b']['name']
        
        return f"""You are an expert football analyst tasked with comparing two sets of match event data for accuracy evaluation.

CONTEXT:
- Our AI pipeline analyzed video clips and produced event detections
- VEO camera system captured ground truth events during the actual match
- Your job is to compare our AI results against the verified ground truth data
- Teams: {team_a_name} vs {team_b_name}

VEO GROUND TRUTH DATA (authoritative):
{veo_ground_truth}

OUR AI ANALYSIS RESULTS:
{our_analysis}

COMPARISON TASK:
1. **Goals Analysis**: Compare detected goals vs ground truth goals
   - Match timestamps (allow ±30 second tolerance for timing differences)
   - Identify true positives, false positives, false negatives
   - Check team attribution accuracy
   - Explain any discrepancies

2. **Shots Analysis**: Compare detected shots vs ground truth shots
   - Match timestamps with tolerance
   - Assess if our AI detected actual shooting events
   - Note any missed or extra shots

3. **Overall Assessment**: 
   - Calculate approximate precision and recall percentages
   - Identify patterns in what our AI does well vs struggles with
   - Provide actionable insights for improvement

OUTPUT FORMAT:
## GOALS COMPARISON
**VEO Ground Truth**: [list actual goals with timestamps]
**Our AI Detected**: [list our detected goals with timestamps and teams]
**Matches**: [list successful matches with tolerance noted]
**False Positives**: [goals we detected that weren't real]
**False Negatives**: [real goals we missed]
**Team Attribution**: [accuracy of which team scored each goal]

## SHOTS COMPARISON  
**VEO Ground Truth**: [list actual shots with timestamps]
**Our AI Detected**: [list our detected shots with timestamps]
**Assessment**: [brief analysis of shot detection accuracy]

## ACCURACY METRICS
**Goals - Precision**: X% (correct goals / total detected goals)
**Goals - Recall**: X% (correct goals / total actual goals)
**Goals - Team Attribution**: X% (correct team assignments)
**Shots - Precision**: X% (approximate assessment)
**Shots - Recall**: X% (approximate assessment)

## KEY INSIGHTS
- What our AI does well
- What needs improvement
- Specific recommendations for better accuracy
- Team identification issues (if any)

## FINAL SCORE ASSESSMENT
Based on VEO ground truth and team attribution accuracy:
- Actual final score: [Team A] X - Y [Team B]
- AI detected score: [if different, explain discrepancy]

Be precise with numbers, timestamps, and percentages. Use football knowledge to assess the quality of matches. Focus on actionable insights for improvement."""

    def evaluate_accuracy(self, match_id: str) -> bool:
        """AI-powered accuracy comparison using Gemini 2.5 Pro"""
        print(f"⚖️ AI-Powered Accuracy Evaluation for {match_id}")
        
        data_dir = Path("../outputs") / match_id
        validator_output_path = data_dir / "1.6_validated_timeline.txt"
        veo_truth_path = data_dir / "1_veo_ground_truth.json"
        output_path = data_dir / "1.7_accuracy_comparison.txt"
        
        if not validator_output_path.exists():
            print(f"❌ Validator output not found: {validator_output_path}")
            print("Run Step 1.6 first: python 1.6_goals_shots_validator.py")
            return False
        
        if not veo_truth_path.exists():
            print(f"❌ VEO ground truth not found: {veo_truth_path}")
            print("Run Step 1.1 first: python 1.1_fetch_veo.py")
            return False
        
        # Load team configuration
        team_config = self.load_team_config(match_id)
        print(f"👕 Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}")
        
        # Read our validator output
        with open(validator_output_path, 'r') as f:
            our_analysis = f.read()
        
        # Read VEO ground truth
        with open(veo_truth_path, 'r') as f:
            veo_data = json.load(f)
        
        # Format ground truth for AI analysis
        veo_formatted = json.dumps(veo_data, indent=2)
        
        print(f"🤖 Analyzing with Gemini 2.5 Pro...")
        print(f"📊 Comparing our {len(our_analysis)} character analysis vs {veo_data.get('total_events', 0)} VEO events")
        
        try:
            # Generate AI comparison
            response = self.model.generate_content(
                self.get_comparison_prompt(our_analysis, veo_formatted, team_config)
            )
            
            if not response or not response.text:
                print("❌ No response from Gemini")
                return False
            
            comparison_result = response.text.strip()
            
            # Save detailed comparison
            with open(output_path, 'w') as f:
                f.write(f"# AI-Powered Accuracy Comparison (V3)\n")
                f.write(f"# Match: {match_id}\n")
                f.write(f"# Teams: {team_config['team_a']['name']} vs {team_config['team_b']['name']}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Model: gemini-2.5-pro\n\n")
                f.write(comparison_result)
            
            print(f"✅ AI comparison complete!")
            print(f"📁 Detailed analysis saved to: {output_path}")
            print("\n" + "="*60)
            print("🎯 AI ACCURACY ANALYSIS")
            print("="*60)
            print(comparison_result)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during AI comparison: {str(e)}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 1.7_accuracy_evaluator.py <match-id>")
        print("Example: python 1.7_accuracy_evaluator.py 20250523-match-23-may-2025-3fc1de88")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        evaluator = AccuracyEvaluator()
        success = evaluator.evaluate_accuracy(match_id)
        
        if success:
            print("🎉 Accuracy evaluation completed successfully!")
        else:
            print("❌ Evaluation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()