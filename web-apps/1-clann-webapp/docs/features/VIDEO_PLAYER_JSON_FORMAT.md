# Complete Guide: Adding Events to Games

## Overview

This is the **complete guide** for adding analysis events to games in the ClannAI platform. Events power the interactive video player, allowing users to jump to specific moments and see game highlights.

**What you'll learn:**
- ✅ How to format event JSON correctly
- ✅ Step-by-step upload process via company dashboard  
- ✅ All supported event types and their colors
- ✅ Troubleshooting common issues
- ✅ Real-world examples and best practices

## 🚀 Quick Start: Adding Events to a Game

### Step 1: Access Company Dashboard
1. **Login** with company credentials:
   - Email: `admin@clann.ai` or `analyst@clann.ai` 
   - Password: `demo123`
2. **Navigate** to Company Dashboard
3. **Find the game** you want to add events to

### Step 2: Upload Events
1. **Click "Add Analysis"** (purple button) next to the game
2. **Paste your JSON** in the textarea that opens
3. **Click "Add Analysis"** to save
4. **Game status** automatically changes to "analyzed"

### Step 3: Test Video Player
1. **User can now** navigate to the game page
2. **Video player shows** colored event markers on timeline
3. **Events sidebar** lists all events with click-to-jump functionality

### Step 4: Verify Events Work
- ✅ Timeline has colored dots for each event
- ✅ Events sidebar shows on the right
- ✅ Clicking events jumps to correct timestamp
- ✅ Current event highlights as video plays

## Supported Formats

The video player supports **two JSON formats** for backwards compatibility:

### Format 1: Direct Array (Recommended)
```json
[
  {
    "type": "goal",
    "timestamp": 330,
    "description": "Amazing strike from midfield",
    "player": "Smith #9"
  },
  {
    "type": "yellow_card", 
    "timestamp": 765,
    "description": "Tactical foul",
    "player": "Jones #3"
  }
]
```

### Format 2: Wrapped Events Object (Legacy)
```json
{
  "events": [
    {
      "type": "goal",
      "timestamp": 330,
      "description": "Amazing strike from midfield", 
      "player": "Smith #9"
    },
    {
      "type": "yellow_card",
      "timestamp": 765,
      "description": "Tactical foul",
      "player": "Jones #3"
    }
  ]
}
```

## Event Object Structure

Each event must include these fields:

### Required Fields
- **`type`** (string): Event type (see supported types below)
- **`timestamp`** (number): Time in seconds from start of video

### Optional Fields  
- **`description`** (string): Human-readable event description
- **`player`** (string): Player involved (name, number, or both)
- **`team`** (string): Team identifier for score tracking ("red", "black", "home", "away", etc.)

## Supported Event Types

The video player color-codes events based on type:

| Type | Color | Description |
|------|-------|-------------|
| `goal` | 🟢 Green | Goals scored |
| `shot` | 🔵 Blue | Shot attempts |
| `foul` | 🔴 Red | Fouls committed |
| `yellow_card` | 🟡 Yellow | Yellow card shown |
| `red_card` | 🔴 Dark Red | Red card shown |
| `substitution` | 🟣 Purple | Player substitution |
| `corner` | 🔄 Cyan | Corner kick |
| `offside` | 🟠 Orange | Offside call |
| `save` | 🟦 Light Blue | Goalkeeper save |

**Note:** Unknown event types default to gray color.

## Complete Example

```json
[
  {
    "type": "shot",
    "timestamp": 15,
    "description": "Early shot attempt",
    "player": "Wilson #7"
  },
  {
    "type": "goal", 
    "timestamp": 17,
    "description": "Opening goal from close range",
    "player": "Wilson #7"
  },
  {
    "type": "foul",
    "timestamp": 120,
    "description": "Defensive challenge in midfield",
    "player": "Miller #3"
  },
  {
    "type": "yellow_card",
    "timestamp": 122,
    "description": "Caution for reckless challenge", 
    "player": "Miller #3"
  },
  {
    "type": "corner",
    "timestamp": 300,
    "description": "Corner kick from left side",
    "player": "Davis #11"
  },
  {
    "type": "substitution",
    "timestamp": 450,
    "description": "Tactical substitution",
    "player": "Rodriguez #12 for Wilson #7"
  },
  {
    "type": "shot",
    "timestamp": 600,
    "description": "Long range effort",
    "player": "Anderson #8"
  },
  {
    "type": "save",
    "timestamp": 602,
    "description": "Excellent save by goalkeeper",
    "player": "Goalkeeper #1"
  }
]
```

## Video Player Features

When properly formatted, the JSON data enables:

