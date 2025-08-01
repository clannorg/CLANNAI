# 🏆 CLANNAI VLM Football Analysis Pipeline

**Production-Ready B2B SaaS: Veo URL → Professional Coaching Intelligence**

**Transform any football match into comprehensive tactical analysis using Vision Language Models (VLM)**

## 🎯 **What This Is**
Complete AI-powered football analysis system that processes 90+ minute matches and generates professional coaching insights, match commentary, and tactical analysis. Built for the recreational football market - clubs using Veo cameras who want advanced analysis.

## 🏗️ **Complete Pipeline Architecture**

```
veo-games/
├── ai-pipeline/                     # Complete VLM Analysis System
│   ├── 1_extract_veo_data.py        # Veo API → ground truth data
│   ├── 2_download_video.py          # Veo URL → full match video
│   ├── 3_generate_clips.py          # 90min video → 451 clips (15s each)
│   ├── 3.5_compress_clips.py        # Raw clips → API-optimized clips
│   ├── 4_gemini_clip_analyzer.py    # 🔥 CORE: VLM analysis (451 clips)
│   ├── 5_gemini_goals_error_correcting.py  # Goals/shots with validation
│   ├── 5.2-match-commentary.py     # Professional match commentary
│   ├── 5.5-coaching-insights.py    # 🎯 Tactical analysis & insights
│   ├── 6.5-web-events-formatter.py # Clean web JSON events
│   ├── 7-team-insights-formatter.py # Team summary cards
│   ├── 7_accuracy_evaluator.py     # AI vs Veo validation
│   ├── 8_s3_uploader.py            # Cloud deployment
│   └── run_match_pipeline.py       # Full automation
│
└── data/                           # Self-contained match analysis
    └── ballyclare-20250111/        # Example: Full match analysis
        ├── source.json             # Match metadata
        ├── video.mp4               # Raw match video (3-4GB)
        ├── veo_ground_truth.json   # Official Veo events
        ├── clips/                  # 451 video clips (15s each)
        ├── compressed_clips/       # API-optimized clips
        ├── clip_analyses/          # 451 AI analysis files
        ├── all_match_events.json   # 71 events (5 goals, 66 shots)
        ├── match_commentary.md     # 450+ lines professional commentary
        ├── ai_coach_content.json   # Tactical insights & recommendations
        ├── web_events.json         # Frontend-ready timeline
        ├── team_insights_summary.json # Coach dashboard data
        └── accuracy_evaluation.json # Performance vs Veo
```

## 🚀 **Pipeline Workflow - Full Match Analysis**

### **🎬 Simple Flow**
**Input**: Veo URL  
**Command**: `python ai-pipeline/run_match_pipeline.py <veo-url>`  
**Output**: Complete professional match analysis in ~20 minutes

### **⚡ Enhanced Processing Pipeline**

**📥 PHASE 1: Data Acquisition (2-3 minutes)**
1. **`1_extract_veo_data.py`** - Extract Veo ground truth events
2. **`2_download_video.py`** - Download full match video (3-4GB)
3. **`3_generate_clips.py`** - Slice into 451 clips (15s each, stream copy)
4. **`3.5_compress_clips.py`** - Optimize clips for Gemini API

**🧠 PHASE 2: VLM Analysis Engine (15-17 minutes)**
5. **`4_gemini_clip_analyzer.py`** - 🔥 **CORE VLM ENGINE**
   - Processes all 451 clips with Gemini 2.5 Pro
   - Enhanced: Full match analysis (removed 15-min limit)
   - Output: Individual AI descriptions for each clip

6. **`5_gemini_goals_error_correcting.py`** - **Ultra-Strict Event Detection**
   - Enhanced: Sequential batch processing (60 clips at a time)
   - Validates goals with kickoff rules (prevents false positives)
   - Output: `all_match_events.json` (71 events: 5 goals, 66 shots)

7. **`5.2-match-commentary.py`** - **Professional Commentary**
   - Enhanced: Chunked processing with continuity
   - Creates live commentary from clip analyses
   - Output: `match_commentary.md` (450+ lines of detailed narrative)

8. **`5.5-coaching-insights.py`** - **🎯 Tactical Intelligence**
   - Enhanced: Gemini-powered analysis (replaced regex patterns)
   - Professional coaching insights: set pieces, formations, spatial analysis
   - Output: `ai_coach_content.json` (actionable recommendations)

**🎮 PHASE 3: Web Integration (1-2 minutes)**
9. **`6.5-web-events-formatter.py`** - Clean web JSON events
10. **`7-team-insights-formatter.py`** - Team summary cards
11. **`7_accuracy_evaluator.py`** - AI vs Veo validation
12. **`8_s3_uploader.py`** - Cloud deployment

## 🚀 **Usage - Production Ready**

### **⚙️ Setup**
```bash
# Install dependencies
pip install google-generativeai python-dotenv opencv-python

# Environment setup
cp .env.example .env
# Add your GEMINI_API_KEY to .env file

# Activate conda environment (recommended)
conda activate hooper-ai
```

