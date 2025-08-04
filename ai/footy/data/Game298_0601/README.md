# Game298_0601 Analysis Plan

## Current State Analysis

### What We Have
- **Video File**: `Game298_0601_p1.mp4` (15 minutes 17 seconds / 917.6 seconds)
- **Manual Timestamps**: Basic CSV with 10 events (2 goals, 4 saves, 2 shots, 1 end)
- **Current Format**: Simple timestamp-based annotations

### What We Need
- **AI-Powered Analysis**: Like the `1_game_events` system
- **Comprehensive Event Detection**: Goals, shots, passes, tackles, fouls, cards, etc.
- **Structured Timeline**: Chronological event timeline with detailed descriptions
- **Match Statistics**: Complete game statistics and insights

## Analysis Strategy

### Phase 1: Video Segmentation
1. **Split 15-minute video into 30-second clips**
   - Total: ~30 clips (917 seconds ÷ 30 seconds)
   - Each clip analyzed independently by AI
   - Maintain chronological order

2. **Clip Naming Convention**
   ```
   Game298_0601_clip_001.mp4 (0:00-0:30)
   Game298_0601_clip_002.mp4 (0:30-1:00)
   ...
   Game298_0601_clip_030.mp4 (14:30-15:17)
   ```

### Phase 2: AI Analysis
1. **Use Football Events Analyzer** (from `1_game_events`)
   - Gemini AI analysis of each clip
   - Focus on critical football events only
   - Consistent event categorization

2. **Event Types to Detect**:
   - **Goals** (with team/player if visible)
   - **Shots on target** (saved/blocked/missed)
   - **Turnovers** (possession changes)
   - **Penalties** (awarded/taken)
   - **Cards** (yellow/red)
   - **Major fouls** (free kicks)
   - **Corner kicks**
   - **Substitutions**
   - **Tactical changes**

### Phase 3: Synthesis
1. **Combine all clip analyses**
   - Chronological timeline
   - Event statistics
   - Match flow analysis

2. **Output Formats**:
   - `events_timeline.json` (structured data)
   - `events_timeline.txt` (human-readable)
   - `event_statistics.json` (match stats)

## Implementation Plan

### Step 1: Video Segmentation Script
```python
# Create video_segmentation.py
# Split Game298_0601_p1.mp4 into 30-second clips
# Use ffmpeg with precise timing
```

### Step 2: Analysis Pipeline
```python
# Use existing football_events_analyzer.py
# Process all clips in Game298_0601
# Generate individual analysis files
```

### Step 3: Synthesis
```python
# Use existing football_events_synthesis.py
# Combine all analyses into timeline
# Generate final reports
```

## Expected Outputs

### Timeline Structure
```
00:40 - Save by goalkeeper - SAVE
00:48 - Goal scored by Team A - GOAL
02:52 - Save by goalkeeper - SAVE
03:06 - Goal scored by Team B - GOAL
...
```

### Statistics
- Total events detected
- Goals per team
- Shot accuracy
- Possession changes
- Fouls and cards
- Set piece efficiency

### Benefits Over Manual Approach
1. **Comprehensive Coverage**: AI detects events you might miss
2. **Consistent Categorization**: Standardized event types
3. **Rich Descriptions**: Detailed event descriptions
4. **Statistical Analysis**: Quantitative match insights
5. **Searchable Timeline**: Easy to find specific moments

## File Structure
```
Game298_0601/
├── Game298_0601_p1.mp4                    # Original video
├── Game298_0601_p1_timestamps.csv         # Manual timestamps (reference)
├── clips/                                  # Generated 30-second clips
│   ├── Game298_0601_clip_001.mp4
│   ├── Game298_0601_clip_002.mp4
│   └── ...
├── analysis/                               # AI analysis outputs
│   ├── events_analysis_001.txt
│   ├── events_analysis_002.txt
│   └── ...
├── synthesis/                              # Final outputs
│   ├── events_timeline.
│   ├── events_timeline.txt
│   └── event_statistics.json
└── README.md                              # This file
```

## Next Steps

1. **Create video segmentation script**
2. **Run analysis pipeline**
3. **Compare AI results with manual timestamps**
4. **Generate comprehensive match report**
5. **Validate accuracy and completeness**

## Questions to Address

1. **Do we have the uncorrupted 15-minute game?**
   - Current file: 15 minutes 17 seconds (917.6 seconds)
   - Appears to be complete based on manual timestamps ending at 15:17
   - Need to verify video quality and completeness

2. **Video Quality Assessment**
   - Check for corruption or missing segments
   - Verify audio/video sync
   - Ensure playable throughout

3. **Manual vs AI Comparison**
   - Compare AI-detected events with manual timestamps
   - Validate accuracy of AI analysis
   - Identify any missed events

## Success Metrics

- **Event Detection Rate**: AI should find more events than manual (10 → 50+)
- **Accuracy**: AI events should align with manual timestamps
- **Completeness**: No major events missed
- **Usefulness**: Rich, searchable timeline for analysis 