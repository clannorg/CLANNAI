# ⚽ Veo Games Analysis System

> **AI-Powered Analysis for Veo Football Matches**

## 🎯 **Overview**

The Veo Games Analysis System provides automated football match analysis for videos downloaded from the [Veo platform](https://veo.co). It integrates seamlessly with the existing CLANNAI football analysis pipeline to deliver comprehensive event detection, player tracking, and tactical insights.

## 📁 **Directory Structure**

```
veo-games/
├── ballyclare-20250111/          # Example match folder
│   ├── raw_video/               # Downloaded Veo video files
│   ├── clips/                   # 30-second processed clips
│   ├── analysis/                # Event analysis JSON files
│   ├── synthesis/               # Match timeline & statistics
│   └── match_info.json          # Match metadata & pipeline status
├── veo_match_analyzer.py        # Individual match analysis
├── veo_pipeline.py              # Multi-match pipeline manager
└── README.md                    # This documentation
```

## 🚀 **Quick Start**

### **1. Analyze the Ballyclare Match**
```bash
cd ai/footy/veo-games
python veo_match_analyzer.py ballyclare-20250111
```

### **2. Check Pipeline Status**
```bash
python veo_pipeline.py status
```

### **3. Create New Match from Veo URL**
```bash
python veo_pipeline.py create --url "https://app.veo.co/matches/your-match-url/" --name "Your Match Name"
```

## 🔧 **Pipeline Components**

### **VeoMatchAnalyzer** (`veo_match_analyzer.py`)
Handles individual match analysis with these steps:

1. **Download**: Uses Ram's `VeoDownloader` to fetch video from Veo platform
2. **Segment**: Splits video into 30-second clips using `VideoSegmentation`
3. **Analyze**: Processes each clip for football events via `FootballEventsAnalyzer`
4. **Synthesize**: Combines analysis into match timeline and statistics

### **VeoPipeline** (`veo_pipeline.py`)
Manages multiple matches and batch operations:

```bash
# List all matches
python veo_pipeline.py list

# Analyze specific match
python veo_pipeline.py analyze --match ballyclare-20250111

# Analyze all matches
python veo_pipeline.py analyze-all

# Create new match structure
python veo_pipeline.py create --url "veo-url" --name "Match Name"

# Print status report
python veo_pipeline.py status
```

## 📊 **Analysis Output**

Each analyzed match produces:

### **Event Timeline** (`synthesis/events_timeline.json`)
```json
{
  "match_info": {
    "match_id": "ballyclare-425e4c3f",
    "duration": "90:00",
    "total_events": 145
  },
  "events": [
    {
      "timestamp": "00:12:30",
      "event_type": "GOAL",
      "team": "home",
      "player": "Player #10",
      "confidence": 0.92,
      "description": "Header from corner kick"
    }
  ]
}
```

### **Event Statistics** (`synthesis/event_statistics.json`)
```json
{
  "summary": {
    "total_goals": 3,
    "total_shots": 18,
    "total_saves": 7,
    "possession_split": {"home": 52, "away": 48}
  },
  "by_team": {
    "home": {"goals": 2, "shots": 12, "saves": 3},
    "away": {"goals": 1, "shots": 6, "saves": 4}
  }
}
```

## 🔗 **Integration with Existing Pipeline**

The Veo system leverages Ram's existing infrastructure:

- **`veo_downloader.py`** - Downloads from Veo platform
- **`video_segmentation.py`** - Splits into analyzable clips
- **`football_events_analyzer.py`** - Core event detection
- **`football_events_synthesis.py`** - Timeline generation
- **`evaluation_tool.py`** - Performance measurement

## 📈 **Performance Tracking**

Based on Ram's evaluation framework, the system tracks:

- **Goal Detection**: ~100% recall, ~3-9% precision (high false positives)
- **Save Detection**: ~59% recall, ~51% precision (best performer)
- **Shot Detection**: ~37% recall, ~11% precision
- **Other Events**: Variable performance (blocks, skills, tackles)

> **Note**: The AI system currently over-detects events (high recall, low precision), which is being addressed in ongoing improvements.

## 🎮 **Video Player Integration**

Analyzed matches can be visualized using the existing video player:

```bash
# Copy analysis to video player
cp synthesis/events_timeline.json ../../web-apps/video-player/local-video-player/public/data/
```

## 🏗️ **Development Workflow**

### **Adding New Matches**
1. Get Veo match URL
2. Run: `python veo_pipeline.py create --url "veo-url" --name "Match Name"`
3. Run: `python veo_match_analyzer.py new-match-folder`
4. Check results: `python veo_pipeline.py status`

### **Batch Processing**
```bash
# Process all pending matches
python veo_pipeline.py analyze-all

# Generate comprehensive report
python veo_pipeline.py status > veo_analysis_report.txt
```

## 🔍 **Troubleshooting**

### **Common Issues**

**Permission Errors**
```bash
sudo chown -R ubuntu:ubuntu ai/footy/veo-games/
```

**Missing Dependencies**
```bash
cd ai/footy
pip install -r requirements.txt
```

**Veo Download Failures**
- Check internet connection
- Verify Veo URL format
- Ensure video is publicly accessible

**Analysis Errors**
- Check video file integrity
- Verify clip generation succeeded
- Review logs in match folder

## 📋 **Dependencies**

Required Python packages (from `../requirements.txt`):
- `opencv-python`
- `requests`
- `pathlib`
- `subprocess`
- `logging`

## 🎯 **Example: Ballyclare Match**

The pre-configured Ballyclare match demonstrates the full pipeline:

**Match Details:**
- **URL**: https://app.veo.co/matches/20250111-ballyclare-425e4c3f/
- **Date**: January 11, 2025
- **Status**: Ready for analysis

**To Analyze:**
```bash
cd ai/footy/veo-games
python veo_match_analyzer.py ballyclare-20250111
```

**Expected Output:**
- Downloaded video in `raw_video/`
- ~180 clips in `clips/` (for 90-minute match)
- Event analysis in `analysis/`
- Match timeline and stats in `synthesis/`

## 🚀 **Future Enhancements**

- **Real-time Analysis**: Stream processing during live matches
- **Multi-camera Support**: Analyze multiple camera angles
- **Enhanced Accuracy**: Improve precision while maintaining recall
- **Tactical Insights**: Formation analysis and strategic recommendations
- **Player Tracking**: Individual player performance metrics

---

**Built on Ram's Football Analysis MVP** | **Integrated with CLANNAI Pipeline** | **Optimized for Veo Platform** 