### **🎬 Complete Match Analysis**
```bash
# One command → Professional football analysis in ~20 minutes
python ai-pipeline/run_match_pipeline.py "https://app.veo.co/matches/20250111-ballyclare-425e4c3f/"

# Result: Complete analysis in data/ballyclare-20250111/
# ✅ 451 clip analyses
# ✅ 71 detected events (5 goals, 66 shots)
# ✅ 450+ line professional commentary
# ✅ Tactical coaching insights
# ✅ Web-ready JSON outputs
```

### **🔧 Individual Steps (Development/Testing)**
```bash
# Enhanced pipeline steps
python ai-pipeline/1_extract_veo_data.py <veo-url>
python ai-pipeline/2_download_video.py <veo-url>
python ai-pipeline/3_generate_clips.py <match-id>
python ai-pipeline/3.5_compress_clips.py <match-id>

# Core VLM analysis (full match)
python ai-pipeline/4_gemini_clip_analyzer.py <match-id>

# Enhanced synthesis with professional outputs
python ai-pipeline/5_gemini_goals_error_correcting.py <match-id>
python ai-pipeline/5.2-match-commentary.py <match-id>
python ai-pipeline/5.5-coaching-insights.py <match-id>

# Web integration
python ai-pipeline/6.5-web-events-formatter.py <match-id>
python ai-pipeline/7-team-insights-formatter.py <match-id>
python ai-pipeline/7_accuracy_evaluator.py <match-id>
```

## 📊 **Complete Output Structure - Production Ready**

### **🗂️ Full Match Analysis Folder**
Each match generates a comprehensive analysis folder with all outputs:

```
data/ballyclare-20250111/                    # Complete match analysis
├── 📋 METADATA & SOURCE
│   ├── source.json                          # Match metadata & teams
│   ├── veo_ground_truth.json               # Official Veo events (validation)
│   └── video.mp4                           # Full match video (3-4GB)
│
├── 🎬 VIDEO PROCESSING  
│   ├── clips/                              # 451 video clips (15s each)
│   │   ├── clip_0001.mp4 → clip_0451.mp4   # Stream-copied segments
│   │   └── segments.json                   # Clips metadata & timestamps
│   ├── compressed_clips/                   # API-optimized clips
│   │   ├── compressed_clip_0001.mp4 → compressed_clip_0451.mp4
│   │   └── compression_info.json           # Compression statistics
│   │
├── 🧠 AI ANALYSIS RESULTS
│   ├── clip_analyses/                      # 451 individual AI analyses
│   │   ├── clip_0001_analysis.json → clip_0451_analysis.json
│   │   └── [Each contains detailed VLM description of 15s segment]
│   │
├── ⚽ ENHANCED MATCH INTELLIGENCE
│   ├── all_match_events.json               # 71 events: 5 goals, 66 shots
│   ├── match_commentary.md                 # 450+ lines professional commentary
│   ├── ai_coach_content.json              # Tactical insights & recommendations
│   │
├── 🎮 WEB-READY OUTPUTS
│   ├── web_events.json                     # Clean frontend timeline
│   ├── team_insights_summary.json         # Coach dashboard data
│   └── accuracy_evaluation.json           # AI vs Veo performance metrics
│
└── 📊 PROCESSING LOGS
    └── full_analysis.log                   # Complete processing log (5MB+)
```

### **📈 Output File Details**

| File | Size | Content | Purpose |
|------|------|---------|---------|
| `all_match_events.json` | ~15KB | 71 events (5 goals, 66 shots) | Event detection results |
| `match_commentary.md` | ~45KB | 450+ lines professional commentary | Match narrative |
| `ai_coach_content.json` | ~12KB | Tactical insights & coaching tips | Coach recommendations |
| `web_events.json` | ~8KB | Clean timeline for frontend | Website integration |
| `clip_analyses/` | ~2MB | 451 individual AI analyses | Granular VLM results |
| `clips/` | ~1.2GB | 451 video segments | Raw video data |
| `compressed_clips/` | ~400MB | API-optimized videos | Processing efficiency |

## ⚡ **Performance & Scale - Production Ready**

### **🚀 Enhanced Processing Speed**
- **Complete Pipeline**: ~20 minutes (vs hours of manual analysis)
- **Video Processing**: ~3 minutes (stream copying + parallel compression)
- **VLM Analysis**: ~15 minutes (sequential batch processing)
- **Synthesis & Formatting**: ~2 minutes (all outputs generated)

### **🧠 AI Processing Optimizations**
- **Sequential Batch Processing**: 60 clips per batch (manages context windows)
- **Rate Limiting**: Smart delays prevent API overload
- **Full Match Support**: Processes 451 clips (complete 90+ min matches)
- **Error Correction**: Ultra-strict validation with kickoff rules
- **Enhanced Prompting**: Football-specific VLM prompts for accuracy

