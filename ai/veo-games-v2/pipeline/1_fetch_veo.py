#!/usr/bin/env python3
"""
1. Fetch Veo metadata and ground truth (v2 wrapper)

- Derives match_id from Veo URL or explicit id
- Reuses existing v1 data if available: ai/veo-games/ai-pipeline/data/<match-id>/1_veo_ground_truth.json
- Writes v2 outputs directory structure and metadata

This script is deterministic and does not call Gemini.
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Veo metadata and ground truth (v2)")
    parser.add_argument("veo_url_or_match_id", help="Veo match URL or explicit match-id")
    parser.add_argument("--out", dest="out_dir", default=None, help="Override outputs directory")
    args = parser.parse_args()

    match_id = derive_match_id(args.veo_url_or_match_id)
    paths = compute_paths(match_id, args.out_dir)
    ensure_dirs(paths)

    used_v1 = copy_ground_truth_if_available(paths)
    write_match_meta(paths.meta_dir, match_id, args.veo_url_or_match_id, used_v1)

    gt_path = paths.outputs_dir / "1_veo_ground_truth.json"
    if not gt_path.exists():
        # Provide a helpful message but do not fail hard to allow offline iteration.
        msg = (
            "Ground truth not found. Either run v1 extractor or provide 1_veo_ground_truth.json\n"
            f"Expected v1 path: {paths.v1_data_dir / '1_veo_ground_truth.json'}\n"
            f"v2 outputs path: {gt_path}"
        )
        print(msg)
        # Write a placeholder to make downstream steps' existence checks clearer
        (paths.outputs_dir / "1_veo_ground_truth.json.missing").write_text(msg, encoding="utf-8")
    else:
        print(f"✅ Copied ground truth → {gt_path}")

    print(f"✅ Metadata written → {paths.meta_dir / 'match_meta.json'}")
    print(f"🎯 Match ID: {match_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())