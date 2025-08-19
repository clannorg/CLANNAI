# Footy1 - 5-a-Side Football Analysis

Analyze **5-a-side games** focusing on goals and cool moments. Simple 5-step pipeline using Gemini.

## What This Analyzes

- 5-a-side football matches
- Indoor football / Futsal  
- 7-a-side games
- Casual pickup games
- **Focus: Goals and particularly cool moments**

## How It Works

### 5-Step Pipeline (Same approach as v4, but 5-a-side focused)

1. **Setup teams** - You manually enter team colors ("orange bibs vs blue shirts")
2. **Make 15-second clips** - Split video into segments
3. **Analyze each clip** - Gemini describes what's happening, focusing on goals/cool moments
4. **Synthesize highlights** - Gemini 2.5 Pro identifies the important moments from all descriptions
5. **Format for webapp** - Structure data for web display

### Team Setup
- **Manual team entry** - You tell it "orange bibs vs blue shirts" etc.
- No complex team detection needed - you know your teams!

## Usage

```bash
# Navigate to pipeline
cd ai/footy1/pipeline
conda activate hooper-ai

# 1. Set up teams (manual input)
python 1_setup_teams.py <match-id>

# 2. Make clips  
python 2_make_clips.py <video-path> <match-id>

# 3. Analyze clips (focus on goals/cool moments)
python 3_analyze_clips.py <match-id>

# 4. Synthesize highlights
python 4_synthesize_highlights.py <match-id>

# 5. Format for webapp
python 5_format_webapp.py <match-id>
```

## Example Workflow

```bash
# Setup
python 1_setup_teams.py "sunday-league-game-1"
# Enter: Team A = "Orange bibs", Team B = "Blue shirts"

# Process video
python 2_make_clips.py "/path/to/game.mp4" "sunday-league-game-1"
python 3_analyze_clips.py "sunday-league-game-1"
python 4_synthesize_highlights.py "sunday-league-game-1"
python 5_format_webapp.py "sunday-league-game-1"
```

## What You Get

### **🎯 For Highlights**
- **Goals** - All goal moments with timestamps
- **Cool moments** - Skills, saves, near-misses
- **Timeline** - When exciting things happened

### **📊 For Webapp**
- **`highlights.json`** - Key moments for timeline
- **`match_summary.json`** - Game overview
- **Video clips** - Goal moments extracted

### **📄 For Review**
- **`clip_descriptions/`** - What Gemini saw in each 15s
- **`synthesis.txt`** - Important moments identified
- **`team_config.json`** - Your team setup

## Key Differences from v4

- **Focus**: Goals and cool moments, not full tactical analysis
- **Teams**: Manual setup (you type colors), no auto-detection  
- **Pace**: Optimized for faster 5-a-side gameplay
- **Output**: Highlight reel focused, not comprehensive match analysis
- **Simpler**: 5 steps instead of 10+

## Requirements

- **Environment**: `hooper-ai` conda environment
- **API Keys**: GEMINI_API_KEY in `.env` file
- **Video**: Any format ffmpeg can handle
- **Storage**: ~1GB per match (much less than full analysis)

---

*Adapted from veo-games-v4 pipeline but streamlined for 5-a-side highlights.*