#!/usr/bin/env python3
"""
Basketball Analysis Accuracy Evaluation
Compares manually annotated shot data with AI-generated events timeline
"""

import pandas as pd
import re
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Tuple, Set
# import matplotlib.pyplot as plt
# import seaborn as sns

class BasketballAccuracyEvaluator:
    def __init__(self):
        self.manual_shots = None
        self.ai_events = None
        self.matched_events = []
        self.unmatched_manual = []
        self.unmatched_ai = []
        
    def load_manual_shots(self, csv_path: str) -> pd.DataFrame:
        """Load manually annotated shot data"""
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} manual shot annotations")
        print(f"   Time range: {df['shot_time_seconds'].min():.1f}s - {df['shot_time_seconds'].max():.1f}s")
        return df
    
    def load_ai_events(self, timeline_path: str) -> List[Dict]:
        """Load AI-generated events timeline"""
        events = []
        
        with open(timeline_path, 'r') as f:
            content = f.read()
        
        # Extract events from timeline
        lines = content.split('\n')
        for line in lines:
            # Match lines like " 1. 00:005.9 - Player_86 (White jersey #86) takes a jump shot – MISSED [LEFT BASKET]"
            if re.match(r'^\s*\d+\.\s+\d{2}:\d{2}', line):
                # Parse event line
                parts = line.strip().split(' - ')
                if len(parts) >= 2:
                    time_part = parts[0]
                    event_part = ' - '.join(parts[1:])
                    
                    # Extract timestamp (format: MM:SSS.S)
                    time_match = re.search(r'(\d{2}):(\d{3})\.(\d+)', time_part)
                    if time_match:
                        minutes = int(time_match.group(1))
                        seconds = int(time_match.group(2))
                        tenths = int(time_match.group(3))
                        total_seconds = minutes * 60 + seconds + tenths / 10
                        
                        # Determine if it's a shot event
                        is_shot = any(keyword in event_part.lower() for keyword in 
                                     ['shot', 'jump shot', 'layup', 'free throw'])
                        
                        # Extract shot outcome
                        shot_made = 'MADE' in event_part.upper()
                        shot_missed = 'MISSED' in event_part.upper()
                        
                        # Determine if bystander
                        is_bystander = 'bystander' in event_part.lower() or 'gray shirt' in event_part.lower()
                        
                        events.append({
                            'timestamp': total_seconds,
                            'time_readable': f"{minutes:02d}:{seconds:02d}",
                            'event_text': event_part,
                            'is_shot': is_shot,
                            'shot_made': shot_made,
                            'shot_missed': shot_missed,
                            'is_bystander': is_bystander,
                            'basket_side': 'LEFT' if 'LEFT BASKET' in event_part else 'RIGHT' if 'RIGHT BASKET' in event_part else 'UNKNOWN'
                        })
        
        print(f"🤖 Loaded {len(events)} AI-generated events")
        print(f"   Shots detected: {sum(1 for e in events if e['is_shot'])}")
        return events
    
    def match_events(self, tolerance_seconds: float = 3.0) -> Dict:
        """Match manual shots with AI events within time tolerance"""
        manual_shots = self.manual_shots
        ai_events = self.ai_events
        
        matched = []
        unmatched_manual = []
        unmatched_ai = []
        
        # Create sets to track matched events
        matched_manual_indices = set()
        matched_ai_indices = set()
        
        # Match shots with events
        for i, manual_shot in manual_shots.iterrows():
            manual_time = manual_shot['shot_time_seconds']
            best_match = None
            best_distance = float('inf')
            
            for j, ai_event in enumerate(ai_events):
                if j in matched_ai_indices:
                    continue
                    
                if ai_event['is_shot']:
                    time_distance = abs(manual_time - ai_event['timestamp'])
                    if time_distance <= tolerance_seconds:
                        if time_distance < best_distance:
                            best_distance = time_distance
                            best_match = (j, ai_event)
            
            if best_match:
                ai_idx, ai_event = best_match
                matched.append({
                    'manual_shot': manual_shot.to_dict(),
                    'ai_event': ai_event,
                    'time_distance': best_distance,
                    'accuracy_score': self.calculate_accuracy_score(manual_shot, ai_event)
                })
                matched_manual_indices.add(i)
                matched_ai_indices.add(ai_idx)
            else:
                unmatched_manual.append(manual_shot.to_dict())
        
        # Find unmatched AI events
        for j, ai_event in enumerate(ai_events):
            if j not in matched_ai_indices and ai_event['is_shot']:
                unmatched_ai.append(ai_event)
        
        self.matched_events = matched
        self.unmatched_manual = unmatched_manual
        self.unmatched_ai = unmatched_ai
        
        return {
            'matched': matched,
            'unmatched_manual': unmatched_manual,
            'unmatched_ai': unmatched_ai
        }
    
    def calculate_accuracy_score(self, manual_shot: pd.Series, ai_event: Dict) -> Dict:
        """Calculate accuracy metrics for a matched shot"""
        # Time accuracy
        time_accuracy = 1.0 - min(abs(manual_shot['shot_time_seconds'] - ai_event['timestamp']) / 10.0, 1.0)
        
        # Shot outcome accuracy
        manual_made = manual_shot['shot_made']
        ai_made = ai_event['shot_made']
        outcome_accuracy = 1.0 if manual_made == ai_made else 0.0
        
        # Bystander detection accuracy
        manual_bystander = manual_shot['is_bystander']
        ai_bystander = ai_event['is_bystander']
        bystander_accuracy = 1.0 if manual_bystander == ai_bystander else 0.0
        
        # Overall accuracy
        overall_accuracy = (time_accuracy + outcome_accuracy + bystander_accuracy) / 3
        
        return {
            'time_accuracy': time_accuracy,
            'outcome_accuracy': outcome_accuracy,
            'bystander_accuracy': bystander_accuracy,
            'overall_accuracy': overall_accuracy
        }
    
    def generate_accuracy_report(self) -> Dict:
        """Generate comprehensive accuracy report"""
        if not self.matched_events:
            return {"error": "No matched events found. Run match_events() first."}
        
        total_manual = len(self.manual_shots)
        total_ai_shots = sum(1 for e in self.ai_events if e['is_shot'])
        total_matched = len(self.matched_events)
        
        # Calculate metrics
        detection_rate = total_matched / total_manual if total_manual > 0 else 0
        precision = total_matched / total_ai_shots if total_ai_shots > 0 else 0
        false_positive_rate = len(self.unmatched_ai) / total_ai_shots if total_ai_shots > 0 else 0
        false_negative_rate = len(self.unmatched_manual) / total_manual if total_manual > 0 else 0
        
        # Average accuracy scores
        avg_time_accuracy = sum(m['accuracy_score']['time_accuracy'] for m in self.matched_events) / len(self.matched_events)
        avg_outcome_accuracy = sum(m['accuracy_score']['outcome_accuracy'] for m in self.matched_events) / len(self.matched_events)
        avg_bystander_accuracy = sum(m['accuracy_score']['bystander_accuracy'] for m in self.matched_events) / len(self.matched_events)
        avg_overall_accuracy = sum(m['accuracy_score']['overall_accuracy'] for m in self.matched_events) / len(self.matched_events)
        
        return {
            'summary': {
                'total_manual_shots': total_manual,
                'total_ai_shots': total_ai_shots,
                'matched_shots': total_matched,
                'unmatched_manual': len(self.unmatched_manual),
                'unmatched_ai': len(self.unmatched_ai)
            },
            'metrics': {
                'detection_rate': detection_rate,
                'precision': precision,
                'false_positive_rate': false_positive_rate,
                'false_negative_rate': false_negative_rate,
                'f1_score': 2 * (precision * detection_rate) / (precision + detection_rate) if (precision + detection_rate) > 0 else 0
            },
            'accuracy_scores': {
                'avg_time_accuracy': avg_time_accuracy,
                'avg_outcome_accuracy': avg_outcome_accuracy,
                'avg_bystander_accuracy': avg_bystander_accuracy,
                'avg_overall_accuracy': avg_overall_accuracy
            },
            'matched_events': self.matched_events,
            'unmatched_manual': self.unmatched_manual,
            'unmatched_ai': self.unmatched_ai
        }
    
    def print_accuracy_report(self, report: Dict):
        """Print formatted accuracy report"""
        if 'error' in report:
            print(f"❌ {report['error']}")
            return
        
        print("🏀 BASKETBALL ANALYSIS ACCURACY REPORT")
        print("=" * 50)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Summary
        summary = report['summary']
        print("📊 SUMMARY")
        print("-" * 30)
        print(f"🎯 Manual shots annotated: {summary['total_manual_shots']}")
        print(f"🤖 AI shots detected: {summary['total_ai_shots']}")
        print(f"✅ Successfully matched: {summary['matched_shots']}")
        print(f"❌ Unmatched manual: {summary['unmatched_manual']}")
        print(f"❌ Unmatched AI: {summary['unmatched_ai']}")
        print()
        
        # Metrics
        metrics = report['metrics']
        print("📈 ACCURACY METRICS")
        print("-" * 30)
        print(f"🎯 Detection Rate: {metrics['detection_rate']:.1%}")
        print(f"🎯 Precision: {metrics['precision']:.1%}")
        print(f"🎯 F1 Score: {metrics['f1_score']:.1%}")
        print(f"❌ False Positive Rate: {metrics['false_positive_rate']:.1%}")
        print(f"❌ False Negative Rate: {metrics['false_negative_rate']:.1%}")
        print()
        
        # Accuracy Scores
        scores = report['accuracy_scores']
        print("🎯 DETAILED ACCURACY SCORES")
        print("-" * 30)
        print(f"⏰ Time Accuracy: {scores['avg_time_accuracy']:.1%}")
        print(f"🎯 Shot Outcome Accuracy: {scores['avg_outcome_accuracy']:.1%}")
        print(f"👥 Bystander Detection: {scores['avg_bystander_accuracy']:.1%}")
        print(f"📊 Overall Accuracy: {scores['avg_overall_accuracy']:.1%}")
        print()
        
        # Performance Assessment
        print("📋 PERFORMANCE ASSESSMENT")
        print("-" * 30)
        if metrics['f1_score'] >= 0.9:
            print("🟢 EXCELLENT: System performs very well")
        elif metrics['f1_score'] >= 0.8:
            print("🟡 GOOD: System performs well with room for improvement")
        elif metrics['f1_score'] >= 0.7:
            print("🟠 FAIR: System needs some improvements")
        else:
            print("🔴 POOR: System needs significant improvements")
        
        print(f"💡 Recommendation: Focus on {'false positives' if metrics['false_positive_rate'] > metrics['false_negative_rate'] else 'false negatives'}")
    
    def save_detailed_report(self, report: Dict, output_path: str):
        """Save detailed accuracy report to JSON"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📁 Detailed report saved to: {output_path}")

def main():
    """Run accuracy evaluation"""
    print("🏀 Basketball Analysis Accuracy Evaluation")
    print("=" * 50)
    print()
    
    # Initialize evaluator
    evaluator = BasketballAccuracyEvaluator()
    
    # Load data
    manual_csv = "1.5_accuracy_eval/all_shots_20250716_143950.csv"
    ai_timeline = "1_game_events/synthesis_output/events_timeline.txt"
    
    print("📊 Loading data...")
    evaluator.manual_shots = evaluator.load_manual_shots(manual_csv)
    evaluator.ai_events = evaluator.load_ai_events(ai_timeline)
    print()
    
    # Match events
    print("🔍 Matching manual shots with AI events...")
    match_results = evaluator.match_events(tolerance_seconds=3.0)
    print(f"✅ Matched {len(match_results['matched'])} events")
    print()
    
    # Generate and print report
    print("📈 Generating accuracy report...")
    report = evaluator.generate_accuracy_report()
    evaluator.print_accuracy_report(report)
    
    # Save detailed report
    output_path = "1.5_accuracy_eval/accuracy_report.json"
    evaluator.save_detailed_report(report, output_path)
    
    print("\n✅ Accuracy evaluation complete!")

if __name__ == "__main__":
    main() 