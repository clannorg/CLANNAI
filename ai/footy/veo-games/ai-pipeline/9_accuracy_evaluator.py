#!/usr/bin/env python3
"""
9. Accuracy Evaluator
AI-powered comparison between our validator results and Veo ground truth
Uses Gemini 2.5 Pro for intelligent analysis
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / '.env')

class AccuracyEvaluator:
    def __init__(self):
        """Initialize the AI-powered accuracy evaluator"""
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🤖 AI-powered accuracy evaluator initialized")

    def get_comparison_prompt(self, our_analysis: str, veo_ground_truth: str) -> str:
        """Create prompt for AI-powered accuracy comparison"""
        return f"""You are an expert football analyst tasked with comparing two sets of match event data for accuracy evaluation.

CONTEXT:
- Our AI pipeline analyzed video clips and produced event detections
- Veo camera system captured ground truth events during the actual match
- Your job is to compare our AI results against the verified ground truth data

VEO GROUND TRUTH DATA (authoritative):
{veo_ground_truth}

OUR AI ANALYSIS RESULTS:
{our_analysis}

COMPARISON TASK:
1. **Goals Analysis**: Compare detected goals vs ground truth goals
   - Match timestamps (allow ±30 second tolerance for timing differences)
   - Identify true positives, false positives, false negatives
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
**Ground Truth**: [list actual goals with timestamps]
**Our AI Detected**: [list our detected goals with timestamps]
**Matches**: [list successful matches with tolerance noted]
**False Positives**: [goals we detected that weren't real]
**False Negatives**: [real goals we missed]

## SHOTS COMPARISON  
**Ground Truth**: [list actual shots with timestamps]
**Our AI Detected**: [list our detected shots with timestamps]
**Assessment**: [brief analysis of shot detection accuracy]

## ACCURACY METRICS
**Goals - Precision**: X% (correct goals / total detected goals)
**Goals - Recall**: X% (correct goals / total actual goals)
**Shots - Precision**: X% (approximate assessment)
**Shots - Recall**: X% (approximate assessment)

## KEY INSIGHTS
- What our AI does well
- What needs improvement
- Specific recommendations

Be precise with numbers, timestamps, and percentages. Use football knowledge to assess the quality of matches."""

    def evaluate_accuracy(self, match_id: str) -> bool:
        """AI-powered accuracy comparison using Gemini 2.5 Pro"""
        print(f"⚖️ AI-Powered Accuracy Evaluation for {match_id}")
        
        data_dir = Path("../data") / match_id
        validator_output_path = data_dir / "validated_timeline.txt"
        veo_truth_path = data_dir / "veo_ground_truth.json"
        
        if not validator_output_path.exists():
            print(f"❌ Validator output not found: {validator_output_path}")
            print("Run Step 6 first: python 6_goals_shots_validator.py")
            return False
        
        if not veo_truth_path.exists():
            print(f"❌ Veo ground truth not found: {veo_truth_path}")
            print("Run Step 1 first: python 1_extract_veo_data.py")
            return False
        
        # Read our validator output
        with open(validator_output_path, 'r') as f:
            our_analysis = f.read()
        
        # Read Veo ground truth
        with open(veo_truth_path, 'r') as f:
            veo_data = json.load(f)
        
        # Format ground truth for AI analysis
        veo_formatted = json.dumps(veo_data, indent=2)
        
        print(f"🤖 Analyzing with Gemini 2.5 Pro...")
        print(f"📊 Comparing our {len(our_analysis)} character analysis vs {veo_data.get('total_events', 0)} Veo events")
        
        try:
            # Generate AI comparison
            response = self.model.generate_content(
                self.get_comparison_prompt(our_analysis, veo_formatted)
            )
            
            if not response or not response.text:
                print("❌ No response from Gemini")
                return False
            
            comparison_result = response.text.strip()
            
            # Save detailed comparison
            comparison_path = data_dir / "ai_accuracy_comparison.txt"
            with open(comparison_path, 'w') as f:
                f.write(f"# AI-Powered Accuracy Comparison\n")
                f.write(f"# Match: {match_id}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Model: gemini-2.0-flash-exp\n\n")
                f.write(comparison_result)
            
            print(f"✅ AI comparison complete!")
            print(f"📁 Detailed analysis saved to: {comparison_path}")
            print("\n" + "="*60)
            print("🎯 AI ACCURACY ANALYSIS")
            print("="*60)
            print(comparison_result)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during AI comparison: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 7_accuracy_evaluator.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    evaluator = AccuracyEvaluator()
    success = evaluator.evaluate_accuracy(match_id)
    
    if success:
        print(f"�� Pipeline Complete! All results in data/{match_id}/")
    else:
        sys.exit(1) 