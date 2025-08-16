# CLANNAI Veo Games v2

A lean, deterministic analysis pipeline with clear contracts to the webapp, fewer moving parts, and schema-validated outputs.

## Why v2

- Single source of truth for web outputs
- Deterministic final gate (no prompt drift in artifacts)
- Stricter goal/shot validation (kickoff/center-spot evidence)
- Clear file structure, fewer overlapping scripts

## High‑level flow

1) Fetch Veo metadata and ground truth
2) Download match video
3) Clip generation (fixed stride 15s) + early sample clip export
4) Clip analysis (Gemini)
5) Synthesis (combine clip descriptions into timeline)
6) Goals/shots validation (AI validation with kickoff logic)
7) Accuracy evaluation (compare AI vs VEO ground truth)
8) Definite events builder (VEO-confirmed events only)
9) Other events extraction (fouls, cards, corners)
10) Web JSON conversion (final format for webapp)

All steps are idempotent and write to a single `outputs/<match-id>/` directory.

## Gemini‑driven pipeline (what calls Gemini)

- 1_fetch_veo.py — Gemini: no
  - Output: `meta/match_meta.json`, `1_veo_ground_truth.json`
- 2_download_video.py — Gemini: no
  - Output: `video.mp4`
- 3_make_clips.py — Gemini: no
  - Output: `clips/*.mp4`, `sample_clip.mp4` (local) and S3 upload (optional)
- 4_analyze_clips.py — Gemini: yes (per‑clip + stitched)
  - Output: `4_clip_descriptions/*.txt`, `5_complete_timeline.txt`, `ai_claims_goals_shots.json`
- 5_validate_events.py — Gemini: yes (strict reasoning with rules)
  - Output: `validated_goals_shots.json`, `validation_log.txt`
- 6_supplement_events.py — Gemini: yes (other events)
  - Output: `other_events.json`
- 7_accuracy_evaluator.py — Gemini: yes (narrative), metrics are deterministic
  - Output: `accuracy_report.json`, `7_accuracy_comparison.txt`
- 7_build_web_json.py — Gemini: no (deterministic sanitizer)
  - Output: `web/events_array.json`, `web/events.json`
- 8_team_insights.py — Gemini: yes (from validated data)
  - Output: `web/team_insights_home.json`, `web/team_insights_away.json`, optional `commentary.md`
- 9_match_summary.py — Gemini: yes (compact UI summary)
  - Output: `web/summary.json`

## Outputs (contract to webapp)

Written under `outputs/<match-id>/`:

- web/events_array.json
  - Direct array of event objects (recommended by webapp)
- web/events.json
  - Wrapped object with `{ "events": [...] }` for legacy compatibility
- web/summary.json
  - Small match summary for UI (totals, key timestamps)
- web/team_insights_home.json
- web/team_insights_away.json
  - Coach-facing insights derived from validated events only
- meta/match_meta.json
  - Match metadata (teams, duration, source urls, ids)
- diagnostics/validation.txt
  - Accepted/rejected goal/shot claims and reasoning
- diagnostics/accuracy.json (optional)
  - Comparison against Veo ground-truth, if available
- commentary.md (optional)
  - Long-form commentary, if enabled

Goals & Shots artifacts (authoritative):
- ai_claims_goals_shots.json — raw AI claims (Gemini clip analysis)
- accuracy_report.json — AI vs VEO, TP/FP/FN, precision/recall, timing deltas
- validated_goals_shots.json — final truth used by the web export (VEO + AI + rules)
- disputed_events.json (optional) — items flagged for manual review

Early sanity check:
- sample_clip.mp4 (local) and S3: `s3://<bucket>/veo-games/<match-id>/sample/sample_clip.mp4`

### Event schema (what the webapp expects)

The webapp accepts either a direct array or `{ "events": [...] }`. We emit both.

Event object (exact fields):
- required
  - `type` (string; enum below)
  - `timestamp` (number; seconds from start)
- optional
  - `description` (string; <= 100 chars)
  - `player` (string)
  - `team` (string; one of `red`, `blue`, `black`, `yellow`, `home`, `away`)

Supported types (and only these):
- `goal`, `shot`, `save`, `foul`, `yellow_card`, `red_card`, `substitution`, `corner`, `offside`

Notes:
- Timestamps are seconds (numbers), ascending order
- Unknown types are rejected during build
- Team field is optional; when present, it powers score tracking for `goal`

## Goals & Shots track (authoritative)

Phases and JSON contracts:

- Phase A — AI claims (Gemini)
  - Input: `clips/*.mp4`
  - Output: `ai_claims_goals_shots.json`
  - Shape: `[ { "type": "goal|shot", "timestamp": <int>, "team"?, "outcome"?, "confidence"?, "source": "ai" } ]`

- Phase B — Accuracy vs VEO (Gemini‑assisted)
  - Inputs: `ai_claims_goals_shots.json`, `1_veo_ground_truth.json`
  - Output: `accuracy_report.json`
  - Shape:
    - `{ "precision": <float>, "recall": <float>, "timing_deltas": [ {"gt": <int>, "ai": <int>, "delta_s": <int>} ], "tp": [<int>], "fp": [<int>], "fn": [<int>] }`
    - Matching window: ±30s; cluster multi‑shots within 5–10s

- Phase C — Validated goals/shots (final truth)
  - Inputs: `ai_claims_goals_shots.json`, `1_veo_ground_truth.json`, `5_complete_timeline.txt`
  - Output: `validated_goals_shots.json`, `validation_log.txt`
  - Shape:
    - `[ { "type": "goal|shot", "timestamp": <int>, "team"?, "outcome"?, "source": "veo|ai|hybrid", "evidence": ["celebration","center_spot","kickoff"] } ]`

