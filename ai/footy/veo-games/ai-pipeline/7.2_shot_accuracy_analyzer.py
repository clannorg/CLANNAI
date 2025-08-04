#!/usr/bin/env python3
"""
7.2 Shot Accuracy Analyzer
Comprehensive Gemini-powered comparison of our AI shot detection vs VEO ground truth
Provides detailed precision, recall, and shot-by-shot analysis
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

class ShotAccuracyAnalyzer:
    def __init__(self):
        """Initialize with Gemini for intelligent shot comparison"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🎯 Shot Accuracy Analyzer initialized with Gemini AI")

    def get_shot_comparison_prompt(self, veo_shots: str, ai_timeline: str) -> str:
        """Create prompt for comprehensive shot accuracy analysis"""
        return f"""You are an expert football analyst comparing shot detection accuracy. 

VEO GROUND TRUTH SHOTS (Authoritative - these definitely happened):
{veo_shots}

OUR AI SYSTEM TIMELINE (Contains our detected shots with descriptions):
{ai_timeline}

TASK: Comprehensive shot detection analysis with the following output format:

## SHOT-BY-SHOT COMPARISON

### VEO SHOTS ANALYSIS
For each VEO shot, determine if our AI detected it:

**VEO Shot 1: [timestamp]**
- VEO Details: [team, time, etc.]
- AI Match: [FOUND/MISSED] - [our timestamp if found, explanation]
- Match Quality: [EXACT/CLOSE/POOR/NONE]
- Confidence: [HIGH/MEDIUM/LOW]

[Repeat for all VEO shots]

### OUR AI FALSE POSITIVES
List shots our AI detected that don't match any VEO shot:
- [timestamp]: [description] - No VEO match

## ACCURACY METRICS
**Total VEO Shots**: [number]
**AI Shots Detected**: [number] 
**True Positives**: [number] (AI shots that match VEO)
**False Positives**: [number] (AI shots with no VEO match)
**False Negatives**: [number] (VEO shots our AI missed)

**Precision**: [TP/(TP+FP)] = [percentage]
**Recall**: [TP/(TP+FN)] = [percentage]
**F1 Score**: [2*Precision*Recall/(Precision+Recall)] = [percentage]

## DETAILED ANALYSIS
**Our AI Strengths**: What types of shots we detect well
**Our AI Weaknesses**: What types of shots we miss or over-detect
**Timing Accuracy**: How close our timestamps are to VEO
**Common Patterns**: Why false positives occur

Use ±30 second tolerance for matching. Be precise with all calculations."""

    def analyze_shot_accuracy(self, match_id: str) -> bool:
        """Comprehensive shot accuracy analysis using Gemini"""
        print(f"🎯 Analyzing shot accuracy for {match_id}")
        
        data_dir = Path("../data") / match_id
        veo_truth_path = data_dir / "1_veo_ground_truth.json"
        ai_timeline_path = data_dir / "6_validated_timeline.txt"
        output_path = data_dir / "7.2_shot_accuracy_analysis.txt"
        
        # Check input files
        if not veo_truth_path.exists():
            print(f"❌ VEO ground truth not found: {veo_truth_path}")
            return False
            
        if not ai_timeline_path.exists():
            print(f"❌ AI timeline not found: {ai_timeline_path}")
            return False
        
        # Read VEO ground truth
        print("📥 Reading VEO ground truth...")
        with open(veo_truth_path, 'r', encoding='utf-8') as f:
            veo_data = json.load(f)
        
        # Extract VEO shots
        veo_shots = []
        for event in veo_data.get('events', []):
            if event.get('labels', {}).get('Event') == 'Shot on goal':
                timestamp = event.get('start_time', '')
                team = event.get('labels', {}).get('Team', 'Unknown')
                veo_shots.append(f"Shot at {timestamp} by {team}")
        
        veo_shots_text = "\n".join([f"{i+1}. {shot}" for i, shot in enumerate(veo_shots)])
        
        # Read AI timeline
        print("📥 Reading AI timeline...")
        with open(ai_timeline_path, 'r', encoding='utf-8') as f:
            ai_timeline = f.read()
        
        print(f"📊 Found {len(veo_shots)} VEO shots to analyze")
        print("🧠 Performing comprehensive analysis with Gemini...")
        
        # Get Gemini analysis
        try:
            prompt = self.get_shot_comparison_prompt(veo_shots_text, ai_timeline)
            response = self.model.generate_content(prompt)
            analysis_result = response.text
            
            # Save results
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Shot Accuracy Analysis\n")
                f.write(f"# Match: {match_id}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Model: gemini-2.0-flash-exp\n\n")
                f.write(analysis_result)
            
            print(f"✅ Shot accuracy analysis saved to: {output_path}")
            
            # Print key metrics
            if "Precision:" in analysis_result and "Recall:" in analysis_result:
                lines = analysis_result.split('\n')
                for line in lines:
                    if 'Precision:' in line or 'Recall:' in line or 'F1 Score:' in line:
                        print(f"📊 {line.strip()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False

def main():
    """Main execution function"""
    if len(sys.argv) != 2:
        print("Usage: python 7.2_shot_accuracy_analyzer.py <match_id>")
        print("Example: python 7.2_shot_accuracy_analyzer.py 19-20250419")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        analyzer = ShotAccuracyAnalyzer()
        success = analyzer.analyze_shot_accuracy(match_id)
        
        if success:
            print(f"🎯 Shot accuracy analysis completed for {match_id}!")
            print(f"📝 Check the detailed analysis in data/{match_id}/7.2_shot_accuracy_analysis.txt")
        else:
            print(f"❌ Shot accuracy analysis failed for {match_id}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()