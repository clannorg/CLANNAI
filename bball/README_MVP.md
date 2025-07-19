# 🏀 Basketball Analysis MVP

> **Simplified AI-Powered Basketball Analysis System**

## 🎯 **MVP GOAL**

Create a streamlined basketball analysis system that processes game footage into three core outputs:
1. **Game Events** - Track all basketball events and statistics (MOST ACCURATE)
2. **Player Profiling** - Identify and describe all players  
3. **Player Tracking** - Individual player performance analysis

## 📁 **DIRECTORY STRUCTURE**

```
basketball-mvp/
├── .env                        # Environment variables (API keys)
├── 0_utils/                    # Video processing, encoding, splitting
│   ├── download_videos.py      # Download videos from Firebase
│   ├── split_videos.py         # Split into 15s clips
│   ├── compress_videos.py      # Compress for API processing
│   ├── config.py               # Settings, paths, configuration
│   └── output/                 # Processed video clips + raw data
│
├── 1_game_events/              # Basketball events system (BEST PERFORMANCE)
│   ├── events_clip_analyzer.py # Analyze 15s clips for events
│   ├── events_synthesis.py     # Create game timeline
│   └── output/                 # game_events.json, game_summary.txt
│
├── 2_player_profiling/         # Player identification system
│   ├── player_clip_analyzer.py # Analyze 15s clips for players
│   ├── player_synthesis.py     # Create player database
│   └── output/                 # player_profiles.json, player_roster.txt
│
├── 3_player_analysis/          # Individual player tracking
│   ├── tracking_clip_analyzer.py # Analyze 15s clips for specific player
│   ├── tracking_synthesis.py   # Create player performance reports
│   └── output/                 # player_[name]_tracking.json
│
├── 4_gemini_info/              # Cost and performance tracking
│   ├── gemini_info.py          # Token usage, costs, API limits
│   ├── cost_calculator.py      # Cost analysis and optimization
│   └── output/                 # cost_reports.json, performance_metrics.txt
│
└── reports/                    # Final presentation reports
    ├── report_generator.py     # Generate final reports
    ├── game_events_report.html
    ├── player_profiles_report.html
    └── player_tracking_report.html
```

## 🚀 **EXECUTION FLOW**

**⚠️ IMPORTANT: Run ALL commands from the A2 directory. Paths are critical for proper file organization.**

### **Step 1: Setup & Data Preparation**
```bash
# Navigate to A2 directory first
cd A2

# Configure environment
python 0_utils/config.py

# Process videos
python 0_utils/download_videos.py
python 0_utils/split_videos.py
python 0_utils/compress_videos.py
```

### **Step 2: Core Analysis Pipeline (PRIORITY ORDER)**
```bash
# 1. Game events (MOST ACCURATE - captures all basketball activity)
python 1_game_events/events_clip_analyzer.py  
python 1_game_events/events_synthesis.py

# 2. Player profiling (identify all players)
python 2_player_profiling/player_clip_analyzer.py
python 2_player_profiling/player_synthesis.py

# 3. Player tracking (individual performance - use events data for accuracy)
python 3_player_analysis/tracking_clip_analyzer.py
python 3_player_analysis/tracking_synthesis.py
```

### **Step 3: Cost Analysis & Reports**
```bash
# Track costs and performance
python 4_gemini_info/gemini_info.py
python 4_gemini_info/cost_calculator.py

# Generate final reports
python reports/report_generator.py
```

**📁 File Organization:**
- All scripts expect to be run from the A2 directory
- Output files are organized in dedicated output folders per module
- Paths are relative to A2 directory structure

## 📊 **OUTPUTS BY DIRECTORY**

### **0_utils/output/**
- `clip_0_00.mp4`, `clip_0_15.mp4`, etc. (15s video clips)
- `video_processing_log.txt`
- `raw_analysis_data.json`
- `processing_metadata.json`

### **1_game_events/output/** ⭐ **BEST PERFORMANCE**
- `game_events.json` - Complete event timeline (MOST ACCURATE)
- `game_summary.txt` - Game statistics and summary
- `event_statistics.json` - Shot attempts, rebounds, turnovers, etc.
- **Captures:** All shots, passes, rebounds, turnovers, defensive actions

### **2_player_profiling/output/**
- `player_profiles.json` - Complete player database
- `player_roster.txt` - Human-readable player list
- `player_aesthetics.json` - Visual signatures and descriptions

### **3_player_analysis/output/**
- `player_[name]_tracking.json` - Individual player performance
- `player_[name]_report.txt` - Performance analysis report
- `performance_metrics.json` - Statistical summaries

### **4_gemini_info/output/**
- `cost_analysis.json` - Token usage and costs
- `performance_metrics.txt` - Processing speeds and efficiency
- `api_usage_report.txt` - Rate limits and optimization data

### **reports/**
- `game_events_report.html` - Game analysis presentation (PRIMARY)
- `player_profiles_report.html` - Presentation-ready player profiles
- `player_tracking_report.html` - Individual player reports

## 💰 **COST TRACKING**

### **`4_gemini_info/gemini_info.py`**
- **Token tracking**: Input/output tokens per clip
- **Processing speed**: Clips per minute, API response times
- **Rate limiting**: API quota usage and limits
- **Error tracking**: Failed requests and retry success rates

### **`4_gemini_info/cost_calculator.py`**
- **Cost per analysis type**: Events vs player profiling vs tracking
- **Cost per game**: Total cost for 40-minute game
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

- **Video Format**: MP4, 15-second clips
- **API**: Google Gemini 2.0 Flash (events), Gemini 2.5 Pro (tracking)
- **Processing**: Parallel clip analysis
- **Configuration**: Environment variables via .env
- **Output**: JSON + HTML reports
- **Scalability**: Handles multiple games/players

---

**Ready for basketball company presentation! 🏀** 