# 🎯 S3 FILES SCHEMA SPECIFICATION
## For ClannAI Website Display (Based on Leo1 Success)

## 📁 **REQUIRED S3 FILES:**

### 1. **🎥 `{match-id}-video-mp4.mp4`**
- **Purpose**: Main match video
- **Format**: MP4 video file
- **Location**: `analysis-videos/` bucket folder

### 2. **📋 `{match-id}-match_metadata-json.json`**
- **Purpose**: Match overview, teams, scores, file references
- **Format**: JSON
- **Location**: `analysis-data/` bucket folder

```json
{
  "match_id": "string",
  "teams": {
    "red_team": {
      "name": "string",           // Team name for UI red side
      "jersey_color": "string"    // Visual description for AI
    },
    "blue_team": {
      "name": "string",           // Team name for UI blue side  
      "jersey_color": "string"    // Visual description for AI
    }
  },
  "counts": {
    "goals": number,              // Total goals in match
    "shots": number               // Total shots in match
  },
  "files": {
    "video_mp4": "string",                    // S3 URL to video
    "web_events_array_json": "string",       // S3 URL to events
    "web_events_json": null,                 // Legacy (unused)
    "timeline_txt": null,                    // Optional full timeline
    "ground_truth_json": null,               // Optional VEO data
    "other_events_txt": null,                // Optional other events
    "tactical_json": null                    // Optional tactical file
  },
  "final_score": "string",                   // Human readable score
  "match_summary": "string",                 // Match narrative paragraph
  "total_events": number,                    // Total events count
  "total_goals": number,                     // Total goals count
  "team_scores": {
    "{team_name}": number,                   // Goals per team
    "{team_name}": number
  }
}
```

### 3. **⚡ `{match-id}-web_events_array-json.json`**
- **Purpose**: Timeline events for website display
- **Format**: JSON Array
- **Location**: `analysis-data/` bucket folder

```json
[
  {
    "timestamp": number,                     // Seconds from match start
    "type": "string",                       // "goal", "shot", "foul", etc.
    "team": "string",                       // Team name (matches metadata)
    "description": "string",                // Human readable description
    "excitement_level": number,             // 1-10 excitement rating
    "original_team_name": "string"          // Original jersey description
  }
]
```

### 4. **🧠 `{match-id}-tactical_analysis-json.json`**
- **Purpose**: Team analysis and tactical insights
- **Format**: JSON
- **Location**: `analysis-data/` bucket folder

```json
{
  "tactical_analysis": {
    "red_team": {
      "team_name": "string",
      "strengths": ["string", "string"],     // Array of strength descriptions
      "weaknesses": ["string", "string"],   // Array of weakness descriptions
      "key_players": ["string", "string"],  // Array of key player descriptions
      "tactical_setup": "string",           // Overall tactical approach
      "performance_summary": "string"       // Team performance summary
    },
    "blue_team": {
      "team_name": "string",
      "strengths": ["string", "string"],
      "weaknesses": ["string", "string"],
      "key_players": ["string", "string"],
      "tactical_setup": "string",
      "performance_summary": "string"
    },
    "match_summary": {
      "final_score": "string",              // Final score display
      "match_story": "string",              // Overall match narrative
      "key_moments": ["string", "string"],  // Important match moments
      "tactical_themes": ["string", "string"] // Tactical patterns observed
    },
    "recommendations": {
      "red_team": ["string", "string"],     // Improvement suggestions
      "blue_team": ["string", "string"]     // Improvement suggestions
    }
  }
}
```

## 🎯 **KEY REQUIREMENTS:**

### **Team Mapping:**
- `metadata.teams.red_team.name` → Website red side
- `metadata.teams.blue_team.name` → Website blue side
- `events[].team` must match team names exactly

### **Event Types:**
- `"goal"` - Goals scored
- `"shot"` - Shots on goal
- `"foul"` - Fouls committed
- `"card"` - Yellow/red cards
- `"corner"` - Corner kicks
- `"penalty"` - Penalty kicks

### **Timestamp Format:**
- Seconds from match start (integer)
- Example: `181` = 3 minutes 1 second

### **File Naming Convention:**
- `{match-id}-{file-type}-{format}.{extension}`
- Example: `dalkey-match_metadata-json.json`

## 🚀 **WEBSITE INTEGRATION:**

1. **Database** stores S3 URLs in `games.metadata.tactical_files`
2. **Frontend** loads files directly from S3 URLs
3. **Events** populate the timeline component
4. **Tactical** analysis populates insights panels
5. **Metadata** provides match info and team mapping

## ✅ **VALIDATION CHECKLIST:**

- [ ] Video file accessible at S3 URL
- [ ] Metadata has both red_team and blue_team
- [ ] Events array has at least 1 event
- [ ] All event.team values match metadata team names
- [ ] Tactical analysis has both teams
- [ ] All S3 URLs return 200 status
- [ ] File naming follows convention
