#!/usr/bin/env python3
"""
6. Web Formatter
Converts timeline to website JSON
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def format_for_web(match_id):
    """Format match timeline for website consumption"""
    print(f"🌐 Step 6: Formatting web JSON for {match_id}")
    
    data_dir = Path("../data") / match_id
    timeline_path = data_dir / "intelligent_match_timeline.json"
    source_path = data_dir / "source.json"
    
    if not timeline_path.exists():
        print(f"❌ Intelligent match timeline not found: {timeline_path}")
        print("Run Step 5 first: python 5_gemini_synthesis.py")
        return False
    
    # Load match timeline
    with open(timeline_path, 'r') as f:
        timeline = json.load(f)
    
    # Load source metadata
    source_data = {}
    if source_path.exists():
        with open(source_path, 'r') as f:
            source_data = json.load(f)
    
    # Extract intelligent analysis
    analysis = timeline.get("intelligent_analysis", {})
    goals = analysis.get("goals_detected", [])
    key_events = analysis.get("key_events", [])
    match_summary = analysis.get("match_summary", {})
    
    # Create web-formatted data with coaching insights
    web_data = {
        "match_id": match_id,
        "url": source_data.get("url", ""),
        "generated_at": datetime.now().isoformat(),
        "coaching_insights": {
            "analysis_method": "Coaching-Focused AI Vision + Kickoff Validation",
            "model_used": "gemini-2.0-flash-exp + gemini-2.5-pro synthesis",
            "clips_analyzed": timeline.get("clips_analyzed", 0),
            "processing_time": round(timeline.get("processing_time_seconds", 0), 1)
        },
        "match_stats": {
            "total_goals_detected": len(goals),
            "total_key_events": len(key_events),
            "match_summary": match_summary
        },
        "goals": [],
        "key_events": [],
        "timeline": []
    }
    
    # Format goals with coaching details
    for goal in goals:
        web_goal = {
            "timestamp": goal["timestamp"],
            "team": goal["scoring_team"],
            "description": goal["description"],
            "confidence": goal["confidence"],
            "evidence": goal.get("evidence", ""),
            "source_clips": goal.get("source_clips", [])
        }
        web_data["goals"].append(web_goal)
    
    # Format key events for coaching insights
    for event in key_events:
        web_event = {
            "timestamp": event["timestamp"],
            "type": event["type"],
            "description": event["description"],
            "confidence": event["confidence"]
        }
        web_data["key_events"].append(web_event)
        
        # Also add to timeline
        web_data["timeline"].append(web_event)
    
    # Add goals to timeline as well
    for goal in goals:
        timeline_event = {
            "timestamp": goal["timestamp"],
            "type": "GOAL",
            "description": goal["description"],
            "confidence": goal["confidence"]
        }
        web_data["timeline"].append(timeline_event)
    
    # Sort timeline by timestamp
    web_data["timeline"].sort(key=lambda x: x["timestamp"])
    
    # Limit key events to top 10 by confidence if available
    if len(web_data["key_events"]) > 10:
        web_data["key_events"] = sorted(web_data["key_events"], 
                                      key=lambda x: x.get("confidence", "HIGH"), 
                                      reverse=True)[:10]
    
    # Save web-formatted data
    web_path = data_dir / "web_format.json"
    with open(web_path, 'w') as f:
        json.dump(web_data, f, indent=2)
    
    print(f"✅ Step 6 complete: Web JSON saved to {web_path}")
    print(f"📊 {len(web_data['timeline'])} timeline events, {len(web_data['key_events'])} key events, {len(web_data['goals'])} goals")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 6_web_formatter.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = format_for_web(match_id)
    
    if success:
        print(f"🎯 Ready for Step 7: Accuracy evaluation")
    else:
        sys.exit(1) 