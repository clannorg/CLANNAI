#!/usr/bin/env python3
"""
1. Extract Veo Data
Gets ground truth events from Veo API
"""

import sys
import os
from pathlib import Path
import re
from datetime import datetime

from veo_extractor import VeoEventExtractor

def create_readable_match_id(veo_match_id, veo_url=""):
    """Convert raw Veo match ID to human-readable format"""
    # Example: 20250111-ballyclare-425e4c3f -> ballyclare-20250111
    
    try:
        # Split by hyphens
        parts = veo_match_id.split('-')
        
        if len(parts) >= 3:
            # Expected format: YYYYMMDD-team-hash
            date_part = parts[0]  # 20250111
            team_part = parts[1]  # ballyclare
            
            # Validate date part
            if len(date_part) == 8 and date_part.isdigit():
                # Format: team-YYYYMMDD
                readable_id = f"{team_part}-{date_part}"
                return readable_id
            
        # Fallback: if we can't parse properly, use first 2 parts
        if len(parts) >= 2:
            return f"{parts[1]}-{parts[0]}"
            
        # Last fallback: use the original ID
        return veo_match_id
        
    except Exception:
        # If anything fails, use original ID
        return veo_match_id

def extract_veo_data(veo_url):
    """Extract ground truth data from Veo URL"""
    print(f"🎯 Step 1: Extracting Veo data from {veo_url}")
    
    # Extract raw match ID from URL
    import re
    pattern = r'/matches/([^/]+)/?'
    match = re.search(pattern, veo_url)
    if not match:
        print("❌ Could not extract match ID from URL")
        return False
    
    raw_match_id = match.group(1)
    print(f"📋 Raw Veo ID: {raw_match_id}")
    
    # Create human-readable match ID
    readable_match_id = create_readable_match_id(raw_match_id, veo_url)
    print(f"📁 Clean Match ID: {readable_match_id}")
    
    # Create data directory with readable name
    data_dir = Path("../data") / readable_match_id
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract Veo events
    extractor = VeoEventExtractor()
    result = extractor.extract_and_save(veo_url, str(data_dir / "veo_ground_truth.json"))
    
    if result:
        # Create source.json with both IDs and rich metadata
        source_data = {
            "url": veo_url,
            "match_id": readable_match_id,
            "veo_match_id": raw_match_id,
            "extracted_at": datetime.now().isoformat(),
            "total_events": result["total_events"],
            "extraction_method": "veo_api_highlights",
            "status": "ready_for_analysis"
        }
        
        # Try to extract additional metadata from match ID
        try:
            parts = raw_match_id.split('-')
            if len(parts) >= 2:
                date_part = parts[0]
                team_part = parts[1]
                
                if len(date_part) == 8 and date_part.isdigit():
                    # Parse date: 20250111 -> 2025-01-11
                    year = date_part[:4]
                    month = date_part[4:6]
                    day = date_part[6:8]
                    formatted_date = f"{year}-{month}-{day}"
                    
                    source_data.update({
                        "date": formatted_date,
                        "primary_team": team_part.title(),
                        "venue": team_part.title()
                    })
        except:
            pass  # If metadata extraction fails, that's okay
        
        with open(data_dir / "source.json", 'w') as f:
            import json
            json.dump(source_data, f, indent=2)
        
        print(f"✅ Step 1 complete: {result['total_events']} events extracted")
        print(f"📁 Data saved to: {data_dir}")
        return readable_match_id
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