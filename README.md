# CLANNAI - Comprehensive Sports Analytics Platform

## 🎯 **Project Overview**

CLANNAI is a unified sports analytics platform that consolidates video analysis, AI insights, CRM tools, and business intelligence into one comprehensive system. Built for multi-sport analytics with a focus on football, GAA, and basketball.

## 🏗️ **Platform Architecture**

```
CLANNAI/
├── 📊 crm/                    # Customer Relationship Management
│   ├── src/                   # Contact finding & scraping tools
│   └── data/                  # Club contacts, targets, analysis data
├── 🤖 ai/                     # AI & Machine Learning
│   ├── ⚽ footy/              # Football Analysis & Insights
│   └── 🏐 gaa/               # GAA (Gaelic) Analysis
├── 🎬 video-editor/           # Video Processing & Editing
│   ├── detection/             # Object detection (YOLOv5)
│   ├── tracking/              # Player & ball tracking
│   ├── video_editing/         # Video editing & effects
│   └── data_transfer/         # Cloud integration (GCP)
└── 🌐 web-apps/               # Web Applications
    ├── clannai-frontend/      # Main React/Next.js frontend
    ├── web-app-clannai/       # Backend API & client
    ├── video-player/          # Standalone video player
    └── kognia-poc/           # 3D visualization
```

## 🚀 **Core Components**

### **📊 CRM System**
- **Contact Finding**: Automated contact discovery for sports organizations
- **Web Scraping**: Enhanced scraping tools for data collection (`enhanced_scraper.py`, `infinite_scroll_scraper.py`)
- **Target Lists**: Generate targeted contact lists (`generate_target_lists.py`)
- **Club Analysis**: Analyze sports clubs and organizations (`analyze_clubs.py`)
- **Data Assets**: 20+ data files including club contacts, targets, analysis logs

### **⚽ Football Analysis**
- **Game Events**: Automated event detection and analysis (`football_events_analyzer.py`)
- **Player Profiling**: Individual player performance insights (`football_player_analyzer.py`)
- **Tactical Analysis**: Formation and strategy analysis (`formation_analyzer.py`)
- **Cost Analysis**: Financial tracking and analysis (`football_cost_tracker.py`)
- **Street Football**: POC for street football analysis (`street_football_analyzer.py`)
- **Game Data**: Complete analysis of Game298_0601 with 47 analysis files

### **🏐 GAA Analysis**
- **Video Processing**: Automated video splitting and processing (`veo_downloader.py`, `clip_splitter.py`)
- **Event Detection**: Goal, kick, and turnover detection (`0_object_detection.py`)
- **Commentary Generation**: AI-powered match commentary (`simple_commentary.py`, `narrative_synthesis.py`)
- **Pipeline Management**: Complete analysis workflows (`run_pipeline.py`)
- **Cost Analysis**: Video token discovery and verification

### **🎬 Video Editor**
- **Video Processing**: Advanced video editing and effects (`video_editor.py`, `video_effects.py`)
- **Object Tracking**: Player and ball tracking (`people_tracking.py`, `ball_tracking.py`)
- **Highlight Creation**: Automated highlight generation (`create_highlight_workflow.py`)
- **Cloud Integration**: GCP and cloud storage support (`gcp_to_local.py`, `local_to_gcp.py`)
- **Detection**: Person detection with YOLOv5 (`simple_yolov5.py`, `person_detect_api.py`)

### **🌐 Web Applications**
- **Frontend**: React/Next.js with video player, dashboard, authentication
- **Backend**: Node.js API with session management, team features, Stripe integration
- **Video Player**: Standalone video player with event overlay, timeline controls
- **3D Visualization**: Kognia POC for 3D sports analysis

## 🛠️ **Getting Started**

### **Prerequisites**
- Python 3.8+
- Node.js 16+
- Conda environment (recommended)
- Git

### **Installation**
```bash
# Clone the repository
git clone https://github.com/clannorg/CLANNAI.git
cd CLANNAI

# Set up conda environment
conda create -n clannai python=3.8
conda activate clannai

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for web apps)
cd web-apps/clannai-frontend && npm install
cd ../web-app-clannai && npm install
```

### **Quick Start**
```bash
# Activate environment
conda activate clannai

# Run football analysis
cd ai/footy
python 1_game_events/football_events_analyzer.py

# Run GAA pipeline
cd ../gaa
python run_pipeline.py

# Use video editor
cd ../../video-editor
python simple_workflow.py

# Start web applications
cd ../web-apps/clannai-frontend
npm run dev
```

## 📋 **Module Overview**

### **CRM Module**
```bash
cd crm/src
python find_contacts.py          # Find contacts
python analyze_clubs.py          # Analyze clubs
python generate_target_lists.py  # Generate target lists
python enhanced_scraper.py       # Enhanced web scraping
```

### **Football Analysis**
```bash
cd ai/footy
python 1_game_events/football_events_analyzer.py  # Event analysis
python 2_player_profiling/football_player_analyzer.py  # Player analysis
python 3_tactical_analysis/formation_analyzer.py  # Tactical analysis
python 4_cost_analysis/football_cost_tracker.py  # Cost analysis
```

### **GAA Analysis**
```bash
cd ai/gaa
python run_pipeline.py  # Complete GAA pipeline
python 4-goal-kick-detection/0_object_detection.py  # Event detection
python 3-half-start-end/1-analyze_clips.py  # Clip analysis
```

### **Video Editor**
```bash
cd video-editor
python video_editing/video_editor.py  # Main video editor
python simple_workflow.py  # Simple workflow
python detection/simple_yolov5.py  # Object detection
```

### **Web Applications**
```bash
cd web-apps/clannai-frontend
npm run dev  # Start frontend

cd ../web-app-clannai
npm start  # Start backend
```

## 🔧 **Development**

### **Adding New Modules**
1. Create new directory in appropriate section
2. Add requirements.txt for dependencies
3. Include README.md with usage instructions
4. Update this main README

### **Code Standards**
- Python 3.8+ compatibility
- React/TypeScript for web components
- Clear documentation
- Modular design
- Error handling

## 📈 **Current Status**

### **✅ Completed Modules**
- [x] **CRM System** - Contact finding, scraping, data analysis
- [x] **Football Analysis** - Events, profiling, tactics, cost analysis
- [x] **GAA Analysis** - Video processing, event detection, commentary
- [x] **Video Editor** - Processing, tracking, editing, cloud integration
- [x] **Web Applications** - Frontend, backend, video player, 3D visualization

### **🚧 In Progress**
- [ ] **AI Enhancement** - Advanced models, 3D analysis
- [ ] **Multi-sport Expansion** - Basketball, rugby, other sports
- [ ] **Production Deployment** - CI/CD, Docker, cloud deployment

### **📋 Planned Features**
- [ ] **Advanced AI Models** - Real-time processing, predictive analytics
- [ ] **3D Analysis** - Spatial tracking, advanced visualization
- [ ] **Mobile Applications** - iOS/Android apps
- [ ] **API Services** - Public APIs for third-party integration
- [ ] **Analytics Dashboard** - Real-time insights and reporting

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 **License**

This project is proprietary to CLANNAI.

## 📞 **Contact**

For questions or support, contact the CLANNAI team.

---

**CLANNAI** - Unifying sports analytics through comprehensive technology solutions.

**Repository:** https://github.com/clannorg/CLANNAI  
**Organization:** clannorg  
**Status:** Production Ready 🚀 