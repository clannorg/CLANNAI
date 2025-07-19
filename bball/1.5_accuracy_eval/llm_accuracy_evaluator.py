#!/usr/bin/env python3
"""
LLM-Based Basketball Accuracy Evaluation
Uses Gemini 2.5 to compare manually annotated shots with AI-generated events
"""

import pandas as pd
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class LLMAccuracyEvaluator:
    def __init__(self):
        """Initialize with Gemini 2.5"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def load_manual_shots(self, csv_path: str) -> str:
        """Load and format manual shots for LLM"""
        df = pd.read_csv(csv_path)
        
        # Format manual shots for LLM
        manual_data = "MANUAL SHOT ANNOTATIONS:\n"
        manual_data += "=" * 50 + "\n"
        manual_data += f"Total shots: {len(df)}\n"
        manual_data += f"Time range: {df['shot_time_seconds'].min():.1f}s - {df['shot_time_seconds'].max():.1f}s\n\n"
        
        for idx, row in df.iterrows():
            time_readable = row['shot_time_readable']
            time_seconds = row['shot_time_seconds']
            is_bystander = "YES" if row['is_bystander'] else "NO"
            shot_made = "MADE" if row['shot_made'] else "MISSED"
            
            manual_data += f"{idx+1}. {time_readable} ({time_seconds:.1f}s) - "
            manual_data += f"Bystander: {is_bystander}, Outcome: {shot_made}\n"
        
        return manual_data
    
    def load_ai_events(self, timeline_path: str) -> str:
        """Load and format AI events for LLM"""
        with open(timeline_path, 'r') as f:
            content = f.read()
        
        # Extract shot events from timeline
        lines = content.split('\n')
        shot_events = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['shot', 'jump shot', 'layup', 'free throw']):
                # Clean up the line
                line = line.strip()
                if line and not line.startswith('=') and not line.startswith('🏀'):
                    shot_events.append(line)
        
        ai_data = "AI-GENERATED SHOT EVENTS:\n"
        ai_data += "=" * 50 + "\n"
        ai_data += f"Total shot events: {len(shot_events)}\n\n"
        
        for i, event in enumerate(shot_events, 1):
            ai_data += f"{i}. {event}\n"
        
        return ai_data
    
    def create_evaluation_prompt(self, manual_data: str, ai_data: str) -> str:
        """Create comprehensive evaluation prompt for Gemini 2.5"""
        return f"""
🏀 BASKETBALL SHOT ACCURACY EVALUATION
========================================

I have two datasets from the same basketball game:
1. Manually annotated shots (ground truth)
2. AI-generated shot events (system output)

Please compare these datasets and evaluate the AI system's accuracy.

{manual_data}

{ai_data}

EVALUATION TASK:
================

1. **Match shots between datasets** - For each manual shot, find the best matching AI event within ±5 seconds time difference.

2. **Evaluate accuracy metrics:**
   - Detection Rate: How many manual shots were detected by AI?
   - Precision: How many AI-detected shots were real shots?
   - Shot Outcome Accuracy: How well did AI predict MADE vs MISSED?
   - Bystander Detection: How well did AI identify bystander vs player shots?

3. **Provide detailed analysis:**
   - List matched shots with time differences
   - List unmatched manual shots (missed by AI)
   - List unmatched AI events (false positives)
   - Identify patterns in errors

OUTPUT FORMAT:
==============

Please provide your analysis in this JSON format:

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
  "matched_events": [
    {{
      "manual_time": "01:12",
      "manual_outcome": "MISSED",
      "manual_bystander": false,
      "ai_time": "01:13.2",
      "ai_outcome": "MISSED",
      "ai_bystander": false,
      "time_difference": 1.2,
      "outcome_match": true,
      "bystander_match": true
    }}
  ],
  "unmatched_manual": [
    {{
      "time": "02:45",
      "outcome": "MADE",
      "bystander": true,
      "reason": "AI missed this shot"
    }}
  ],
  "unmatched_ai": [
    {{
      "time": "03:12.5",
      "event": "Player takes jump shot - MADE",
      "reason": "False positive - no corresponding manual shot"
    }}
  ],
  "analysis": {{
    "strengths": ["Good at detecting made shots", "Accurate timing"],
    "weaknesses": ["Misses some bystander shots", "Confuses similar players"],
    "recommendations": ["Improve bystander detection", "Better player identification"]
  }}
}}

IMPORTANT:
- Allow ±5 seconds time tolerance for matching
- Consider shot type, outcome, and player/bystander status
- Be thorough but realistic in your assessment
- If you can't find a good match, don't force one
"""

    def evaluate_with_llm(self, manual_csv_path: str, ai_timeline_path: str) -> dict:
        """Run LLM-based accuracy evaluation"""
        print("🏀 Loading data for LLM evaluation...")
        
        # Load and format data
        manual_data = self.load_manual_shots(manual_csv_path)
        ai_data = self.load_ai_events(ai_timeline_path)
        
        # Count shot events from the AI data
        shot_count = ai_data.count('AI-GENERATED SHOT EVENTS:') + ai_data.count('takes a jump shot') + ai_data.count('takes a layup') + ai_data.count('free throw')
        
        print(f"📊 Manual shots: {manual_data.count('Bystander:')} total")
        print(f"🤖 AI events: {shot_count} shot events found")
        
        # Create prompt
        prompt = self.create_evaluation_prompt(manual_data, ai_data)
        
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
    
    def print_llm_report(self, report: dict):
        """Print formatted LLM accuracy report"""
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
        
        # Sample matches
        if 'matched_events' in report and report['matched_events']:
            print("🔗 SAMPLE MATCHED EVENTS")
            print("-" * 30)
            for i, match in enumerate(report['matched_events'][:5], 1):
                print(f"{i}. Manual: {match.get('manual_time', 'N/A')} ({match.get('manual_outcome', 'N/A')})")
                print(f"   AI: {match.get('ai_time', 'N/A')} ({match.get('ai_outcome', 'N/A')})")
                print(f"   Time diff: {match.get('time_difference', 'N/A')}s")
                print(f"   Match: {'✅' if match.get('outcome_match') else '❌'} outcome, {'✅' if match.get('bystander_match') else '❌'} bystander")
                print()
    
    def save_llm_report(self, report: dict, output_path: str):
        """Save LLM evaluation report"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📁 LLM report saved to: {output_path}")

def main():
    """Run LLM-based accuracy evaluation"""
    print("🏀 LLM Basketball Accuracy Evaluation")
    print("=" * 50)
    print("🤖 Using Gemini 2.5 for intelligent shot matching")
    print()
    
    # Initialize evaluator
    evaluator = LLMAccuracyEvaluator()
    
    # File paths
    manual_csv = "1.5_accuracy_eval/all_shots_20250716_143950.csv"
    ai_timeline = "1_game_events/synthesis_output/events_timeline.txt"
    
    # Run evaluation
    print("🚀 Starting LLM evaluation...")
    report = evaluator.evaluate_with_llm(manual_csv, ai_timeline)
    
    # Print and save results
    evaluator.print_llm_report(report)
    evaluator.save_llm_report(report, "1.5_accuracy_eval/llm_accuracy_report.json")
    
    print("\n✅ LLM accuracy evaluation complete!")

if __name__ == "__main__":
    main() 