# ⚽ Football Analysis MVP

> **AI-Powered Football Video Analysis System**

## 🎯 **MVP GOAL**

Create a streamlined football analysis system that processes match footage into four core outputs:
1. **Game Events** - Track all football events and statistics (MOST ACCURATE)
2. **Player Profiling** - Identify and describe all players  
3. **Tactical Analysis** - Formation detection and strategic insights (FOOTBALL UNIQUE)
4. **Cost Analysis** - Monitor API usage and optimize efficiency

## 📁 **DIRECTORY STRUCTURE**

```
A3_footy/
├── .env                        # Environment variables (API keys)
├── 0_utils/                    # Video processing, encoding, splitting
│   ├── football_video_processor.py # Process 90-min matches into 30s clips
│   ├── veo_downloader.py      # Download from Veo platform
│   ├── config.py               # Settings, paths, configuration
│   └── output/                 # Processed video clips + raw data
│
├── 1_game_events/              # Football events system (BEST PERFORMANCE)
│   ├── football_events_analyzer.py # Analyze 30s clips for events
│   ├── football_events_synthesis.py # Create match timeline
│   └── output/                 # match_events.json, match_timeline.txt
│
├── 2_player_profiling/         # Player identification system
│   ├── football_player_analyzer.py # Analyze 30s clips for players
│   ├── football_player_synthesis.py # Create player database
│   └── output/                 # player_profiles.json, player_roster.txt
│
├── 3_tactical_analysis/        # Tactical insights (FOOTBALL UNIQUE)
│   ├── formation_analyzer.py   # Formation detection (4-3-3, 4-4-2)
│   ├── possession_analyzer.py  # Ball possession patterns
│   ├── tactical_synthesis.py   # Generate tactical reports
│   └── output/                 # tactical_insights.json, formation_report.txt
│
├── 4_cost_analysis/            # Cost tracking and optimization
│   ├── football_cost_tracker.py # Monitor API usage and costs
│   ├── cost_comparison.py      # Football vs Basketball efficiency
│   └── output/                 # cost_reports.json, efficiency_metrics.txt
│
└── reports/                    # Final presentation reports
    ├── report_generator.py     # Generate final reports
    ├── match_events_report.html
    ├── player_profiles_report.html
    └── tactical_analysis_report.html
```

## 🚀 **EXECUTION FLOW**

**⚠️ IMPORTANT: Run ALL commands from the A3_footy directory. Paths are critical for proper file organization.**

### **Step 1: Setup & Data Preparation**
```bash
# Navigate to A3_footy directory first
cd A3_footy

# Configure environment
python 0_utils/config.py

# Process videos
python 0_utils/football_video_processor.py
python 0_utils/veo_downloader.py
```

### **Step 2: Core Analysis Pipeline (PRIORITY ORDER)**
```bash
# 1. Game events (MOST ACCURATE - captures all football activity)
python 1_game_events/football_events_analyzer.py  
python 1_game_events/football_events_synthesis.py

# 2. Player profiling (identify all players)
python 2_player_profiling/football_player_analyzer.py
python 2_player_profiling/football_player_synthesis.py

# 3. Tactical analysis (football-specific insights)
python 3_tactical_analysis/formation_analyzer.py
python 3_tactical_analysis/possession_analyzer.py
python 3_tactical_analysis/tactical_synthesis.py
```

### **Step 3: Cost Analysis & Reports**
```bash
# Track costs and performance
python 4_cost_analysis/football_cost_tracker.py
python 4_cost_analysis/cost_comparison.py

# Generate final reports
python reports/report_generator.py
```

**📁 File Organization:**
- All scripts expect to be run from the A3_footy directory
- Output files are organized in dedicated output folders per module
- Paths are relative to A3_footy directory structure

## 📊 **OUTPUTS BY DIRECTORY**

### **0_utils/output/**
- `football_clip_001.mp4`, `football_clip_002.mp4`, etc. (30s video clips)
- `processing_report.json` (video metadata and statistics)
- `veo_download_log.txt` (download tracking and errors)
- `raw_analysis_data.json` (initial processing data)

### **1_game_events/output/** ⭐ **BEST PERFORMANCE**
- `match_events.json` - Complete event timeline (MOST ACCURATE)
- `match_timeline.txt` - Human-readable match summary
- `event_statistics.json` - Goals, shots, passes, tackles, cards
- **Captures:** All goals, passes, tackles, fouls, cards, set pieces

### **2_player_profiling/output/**
- `player_profiles.json` - Complete player database
- `player_roster.txt` - Human-readable player list
- `team_formations.json` - Formation and positioning data
- `player_aesthetics.json` - Visual signatures and descriptions

