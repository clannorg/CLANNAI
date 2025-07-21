# CLANNAI - Comprehensive Sports Analytics Platform

## 🎯 **Project Overview**

CLANNAI is a unified sports analytics platform that consolidates video analysis, AI insights, CRM tools, and business intelligence into one comprehensive system.

## 🏗️ **Platform Architecture**

```
CLANNAI/
├── 📊 crm/                    # Customer Relationship Management
├── ⚽ footy/                   # Football Analysis & Insights
├── 🏐 gaa/                     # GAA (Gaelic) Analysis
├── 🎬 video-editor/           # Video Processing & Editing
├── 🌐 web-apps/               # Web Applications (Future)
├── 🤖 ai/                     # AI & Machine Learning (Future)
└── 🛠️ shared/                # Shared Utilities (Future)
```

## 🚀 **Core Components**

### **📊 CRM System**
- **Contact Finding**: Automated contact discovery for sports organizations
- **Web Scraping**: Enhanced scraping tools for data collection
- **Target Lists**: Generate targeted contact lists
- **Club Analysis**: Analyze sports clubs and organizations

### **⚽ Football Analysis**
- **Game Events**: Automated event detection and analysis
- **Player Profiling**: Individual player performance insights
- **Tactical Analysis**: Formation and strategy analysis
- **Cost Analysis**: Financial tracking and analysis
- **Street Football**: POC for street football analysis

### **🏐 GAA Analysis**
- **Video Processing**: Automated video splitting and processing
- **Event Detection**: Goal, kick, and turnover detection
- **Commentary Generation**: AI-powered match commentary
- **Pipeline Management**: Complete analysis workflows

### **🎬 Video Editor**
- **Video Processing**: Advanced video editing and effects
- **Object Tracking**: Player and ball tracking
- **Highlight Creation**: Automated highlight generation
- **Cloud Integration**: GCP and cloud storage support

## 🛠️ **Getting Started**

### **Prerequisites**
- Python 3.8+
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

# Install dependencies
pip install -r requirements.txt
```

### **Quick Start**
```bash
# Activate environment
conda activate clannai

# Run football analysis
cd footy
python 1_game_events/football_events_analyzer.py

# Run GAA pipeline
cd ../gaa
python run_pipeline.py

# Use video editor
cd ../video-editor
python simple_workflow.py
```

## 📋 **Module Overview**

### **CRM Module**
```bash
cd crm/src
python find_contacts.py          # Find contacts
python analyze_clubs.py          # Analyze clubs
python generate_target_lists.py  # Generate target lists
```

### **Football Analysis**
```bash
cd footy
python 1_game_events/football_events_analyzer.py  # Event analysis
python 2_player_profiling/football_player_analyzer.py  # Player analysis
python 3_tactical_analysis/formation_analyzer.py  # Tactical analysis
```

### **GAA Analysis**
```bash
cd gaa
python run_pipeline.py  # Complete GAA pipeline
python 4-goal-kick-detection/0_object_detection.py  # Event detection
```

### **Video Editor**
```bash
cd video-editor
python video_editing/video_editor.py  # Main video editor
python simple_workflow.py  # Simple workflow
```

## 🔧 **Development**

### **Adding New Modules**
1. Create new directory in appropriate section
2. Add requirements.txt for dependencies
3. Include README.md with usage instructions
4. Update this main README

### **Code Standards**
- Python 3.8+ compatibility
- Clear documentation
- Modular design
- Error handling

## 📈 **Roadmap**

### **Phase 1: Consolidation** ✅
- [x] Consolidate existing modules
- [x] Standardize structure
- [x] Create unified documentation

### **Phase 2: Web Applications** 🚧
- [ ] Frontend web application
- [ ] Backend API services
- [ ] User authentication
- [ ] Dashboard interface

### **Phase 3: AI Enhancement** 🚧
- [ ] Advanced AI models
- [ ] 3D analysis capabilities
- [ ] Real-time processing
- [ ] Predictive analytics

### **Phase 4: Production** 🚧
- [ ] CI/CD pipeline
- [ ] Docker containers
- [ ] Cloud deployment
- [ ] Monitoring & logging

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