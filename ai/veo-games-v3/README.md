# VEO Games v3 - Complete Football Analysis Pipeline

**Self-contained, color-based pipeline that processes VEO match footage into interactive web analysis**

## What This Pipeline Does

**Transforms this:** VEO match URL  
**Into this:** Interactive web app with timeline events, tactical analysis, and video player

🎬 **Input**: `https://app.veo.co/matches/team-vs-team-date/`  
🌐 **Output**: Website-ready JSON files + S3 URLs for instant integration

## 10-Step Pipeline Flow

**📥 Phase 1a: Get Video + Sample** *(Automated)*
1. **`1.1_fetch_veo.py`** - Extract ground truth events from VEO API (goals, shots, fouls)
2. **`1.2_download_video.py`** - Download full match video + create 15-second sample clip

**🏗️ Phase 1b: Manual Team Setup** *(Interactive)*
3. **`1.3_setup_match.py`** - Human identifies teams by watching sample clip
   - Set team names: "Cookstown Youth" vs "Bourneview YM" 
   - Set jersey colors: "yellow" vs "all blue"
   - Creates team configuration for color-based AI analysis

**📊 Phase 1c: Prep with Known Teams** *(Automated)*
4. **`1.4_make_clips.py`** - Split video into 416 x 15-second clips
5. **`1.5_analyze_clips.py`** - AI describes each clip: "Yellow team attacks, Blue team defends"
6. **`1.6_synthesis.py`** - Combine all descriptions into complete match timeline

**🧠 Phase 2: AI Analysis** *(Automated)*
7. **`2.1_mega_analyzer.py`** - **MEGA BRAIN** combines VEO truth + AI timeline
   - Creates human-readable analysis files (plain text)
   - Cross-references AI observations with VEO verified events
8. **`2.2_format_for_webapp.py`** - Convert text analysis → webapp JSON format
   - Maps colors to UI teams: Yellow → "red", Blue → "blue"

**🚀 Phase 3: Upload & Finalize** *(Automated)*
9. **`3.1_write_metadata.py`** - Generate final metadata with team names + file URLs
10. **`3.2_s3_uploader.py`** - Upload all files to S3 CDN for web access

## What You Get Out

### **📊 For Website Integration (Ready-to-Use)**
- **`web_events_array.json`** - Timeline events: `[{"type": "goal", "timestamp": 1850, "team": "red", "description": "Header from corner"}]`
- **`11_tactical_analysis.json`** - Team insights: strengths, weaknesses, key moments
- **`match_metadata.json`** - Team names, jersey colors, file URLs, event counts
- **`video.mp4` on S3** - Full match video for web player

### **📄 For Human Review (Text Analysis)**
- **`mega_events.txt`** - Natural language: "30:50 - GOAL: Yellow team - Header from corner kick"
- **`mega_tactical.txt`** - Team analysis: strengths, weaknesses, tactical setup
- **`mega_summary.txt`** - Match overview: final score, key moments, match narrative
- **`5_complete_timeline.txt`** - Full 416-clip timeline for debugging

### **🔗 For System Integration**
- **`s3_locations.json`** - All S3 URLs for programmatic access
- **`1_veo_ground_truth.json`** - Original VEO events for validation
- **`match_config.json`** - Your manual team setup for reference

### **🎯 Direct Website Upload**
All files automatically uploaded to S3 with URLs like:
```
https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/match-id-web_events_array-json.json
```

**Copy-paste these URLs directly into your dashboard - no additional processing needed!**

## Quick Start

### **🔧 Setup**
```bash
cd /home/ubuntu/CLANNAI/ai/veo-games-v3/pipeline
conda activate hooper-ai  # Required environment
```

### **⚡ Run Full Pipeline** 
Replace `<veo-url>` with your VEO match URL:
```bash
# Phase 1a: Get Video + Sample (Automated)
python3 1.1_fetch_veo.py "https://app.veo.co/matches/team-vs-team-date/"
python3 1.2_download_video.py <match-id>

# Phase 1b: Manual Team Setup (Interactive - watch sample clip first!)
python3 1.3_setup_match.py <match-id>

# Phase 1c: Prep with Known Teams (Automated)
python3 1.4_make_clips.py <match-id>
python3 1.5_analyze_clips.py <match-id>
python3 1.6_synthesis.py <match-id>

# Phase 2: AI Analysis (Automated)
python3 2.1_mega_analyzer.py <match-id>
python3 2.2_format_for_webapp.py <match-id>

# Phase 3: Upload & Finalize (Automated)
python3 3.1_write_metadata.py <match-id>
python3 3.2_s3_uploader.py <match-id>
```

### **📋 Example: Cookstown vs Bourneview**
```bash
python3 1.1_fetch_veo.py "https://app.veo.co/matches/cookstown-youth-football-club-20250729-cookstown-youth-vs-bourneview-ym-12011faa/"
python3 1.2_download_video.py cookstown-youth-football-club-20250729-cookstown-youth-vs-bourneview-ym-12011faa
# ... continue with same match-id for all steps
```

## Key Advantages

- **🎯 Self-contained**: No dependencies on old v1/v2 data
- **🌈 Color-based**: Consistent team identification throughout  
- **📱 Website-ready**: Direct S3 URLs for dashboard integration
- **🧠 Smart analysis**: MEGA analyzer combines AI + VEO ground truth
- **🔄 Repeatable**: Clear numbered steps, logical flow
- **⚡ Fast**: ~20 minutes for full 90-minute match analysis

## Requirements

- **Environment**: `hooper-ai` conda environment
- **API Keys**: GEMINI_API_KEY in `ai/.env`
- **Storage**: ~4GB per match (video + clips + analysis)
- **Internet**: VEO API access + S3 upload capability