### **3_tactical_analysis/output/** 🆕 **FOOTBALL UNIQUE**
- `formation_analysis.json` - Team formations detected (4-3-3, 4-4-2, etc.)
- `possession_patterns.json` - Ball possession and build-up analysis
- `tactical_report.txt` - Strategic insights and key moments
- `key_moments.json` - Critical match moments and momentum shifts

### **4_cost_analysis/output/**
- `football_cost_analysis.json` - Token usage and costs
- `cost_comparison.txt` - Football vs Basketball efficiency
- `performance_metrics.txt` - Processing speeds and accuracy
- `api_usage_report.txt` - Rate limits and optimization data

### **reports/**
- `match_events_report.html` - Match analysis presentation (PRIMARY)
- `player_profiles_report.html` - Presentation-ready player profiles
- `tactical_analysis_report.html` - Tactical insights and formation analysis

## 💰 **COST TRACKING**

### **`4_cost_analysis/football_cost_tracker.py`**
- **Token tracking**: Input/output tokens per clip
- **Processing speed**: Clips per minute, API response times
- **Rate limiting**: API quota usage and limits
- **Error tracking**: Failed requests and retry success rates

### **`4_cost_analysis/cost_comparison.py`**
- **Cost per analysis type**: Events vs player profiling vs tactical
- **Cost per match**: Total cost for 90-minute match
- **Optimization suggestions**: Batch processing, clip selection
- **Budget planning**: Cost estimates for different analysis depths

## 🎯 **PRESENTATION READY**

Each directory produces:
- **Clear outputs** in dedicated output folders
- **Progress tracking** during processing
- **Error handling** with retry logic
- **Structured data** for further analysis
- **Human-readable reports** for immediate use

## 🔧 **TECHNICAL SPECS**

- **Video Format**: MP4, 30-second clips (vs 15s basketball)
- **API**: Google Gemini 2.0 Flash (events), Gemini 2.5 Pro (tactical)
- **Processing**: Parallel clip analysis
- **Configuration**: Environment variables via .env
- **Output**: JSON + HTML reports
- **Scalability**: Handles multiple matches/teams

## ⚽ **FOOTBALL-SPECIFIC FEATURES**

### **Event Detection (vs Basketball)**
- **Goals** (vs shots)
- **Passes** (vs dribbles) 
- **Tackles** (vs rebounds)
- **Fouls & Cards** (yellow/red cards)
- **Set Pieces** (corners, free kicks, penalties)
- **Formation Changes** (vs player substitutions)

### **Tactical Analysis (FOOTBALL UNIQUE)**
- **Formation Detection**: 4-3-3, 4-4-2, 3-5-2, etc.
- **Possession Patterns**: Build-up play, counter-attacks
- **Pressing Strategies**: High press, mid-block, low block
- **Attacking Phases**: Transition, build-up, final third
- **Defensive Organization**: Shape, compactness, pressure

### **Player Profiling (Football-Specific)**
- **Position Identification**: GK, DEF, MID, FWD
- **Jersey Numbers**: Team colors and numbers
- **Movement Patterns**: Positional play and runs
- **Team Formation Roles**: Position-specific responsibilities

## 💰 **COST PROJECTIONS**

### **Per 90-Minute Football Match**
- **Clip Count**: 180 (90 minutes ÷ 30 seconds)
- **API Calls**: 360 (180 events + 180 insights)
- **Estimated Cost**: $0.0756 (180 × $0.000210 × 2)
- **Processing Time**: ~15 minutes (with rate limiting)

### **Cost Comparison**
| Analysis Type | Duration | Cost | Cost per Minute |
|---------------|----------|------|-----------------|
| **Basketball** | 10 min | $0.0168 | $0.00168 |
| **Football** | 90 min | $0.0756 | $0.00084 |

**Football is 50% more cost-efficient per minute!**

## 🎯 **SUCCESS METRICS**

### **Accuracy Targets**
- **Event Detection**: >80% (similar to basketball)
- **Goal Detection**: >85% (on target vs off target)
- **Pass Accuracy**: >90% (successful vs unsuccessful)
- **Formation Detection**: >80% (4-3-3, 4-4-2, etc.)
- **Card Detection**: >95% (yellow/red card identification)

### **Performance Targets**
- **Processing Speed**: <20 minutes for 90-minute match
- **Cost Efficiency**: <$0.10 per full match
- **Rate Limit Compliance**: 100% (no 429 errors)

## 🏆 **EXPECTED BENEFITS**

### **Compared to Basketball**
- **Larger Market**: Football is more globally popular
- **Longer Content**: 90 minutes vs 10 minutes
- **More Events**: Complex tactical analysis
- **Higher Value**: Professional football analysis

### **Business Opportunities**
- **Amateur Teams**: Performance analysis
- **Coaching**: Tactical insights
- **Scouting**: Player evaluation
- **Broadcasting**: Match highlights and analysis

---

**Ready for football company presentation! ⚽** 