✅ **Timeline Markers**: Colored dots on the video progress bar  
✅ **Events Sidebar**: Scrollable list of all events  
✅ **Click Navigation**: Click events to jump to timestamps  
✅ **Auto-Highlighting**: Current event highlighted as video plays  
✅ **Team-Based Scoring**: Live score tracking by team (Red: 2 - Black: 1)  
✅ **Event Filtering**: Filter by event type (future feature)  
✅ **Keyboard Navigation**: Previous/next event buttons

## Team-Based Score Tracking

When events include a `team` field, the video player will:

- **Track goals separately** for each team
- **Display live scores** in header: "Red: 2 - Black: 1" 
- **Update in real-time** as video plays through goal events
- **Color-code teams** (red text for red team, blue for black team)
- **Support any team names**: "red"/"black", "home"/"away", "team1"/"team2"

**Example with teams:**
```json
[
  {"type": "goal", "timestamp": 120, "player": "#9", "team": "red"},
  {"type": "goal", "timestamp": 300, "player": "#11", "team": "black"}
]
```
**Result:** Header shows "Red: 1 - Black: 1" after 300 seconds  

## Database Storage

Store in PostgreSQL as JSONB:

```sql
-- Direct array format (recommended)
UPDATE games SET ai_analysis = '[
  {"type": "goal", "timestamp": 120, "description": "Great goal!", "player": "#9"}
]'::jsonb WHERE id = 'game-id';

-- Convert legacy format to direct array
UPDATE games SET ai_analysis = ai_analysis->'events' 
WHERE jsonb_typeof(ai_analysis) = 'object' 
AND ai_analysis ? 'events';
```

## Company Dashboard Upload

When uploading analysis via the company dashboard:

1. **Paste JSON** in the analysis textarea
2. **Format will be auto-detected** (array or wrapped)
3. **Game status** automatically set to "analyzed"
4. **Events become clickable** in video player

## Validation

The video player validates:
- ✅ Data is an array or has `events` property
- ✅ Each event has required `type` and `timestamp` 
- ✅ Timestamps are numeric (seconds)
- ⚠️ Invalid events are skipped silently

## Best Practices

1. **Use direct array format** for new implementations
2. **Sort events by timestamp** (ascending order)
3. **Use consistent event types** from the supported list
4. **Include player info** when available for better UX
5. **Keep descriptions concise** but descriptive
6. **Use seconds for timestamps** (not minutes:seconds)

## 🔧 Troubleshooting & Common Issues

### Events Not Showing in Video Player

**❌ Problem:** No event markers on timeline  
**✅ Solutions:**
- Verify JSON is valid (use JSON validator)
- Check game status is "analyzed" in database
- Ensure `timestamp` values are numbers (not strings like "120")
- Confirm events array is not empty

### Colors Not Working Correctly

**❌ Problem:** All events show as gray dots  
**✅ Solutions:**
- Use exact event types: `"goal"` not `"Goal"` or `"GOAL"`
- Check spelling: `"yellow_card"` not `"yellowcard"`
- Refer to supported types table above

### Can't Click Events / Jump Not Working

**❌ Problem:** Clicking events doesn't jump to timestamp  
**✅ Solutions:**
- Verify `timestamp` is a number: `"timestamp": 120` not `"timestamp": "120"`
- Check timestamps are within video duration
- Ensure video player has loaded properly

### JSON Upload Fails

**❌ Problem:** "Invalid JSON format" error  
**✅ Solutions:**
```json
// ❌ WRONG - Missing quotes around keys
[{type: "goal", timestamp: 120}]

// ✅ CORRECT - Proper JSON format  
[{"type": "goal", "timestamp": 120}]
```

### Events Out of Order

**❌ Problem:** Events don't highlight correctly as video plays  
**✅ Solution:** Sort events by timestamp:
```json
// ✅ CORRECT - Chronological order
[
  {"type": "shot", "timestamp": 30},
  {"type": "goal", "timestamp": 45}, 
  {"type": "foul", "timestamp": 120}
]
```

## ⚠️ Common Mistakes to Avoid

1. **String timestamps:** Use `120` not `"120"` or `"2:00"`
2. **Wrong event types:** Use `"yellow_card"` not `"yellow"` 
3. **Missing required fields:** Always include `type` and `timestamp`
4. **Invalid JSON:** Use online JSON validator to check format
5. **Events past video end:** Don't add events beyond video duration
6. **Duplicate timestamps:** Multiple events at same time are OK but may overlap visually

## 🚨 System Behavior Notes

- **Automatic detection:** System accepts both `[...]` and `{"events": [...]}` formats
- **Error handling:** Invalid events are skipped silently (check browser console)
- **Performance:** 100+ events work fine, but consider user experience
- **Updates:** Re-uploading JSON completely replaces previous events
- **Permissions:** Only company users can upload/modify events

