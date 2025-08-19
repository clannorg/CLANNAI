# AI Pipeline Output Format Specification

## Overview
This document defines the exact JSON formats your AI pipeline must output for the ClannAI web app, based on the working East London Ballers example.

## Required Files

Your AI must upload 3 files to S3 and provide 1 metadata file:

1. **`match_metadata.json`** - Main metadata with URLs to other files
2. **`web_events_array.json`** - Timeline events for video player
3. **`11_tactical_analysis.json`** - Team analysis and insights
4. **Video file** - The processed match video

## 1. Match Metadata Format (`match_metadata.json`)

**Purpose:** Main file that the web app reads first. Contains team info and URLs to all other analysis files.

```json
{
  "match_id": "20250523-match-23-may-2025-3fc1de88",
  "teams": {
    "red_team": {
      "name": "East London Ballers",
      "jersey_color": "blue and turquoise"
    },
    "blue_team": {
      "name": "Opposition", 
      "jersey_color": "white"
    }
  },
  "counts": {
    "goals": 2,
    "shots": 12
  },
  "files": {
    "video_mp4": "https://end-nov-webapp-clann.s3.amazonaws.com/analysis-videos/20250523-match-23-may-2025-3fc1de88-video-mp4.mp4",
    "web_events_array_json": "https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/20250523-match-23-may-2025-3fc1de88-web_events_array-json.json",
    "tactical_json": "https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/20250523-match-23-may-2025-3fc1de88-11_tactical_analysis-json.json"
  },
  "final_score": "1-4",
  "match_summary": "Match overview:\n\nMatch: East London Ballers vs Opposition\nFinal Score: 1-4\n..."
}
```

### Key Points:
- **`jersey_color`**: Used for UI colors (e.g., "blue and turquoise" → blue timeline dots)
- **`files.web_events_array_json`**: MUST point to the events file
- **`files.tactical_json`**: MUST point to the tactical analysis file
- **`files.video_mp4`**: MUST point to the processed video
- **`match_id`**: Should be unique identifier for this match

## 2. Events Format (`web_events_array.json`)

**Purpose:** Timeline events that appear on the video player. Each event creates a clickable dot on the timeline.

```json
[
  {
    "type": "goal",
    "timestamp": 3722,
    "team": "white",
    "description": "Rebound after shot saved"
  },
  {
    "type": "shot", 
    "timestamp": 6091,
    "team": "blue",
    "description": "East London Ballers - Shot on goal"
  },
  {
    "type": "foul",
    "timestamp": 1188,
    "team": "blue", 
    "description": "East London Ballers commits a foul"
  }
]
```

### Key Points:
- **`timestamp`**: Seconds from match start (e.g., 3722 = 62:02)
- **`team`**: MUST match jersey colors from metadata ("blue", "white", etc.)
- **`type`**: Supported types: `goal`, `shot`, `foul`, `corner`, `throw_in`, `yellow_card`, `red_card`, `offside`
- **Events are sorted by timestamp** (ascending order)

### Team Color Mapping:
```
East London Ballers (jersey: "blue and turquoise") → team: "blue"
Opposition (jersey: "white") → team: "white"
```

## 3. Tactical Analysis Format (`11_tactical_analysis.json`)

**Purpose:** Team insights displayed in the "Insights" tab of the web app.

```json
{
  "team_a": {
    "team_name": "East London Ballers",
    "team_color": "blue",
    "strengths": [
      "Ability to break through defense",
      "Counter-attacking potential"
    ],
    "weaknesses": [
      "Inability to convert chances", 
      "Defensive vulnerabilities"
    ],
    "key_players": [
      "Attacking midfielders"
    ],
    "tactical_setup": "Attempted to build from the back and launch counter-attacks.",
    "performance_summary": "Showed moments of attacking promise but struggled to convert chances."
  },
  "team_b": {
    "team_name": "Opposition",
    "team_color": "white", 
    "strengths": ["Clinical finishing"],
    "weaknesses": ["Discipline (red card)"],
    "key_players": ["Attacking forwards"],
    "tactical_setup": "Established attacking intent early.",
    "performance_summary": "Dominated the scoring with clinical finishing."
  },
  "match_summary": {
    "final_score": "East London Ballers 1 - 4 Opposition",
    "key_moments": [
      "Opposition's opening header at 32:48",
      "East London Ballers' goal at 41:19"
    ],
    "turning_points": [
      "Opposition's early goal surge"
    ],
    "overall_narrative": "Opposition dominated the match with clinical finishing..."
  }
}
```

### Key Points:
- **`team_color`**: Should match the jersey color identifier ("blue", "white")
- **Arrays can have multiple items** (strengths, weaknesses, etc.)
- **`key_moments`** should reference actual timestamps when possible

## Why This Format Works

1. **Team Color Consistency**: Jersey colors are used consistently across all files
2. **URL Structure**: All analysis files are referenced by URL in the metadata
3. **Timeline Integration**: Events timestamp format works directly with video player
4. **UI Mapping**: Team colors map directly to UI elements (timeline dots, team badges)

## Upload Process

1. **Process match** → Generate all 4 files
2. **Upload files to S3** → Get URLs for each file
3. **Create metadata.json** → Include all S3 URLs
4. **Upload metadata to S3** → Get final metadata URL
5. **Call web app API** → `/api/games/{id}/upload-metadata` with metadata URL

## Common Issues to Avoid

- ❌ **Wrong team colors**: Using team names instead of jersey colors in events
- ❌ **Missing URLs**: Not including all required file URLs in metadata
- ❌ **Timestamp format**: Using MM:SS instead of total seconds
- ❌ **Unsorted events**: Events not in chronological order
- ❌ **Invalid event types**: Using types not supported by the web app

## Testing Your Format

Use the East London Ballers game as your reference - if your format matches theirs exactly, it will work in the web app.