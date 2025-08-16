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


def build_metadata(match_id: str, outputs_dir: Path) -> dict:
    s3_locations = load_json(outputs_dir / "s3_locations.json")
    mega = load_json(outputs_dir / "mega_analysis.json")

    # S3 URLs if available; else None
    s3_urls = (s3_locations or {}).get("s3_urls", {})
    def url_for(name: str):
        entry = s3_urls.get(name, {})
        return entry.get("url")

    # Counts from mega analysis if present
    match_analysis = mega.get("match_analysis", {})
    goals_total = match_analysis.get("goals_analysis", {}).get("total_veo_verified_goals", 0)
    shots_total = match_analysis.get("shots_analysis", {}).get("total_veo_verified_shots", 0)

    metadata = {
        "match_id": match_id,
        "teams": {
            # Placeholder names/colors that reflect jersey colors visible in video
            "red_team": {
                "name": "Black/White Team",
                "jersey_color": "black and white striped",
            },
            "blue_team": {
                "name": "Blue Team",
                "jersey_color": "blue",
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

