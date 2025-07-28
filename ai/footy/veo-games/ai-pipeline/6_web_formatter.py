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
    timeline_path = data_dir / "match_timeline.json"
    source_path = data_dir / "source.json"
    
    if not timeline_path.exists():
        print(f"❌ Match timeline not found: {timeline_path}")
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
    
    # Create web-formatted data
    web_data = {
        "match_id": match_id,
        "url": source_data.get("url", ""),
        "generated_at": datetime.now().isoformat(),
        "match_stats": {
            "total_ai_events": timeline["total_events"],
            "total_veo_events": source_data.get("total_events", 0),
            "average_ai_confidence": timeline["average_confidence"],
            "clips_analyzed": timeline["gemini_summary"]["clips_analyzed"]
        },
        "event_summary": {
            "goals": timeline["event_types"].get("GOAL", 0),
            "shots_on_goal": timeline["event_types"].get("SHOT_ON_GOAL", 0),
            "saves": timeline["event_types"].get("SAVE", 0),
            "corners": timeline["event_types"].get("CORNER", 0),
            "fouls": timeline["event_types"].get("FOUL", 0)
        },
        "timeline": [],
        "key_moments": [],
        "ai_insights": {
            "model_used": "gemini-pro-vision",
            "processing_method": "15-second clip analysis with synthesis",
            "confidence_threshold": 0.5
        }
    }
    
    # Format timeline events for web
    for event in timeline["events"]:
        web_event = {
            "timestamp": event["timestamp"],
            "type": event["type"],
            "confidence": round(event["confidence"], 2),
            "description": event.get("description", ""),
            "is_key_moment": event["confidence"] > 0.8
        }
        
        web_data["timeline"].append(web_event)
        
        # Add to key moments if high confidence
        if event["confidence"] > 0.8:
            web_data["key_moments"].append(web_event)
    
    # Sort key moments by confidence
    web_data["key_moments"].sort(key=lambda x: x["confidence"], reverse=True)
    
    # Limit key moments to top 10
    web_data["key_moments"] = web_data["key_moments"][:10]
    
    # Save web-formatted data
    web_path = data_dir / "web_format.json"
    with open(web_path, 'w') as f:
        json.dump(web_data, f, indent=2)
    
    print(f"✅ Step 6 complete: Web JSON saved to {web_path}")
    print(f"📊 {len(web_data['timeline'])} events, {len(web_data['key_moments'])} key moments")
    
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