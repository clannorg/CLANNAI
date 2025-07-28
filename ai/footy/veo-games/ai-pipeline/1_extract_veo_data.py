#!/usr/bin/env python3
"""
1. Extract Veo Data
Gets ground truth events from Veo API
"""

import sys
import os
from pathlib import Path

from veo_extractor import VeoEventExtractor

def extract_veo_data(veo_url):
    """Extract ground truth data from Veo URL"""
    print(f"🎯 Step 1: Extracting Veo data from {veo_url}")
    
    # Extract match ID from URL
    import re
    pattern = r'/matches/([^/]+)/?'
    match = re.search(pattern, veo_url)
    if not match:
        print("❌ Could not extract match ID from URL")
        return False
    
    match_id = match.group(1)
    print(f"📋 Match ID: {match_id}")
    
    # Create data directory
    data_dir = Path("../data") / match_id
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract Veo events
    extractor = VeoEventExtractor()
    result = extractor.extract_and_save(veo_url, str(data_dir / "veo_ground_truth.json"))
    
    if result:
        # Create source.json with metadata
        source_data = {
            "url": veo_url,
            "match_id": match_id,
            "extracted_at": result["extraction_time"],
            "total_events": result["total_events"]
        }
        
        with open(data_dir / "source.json", 'w') as f:
            import json
            json.dump(source_data, f, indent=2)
        
        print(f"✅ Step 1 complete: {result['total_events']} events extracted")
        return match_id
    else:
        print("❌ Step 1 failed: Could not extract Veo data")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 1_extract_veo_data.py <veo-url>")
        sys.exit(1)
    
    veo_url = sys.argv[1]
    match_id = extract_veo_data(veo_url)
    
    if match_id:
        print(f"🎯 Ready for Step 2: Download video for {match_id}")
    else:
        sys.exit(1) 