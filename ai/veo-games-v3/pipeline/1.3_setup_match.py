#!/usr/bin/env python3
"""
Setup Match Configuration
Creates manual team configuration before running analysis pipeline.

Usage:
  python3 setup_match.py <match-id>

Example:  
  python3 setup_match.py cookstown-youth-football-club-20250729-cookstown-youth-vs-bourneview-ym-12011faa
"""

import sys
import json
from pathlib import Path

def create_match_config(match_id: str):
    """Interactive setup for match teams and colors"""
    
    print(f"🏆 Match Setup: {match_id}")
    print("=" * 60)
    
    # Get team information
    print("\nTeam Setup (we'll call them Team A and Team B internally)")
    print("Team A will be mapped to 'red' in the UI")
    print("Team B will be mapped to 'blue' in the UI")
    print()
    
    team_a_name = input("Enter Team A name (e.g., 'Cookstown Youth FC'): ").strip()
    team_a_jersey = input("Enter Team A jersey colors (e.g., 'red and white'): ").strip()
    
    print()
    team_b_name = input("Enter Team B name (e.g., 'Bourneview YM'): ").strip()
    team_b_jersey = input("Enter Team B jersey colors (e.g., 'all blue'): ").strip()
    
    # Optional match info
    print()
    match_date = input("Enter match date (YYYY-MM-DD) [optional]: ").strip() or None
    venue = input("Enter venue name [optional]: ").strip() or None
    
    # Create config
    config = {
        "match_id": match_id,
        "team_a": {
            "name": team_a_name,
            "jersey": team_a_jersey,
            "ui_color": "red"
        },
        "team_b": {
            "name": team_b_name,
            "jersey": team_b_jersey, 
            "ui_color": "blue"
        }
    }
    
    if match_date:
        config["match_date"] = match_date
    if venue:
        config["venue"] = venue
        
    # Save to outputs directory
    outputs_dir = Path("../outputs") / match_id
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = outputs_dir / "match_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print("✅ Match configuration saved!")
    print(f"📄 Config file: {config_path}")
    print()
    print("Team Mapping:")
    print(f"  • {team_a_name} ({team_a_jersey}) → Team A → UI 'red'")
    print(f"  • {team_b_name} ({team_b_jersey}) → Team B → UI 'blue'")
    print()
    print("Next steps:")
    print(f"  1. python3 1_fetch_veo.py <veo-url>")
    print(f"  2. python3 2_download_video.py {match_id}")
    print(f"  3. python3 3_make_clips.py {match_id}")
    print(f"  4. python3 mega_analyzer.py {match_id}")
    print(f"  5. python3 format_for_webapp.py {match_id}")
    print(f"  6. python3 10_s3_uploader.py {match_id}")
    print(f"  7. python3 12_write_metadata.py {match_id}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 setup_match.py <match-id>")
        print("Example: python3 setup_match.py cookstown-youth-vs-bourneview-20250729")
        sys.exit(1)
    
    match_id = sys.argv[1]
    create_match_config(match_id)

if __name__ == "__main__":
    main()