# Footy2 - Advanced 5-a-Side Football Analysis

The **most detailed football analysis pipeline ever created**. Generates professional-level tactical insights with detailed play-by-play descriptions, player analysis, and interactive webapp integration.

## What This Analyzes

- 5-a-side football matches with **complete tactical breakdown**
- **Detailed play-by-play** descriptions of every 15-second segment  
- **Player identification** by appearance and performance
- **Tactical patterns** only visible with full game data
- **Interactive moments** with clickable timestamps
- **Professional coaching insights** and training recommendations

## How It Works

### 7-Step Advanced Pipeline

1. **Setup teams** - Detailed team configuration with visual appearance
2. **Make 15-second clips** - Split video into analyzable segments
3. **Analyze clips** - **Detailed chronological descriptions** with exact timing and player identification
4. **Synthesize highlights** - **Generous goal detection** with exact timestamps 
5. **Generate sick tactical analysis** - **Professional-level insights** using full game timeline
6. **Convert to webapp JSON** - **Interactive format** with player cards and clickable moments
7. **Upload to S3** - Cloud integration for webapp display

### Key Features
- **Exact timestamps** calculated to the second
- **Player nicknames** based on observations ("The White Shirt Sharpshooter")
- **Impact ratings** (X/10) for all tactical elements
- **Evidence-based analysis** with specific timeline references
- **Priority-based recommendations** with coaching drills

## Usage

```bash
# Navigate to pipeline
cd ai/footy2/pipeline
conda activate hooper-ai

# 1. Setup teams with detailed appearance
python 1_setup_teams.py <match-id>

# 2. Make clips  
python 2_make_clips.py <video-path> <match-id>

# 3. Analyze clips with detailed descriptions
python 3_analyze_clips.py <match-id>

# 4. Synthesize highlights with exact timestamps
python 4_synthesize_highlights.py <match-id>

# 5. Generate sick tactical analysis
python 4.7_generate_sick_analysis.py <match-id>

# 6. Convert to webapp-friendly JSON
python 4.8_convert_sick_to_json.py <match-id>

# 7. Upload to S3 for webapp (with video clips!)
python 6_s3_uploader_with_clips.py <match-id>
```

## Example Workflow

```bash
# Setup with detailed team info
python 1_setup_teams.py leo1
# Enter: Team A = "clann" (no bibs/colours)
#        Team B = "lostthehead" (orange bibs)

# Full analysis pipeline
python 2_make_clips.py "/path/to/leo1.mp4" leo1
python 3_analyze_clips.py leo1
python 4_synthesize_highlights.py leo1
python 4.7_generate_sick_analysis.py leo1
python 4.8_convert_sick_to_json.py leo1
python 6_s3_uploader_with_clips.py leo1
```

## What You Get

### **🔥 Sick Tactical Analysis**
- **Player cards** with nicknames like "The White Shirt Sharpshooter"
- **Impact ratings** (9.5/10) for all tactical elements
- **Evidence timestamps** for every claim
- **Priority-based recommendations** (🎯 HIGH, ⚡ MEDIUM, 💡 LOW)
- **Wild insights** only possible with full game data

### **📊 For Webapp Integration**
- **`web_events_array.json`** - Timeline events with exact timestamps
- **`sick_tactical_analysis.json`** - Interactive tactical insights
- **`match_metadata.json`** - Game overview and team info
- **S3 URLs** - Cloud-hosted files ready for webapp

### **📄 For Human Review**
- **`full_timeline.txt`** - Every 15-second segment described (195KB+)
- **`highlights.txt`** - Key moments with tactical significance
- **`sick_tactical_analysis.txt`** - Human-readable tactical breakdown
- **`clip_descriptions/`** - Individual clip analysis files

### **🎯 Example Outputs**
- **Match Summary**: "This wasn't a football match; it was a siege..."
- **Player Analysis**: "👑 THE WHITE SHIRT SHARPSHOOTER (9.5/10): Stats: 6+ goals, 20+ shots..."
- **Wild Insights**: "The Woodwork Anomaly: 21 frame hits - psychological warfare"
- **Coaching**: "🎯 HIGH PRIORITY: Drill Defensive Transitions - Run 3-on-2 counter-attack drills..."

## Key Advances from Footy1

- **Detailed descriptions**: Chronological play-by-play with exact timing
- **Player identification**: By appearance, role, and performance
- **Professional analysis**: Coaching-level insights with evidence
- **Interactive elements**: Clickable moments and rich data structures
- **Webapp optimization**: JSON formats designed for frontend display
- **Evidence-based**: Every claim backed by timeline references
- **Advanced**: 7-step pipeline generating multiple output formats
- **Video clips**: All 15-second segments uploaded to S3 for media conversion

## Requirements

- **Environment**: `hooper-ai` conda environment
- **API Keys**: GEMINI_API_KEY in `.env` file
- **Video**: Any format ffmpeg can handle
- **Storage**: ~2GB per match (detailed analysis requires more data)
- **AWS**: S3 credentials for webapp integration

---

*The most advanced football analysis pipeline ever created - pushes AI and webapp capabilities to their limits.*