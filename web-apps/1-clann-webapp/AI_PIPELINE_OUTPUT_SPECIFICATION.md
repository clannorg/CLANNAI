# AI Pipeline Output Specification for ClannAI WebApp

**CRITICAL**: This document defines the EXACT JSON formats your AI pipeline must output for the webapp to display properly.

## 📋 Required Files Overview

Your AI pipeline must generate these 4 files and upload them to S3:

1. **Video File** (`.mp4`) - The processed match video
2. **Events File** (`.json`) - Timeline events for video player
3. **Tactical Analysis File** (`.json`) - Team insights and analysis  
4. **Metadata File** (`.json`) - Master config pointing to other files

---

## 1. 🎥 Video File Format

**File**: `{match-id}-video.mp4`  
**Location**: `s3://bucket/analysis-videos/`  
**Format**: Standard MP4 video file

---

## 2. ⚽ Events File Format

**File**: `{match-id}-web_events_array-json.json`  
**Location**: `s3://bucket/analysis-data/`  
**Format**: JSON Array

### Required Structure:
```json
[
  {
    "type": "goal",
    "timestamp": 930,
    "team": "red",
    "description": "Header from corner kick by striker",
    "player": "Striker #9"
  },
  {
    "type": "shot", 
    "timestamp": 1245,
    "team": "blue",
    "description": "Long range effort saved",
    "player": "Midfielder #8"
  }
]
```

### Field Specifications:
- **`type`** (required): Event type - `"goal"`, `"shot"`, `"foul"`, `"yellow_card"`, `"red_card"`, `"corner"`, `"save"`, `"substitution"`, `"offside"`
- **`timestamp`** (required): Time in seconds from video start (e.g., 15:30 = 930 seconds)
- **`team`** (required): Team color identifier - `"red"`, `"blue"`, `"white"`, `"black"`
- **`description`** (optional): Human-readable description (max 100 chars)
- **`player`** (optional): Player name/number

---

## 3. 🧠 Tactical Analysis File Format

**File**: `{match-id}-11_tactical_analysis-json.json`  
**Location**: `s3://bucket/analysis-data/`  
**Format**: JSON Object

### Required Structure:
```json
{
  "tactical_analysis": {
    "red_team": {
      "team_name": "East London Ballers",
      "strengths": [
        "Effective counter-attacks from defensive thirds",
        "Strong aerial presence on set pieces"
      ],
      "weaknesses": [
        "Vulnerable to pace on the flanks",
        "Loose passing under pressure"
      ],
      "key_players": [
        "Central striker: Clinical finishing",
        "Right winger: Pace and crossing"
      ],
      "tactical_setup": "4-4-2 formation with emphasis on...",
      "performance_summary": "Controlled tempo and created..."
    },
    "blue_team": {
      "team_name": "Opposition FC",
      "strengths": ["Solid defensive shape"],
      "weaknesses": ["Lack of creativity in attack"],
      "key_players": ["Goalkeeper: Key saves"],
      "tactical_setup": "5-3-2 defensive formation",
      "performance_summary": "Struggled to create chances"
    }
  },
  "match_overview": {
    "final_score": "East London Ballers 3 - Opposition FC 1",
    "key_tactical_story": "Match narrative paragraph"
  },
  "key_moments": [
    "Opening goal changed momentum at 15:30",
    "Second half dominance by home team"
  ],
  "manager_recommendations": {
    "red_team": [
      "Work on defensive transitions",
      "Improve set piece defending"
    ],
    "blue_team": [
      "Focus on creative midfield play",
      "Practice finishing in final third"
    ]
  }
}
```

---

## 4. 📊 Metadata File Format

**File**: `{match-id}-match_metadata-json.json`  
**Location**: `s3://bucket/analysis-data/`  
**Format**: JSON Object

### Required Structure:
```json
{
  "match_id": "leo1",
  "video_url": "https://bucket.s3.region.amazonaws.com/analysis-videos/leo1-video.mp4",
  "events_url": "https://bucket.s3.region.amazonaws.com/analysis-data/leo1-web_events_array-json.json",
  "tactical_url": "https://bucket.s3.region.amazonaws.com/analysis-data/leo1-11_tactical_analysis-json.json",
  "teams": {
    "red_team": {
      "name": "East London Ballers",
      "jersey_color": "blue"
    },
    "blue_team": {
      "name": "Opposition FC", 
      "jersey_color": "orange"
    }
  },
  "counts": {
    "goals": 4,
    "shots": 12,
    "fouls": 8
  },
  "match_type": "5-a-side",
  "final_score": "East London Ballers 3 - Opposition FC 1"
}
```

### Critical Fields:
- **`video_url`** (required): Full S3 URL to video file
- **`events_url`** (required): Full S3 URL to events JSON
- **`tactical_url`** (required): Full S3 URL to tactical analysis JSON
- **`teams.red_team.name`** (required): Actual team name
- **`teams.red_team.jersey_color`** (required): Color name (e.g., "blue", "red", "white", "orange")
- **`teams.blue_team.*`** (required): Same structure for opposition

---

## 🎯 Team Color Mapping Rules

### AI Pipeline Output:
- Events use color identifiers: `"red"`, `"blue"`, `"white"`, `"black"`
- First team (home) = `"red"`
- Second team (away) = `"blue"`

### Jersey Color Names:
Use simple color names in metadata:
- ✅ `"blue"`, `"red"`, `"white"`, `"orange"`, `"black"`, `"yellow"`, `"green"`
- ❌ `"blue and turquoise"`, `"non-bibs / colours"`

---

## ✅ Validation Checklist

Before uploading, verify:

- [ ] All 4 files exist on S3
- [ ] All URLs in metadata are publicly accessible
- [ ] Events array has required `type` and `timestamp` fields
- [ ] Tactical analysis has `red_team` and `blue_team` objects
- [ ] Team names match between files
- [ ] Jersey colors are simple color names
- [ ] Timestamps are in seconds (not MM:SS format)

---

## 🚨 Common Errors to Avoid

1. **Missing URLs in metadata** - Causes 500 errors
2. **Wrong timestamp format** - Use seconds, not "15:30"
3. **Complex color descriptions** - Use simple color names
4. **Mismatched team names** - Keep consistent across files
5. **Missing required fields** - All marked fields are mandatory

---

**This specification is extracted directly from the webapp code and represents the exact format requirements. Any deviation will cause display issues or errors.**