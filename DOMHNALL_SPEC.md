# 🚀 DOMHNALL PROJECT SPECIFICATION

**Goal:** Build automated cloud platform for football analysis  
**Timeline:** Complete by August 31, 2025  
**Payment:** £20,000 (triple trigger: fundraising + tech delivery + deadline)

---

## 🎯 WHAT WE'RE BUILDING

**User Experience:**
1. User pastes VEO URL → `https://app.veo.co/matches/xyz`
2. System processes automatically in <10 minutes
3. User gets interactive video player with AI analysis

**Current State:** AI pipeline works perfectly (proven on 200+ matches)  
**Missing:** Cloud automation + web interface

---

## 🔧 TECHNICAL REQUIREMENTS

### Core System
- **Input:** VEO URLs or direct video uploads
- **Processing:** <10 minutes per match (target: 5 minutes)
- **Output:** Interactive web player with 66+ timeline events
- **Capacity:** Handle 20+ concurrent analyses
- **Uptime:** 99.5% availability

### Infrastructure Stack
```
Frontend: Next.js + React (already exists at clannai.com)
Backend: FastAPI + PostgreSQL (AWS RDS ready)
Processing: Auto-scaling EC2 (c5.4xlarge instances)
Storage: S3 buckets with lifecycle management
Queue: Redis + Celery for job management
```

### Cost Controls
- **Per match:** <£0.50 processing cost
- **Auto-scaling:** 0-3 instances (prevent runaway costs)
- **User limits:** Rate limiting to prevent abuse
- **Monitoring:** Real-time cost alerts

---

## 💰 PAYMENT STRUCTURE

**£20,000 paid ONLY when ALL THREE conditions met:**

1. **Fundraising:** Company raises >£300,000
2. **Technical Delivery:** Full system working as specified
3. **Deadline:** Completed by August 31, 2025

**If any condition fails = £0 payment**

---

## ✅ SUCCESS CRITERIA

### Technical Deliverables
- [ ] User uploads VEO URL → Gets analysis in <10 minutes
- [ ] Interactive video player with timeline events
- [ ] System handles 20+ concurrent matches
- [ ] 99.5% uptime over 30-day verification
- [ ] Cost per analysis <£0.50
- [ ] Mobile-responsive interface

### Business Requirements
- [ ] Production-ready for customer demos
- [ ] Scalable to 1000+ matches/day
- [ ] Complete documentation and handover
- [ ] Security and compliance ready

---

## 🏗️ WHAT EXISTS vs WHAT'S NEEDED

### ✅ Already Built
- Complete AI analysis pipeline (10 scripts, 15-minute processing)
- Frontend web app (Next.js at clannai.com)
- Database schema (AWS RDS PostgreSQL)
- S3 storage architecture
- Domain and SSL certificates

### 🔨 Needs Building
- **Cloud automation:** Auto-scaling EC2 processing
- **Job queue system:** Redis + Celery for background jobs
- **API integration:** Connect frontend to processing pipeline
- **Monitoring:** Cost controls and performance tracking
- **User management:** Rate limiting and subscription tiers

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: Foundation (Weeks 1-4)
- AWS infrastructure automation
- Job queue and processing system
- Basic API endpoints

### Phase 2: Integration (Weeks 5-8)
- Frontend-backend connection
- Real-time progress tracking
- Error handling and retries

### Phase 3: Production (Weeks 9-12)
- Auto-scaling and cost controls
- Monitoring and alerting
- Security hardening

### Phase 4: Launch Ready (Weeks 13-16)
- Performance optimization
- Documentation and handover
- 30-day verification period

---

## 🎯 BOTTOM LINE

**What Domhnall Builds:** Cloud automation to make our proven AI pipeline user-facing  
**What We Get:** VEO URL → 10-minute processing → Interactive analysis  
**What It Costs:** £20k (only if fundraising + delivery + deadline all met)  
**When It's Done:** August 31, 2025

**The AI works. The frontend exists. We just need the cloud plumbing.** 🚀