## 🎯 Real-World Workflow

### Typical Analysis Process
1. **VM Analysis** generates events JSON from video
2. **Company user** reviews and uploads via dashboard
3. **Game status** changes from "pending" → "analyzed"
4. **Users access** enhanced video player with events
5. **Click events** to jump to key moments

### Converting Time Formats
If your analysis system outputs `MM:SS` format, convert to seconds:

```javascript
// Convert "05:30" to 330 seconds
function timeToSeconds(timeString) {
  const [minutes, seconds] = timeString.split(':').map(Number);
  return (minutes * 60) + seconds;
}

// Example: "12:45" → 765 seconds
```

## 📝 Ready-to-Use Examples

### Example 1: Quick Test (Copy & Paste)
```json
[
  {"type": "shot", "timestamp": 30, "description": "Early chance", "player": "#9", "team": "red"},
  {"type": "goal", "timestamp": 32, "description": "1-0 Goal!", "player": "#9", "team": "red"}, 
  {"type": "yellow_card", "timestamp": 180, "description": "Booking", "player": "#5", "team": "black"},
  {"type": "corner", "timestamp": 300, "description": "Corner kick", "player": "#7", "team": "red"},
  {"type": "goal", "timestamp": 450, "description": "Equalizer!", "player": "#11", "team": "black"},
  {"type": "shot", "timestamp": 600, "description": "Long shot", "player": "#11", "team": "black"},
  {"type": "goal", "timestamp": 720, "description": "Winner!", "player": "#9", "team": "red"}
]
```

### Example 2: Detailed Match Analysis
```json
[
  {"type": "shot", "timestamp": 15, "description": "Opening shot wide of target", "player": "Martinez #10"},
  {"type": "goal", "timestamp": 127, "description": "Header from corner kick", "player": "Johnson #4"},
  {"type": "foul", "timestamp": 245, "description": "Sliding tackle in midfield", "player": "Silva #8"},
  {"type": "yellow_card", "timestamp": 247, "description": "Caution for reckless challenge", "player": "Silva #8"},
  {"type": "corner", "timestamp": 380, "description": "Corner won after deflected shot", "player": "Wilson #7"},
  {"type": "save", "timestamp": 382, "description": "Diving save from close range", "player": "Goalkeeper #1"},
  {"type": "substitution", "timestamp": 1890, "description": "Tactical change for final push", "player": "Rodriguez #11 for Martinez #10"},
  {"type": "shot", "timestamp": 2100, "description": "Long-range effort over the bar", "player": "Rodriguez #11"},
  {"type": "foul", "timestamp": 2450, "description": "Professional foul to stop counter", "player": "Brown #3"},
  {"type": "red_card", "timestamp": 2453, "description": "Second yellow card", "player": "Brown #3"},
  {"type": "goal", "timestamp": 2670, "description": "Free kick into top corner", "player": "Wilson #7"}
]
```

### Example 3: Basketball Events
```json
[
  {"type": "shot", "timestamp": 45, "description": "3-pointer from the arc", "player": "Smith #23"},
  {"type": "goal", "timestamp": 47, "description": "3-pointer scores", "player": "Smith #23"},
  {"type": "foul", "timestamp": 120, "description": "Defensive foul on drive", "player": "Johnson #15"},
     {"type": "substitution", "timestamp": 300, "description": "Fresh legs off the bench", "player": "Williams #8 for Davis #12"}
 ]
 ``` 

## 📋 Quick Reference Card

### Essential Format
```json
[
  {"type": "EVENT_TYPE", "timestamp": SECONDS, "description": "Text", "player": "#Number"}
]
```

### Event Types & Colors
- `goal` 🟢 | `shot` 🔵 | `foul` 🔴 | `yellow_card` 🟡 | `red_card` 🔴  
- `substitution` 🟣 | `corner` 🔄 | `save` 🟦 | `offside` 🟠

### Upload Process
1. Login: `admin@clann.ai` / `demo123`
2. Company Dashboard → Find Game → "Add Analysis" 
3. Paste JSON → Submit → Game status becomes "analyzed"

### Validation Checklist
- ✅ Valid JSON format (use validator)
- ✅ Timestamps as numbers (not strings)  
- ✅ Event types from supported list
- ✅ Events in chronological order
- ✅ All events within video duration

### Common Fixes
- **No events showing:** Check game status = "analyzed"
- **Gray dots:** Fix event type spelling/case
- **Can't click:** Convert timestamp strings to numbers
- **JSON error:** Add quotes around all keys and string values 