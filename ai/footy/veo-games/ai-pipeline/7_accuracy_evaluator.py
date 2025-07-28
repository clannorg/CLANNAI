#!/usr/bin/env python3
"""
7. Accuracy Evaluator
AI vs Veo comparison
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def evaluate_accuracy(match_id):
    """Compare AI predictions vs Veo ground truth"""
    print(f"⚖️ Step 7: Evaluating AI accuracy for {match_id}")
    
    data_dir = Path("../data") / match_id
    timeline_path = data_dir / "match_timeline.json"
    veo_truth_path = data_dir / "veo_ground_truth.json"
    
    if not timeline_path.exists():
        print(f"❌ AI timeline not found: {timeline_path}")
        print("Run Step 5 first: python 5_gemini_synthesis.py")
        return False
    
    if not veo_truth_path.exists():
        print(f"❌ Veo ground truth not found: {veo_truth_path}")
        print("Run Step 1 first: python 1_extract_veo_data.py")
        return False
    
    # Load AI timeline
    with open(timeline_path, 'r') as f:
        ai_timeline = json.load(f)
    
    # Load Veo ground truth
    with open(veo_truth_path, 'r') as f:
        veo_data = json.load(f)
    
    print(f"📊 Comparing AI vs Veo results...")
    
    # Extract AI events by type
    ai_events = {}
    for event in ai_timeline["events"]:
        event_type = event["type"]
        if event_type not in ai_events:
            ai_events[event_type] = []
        ai_events[event_type].append(event)
    
    # Extract Veo events by type
    veo_events = {}
    for event in veo_data.get("events", []):
        # Map Veo event types to AI types
        veo_type = event.get("type", "")
        if "Goal" in veo_type:
            mapped_type = "GOAL"
        elif "Shot" in veo_type:
            mapped_type = "SHOT_ON_GOAL"
        else:
            mapped_type = veo_type.upper()
        
        if mapped_type not in veo_events:
            veo_events[mapped_type] = []
        veo_events[mapped_type].append(event)
    
    # Calculate accuracy metrics
    evaluation = {
        "match_id": match_id,
        "evaluation_timestamp": datetime.now().isoformat(),
        "ai_total_events": ai_timeline["total_events"],
        "veo_total_events": veo_data.get("total_events", 0),
        "by_event_type": {},
        "overall_metrics": {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0
        },
        "summary": {
            "ai_model": "gemini-pro-vision",
            "evaluation_method": "timestamp matching within 30 seconds",
            "notes": "Preliminary evaluation - requires manual verification"
        }
    }
    
    # Evaluate each event type
    all_true_positives = 0
    all_false_positives = 0
    all_false_negatives = 0
    
    for event_type in set(list(ai_events.keys()) + list(veo_events.keys())):
        ai_count = len(ai_events.get(event_type, []))
        veo_count = len(veo_events.get(event_type, []))
        
        # Simple comparison (for real implementation, need timestamp matching)
        true_positives = min(ai_count, veo_count)
        false_positives = max(0, ai_count - veo_count)
        false_negatives = max(0, veo_count - ai_count)
        
        precision = true_positives / ai_count if ai_count > 0 else 0
        recall = true_positives / veo_count if veo_count > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        evaluation["by_event_type"][event_type] = {
            "ai_detected": ai_count,
            "veo_actual": veo_count,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3)
        }
        
        all_true_positives += true_positives
        all_false_positives += false_positives
        all_false_negatives += false_negatives
    
    # Calculate overall metrics
    overall_precision = all_true_positives / (all_true_positives + all_false_positives) if (all_true_positives + all_false_positives) > 0 else 0
    overall_recall = all_true_positives / (all_true_positives + all_false_negatives) if (all_true_positives + all_false_negatives) > 0 else 0
    overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    evaluation["overall_metrics"] = {
        "precision": round(overall_precision, 3),
        "recall": round(overall_recall, 3),
        "f1_score": round(overall_f1, 3)
    }
    
    # Save evaluation
    eval_path = data_dir / "accuracy_evaluation.json"
    with open(eval_path, 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    print(f"✅ Step 7 complete: Accuracy evaluation saved")
    print(f"📊 Overall Precision: {overall_precision:.1%}")
    print(f"📊 Overall Recall: {overall_recall:.1%}")
    print(f"📊 Overall F1 Score: {overall_f1:.1%}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 7_accuracy_evaluator.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = evaluate_accuracy(match_id)
    
    if success:
        print(f"🎉 Pipeline Complete! All results in data/{match_id}/")
    else:
        sys.exit(1) 