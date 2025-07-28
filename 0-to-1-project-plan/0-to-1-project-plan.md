# CLANNAI 0→1 Sprint Plan
**Goal:** Get 5 paying customers at $5/game  
**Duration:** 2 weeks (July 20th - August 3rd)  
**Team:** Thomas, Ram, John

## 🎯 **Sprint Overview**

### **What We're Selling**
- **Content Package:** Match highlights, social media clips, player-following reels
- **Analytics Package:** Event detection, player ratings, game summaries
- **Pricing:** $5 per game analysis (1 free trial game)

### **Target Market**
- **Primary:** 5-a-side football clubs with VEO cameras
- **Secondary:** Div 1-10 level teams
- **Geography:** Focus on 3 specific locations initially
- **Total Market:** 100k clubs with VEO systems

### **Success Metrics**
- **Technical:** Full pipeline working end-to-end
- **Customer:** 5 paying customers at $5/game
- **Content:** 3 marketing reels showcasing capabilities
- **Process:** Human annotation system reducing AI false positives

## 📊 **Team Roles & Responsibilities**

### **Thomas (Web Platform + Infrastructure)**
- Web platform development
- GitHub organization
- AWS infrastructure setup
- Customer dashboard
- Video processing pipeline integration
- **Download highlights button** - Allow clubs to download their match highlight videos

### **Ram (AI/ML Development)**
- Gemini integration for event detection
- Cost/rate limit analysis for Google Cloud credits
- Test accuracy against existing 350-game dataset
- Automated player tracking and camera following

### **John (Customer Outreach + Content + Annotators)**
- Customer outreach (100 calls + 100 emails)
- Video processing and content generation
- Managing human annotators
- Research what analytics coaches actually want

## 🚀 **Week 1: Core Platform Development**

### **Days 1-2: AI Annotation Interface (Thomas)**
- [ ] Build web app to display Ram's Gemini analysis results
- [ ] Video player with timeline synced to detected events
- [ ] Event visualization (shots, goals, saves marked on timeline)

### **Days 3-4: Human Annotation System (Thomas)**
- [ ] Interface for human labellers to review AI detections
- [ ] Edit/add/remove event timestamps and classifications
- [ ] Approval workflow (AI → Human review → Final)

### **Days 5-7: Video Processing Pipeline (Thomas)**
- [ ] Integrate existing video_editor → software_cam.py → zoom.py workflow
- [ ] Automate reel generation from approved annotations
- [ ] Export system for different formats (vertical IG, horizontal YouTube)

### **Week 1: AI Development (Ram)**
- [ ] Set up Gemini system for event detection
- [ ] Cost/rate limit analysis for Google Cloud credits
- [ ] Test accuracy against existing infer.py script on 350 games

### **Week 1-2: Customer Outreach (John)**
- [ ] Secure VEO club contact list (100k clubs total)
- [ ] 100 phone calls + 100 emails to clubs in target locations
- [ ] Focus on 5-a-side clubs and Div 1-10 teams
- [ ] Goal: 20 free trial signups → 10 paid customers at $5/game

## 🎯 **Week 2: Customer-Facing Features**

### **Days 8-10: Customer Dashboard (Thomas)**
- [ ] Upload interface for VEO footage
- [ ] View analytics results and download reels
- [ ] Simple customer management for John

### **Days 11-14: Pipeline Integration & Testing (Thomas)**
- [ ] Full end-to-end workflow: Upload → AI Analysis → Human Review → Reel Generation
- [ ] Test with existing 350-game dataset
- [ ] Performance optimization and bug fixes

### **Week 2: AI Integration (Ram)**
- [ ] Integrate Gemini API with Thomas's web platform
- [ ] Fine-tune detection accuracy (minimize false positives)
- [ ] Set up automated player tracking and camera following

### **Week 1-2: Content Creation (John)**
- [ ] Create 3 marketing reels showcasing our capabilities
- [ ] Handle video processing pipeline and reel generation
- [ ] Manage content creation workflow from raw footage to final reels
- [ ] Optimize existing video_editor → software_cam.py → zoom.py pipeline

## 📋 **Daily Standup Template**

### **Thomas's Updates:**
- What did you complete yesterday?
- What are you working on today?
- Any blockers or dependencies?

### **Ram's Updates:**
- Gemini integration progress?
- Accuracy testing results?
- API cost analysis?

### **John's Updates:**
- Customer outreach progress?
- Content creation status?
- Annotator management?

## 🎯 **Success Criteria**

### **Technical Milestones:**
- [ ] AI Annotation Interface working
- [ ] Human Annotation System functional
- [ ] Video Processing Pipeline automated
- [ ] Customer Dashboard deployed
- [ ] End-to-end workflow tested

### **Business Milestones:**
- [ ] 20 free trial signups
- [ ] 10 paid customers
- [ ] 3 marketing reels created
- [ ] Customer feedback collected

### **Process Milestones:**
- [ ] Human annotation workflow established
- [ ] Quality control system in place
- [ ] Customer onboarding process defined

## 📞 **Communication Plan**

### **Daily Standups:** 15 minutes each morning
### **Weekly Reviews:** Friday afternoons
### **Emergency Sync:** As needed for blockers

## 🚨 **Risk Mitigation**

### **Technical Risks:**
- **Gemini API costs too high** → Ram monitors usage, sets limits
- **Video processing too slow** → Thomas optimizes pipeline
- **Integration issues** → Daily testing, incremental development

### **Business Risks:**
- **Low customer response** → John diversifies outreach channels
- **Content quality issues** → Human review process
- **Pricing resistance** → Flexible trial offers

---

**Next Steps:** Review individual task breakdowns in `/tasks/` folder 