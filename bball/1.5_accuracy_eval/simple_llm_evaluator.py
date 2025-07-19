#!/usr/bin/env python3
"""
Simple LLM Basketball Accuracy Evaluation
Passes CSV and timeline files directly to Gemini 2.5
"""

import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SimpleLLMEvaluator:
    def __init__(self):
        """Initialize with Gemini 2.5"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def load_files_as_text(self, csv_path: str, timeline_path: str) -> tuple:
        """Load both files as plain text"""
        # Load CSV as text
        with open(csv_path, 'r') as f:
            csv_content = f.read()
        
        # Load timeline as text
        with open(timeline_path, 'r') as f:
            timeline_content = f.read()
        
        return csv_content, timeline_content
    
    def create_simple_prompt(self, csv_content: str, timeline_content: str) -> str:
        """Create simple evaluation prompt"""
        return f"""
🏀 BASKETBALL SHOT ACCURACY EVALUATION
========================================

I have two files from the same basketball game:

1. **MANUAL ANNOTATIONS (CSV):**
```
{csv_content}
```

2. **AI-GENERATED EVENTS (TIMELINE):**
```
{timeline_content}
```

TASK: Compare these two datasets and evaluate the AI system's accuracy.

REQUIREMENTS:
- Match shots between the datasets (allow ±5 seconds time difference)
- Calculate detection rate, precision, and accuracy metrics
- Identify strengths and weaknesses of the AI system
- Provide specific examples of matches and mismatches

OUTPUT FORMAT (JSON):
{{
  "summary": {{
    "total_manual_shots": 107,
    "total_ai_shots": 85,
    "matched_shots": 78,
    "unmatched_manual": 29,
    "unmatched_ai": 7
  }},
  "metrics": {{
    "detection_rate": 0.73,
    "precision": 0.92,
    "shot_outcome_accuracy": 0.85,
    "bystander_detection_accuracy": 0.78,
    "overall_accuracy": 0.82
  }},
  "sample_matches": [
    {{
      "manual": "01:12 - MADE (bystander)",
      "ai": "01:13.2 - Bystander takes jump shot - MADE",
      "time_diff": 1.2,
      "match_quality": "excellent"
    }}
  ],
  "analysis": {{
    "strengths": ["Good at detecting made shots"],
    "weaknesses": ["Misses some bystander shots"],
    "recommendations": ["Improve bystander detection"]
  }}
}}

Be thorough but realistic in your assessment. If you can't find a good match, don't force one.
"""

    def evaluate_accuracy(self, csv_path: str, timeline_path: str) -> dict:
        """Run simple LLM evaluation"""
        print("🏀 Loading files for LLM evaluation...")
        
        # Load files as text
        csv_content, timeline_content = self.load_files_as_text(csv_path, timeline_path)
        
        print(f"📊 CSV file: {len(csv_content)} characters")
        print(f"🤖 Timeline file: {len(timeline_content)} characters")
        
        # Create prompt
        prompt = self.create_simple_prompt(csv_content, timeline_content)
        
        print("\n🤖 Sending to Gemini 2.5 for evaluation...")
        print("⏳ This may take a minute...")
        
        try:
            # Call Gemini 2.5
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            print("✅ Received LLM response")
            
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    result = json.loads(json_str)
                    return result
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing JSON: {e}")
                    print("📄 Raw response:")
                    print(response_text)
                    return {"error": "Failed to parse LLM response", "raw_response": response_text}
            else:
                print("❌ No JSON found in response")
                print("📄 Raw response:")
                print(response_text)
                return {"error": "No JSON in response", "raw_response": response_text}
                
        except Exception as e:
            print(f"❌ Error calling Gemini API: {e}")
            return {"error": str(e)}
    
    def print_report(self, report: dict):
        """Print formatted report"""
        if 'error' in report:
            print(f"❌ LLM Evaluation Error: {report['error']}")
            if 'raw_response' in report:
                print("\n📄 Raw LLM Response:")
                print(report['raw_response'])
            return
        
        print("🏀 LLM ACCURACY EVALUATION REPORT")
        print("=" * 50)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Summary
        if 'summary' in report:
            summary = report['summary']
            print("📊 SUMMARY")
            print("-" * 30)
            print(f"🎯 Manual shots: {summary.get('total_manual_shots', 'N/A')}")
            print(f"🤖 AI shots detected: {summary.get('total_ai_shots', 'N/A')}")
            print(f"✅ Matched shots: {summary.get('matched_shots', 'N/A')}")
            print(f"❌ Unmatched manual: {summary.get('unmatched_manual', 'N/A')}")
            print(f"❌ Unmatched AI: {summary.get('unmatched_ai', 'N/A')}")
            print()
        
        # Metrics
        if 'metrics' in report:
            metrics = report['metrics']
            print("📈 ACCURACY METRICS")
            print("-" * 30)
            print(f"🎯 Detection Rate: {metrics.get('detection_rate', 0):.1%}")
            print(f"🎯 Precision: {metrics.get('precision', 0):.1%}")
            print(f"🎯 Shot Outcome Accuracy: {metrics.get('shot_outcome_accuracy', 0):.1%}")
            print(f"👥 Bystander Detection: {metrics.get('bystander_detection_accuracy', 0):.1%}")
            print(f"📊 Overall Accuracy: {metrics.get('overall_accuracy', 0):.1%}")
            print()
        
        # Sample matches
        if 'sample_matches' in report and report['sample_matches']:
            print("🔗 SAMPLE MATCHES")
            print("-" * 30)
            for i, match in enumerate(report['sample_matches'][:5], 1):
                print(f"{i}. Manual: {match.get('manual', 'N/A')}")
                print(f"   AI: {match.get('ai', 'N/A')}")
                print(f"   Time diff: {match.get('time_diff', 'N/A')}s")
                print(f"   Quality: {match.get('match_quality', 'N/A')}")
                print()
        
        # Analysis
        if 'analysis' in report:
            analysis = report['analysis']
            print("💡 LLM ANALYSIS")
            print("-" * 30)
            
            if 'strengths' in analysis:
                print("✅ Strengths:")
                for strength in analysis['strengths']:
                    print(f"   • {strength}")
                print()
            
            if 'weaknesses' in analysis:
                print("❌ Weaknesses:")
                for weakness in analysis['weaknesses']:
                    print(f"   • {weakness}")
                print()
            
            if 'recommendations' in analysis:
                print("💡 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"   • {rec}")
                print()
    
    def save_report(self, report: dict, output_path: str):
        """Save evaluation report"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📁 Report saved to: {output_path}")

def main():
    """Run simple LLM evaluation"""
    print("🏀 Simple LLM Basketball Accuracy Evaluation")
    print("=" * 50)
    print("🤖 Passing files directly to Gemini 2.5")
    print()
    
    # Initialize evaluator
    evaluator = SimpleLLMEvaluator()
    
    # File paths
    csv_path = "1.5_accuracy_eval/all_shots_20250716_143950.csv"
    timeline_path = "1_game_events/synthesis_output/events_timeline.txt"
    
    # Run evaluation
    print("🚀 Starting evaluation...")
    report = evaluator.evaluate_accuracy(csv_path, timeline_path)
    
    # Print and save results
    evaluator.print_report(report)
    evaluator.save_report(report, "1.5_accuracy_eval/simple_llm_report.json")
    
    print("\n✅ Simple LLM evaluation complete!")

if __name__ == "__main__":
    main() 