# CLANNAI Migration Plan

## 🎯 **Project Overview**

Consolidating multiple scattered repositories into a unified **CLANNAI** organization with a single, comprehensive sports analytics platform.

### **Current Local Structure:**
```
/home/ubuntu/clann-25/
├── README.md
├── crm/
├── footy/
├── gaa/
├── shared/
└── video-editor/
```

### **Missing Repositories (From Migration Plan):**
- `clannai-frontend` - Frontend web app
- `Web-App-ClannAI` - Backend web app  
- `gaa-analysis-pipeline` - GAA AI analysis
- `csv-to-visuals` - Analytics for both sports
- `interpolating_ballyclare` - 3D analysis for GAA
- `game-3d-vis` - Kognia POC
- `CRM-ClannAI` - Customer management

## 🏗️ **Target Structure**

```
clann-ai-platform/
├── 🌐 web-apps/
│   ├── clannai-frontend/     # Main frontend application
│   └── web-app-clannai/      # Backend API and services
├── 🤖 ai/
│   ├── gaa/
│   │   ├── analysis-pipeline/    # gaa-analysis-pipeline
│   │   ├── csv-to-visuals/      # csv-to-visuals (GAA)
│   │   └── 3d-analysis/         # interpolating_ballyclare
│   ├── football/
│   │   ├── analysis-pipeline/    # New football AI
│   │   ├── csv-to-visuals/      # csv-to-visuals (Football)
│   │   └── 3d-analysis/         # New football 3D
│   └── nice-to-have/
│       └── kognia-poc/          # game-3d-vis
├── 🎥 video-editor/
│   ├── processing/              # Video processing tools
│   ├── editing/                 # Video editing interface
│   ├── export/                  # Export functionality
│   └── shared/                  # Common video utilities
├── 🎬 video-player/
│   ├── playback/                # Video playback engine
│   ├── annotation/              # Annotation interface
│   ├── timeline/                # Timeline controls
│   └── shared/                  # Common player utilities
├── 📊 crm/
│   └── customer-management/     # CRM-ClannAI
└── 🛠️ shared/
    └── utilities/              # Common tools across all systems
```

## 🚀 **Migration Strategy**

### **Phase 1: Repository Discovery**
1. **Audit existing repos** - What do we actually have?
2. **Identify missing repos** - Are they under different orgs/users?
3. **Map current to target** - Which repos go where?
4. **Plan new development** - What needs to be built from scratch?

### **Phase 2: Local Consolidation**
1. **Create migration workspace** - This folder
2. **Clone all repos** - Get everything locally
3. **Organize by structure** - Move into target folders
4. **Resolve conflicts** - Handle duplicate files/dependencies
5. **Standardize interfaces** - Common APIs and data formats

### **Phase 3: New Organization Setup**
1. **Create CLANNAI organization** on GitHub
2. **Create clann-ai-platform repository**
3. **Push consolidated code** to new repo
4. **Set up CI/CD** and deployment
5. **Update documentation** and setup scripts

### **Phase 4: New Development**
1. **Football analysis pipeline** - New AI for soccer
2. **Football 3D analysis** - 3D tracking for football
3. **Video editor system** - Complete editing platform
4. **Shared utilities** - Common tools and configs

## 📊 **Repository Mapping**

### **Confirmed Mappings:**
- `thomasbradley99/compu.J_webapp` → `web-apps/web-app-clannai/`
- `thomasbradley99/gaa-poc` → `ai/gaa/analysis-pipeline/`
- `thomasbradley99/local-video-player` → `video-player/playback/`
- `thomasbradley99/gemini-mma-analytics` → `ai/nice-to-have/mma-analytics/`

### **Current Local Content:**
- `clann-25/footy/` → `ai/football/analysis-pipeline/` (existing work)
- `clann-25/gaa/` → `ai/gaa/` (merge with gaa-poc)
- `clann-25/video-editor/` → `video-editor/` (existing work)
- `clann-25/crm/` → `crm/customer-management/`

### **Missing Repositories:**
- `clannai-frontend` - Need to find or create
- `csv-to-visuals` - Need to find or create
- `interpolating_ballyclare` - Need to find or create
- `game-3d-vis` - Need to find or create
- `CRM-ClannAI` - Need to find or create

## 🛠️ **Technical Considerations**

### **Git History Preservation:**
- Keep individual repo histories where possible
- Use git subtree or submodule for complex cases
- Document original sources in README files

### **Dependency Management:**
- Consolidate requirements.txt files
- Standardize Python environments
- Unify Node.js dependencies
- Create shared package.json

### **Configuration:**
- Standardize .env files
- Create shared config templates
- Unify API key management
- Standardize database connections

### **Build & Deployment:**
- Create unified Docker setup
- Standardize CI/CD pipelines
- Create one-command deployment
- Set up environment management

## 📝 **Migration Checklist**

### **Discovery Phase:**
- [ ] Audit all existing repositories
- [ ] Identify missing repositories
- [ ] Map current structure to target
- [ ] Plan new development needs

### **Local Consolidation:**
- [ ] Clone all repositories locally
- [ ] Organize into target structure
- [ ] Resolve file conflicts
- [ ] Standardize dependencies
- [ ] Test all functionality

### **Organization Setup:**
- [ ] Create CLANNAI organization
- [ ] Create clann-ai-platform repository
- [ ] Push consolidated code
- [ ] Set up CI/CD
- [ ] Create deployment scripts

### **New Development:**
- [ ] Football analysis pipeline
- [ ] Football 3D analysis
- [ ] Video editor system
- [ ] Shared utilities
- [ ] Documentation updates

## 🎯 **Success Criteria**

1. **All existing functionality preserved**
2. **Unified development environment**
3. **Simplified deployment process**
4. **Clear module boundaries**
5. **Shared dependencies and utilities**
6. **Comprehensive documentation**
7. **Easy onboarding for new developers**

## 🚨 **Risks & Mitigation**

### **Risks:**
- **Lost functionality** - Missing repos or broken integrations
- **Complex dependencies** - Conflicting requirements
- **Git history loss** - Important commit history
- **Deployment issues** - Broken CI/CD

### **Mitigation:**
- **Thorough testing** at each phase
- **Backup original repos** before changes
- **Incremental migration** - one module at a time
- **Comprehensive documentation** of changes

---

**Next Steps:** Audit existing repositories and create detailed migration plan with actual repo mappings. 