#!/usr/bin/env python3
"""
1. Setup Teams
Manual team configuration for 5-a-side games
"""

import sys
import json
from pathlib import Path

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python 1_setup_teams.py <match-id> [game-type]")
        print("Example: python 1_setup_teams.py sunday-league-game-1")
        print("Example: python 1_setup_teams.py leo1 6-a-side")
        print("Game types: 5-a-side, 6-a-side, 7-a-side, 8-a-side, 11-a-side, futsal")
        sys.exit(1)
    
    match_id = sys.argv[1]
    game_type = sys.argv[2] if len(sys.argv) == 3 else '5-a-side'
    
    # Create outputs directory
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🏗️  Setting up teams for match: {match_id}")
    print("=" * 50)
    print("\n🎯 CONTEXT: You're setting up detailed team info for AI agents that will")
    print("   watch 15-second segments and describe exactly what they see.")
    print("   The more specific you are about team colors/appearance, the better!")
    
    # Get team information
    print("\n👕 Team A:")
    team_a_name = input("  Team A name (e.g., 'The Lads', 'clann'): ").strip()
    print("  💡 Be very specific about what Team A looks like:")
    team_a_colors = input("  Team A appearance (e.g., 'orange bibs over white shirts', 'no bibs/colours'): ").strip()
    
    print("\n👕 Team B:")
    team_b_name = input("  Team B name (e.g., 'Other Team', 'lostthehead'): ").strip()
    print("  💡 Be very specific about what Team B looks like:")
    team_b_colors = input("  Team B appearance (e.g., 'blue shirts', 'red bibs over black shirts'): ").strip()
    
    print("\n📝 Additional context (optional):")
    additional_context = input("  Any other details? (playing style, key players, etc.): ").strip()
    
    # Create team configuration
    team_config = {
        'match_id': match_id,
        'team_a': {
            'name': team_a_name or 'Team A',
            'colors': team_a_colors or 'first team colors'
        },
        'team_b': {
            'name': team_b_name or 'Team B', 
            'colors': team_b_colors or 'second team colors'
        },
        'game_type': game_type,
        'focus': 'detailed play-by-play description',
        'additional_context': additional_context or ''
    }
    
    # Save configuration
    config_file = outputs_dir / 'team_config.json'
    with open(config_file, 'w') as f:
        json.dump(team_config, f, indent=2)
    
    print(f"\n✅ Team setup complete!")
    print(f"📄 Configuration saved to: {config_file}")
    print(f"\n📋 Summary:")
    print(f"   Team A: {team_config['team_a']['name']} ({team_config['team_a']['colors']})")
    print(f"   Team B: {team_config['team_b']['name']} ({team_config['team_b']['colors']})")
    if additional_context:
        print(f"   Context: {additional_context}")
    print(f"   Focus: {team_config['focus']}")
    print(f"\n🎯 Ready for step 2: python 2_make_clips.py <video-path> {match_id}")
    print(f"💡 This approach will generate detailed play-by-play descriptions")
    print(f"   with specific timings that can be easily verified!")

if __name__ == "__main__":
    main()