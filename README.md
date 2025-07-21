# CLANNAI - Comprehensive Sports Analytics Platform

**Repository:** https://github.com/clannorg/CLANNAI  
**Organization:** https://github.com/clannorg  
**Status:** Production Ready 🚀

## 🎯 **Platform Overview**

CLANNAI is a comprehensive sports analytics platform that combines AI-powered video analysis, customer relationship management, and web applications to deliver actionable insights for football and GAA teams.

## 🏗️ **Platform Architecture**

```
CLANNAI/
├── 📊 crm/                    # Customer Relationship Management
├── 🤖 ai/                     # AI/ML Analysis
│   ├── footy/                 # Football Analysis & Insights
│   └── gaa/                   # GAA (Gaelic) Analysis
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

### **📊 CRM (Customer Relationship Management)**
- Contact finding and web scraping tools
- Target list generation for VEO camera clubs
- Customer outreach automation
- **Key Files:** `crm/src/contact_finder.py`, `crm/src/enhanced_scraper.py`

### **🤖 AI Analysis (Football & GAA)**
- Event detection (goals, shots, saves, turnovers)
- Player tracking and performance analysis
- Tactical analysis and formation detection
- **Key Files:** `ai/footy/football_events_analyzer.py`, `ai/gaa/run_pipeline.py`

### **🎬 Video Editor**
- Automated video processing pipeline
- Player and ball tracking
- Highlight reel generation
- Cloud integration (GCP)
- **Key Files:** `video-editor/simple_workflow.py`, `video-editor/video_editing/`

### **🌐 Web Applications**
- React/Next.js frontend for video analysis
- Backend API for data management
- Standalone video player with event overlay
- 3D visualization capabilities

## 🛠️ **Getting Started**

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- Conda (for environment management)
- Git

### **Installation**

#### **Option 1: Unified Environment (Recommended)**
```bash
# Clone repository
git clone https://github.com/clannorg/CLANNAI.git
cd CLANNAI

# Run setup script (for new VMs)
./setup-clann.sh

# Or manually create environment
conda env create -f clann-unified.yml
conda activate clann-unified
```

#### **Option 2: Individual Module Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install video editor dependencies
pip install -r video-editor/requirements.txt

# Install Node.js dependencies (for web apps)
cd web-apps/clannai-frontend && npm install
```

### **Quick Start Commands**

#### **CRM Tools**
```bash
conda activate clann-unified
cd crm/src
python contact_finder.py
```

#### **AI Analysis**
```bash
conda activate clann-unified
cd ai/footy
python football_events_analyzer.py
```

#### **Video Processing**
```bash
conda activate clann-unified
cd video-editor
python simple_workflow.py
```

#### **Web Applications**
```bash
cd web-apps/clannai-frontend
npm run dev
```

## 📋 **Module Overview**

### **CRM Module**
- **Purpose:** Customer acquisition and management
- **Key Features:** Web scraping, contact finding, target list generation
- **Usage:** `python crm/src/enhanced_scraper.py`

### **AI Analysis Module**
- **Purpose:** Automated event detection and analysis
- **Key Features:** Gemini integration, player tracking, tactical analysis
- **Usage:** `python ai/footy/football_events_analyzer.py`

### **Video Editor Module**
- **Purpose:** Automated video processing and editing
- **Key Features:** YOLOv5 detection, tracking, reel generation
- **Usage:** `python video-editor/simple_workflow.py`

### **Web Applications Module**
- **Purpose:** User interface and data visualization
- **Key Features:** Video player, analytics dashboard, 3D visualization
- **Usage:** `npm run dev` (in web-apps/clannai-frontend)

## 🎯 **Development Guidelines**

### **Environment Management**
- Use `clann-unified` conda environment for all development
- All team members use the same environment for consistency
- Environment file: `clann-unified.yml`

### **Code Organization**
- Keep modules separate but interconnected
- Use shared utilities in common locations
- Follow existing naming conventions

### **Testing**
- Test each module independently
- Use existing test files as templates
- Validate video processing pipeline end-to-end

## 📊 **Current Status**

### **✅ Completed Features**
- CRM contact finding and scraping
- Football event detection pipeline
- GAA analysis pipeline
- Video processing workflow
- Web application framework
- Unified environment setup

### **🔄 In Progress**
- Gemini AI integration
- Human annotation system
- Customer dashboard
- Video reel automation

### **📋 Planned Features**
- Real-time video analysis
- Advanced player tracking
- 3D visualization
- Mobile applications

## 🚀 **Sprint Planning**

See `0-to-1-project-plan/` for current sprint details:
- **Goal:** 5 paying customers at $5/game
- **Duration:** 2 weeks (July 20th - August 3rd)
- **Team:** Thomas, Ram, John

## 📞 **Contact**

- **Repository:** https://github.com/clannorg/CLANNAI
- **Organization:** https://github.com/clannorg
- **Status:** Production Ready 🚀

## 📄 **License**

This project is proprietary to CLANNAI team. 