#!/usr/bin/env python3
"""
12. Write Match Metadata

Creates a minimal match_metadata.json for the given match-id using existing
outputs. Includes team colors (placeholders), key S3 file URLs (if uploaded),
and basic counts from mega_analysis.json when available.

Usage:
  python 12_write_metadata.py <match-id>

Example:
  python 12_write_metadata.py 20250523-match-23-may-2025-3fc1de88
"""

import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def parse_final_score(outputs_dir: Path) -> dict:
    """Parse final score and match summary from mega_summary.txt"""
    summary_path = outputs_dir / "mega_summary.txt"
    if not summary_path.exists():
        return {}
    
    try:
        with open(summary_path, "r") as f:
            content = f.read()
        
        # Extract final score line
        final_score = None
        winner = None
        match_summary = content.strip()
        
        for line in content.split('\n'):
            if line.startswith("Final Score:"):
                final_score = line.replace("Final Score: ", "").strip()
                # Determine winner from score (assumes format "Team A X - Y Team B")
                if " - " in final_score:
                    parts = final_score.split(" - ")
                    if len(parts) == 2:
                        left_part = parts[0].strip()
                        right_part = parts[1].strip()
                        # Extract scores (last word of each part should be the number)
                        left_score = int(left_part.split()[-1])
                        right_score = int(right_part.split()[0])
                        if left_score > right_score:
                            winner = " ".join(left_part.split()[:-1])
                        elif right_score > left_score:
                            winner = " ".join(right_part.split()[1:])
                        else:
                            winner = "Draw"
                break
        
        return {
            "final_score": final_score,
            "winner": winner,
            "match_summary": match_summary
        }
    except Exception:
        return {}


def build_metadata(match_id: str, outputs_dir: Path) -> dict:
    s3_locations = load_json(outputs_dir / "s3_locations.json")
    web_events = load_json(outputs_dir / "web_events_array.json")
    match_config = load_json(outputs_dir / "match_config.json")
    
    # Parse final score and match summary
    score_info = parse_final_score(outputs_dir)

    # S3 URLs if available; else None
    s3_urls = (s3_locations or {}).get("s3_urls", {})
    def url_for(name: str):
        entry = s3_urls.get(name, {})
        return entry.get("url")

    # Counts from web events array (what the website actually uses)
    if web_events and isinstance(web_events, list):
        goals_total = len([e for e in web_events if e.get("type") == "goal"])
        shots_total = len([e for e in web_events if e.get("type") == "shot"])
    else:
        goals_total = 0
        shots_total = 0

    # Use team names from match_config.json if available, otherwise use defaults
    if match_config and "team_a" in match_config and "team_b" in match_config:
        red_team_name = match_config["team_a"]["name"]
        red_team_jersey = match_config["team_a"]["jersey"]
        blue_team_name = match_config["team_b"]["name"] 
        blue_team_jersey = match_config["team_b"]["jersey"]
    else:
        # Fallback to generic names if no config found
        red_team_name = "Team A"
        red_team_jersey = "unknown"
        blue_team_name = "Team B"
        blue_team_jersey = "unknown"

    metadata = {
        "match_id": match_id,
        "teams": {
            "red_team": {
                "name": red_team_name,
                "jersey_color": red_team_jersey,
            },
            "blue_team": {
                "name": blue_team_name,
                "jersey_color": blue_team_jersey,
            },
        },
        "counts": {
            "goals": goals_total,
            "shots": shots_total,
        },
        "files": {
            "video_mp4": url_for("video.mp4"),
            "web_events_array_json": url_for("web_events_array.json"),
            "web_events_json": url_for("web_events.json"),
            "timeline_txt": url_for("5_complete_timeline.txt"),
            "ground_truth_json": url_for("1_veo_ground_truth.json"),
            "other_events_txt": url_for("8_other_events.txt"),
            "tactical_json": url_for("11_tactical_analysis.json"),
        },
    }
    
    # Add final score info if available
    if score_info.get("final_score"):
        metadata["final_score"] = score_info["final_score"]
    if score_info.get("winner"):
        metadata["winner"] = score_info["winner"]
    if score_info.get("match_summary"):
        metadata["match_summary"] = score_info["match_summary"]

    return metadata


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python 12_write_metadata.py <match-id>")
        sys.exit(1)

    match_id = sys.argv[1]
    outputs_dir = Path("../outputs") / match_id
    outputs_dir.mkdir(parents=True, exist_ok=True)

    metadata = build_metadata(match_id, outputs_dir)
    out_path = outputs_dir / "match_metadata.json"
    with open(out_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Wrote metadata: {out_path}")


if __name__ == "__main__":
    main()

