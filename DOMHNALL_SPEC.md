# ClannAI - Automated Football Analysis Platform
## Technical Specification for Full-Stack Development

**Target:** Complete automated platform by Friday  
**Goal:** VEO URL → 15-minute AI processing → Interactive web player

---

## 🎯 Product Overview

Transform any VEO match URL into intelligent tactical analysis in 15 minutes. Users paste a VEO URL, wait for automated AI processing, then get an interactive video player with 66+ timeline events (goals, shots, fouls, cards, tactical moments) plus coaching insights.

**Current State:** AI pipeline proven and working (generates complete analysis files)  
**Needed:** Cloud automation + web frontend to make it user-facing

---

## 🏗️ Architecture Requirements

### Frontend (Next.js/React)
```typescript
// Required Pages:
- Landing page with VEO URL input
- Processing status page with progress bar
- Interactive video player with timeline
- User dashboard with match history

// Core API Integration:
POST /api/matches/analyze          // Start analysis
GET  /api/matches/:id/status      // Check progress  
GET  /api/matches/:id/results     // Get final data
GET  /api/matches/:id/player      // Load video player
```

### Backend API (FastAPI/Python)
```python
# Required Endpoints:
@app.post("/analyze")
async def start_analysis(veo_url: str, user_id: str):
    # Validate VEO URL, create processing job, return job_id

@app.get("/status/{job_id}")  
async def get_status(job_id: str):
    # Return processing status + progress percentage

@app.get("/results/{match_id}")
async def get_results(match_id: str):
    # Return all analysis files + S3 URLs for video player
```

### Job Processing System
```python
# Background job that runs existing AI pipeline:
@celery.task
def process_match(veo_url: str, match_id: str):
    # Execute 10 AI pipeline scripts in sequence
    # Update progress in database
    # Upload results to S3
    # Notify frontend when complete
```

---

## ☁️ AWS Infrastructure Specification

### Compute Resources
- **Processing:** EC2 `c5.4xlarge` (16 vCPU, 32GB RAM) with auto-scaling 1-5 instances
- **API:** ECS Fargate containers (2 vCPU, 4GB RAM) scaling 2-10 based on load
- **Database:** RDS PostgreSQL for job tracking and user management

### Storage Architecture
```
S3 Buckets:
├── clannai-raw-videos/      # Downloaded VEO videos (auto-delete 30 days)
├── clannai-analysis/        # JSON analysis files (permanent)
├── clannai-web-assets/      # Optimized files for web player
└── clannai-clips/          # Video segments (auto-delete 7 days)
```

### Core Database Schema
```sql
users (id, email, subscription_tier, credits_remaining)
matches (id, veo_url, status, created_at, processing_time)  
analysis_results (match_id, file_type, s3_url, file_size)
processing_jobs (id, match_id, status, progress_percent, error_logs)
```

---

## 🔄 Automated Processing Workflow

### 1. User Input
- User pastes VEO URL: `https://app.veo.co/matches/xyz`
- Frontend validates URL format
- API creates processing job with unique ID

### 2. Background Processing
```bash
# EC2 instance automatically runs existing AI pipeline:
cd /opt/clannai/ai-pipeline
conda activate hooper-ai

# Steps 1-10 (existing working scripts):
python 1_extract_veo_data.py $VEO_URL      # 1 min
python 2_download_video.py $MATCH_ID        # 2 mins  
python 3_generate_clips.py $MATCH_ID        # 2 mins
python 4_simple_clip_analyzer.py $MATCH_ID  # 6 mins
python 5_synthesis.py $MATCH_ID             # 30 secs
python 6.5_veo_comparator.py $MATCH_ID      # 1 min
python 7.5_definite_events_builder.py $MATCH_ID  # 1 min
python 8.5_other_events_extractor.py $MATCH_ID   # 1 min
python 9.5_match_summary_generator.py $MATCH_ID  # 30 secs
python 10_s3_uploader.py $MATCH_ID          # 1 min

# Total: ~15 minutes
```

### 3. Results Available
Frontend receives completion notification and loads:
- Interactive video player with timeline events
- Match summary and tactical insights
- Downloadable analysis reports

---

## 💻 Frontend Specifications

### Landing Page
- **Hero section:** "Paste VEO URL → Get AI Analysis in 15 Minutes"
- **Live demo:** Embedded video player showing sample analysis
- **Input form:** VEO URL validation + "Analyze Match" button
- **Pricing:** Clear pricing display (pay-per-match or subscription)

### Processing Page  
- **Progress bar:** Real-time updates (Downloading → Analyzing → Building Timeline)
- **Estimated time:** Countdown timer showing minutes remaining
- **Background info:** What the AI is doing at each step
- **Option to close:** Email notification when complete

