#!/usr/bin/env python3
"""
2. Player Profiler
Analyzes clips to identify and profile all players in the game
Uses Gemini to build comprehensive player descriptions
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

class PlayerProfiler:
    def __init__(self):
        """Initialize the player profiler with Gemini"""
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🤖 Player profiler initialized with Gemini 2.0 Flash")
        
        # Player database to track all players across clips
        self.players_db = {}
        self.player_counter = 0

    def get_player_analysis_prompt(self, clip_path: str, clip_timestamp: str) -> str:
        """Create prompt for comprehensive player analysis"""
        return f"""You are an expert football analyst tasked with identifying and profiling ALL players visible in this football video clip.

CLIP INFO:
- Timestamp: {clip_timestamp}
- Duration: 15 seconds

ANALYSIS TASK:
1. **Identify ALL visible players** - Every person on the pitch
2. **Create detailed visual descriptions** for each player
3. **Determine player positions/roles** based on behavior and positioning
4. **Note any distinctive features** (jersey colors, numbers, physical characteristics)
5. **Track player movements and actions** during this clip

OUTPUT FORMAT (JSON):
{{
  "clip_timestamp": "{clip_timestamp}",
  "players": [
    {{
      "player_id": "P1",
      "visual_description": "Detailed description of appearance, kit, features",
      "position": "striker/midfielder/defender/goalkeeper/unknown",
      "team": "team_color_or_bib_color",
      "jersey_number": "number_if_visible",
      "distinctive_features": ["black hair", "orange bib", "tall", "beard", etc.],
      "actions_in_clip": ["passing", "running", "shooting", "marking", etc.],
      "location_on_pitch": "left_wing/center/right_wing/defensive_half/attacking_half",
      "confidence": "high/medium/low"
    }}
  ],
  "total_players_visible": 8,
  "teams_identified": ["orange_bibs", "blue_shirts", "etc"],
  "analysis_notes": "Any additional observations about player interactions, formations, etc."
}}

IMPORTANT:
- Be as detailed as possible in visual descriptions
- Include ALL players visible, even if partially obscured
- Use consistent player_id format (P1, P2, P3, etc.)
- Note team affiliations by colors/bibs
- Describe any distinctive physical features
- Track what each player is doing in this clip

