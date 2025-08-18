#!/usr/bin/env python3
"""
1.1 Fetch Veo metadata and ground truth (v3)

- Derives match_id from Veo URL
- Extracts ground truth events directly from VEO API
- Writes v3 outputs directory structure and metadata

This script calls VEO API to get ground truth events.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from veo_extractor import VeoEventExtractor


@dataclass
class Paths:
    repo_root: Path
    v2_root: Path
    outputs_dir: Path
    meta_dir: Path
    v1_data_dir: Path


def derive_match_id(veo_url_or_id: str) -> str:
    """Derive a stable match_id from either a Veo URL or raw id string."""
    candidate = veo_url_or_id.strip()
    if candidate.startswith("http://") or candidate.startswith("https://"):
        # Take the last non-empty path segment as id
        parts = [p for p in re.split(r"[/\\]", candidate) if p]
        return parts[-1]
    # Normalize: lowercase and replace spaces with dashes
    return re.sub(r"\s+", "-", candidate.lower())


def compute_paths(match_id: str, out_dir: Optional[str]) -> Paths:
    script_path = Path(__file__).resolve()
    # repo_root = .../CLANNAI
    repo_root = script_path.parents[3]
    v2_root = script_path.parents[1]
    outputs_dir = (Path(out_dir).resolve() if out_dir else v2_root / "outputs" / match_id)
    meta_dir = outputs_dir / "meta"
    v1_data_dir = repo_root / "ai" / "veo-games" / "ai-pipeline" / "data" / match_id
    return Paths(repo_root, v2_root, outputs_dir, meta_dir, v1_data_dir)


def ensure_dirs(paths: Paths) -> None:
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    paths.meta_dir.mkdir(parents=True, exist_ok=True)


def copy_ground_truth_if_available(paths: Paths) -> bool:
    src = paths.v1_data_dir / "1_veo_ground_truth.json"
    if src.exists():
        dst = paths.outputs_dir / "1_veo_ground_truth.json"
        shutil.copy2(src, dst)
        return True
    return False


def write_match_meta(meta_dir: Path, match_id: str, veo_url_or_id: str, used_v1: bool) -> None:
    meta = {
        "match_id": match_id,
        "input": veo_url_or_id,
        "source": "v1_reuse" if used_v1 else "manual",
    }
    (meta_dir / "match_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def extract_ground_truth(veo_url: str, gt_path: Path) -> bool:
    """Extract ground truth events from VEO API"""
    print(f"📡 Extracting ground truth from VEO API...")
    
    try:
        extractor = VeoEventExtractor()
        result = extractor.extract_and_save(veo_url, str(gt_path))
        
        if result:
            print(f"✅ Ground truth extracted: {result['total_events']} events")
            return True
        else:
            print("❌ Failed to extract ground truth from VEO")
            return False
            
    except Exception as e:
        print(f"❌ Ground truth extraction failed: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Veo metadata and ground truth (v3)")
    parser.add_argument("veo_url_or_match_id", help="Veo match URL (required for ground truth extraction)")
    parser.add_argument("--out", dest="out_dir", default=None, help="Override outputs directory")
    args = parser.parse_args()

    # For v3, we require a full VEO URL for ground truth extraction
    veo_url = args.veo_url_or_match_id
    if not veo_url.startswith("http"):
        print("❌ v3 requires full VEO URL for ground truth extraction")
        print("Example: python3 1.1_fetch_veo.py 'https://app.veo.co/matches/cookstown-youth.../")
        return 1

    match_id = derive_match_id(veo_url)
    paths = compute_paths(match_id, args.out_dir)
    ensure_dirs(paths)

    # Try to copy existing v1 ground truth first (for backwards compatibility)
    used_v1 = copy_ground_truth_if_available(paths)
    
    gt_path = paths.outputs_dir / "1_veo_ground_truth.json"
    
    # If no v1 ground truth found, extract from VEO API
    if not gt_path.exists():
        print(f"🎯 No existing ground truth found, extracting from VEO...")
        success = extract_ground_truth(veo_url, gt_path)
        if not success:
            # Create a .missing file but don't fail completely
            msg = f"Ground truth extraction failed from: {veo_url}"
            (paths.outputs_dir / "1_veo_ground_truth.json.missing").write_text(msg, encoding="utf-8")
            print("⚠️  Continuing without ground truth (pipeline will still work)")
    else:
        print(f"✅ Using existing ground truth → {gt_path}")

    write_match_meta(paths.meta_dir, match_id, veo_url, used_v1)
    
    print(f"✅ Metadata written → {paths.meta_dir / 'match_meta.json'}")
    print(f"🎯 Match ID: {match_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())