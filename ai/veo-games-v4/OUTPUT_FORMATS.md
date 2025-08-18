# VEO Games v3 - Output Formats Specification

Clean separation: **Mega analyzer outputs plain text**, **formatter converts to JSON**.

## Part 1: Mega Analyzer Outputs (Plain Text)

### `mega_events.txt`
Natural language event descriptions, one per line:
```
15:30 - GOAL: East London Ballers - Header from corner kick by striker
18:45 - SHOT: East London Ballers - Long range effort saved by goalkeeper  
22:10 - FOUL: Opposition FC - Late tackle in midfield, yellow card shown
35:20 - CORNER: East London Ballers - Cross cleared, corner awarded
```

**Format:** `MM:SS - TYPE: Team Name - Natural description`
- **Time:** Minutes:seconds from match start
- **Type:** GOAL, SHOT, FOUL, CORNER, SAVE, CARD, etc.
- **Team:** Real team name (not "red"/"blue")
- **Description:** Human-readable event description

### `mega_tactical.txt`
Tactical analysis in plain text sections:
```
=== EAST LONDON BALLERS ===
Strengths:
- Effective counter-attacks from defensive thirds
- Strong aerial presence on set pieces
- Quick transitions through midfield

Weaknesses:  
- Vulnerable to pace on the flanks
- Loose passing under pressure

Key Players:
- Central striker: Clinical finishing, good hold-up play
- Right winger: Pace and crossing ability

=== OPPOSITION FC ===
Strengths:
- Solid defensive shape
- Good pressing in final third

Weaknesses:
- Lack of creativity in attack
- Poor set piece defending

=== MATCH SUMMARY ===
Final Score: East London Ballers 3 - Opposition FC 1

Key Moments:
- Opening goal changed momentum at 15:30
- Opposition equalized against run of play at 38:20
- Second half dominance by East London Ballers

Overall: East London Ballers controlled tempo and created better chances throughout.
```

### `mega_summary.txt`
Match context and metadata:
```
Match: East London Ballers vs Opposition FC
Date: 2025-05-23
Venue: London Community Ground
Duration: 90 minutes

Jersey Colors:
- East London Ballers: Red and white striped
- Opposition FC: All blue

Final Score: 3-1
Goals: 5 total
Shots: 18 total  
Fouls: 15 total
Corners: 10 total
Cards: 2 yellow, 0 red
```

## Part 2: Webapp Formatter Outputs (JSON)

The `format_for_webapp.py` script reads the plain text files and converts them to:

### `web_events_array.json` 
```json
[
  {
    "type": "goal",
    "timestamp": 930,
    "team": "blue", 
    "description": "Header from corner kick by striker",
    "player": "Striker"
  }
]
```

**Conversion rules:**
- `15:30` → `timestamp: 930` (15*60 + 30)
- `East London Ballers` → `team: "blue"` (map to jersey color for reliability)
- `Opposition FC` → `team: "red"` (map to jersey color for reliability)
- `GOAL` → `type: "goal"` (lowercase)

### `11_tactical_analysis.json`
```json
{
  "red_team": {
    "team_name": "East London Ballers",
    "strengths": ["Effective counter-attacks from defensive thirds", "..."],
    "weaknesses": ["Vulnerable to pace on the flanks", "..."],
    "key_players": ["Central striker: Clinical finishing", "..."],
    "tactical_setup": "4-4-2 formation with emphasis on...",
    "performance_summary": "Controlled tempo and created..."
  },
  "blue_team": { /* ... */ },
  "match_summary": {
    "final_score": "East London Ballers 3 - Opposition FC 1",
    "key_moments": ["Opening goal changed momentum at 15:30", "..."],
    "turning_points": ["Second half dominance", "..."],
    "overall_narrative": "East London Ballers controlled tempo..."
  }
}
```

## Part 3: Pipeline Flow

1. **Mega analyzer** → Plain text (natural language, easy to read/debug)
2. **Formatter** → JSON (structured data for webapp)
3. **S3 uploader** → Uploads JSON files  
4. **Metadata writer** → Creates match_metadata.json

**Benefits:**
- Mega analyzer stays simple (just natural language)
- Formatter handles all JSON complexity
- Easy to debug plain text outputs
- Clean separation of concerns