Analyze the video clip and provide the JSON response."""

    def analyze_clip(self, clip_path: str, clip_timestamp: str) -> dict:
        """Analyze a single clip for player identification"""
        print(f"🔍 Analyzing clip: {clip_timestamp}")
        
        try:
            # Create the prompt
            prompt = self.get_player_analysis_prompt(clip_path, clip_timestamp)
            
            # Generate response from Gemini
            response = self.model.generate_content([prompt, clip_path])
            
            # Parse the JSON response
            try:
                analysis = json.loads(response.text)
                print(f"✅ Found {analysis.get('total_players_visible', 0)} players in {clip_timestamp}")
                return analysis
            except json.JSONDecodeError:
                print(f"❌ Failed to parse JSON response for {clip_timestamp}")
                return {"clip_timestamp": clip_timestamp, "players": [], "error": "JSON parse failed"}
                
        except Exception as e:
            print(f"❌ Error analyzing clip {clip_timestamp}: {e}")
            return {"clip_timestamp": clip_timestamp, "players": [], "error": str(e)}

    def merge_player_profiles(self, clip_analyses: list) -> dict:
        """Merge player data across all clips to build comprehensive profiles"""
        print("🔄 Merging player profiles across all clips...")
        
        # Track players across clips
        player_tracker = {}
        
        for clip_analysis in clip_analyses:
            if "players" not in clip_analysis:
                continue
                
            for player in clip_analysis["players"]:
                # Create unique player identifier based on visual description
                visual_key = self.create_visual_key(player)
                
                if visual_key not in player_tracker:
                    player_tracker[visual_key] = {
                        "player_id": f"P{len(player_tracker) + 1}",
                        "visual_description": player.get("visual_description", ""),
                        "distinctive_features": player.get("distinctive_features", []),
                        "team": player.get("team", ""),
                        "jersey_number": player.get("jersey_number", ""),
                        "positions_observed": [],
                        "actions_observed": [],
                        "locations_observed": [],
                        "appearances": 0,
                        "first_seen": clip_analysis["clip_timestamp"],
                        "last_seen": clip_analysis["clip_timestamp"]
                    }
                
                # Update player profile
                profile = player_tracker[visual_key]
                profile["appearances"] += 1
                profile["last_seen"] = clip_analysis["clip_timestamp"]
                
                if player.get("position"):
                    profile["positions_observed"].append(player["position"])
                
                if player.get("actions_in_clip"):
                    profile["actions_observed"].extend(player["actions_in_clip"])
                
                if player.get("location_on_pitch"):
                    profile["locations_observed"].append(player["location_on_pitch"])
        
        # Build final profiles
        final_profiles = []
        for visual_key, profile in player_tracker.items():
            # Determine most common position
            if profile["positions_observed"]:
                position_counts = {}
                for pos in profile["positions_observed"]:
                    position_counts[pos] = position_counts.get(pos, 0) + 1
                primary_position = max(position_counts, key=position_counts.get)
            else:
                primary_position = "unknown"
            
            # Get unique actions and locations
            unique_actions = list(set(profile["actions_observed"]))
            unique_locations = list(set(profile["locations_observed"]))
            
            final_profile = {
                "player_id": profile["player_id"],
                "visual_description": profile["visual_description"],
                "distinctive_features": profile["distinctive_features"],
                "team": profile["team"],
                "jersey_number": profile["jersey_number"],
                "primary_position": primary_position,
                "all_positions_observed": profile["positions_observed"],
                "actions_observed": unique_actions,
                "locations_observed": unique_locations,
                "appearances": profile["appearances"],
                "first_seen": profile["first_seen"],
                "last_seen": profile["last_seen"],
                "confidence": "high" if profile["appearances"] > 3 else "medium"
            }
            
            final_profiles.append(final_profile)
        
        return {
            "total_players": len(final_profiles),
            "profiles": final_profiles,
            "teams_identified": list(set(p["team"] for p in final_profiles if p["team"]))
        }

    def create_visual_key(self, player: dict) -> str:
        """Create a unique key for player identification based on visual features"""
        features = []
        
        # Add distinctive features
        if player.get("distinctive_features"):
            features.extend(player["distinctive_features"])
        
        # Add team/kit info
        if player.get("team"):
            features.append(player["team"])
        
        # Add jersey number if available
        if player.get("jersey_number"):
            features.append(f"#{player['jersey_number']}")
        
        # Create a consistent key
        return "_".join(sorted(features)).lower()

    def profile_players(self, game_id: str) -> bool:
        """Main function to profile all players in a game"""
        print(f"🎯 Step 2: Player Profiling for {game_id}")
        
        data_dir = Path("../data") / game_id
        clips_dir = data_dir / "clips"
        segments_file = clips_dir / "segments.json"
        
        if not clips_dir.exists():
            print(f"❌ Clips directory not found: {clips_dir}")
            print("Run Step 1 first: python 1_generate_clips.py")
            return False
        
        if not segments_file.exists():
            print(f"❌ Segments file not found: {segments_file}")
            return False
        
        # Load clips metadata
        with open(segments_file, 'r') as f:
            segments_data = json.load(f)
        
        clips = segments_data.get("clips", [])
        print(f"📊 Found {len(clips)} clips to analyze")
        
        # Analyze each clip
        clip_analyses = []
        total_clips = len(clips)
        
        for i, clip_info in enumerate(clips, 1):
            clip_filename = clip_info["filename"]
            clip_timestamp = clip_info["timestamp"]
            clip_path = clips_dir / clip_filename
            
            if not clip_path.exists():
                print(f"⚠️  Clip not found: {clip_filename}")
                continue
            
            print(f"🔄 Processing {i}/{total_clips}: {clip_filename}")
            
            # Analyze the clip
            analysis = self.analyze_clip(str(clip_path), clip_timestamp)
            clip_analyses.append(analysis)
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        # Merge profiles across all clips
        print("🔄 Building comprehensive player profiles...")
        final_profiles = self.merge_player_profiles(clip_analyses)
        
        # Save results
        output_dir = Path("../output") / game_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual clip analyses
        with open(output_dir / "clip_analyses.json", 'w') as f:
            json.dump(clip_analyses, f, indent=2)
        
        # Save final player profiles
        with open(output_dir / "player_profiles.json", 'w') as f:
            json.dump(final_profiles, f, indent=2)
        
        # Create human-readable summary
        self.create_profile_summary(final_profiles, output_dir)
        
        print("\n🎯 PLAYER PROFILING COMPLETE!")
        print("=" * 50)
        print(f"✅ Analyzed {len(clip_analyses)} clips")
        print(f"👥 Identified {final_profiles['total_players']} unique players")
        print(f"🏟️  Teams: {', '.join(final_profiles['teams_identified'])}")
        print(f"📁 Results saved to: {output_dir}")
        
        return True

    def create_profile_summary(self, profiles_data: dict, output_dir: Path):
        """Create a human-readable summary of player profiles"""
        summary = []
        summary.append("# PLAYER PROFILES SUMMARY")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Total Players: {profiles_data['total_players']}")
        summary.append(f"Teams: {', '.join(profiles_data['teams_identified'])}")
        summary.append("")
        
        for profile in profiles_data["profiles"]:
            summary.append(f"## {profile['player_id']}")
            summary.append(f"**Visual Description:** {profile['visual_description']}")
            summary.append(f"**Team:** {profile['team']}")
            summary.append(f"**Position:** {profile['primary_position']}")
            summary.append(f"**Jersey:** {profile['jersey_number']}")
            summary.append(f"**Features:** {', '.join(profile['distinctive_features'])}")
            summary.append(f"**Appearances:** {profile['appearances']} clips")
            summary.append(f"**Actions:** {', '.join(profile['actions_observed'])}")
            summary.append(f"**Locations:** {', '.join(profile['locations_observed'])}")
            summary.append(f"**Confidence:** {profile['confidence']}")
            summary.append("")
        
        with open(output_dir / "profiles_summary.md", 'w') as f:
            f.write('\n'.join(summary))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 2_player_profiler.py <game-id>")
        print("Example: python 2_player_profiler.py brixton5s-20240807")
        sys.exit(1)
    
    game_id = sys.argv[1]
    
    try:
        profiler = PlayerProfiler()
        success = profiler.profile_players(game_id)
        
        if success:
            print(f"🎯 Ready for Step 3: Individual player action tracking")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 