### Video Player Interface
```
┌─────────────────────────────────────────────────────────────┐
│ Left Panel: AI Insights    │ Center: Video Player           │
│ - Match Summary           │ - Timeline with 66 events      │
│ - Team Analysis           │ - Click events to jump         │
│ - Coaching Tips           │ - Hover for descriptions       │
│ - Key Moments             │ - Filter by event type         │
└───────────────────────────┴─────────────────────────────────┘
```

### Required Interactive Features
- **Timeline Events:** Goals, shots, fouls, cards, corners, substitutions
- **Event Filtering:** Show/hide specific event types
- **Quick Navigation:** Click any event to jump to that moment
- **Rich Descriptions:** AI-generated context for each event
- **Download Options:** PDF reports, JSON data export

---

## 📊 Performance & Scaling Requirements

### Target Metrics
- **Processing Time:** <18 minutes per match (current: ~15 minutes)
- **Uptime:** 99.5% availability
- **Concurrent Processing:** Handle 20+ matches simultaneously
- **API Response:** <500ms for status checks
- **Video Loading:** <3 seconds to start playback

### Cost Optimization
- **Per-match cost:** <$0.50 (current estimate: $0.37)
- **Auto-scaling:** Spin up/down EC2 instances based on queue length
- **Storage lifecycle:** Auto-delete temporary files after set periods
- **CDN caching:** CloudFront for fast video delivery

### Monitoring Requirements
```python
# Essential CloudWatch metrics:
- Processing success rate (target: >95%)
- Average queue wait time (target: <2 minutes)  
- Storage costs per match (target: <$0.10)
- User session duration (engagement metric)

# Critical alerts:
- Processing failure >5% → Page engineer
- Queue backup >50 jobs → Auto-scale
- Cost spike >150% → Financial alert
```

---

## 🔐 Security & Compliance

### Authentication & Authorization
- **User accounts:** JWT-based authentication
- **Rate limiting:** Prevent abuse (10 analyses/hour for free tier)
- **VEO credentials:** Secure storage in AWS Secrets Manager
- **API security:** Input validation, SQL injection prevention

### Data Protection
- **Video storage:** Encrypted at rest, auto-deletion policies
- **User data:** GDPR-compliant data handling
- **Access control:** Pre-signed S3 URLs with expiration
- **Network security:** VPC with private subnets for processing

---

## 🚀 Deployment & DevOps

### Infrastructure as Code
```hcl
# Terraform resources needed:
- ECS cluster for API services
- Auto Scaling Group for processing instances  
- RDS PostgreSQL with automated backups
- S3 buckets with lifecycle policies
- CloudFront distribution for global video delivery
- Route53 for custom domain (clannai.com)
- SSL certificates via ACM
```

### CI/CD Pipeline
```yaml
# Required deployment flow:
1. Code push → Automated tests
2. Tests pass → Build Docker images
3. Deploy to staging → Integration tests  
4. Manual approval → Production deployment
5. Health checks → Rollback if issues
```

---

## 📋 Delivery Milestones

### Week 1: Foundation (Days 1-2)
- [ ] AWS infrastructure setup (EC2, S3, RDS)
- [ ] Basic API with job creation endpoints
- [ ] Database schema + user management
- [ ] Job queue system (Redis + Celery)

### Week 2: Core Processing (Days 3-4)  
- [ ] EC2 automation for AI pipeline execution
- [ ] Real-time progress tracking
- [ ] S3 integration for file uploads
- [ ] Error handling + retry logic

### Week 3: Frontend (Days 5-6)
- [ ] Landing page with VEO URL input
- [ ] Processing status page with progress updates
- [ ] Interactive video player with timeline
- [ ] Results display + download features

### Week 4: Production Ready (Day 7)
- [ ] Auto-scaling configuration
- [ ] Monitoring + alerting setup
- [ ] Security hardening + SSL
- [ ] Performance optimization
- [ ] Final testing + deployment

---

## 🎯 Success Criteria

**Technical Requirements:**
- ✅ User can paste VEO URL and get analysis in <18 minutes
- ✅ Interactive video player with 66+ timeline events  
- ✅ System handles 20+ concurrent analyses
- ✅ 99.5% uptime with proper monitoring
- ✅ Mobile-responsive interface

**Business Requirements:**
- ✅ Cost per analysis <$0.50
- ✅ User-friendly interface (non-technical coaches can use)
- ✅ Scalable to 1000+ matches/day
- ✅ Ready for customer demos and beta testing

---
---

## 📞 Contact & Resources

**Existing Assets:**
- Complete AI pipeline (proven, generates all required outputs)
- AWS account with appropriate permissions
- Domain registration ready
- Sample analysis files for testing

**Support Available:**
- AI pipeline documentation and examples
- AWS architecture guidance
- Product requirements clarification
- Beta testing coordination

**Let's build something incredible. 🚀**

---

*This specification provides everything needed to build a complete automated football analysis platform. The AI engine is proven - now we need the cloud automation and user interface to make it market-ready.*