Validation policy:
- Goals: include all VEO goals; accept AI‑only goals only with strong evidence — celebration + center‑spot/explicit kickoff within ≤60s or the next 1–2 clips; reject if next restart is free/goal/corner (no kickoff); ignore penalty shootouts.
- Shots: must include outcome (saved/missed/blocked/goal); drop non‑on‑target headers; penalties mapped as shot/goal accordingly.

## Deterministic sanitizer rules (step 7)

Before saving `web/events*` we reclassify and clean:
- Drop: kickoffs, goal kicks, warm‑ups, pre/post‑match, penalty shootouts
- `foul` mapping: free kick / tackle / foul → `foul`
- Throw‑in → `turnover` (only `corner` if explicitly a corner)
- Penalties:
  - awarded → `foul`
  - taken/saved/missed → `shot`
  - scored → `goal`
- Team normalization: map variants (e.g., `striped`, `black_and_white`, `white (striped)`) → `black`
- Deduplicate events within 5s window by priority: `goal` > `shot` > `save` > `foul` > `corner` > `turnover`

## Strict goal/shot validation (step 5)

- Require center‑circle kickoff or explicit "ball placed on the center spot" within ≤ 60s or the next 1–2 clips after a claimed goal
- Reject goals followed by only free kicks / corners / goal kicks / generic open play (no kickoff evidence)
- Exclude penalty shootout segments from goals/shots
- Shots: require explicit outcome in description (saved/missed/blocked/goal)

## Early sanity check (sample clip)

- Generated in `3_make_clips.py` immediately after `video.mp4`
- Defaults: center‑of‑video time, aligned to 15s; override via `--sample-ts-seconds <int>`
- Local: `outputs/<match-id>/sample_clip.mp4`
- S3: `s3://<bucket>/veo-games/<match-id>/sample/sample_clip.mp4`
- CLI flags: `--emit-sample true|false` (default true), `--sample-s3-upload true|false` (default true)
- Orchestrator convenience: `--stop-after-sample` to exit early for manual check

## Directory structure

```
ai/veo-games-v2/
├── pipeline/
│   ├── 1_fetch_veo.py
│   ├── 2_download_video.py
│   ├── 3_make_clips.py
│   ├── 4_analyze_clips.py
│   ├── 5_validate_events.py
│   ├── 6_supplement_events.py
│   ├── 7_accuracy_evaluator.py
│   ├── 7_build_web_json.py
│   ├── 8_team_insights.py
│   ├── 9_match_summary.py
│   └── 0_run.py
├── schemas/
│   ├── events.schema.json
│   ├── summary.schema.json
│   ├── team_insights.schema.json
│   └── match_meta.schema.json
└── outputs/<match-id>/ (generated)
```

## Run it

- Environment
  - Python 3.9+
  - Conda env: `hooper-ai` (recommended)
  - `.env` at repo root with:
    - `GEMINI_API_KEY`
    - Veo credentials/tokens if required by fetcher
    - S3 bucket/prefix if uploading sample clip: `S3_BUCKET`, `S3_PREFIX`

- Orchestrator
```
python 0_run.py <veo-url|match-id> \
  --stop-after-sample false \
  --rebuild false
```

- One‑by‑one (idempotent)
```
python 1_fetch_veo.py <match-id>
python 2_download_video.py <match-id>
python 3_make_clips.py <match-id> --emit-sample true --sample-s3-upload true
python 4_analyze_clips.py <match-id>
python 5_synthesis.py <match-id>
python 6_goals_shots_validator.py <match-id>
python 7_accuracy_evaluator.py <match-id>
python 7.5_definite_events_builder.py <match-id>
python 8.5_other_events_extractor.py <match-id>
python 9_convert_to_web_format.py <match-id>
```

## Webapp alignment

- Mirrors `web-apps/1-clann-webapp/VIDEO_PLAYER_JSON_FORMAT.md`
- Emits both direct array (`web/events_array.json`) and wrapped (`web/events.json`)
- Only allowed event types; timestamps as numbers; ascending order

## Summary JSON (example fields)

- `goals_total`, `shots_total`, `fouls_total`
- `first_goal_ts`, `last_goal_ts`
- `penalties`: { `awarded`: n, `scored`: n, `saved`: n }
- `teams`: { `home`: name/id, `away`: name/id }

## Team insights JSON (example fields)

- `strengths[]` / `weaknesses[]` with evidence timestamps
- `training_drills[]` (actionable drills)
- `key_moments[]`
- `performance_metrics` (attacking/defending aggregates)

All insights are derived from validated/sanitized events (no raw‑LLM hallucinations in final outputs).

## Diagnostics

- `diagnostics/validation.txt`: accepted vs. rejected goals/shots with evidence
- `diagnostics/accuracy.json`: precision/recall vs Veo ground truth if available

## Migration from v1

- v1 files are unchanged; v2 can read v1 artifacts for prototyping
- Webapp should prefer v2 `web/events_array.json` when present
- Replace v1 converters/formatters gradually with v2 step 7

## Troubleshooting

- No events in UI: validate JSON; ensure only supported types; check timestamps numeric
- Too many corners: verify sanitizer mapping (throw‑ins / free kicks → not `corner`)
- False‑positive goals: confirm kickoff/center‑spot evidence rule in step 5

## License / Ownership

Internal CLANNAI tooling. Proprietary.