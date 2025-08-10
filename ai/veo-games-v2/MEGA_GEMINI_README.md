# MEGA-GEMINI PIPELINE APPROACH

## Current Problem
Our v2 pipeline makes **6 separate Gemini calls** in sequence, creating a "telephone game" where:
- Step 4: Analyze clips → misses goals (0/5 detected)
- Step 6: Validate goals → can't validate what wasn't detected  
- Step 8: Extract other events → works but no context
- Step 9: Convert to web format → limited by previous steps
- Step 11: Tactical analysis → limited context

**Result: Missing 5/5 goals, 18/18 shots despite VEO ground truth available**

## Mega-Gemini Solution

**Replace steps 4-11 with ONE context-aware Gemini call**

### Single Input Package
```
INPUTS TO MEGA-GEMINI:
├── 5_complete_timeline.txt (90min in 600x15s chunks)
├── 1_veo_ground_truth.json (23 VEO events: 5 goals, 18 shots)  
├── meta/match_meta.json (teams, duration, colors)
└── team_mapping: Blue vs Black/White
```

### Single Output Package
```json
{
  "validated_events": {
    "goals": [
      {
        "timestamp": 1968,
        "time_display": "32:48", 
        "team": "blue",
        "description": "Goal scored",
        "source": "veo_confirmed",
        "veo_match": true,
        "ai_detected": false
      }
    ],
    "shots": [ ... ],
    "other_events": [
      {
        "type": "foul",
        "timestamp": 1488,
        "team": "black", 
        "description": "Foul committed"
      }
    ]
  },
  "web_events_array": [
    // Direct webapp format - goals, shots, fouls, cards, corners, subs
  ],
  "tactical_analysis": {
    "red_team": {
      "strengths": ["Strong attacking in final third"],
      "weaknesses": ["Defensive transitions"],
      "manager_recommendations": {
        "attacking": ["Focus on wing play"],
        "defending": ["Compact defensive shape"]
      }
    },
    "blue_team": { ... }
  },
  "accuracy_metrics": {
    "goals": {
      "precision": 0.0,  // 0 correct / 0 detected
      "recall": 0.0,     // 0 detected / 5 actual
      "veo_events": 5,
      "ai_detected": 0,
      "true_positives": 0,
      "false_positives": 0,
      "false_negatives": 5
    },
    "shots": { ... }
  },
  "match_summary": {
    "total_goals": 5,
    "total_shots": 18,
    "goal_times": [1968, 2137, 2479, 3122, 6076],
    "score_progression": [
      {"time": 1968, "score": "1-0"},
      {"time": 2137, "score": "2-0"}
    ]
  }
}
```

## Benefits

### 🎯 **Accuracy**
- Cross-validation: Gemini sees BOTH AI timeline AND VEO ground truth
- Context-aware: Full match knowledge for better event detection
- Smart reconciliation: "VEO says goal at 32:48, let me check timeline around that time"

### ⚡ **Speed** 
- 1 Gemini call vs 6 separate calls
- No inter-step dependencies 
- Parallel processing of all analysis types

### 🔒 **Deterministic**
- Single source of truth
- Consistent team mappings
- No prompt drift between steps

### 🧠 **Intelligent**
- "I see VEO detected a goal at 32:48, checking timeline clips around 1968s..."
- "Timeline shows celebration and center-circle restart after this event"
- "AI missed this goal but evidence is clear in timeline"

## Mega-Prompt Strategy

```
You are analyzing a 90-minute football match. You have:

1. COMPLETE MATCH TIMELINE: 600 15-second clips analyzed by AI
2. VEO GROUND TRUTH: 23 verified events (5 goals, 18 shots)  
3. TEAMS: Blue (blue jerseys) vs Black/White (striped jerseys)

YOUR TASK: Produce comprehensive match analysis with perfect accuracy by cross-referencing AI timeline against VEO truth.

CRITICAL INSTRUCTIONS:
- Every VEO goal/shot MUST appear in final output (they are ground truth)
- For each VEO event, find supporting evidence in timeline
- AI timeline may miss events - use VEO times to locate them
- Reject AI events not supported by VEO (unless overwhelming evidence)
- Generate tactical insights from validated events only

OUTPUT FORMAT: Single JSON with validated_events, web_events_array, tactical_analysis, accuracy_metrics
```

## Implementation Plan

1. **Create `mega_analyzer.py`**
   - Reads: timeline + VEO + metadata
   - Calls: Gemini 2.5 Pro with full context
   - Outputs: Complete analysis JSON

2. **Test on current match**
   - Input: Our 600 clips + VEO 23 events
   - Expected: Find all 5 goals, 18 shots
   - Validate: Web format + tactical analysis

3. **Replace pipeline steps 4-11**
   - Keep: 1-3 (data + clips)  
   - Replace: 4-11 with single mega call
   - Maintain: Same output contracts

## Expected Results

- **Goals detected**: 5/5 (vs current 0/5)
- **Shots detected**: 18/18 (vs current 0/18) 
- **Processing time**: ~2 minutes (vs ~15 minutes)
- **Accuracy**: Perfect precision/recall on VEO events
- **Context**: Rich tactical insights from complete match view

## File Structure

```
mega_analyzer.py → outputs/
├── mega_analysis.json (complete output)
├── web_events_array.json (extracted for webapp)
├── 11_tactical_analysis.json (extracted for webapp)
└── accuracy_report.json (extracted for validation)
```

Ready to implement!