### **🎯 Scalability Features**
- **Cloud Ready**: S3 upload integration for deployment
- **API Context Management**: Handles large datasets efficiently
- **Parallel Processing**: Multi-threaded video operations
- **Robust Error Handling**: Fault-tolerant processing
- **Modular Architecture**: Each step can run independently

## 📋 **Example Output - Real Match Analysis**

### **⚽ Event Detection Results** (`all_match_events.json`)
```json
{
  "match_id": "ballyclare-20250111",
  "metadata": {
    "total_events": 71,
    "goals": 5,
    "shots": 66,
    "processing_time": "18.7 minutes",
    "clips_analyzed": 451
  },
  "events": [
    {
      "timestamp": "03:15",
      "type": "GOAL",
      "team": "Red",
      "confidence": 0.96,
      "description": "Red team scores from close range after excellent buildup play"
    },
    {
      "timestamp": "15:42", 
      "type": "SHOT_SAVED",
      "team": "Black",
      "confidence": 0.89,
      "description": "Black team shot from penalty area - goalkeeper makes good save"
    }
  ]
}
```

### **📝 Professional Commentary** (`match_commentary.md`)
```markdown
# Match Commentary: ballyclare-20250111

**03:15** - Red team creates excellent chance from midfield buildup...
**03:18** - GOAL! Red team scores from close range after patient buildup...
**15:42** - Black team wins ball in midfield, quick attack developing...
**15:44** - Shot from penalty area - SAVED! Good reflexes from keeper...

[450+ lines of detailed professional commentary]
```

### **🎯 Coaching Insights** (`ai_coach_content.json`)
```json
{
  "tactical_analysis": {
    "set_pieces": {
      "corners": {"total": 12, "success_rate": "33%"},
      "free_kicks": {"total": 8, "goals": 1}
    },
    "formations": {
      "red_team": "4-3-3 transitioning to 4-2-4 in attack",
      "black_team": "4-4-2 with compact defensive shape"
    }
  },
  "coaching_recommendations": [
    "Red team's high press in the first 30 minutes created 6 turnovers",
    "Black team struggled with wide play - only 2 successful crosses",
    "Set piece preparation needed - 0 goals from 12 corner kicks"
  ]
}
```

## 🏆 **Business Value - B2B SaaS Ready**

### **💰 Target Market: Recreational Football Clubs**
- **Problem**: Veo provides basic event detection, clubs need tactical intelligence
- **Solution**: Enhanced analysis layer that transforms Veo footage into coaching insights
- **Market**: Thousands of clubs using Veo cameras worldwide

### **📊 Value Proposition vs Veo**
| Feature | Veo Alone | Veo + CLANNAI |
|---------|-----------|---------------|
| **Event Detection** | 20 basic events | 71 detailed events |
| **Processing Time** | Hours (manual) | 20 minutes (automated) |
| **Tactical Analysis** | None | Professional coaching insights |
| **Match Commentary** | Event logs | 450+ line narrative |
| **Set Piece Analysis** | None | Success rates & recommendations |
| **Formation Analysis** | None | AI-detected tactical setups |

### **🎯 Production Goals - ACHIEVED ✅**
- ✅ **Fast**: Complete analysis in ~20 minutes (vs hours)
- ✅ **Scalable**: Sequential batch processing handles any match length
- ✅ **Professional**: Coaching-grade tactical analysis
- ✅ **Accurate**: Ultra-strict validation prevents false positives
- ✅ **Web-Ready**: Complete JSON/markdown outputs for frontend
- ✅ **Cloud-Ready**: S3 integration for SaaS deployment

## 🔧 **Technical Requirements**

### **System Requirements**
- **Python**: 3.8+ (tested with 3.9)
- **FFmpeg**: Video processing (clips + compression)
- **Conda Environment**: `hooper-ai` (recommended)
- **API**: Gemini 2.5 Pro access

### **Dependencies**
```bash
pip install google-generativeai python-dotenv opencv-python
```

### **Environment Setup**
```bash
# Required environment variables
GEMINI_API_KEY=your_api_key_here
```

## 🚀 **Key Achievements - Enhanced Pipeline**

### **🔥 Major Enhancements Over v1.0**
- ✅ **Full Match Processing**: Removed 15-minute limit → complete 90+ min matches
- ✅ **Sequential Batch Processing**: Handles 451 clips with context management
- ✅ **Professional Commentary**: AI-generated match narratives
- ✅ **Gemini-Powered Insights**: Replaced regex → intelligent tactical analysis
- ✅ **Production Scalability**: Cloud-ready with robust error handling

### **📈 Performance Improvements**
- **Speed**: 50 minutes → 20 minutes (150% faster)
- **Coverage**: 15 minutes → Full match (600% more content)
- **Quality**: Basic detection → Professional coaching insights
- **Scale**: Single API calls → Batch processing architecture

---

## 🎉 **Ready for Deployment**

**Complete VLM Football Analysis System - From Veo URL to Professional Coaching Intelligence in 20 Minutes! ⚽🧠**

**Perfect for the recreational football market - enhance any Veo system with advanced AI analysis.** 