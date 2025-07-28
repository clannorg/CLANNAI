#!/usr/bin/env python3
"""
5. Gemini Synthesis
Combines all clip analyses into one match timeline
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def synthesize_match(match_id):
    """Synthesize all clip analyses into match timeline"""
    print(f"🔄 Step 5: Synthesizing match timeline for {match_id}")
    
    data_dir = Path("../data") / match_id
    analyses_dir = data_dir / "clip_analyses"
    
    if not analyses_dir.exists():
        print(f"❌ Clip analyses not found: {analyses_dir}")
        print("Run Step 4 first: python 4_gemini_clip_analyzer.py")
        return False
    
    # Collect all clip analyses
    analysis_files = list(analyses_dir.glob("*_analysis.json"))
    if not analysis_files:
        print(f"❌ No analysis files found in {analyses_dir}")
        return False
    
    print(f"📊 Synthesizing {len(analysis_files)} clip analyses...")
    
    all_events = []
    total_confidence = 0
    events_with_confidence = 0
    
    for analysis_file in sorted(analysis_files):
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
        
        # Extract events from this clip
        for event in analysis.get('events_detected', []):
            # Calculate absolute timestamp
            clip_start = analysis['start_seconds']
            event_timestamp = clip_start + event.get('timestamp_in_clip', 0)
            
            # Convert to minutes:seconds format
            minutes = int(event_timestamp // 60)
            seconds = int(event_timestamp % 60)
            timestamp_str = f"{minutes}:{seconds:02d}"
            
            synthesized_event = {
                "timestamp": timestamp_str,
                "timestamp_seconds": event_timestamp,
                "type": event['type'],
                "confidence": event['confidence'],
                "description": event.get('description', ''),
                "source_clip": analysis['clip_filename'],
                "gemini_model": analysis.get('gemini_model', 'gemini-pro-vision')
            }
            
            all_events.append(synthesized_event)
            total_confidence += event['confidence']
            events_with_confidence += 1
    
    # Sort events by timestamp
    all_events.sort(key=lambda x: x['timestamp_seconds'])
    
    # Calculate match statistics
    avg_confidence = total_confidence / events_with_confidence if events_with_confidence > 0 else 0
    
    event_types = {}
    for event in all_events:
        event_type = event['type']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    # Create match timeline
    match_timeline = {
        "match_id": match_id,
        "synthesis_timestamp": datetime.now().isoformat(),
        "total_events": len(all_events),
        "average_confidence": round(avg_confidence, 3),
        "event_types": event_types,
        "events": all_events,
        "gemini_summary": {
            "clips_analyzed": len(analysis_files),
            "events_detected": len(all_events),
            "confidence_threshold_used": 0.5
        }
    }
    
    # Save match timeline
    timeline_path = data_dir / "match_timeline.json"
    with open(timeline_path, 'w') as f:
        json.dump(match_timeline, f, indent=2)
    
    print(f"✅ Step 5 complete: {len(all_events)} events synthesized")
    print(f"📊 Event breakdown: {event_types}")
    print(f"🎯 Average confidence: {avg_confidence:.1%}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 5_gemini_synthesis.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = synthesize_match(match_id)
    
    if success:
        print(f"🎯 Ready for Step 6: Web formatting")
    else:
        sys.exit(1) 