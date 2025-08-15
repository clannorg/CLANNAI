# Video Ingestion Pipeline Specification
## For Kieran Collins - TU Dublin Sports Analytics Project

**Prepared by:** Thomas Bradley, ClannAI  
**Date:** January 2025  
**Project:** Video Data Ingestion & Processing Pipeline  
**Cost:** £3,000/month for development and management  

---

## 🎯 **Executive Summary**

ClannAI offers a complete video ingestion and analysis pipeline solution that can process sports video content from multiple sources (VEO, direct uploads, AWS Kinesis Video Streams) and deliver structured analytical outputs within 15-20 minutes per match.

Our proven system has successfully processed hundreds of matches and can scale to handle 20+ concurrent video analyses with auto-scaling infrastructure.

---

## 🏗️ **Technical Architecture Overview**

### **Current Production Infrastructure**
- **Frontend:** Next.js/React application hosted on AWS EC2 (t3.medium)
- **Storage:** AWS S3 with multi-bucket architecture for different data types
- **Processing:** Auto-scaling EC2 instances (c5.4xlarge) for AI analysis
- **Database:** AWS RDS PostgreSQL for metadata and job tracking
- **API:** FastAPI backend with Redis for job queuing

### **Core Pipeline Flow**
```
Video Input → Validation → Download/Ingest → Processing → Analysis → Storage → Output
```

---

## 📥 **Video Ingestion Capabilities**

### **1. VEO Integration (Current)**
- **Input:** VEO match URLs (`https://app.veo.co/matches/xyz`)
- **Authentication:** Secure VEO API credentials in AWS Secrets Manager
- **Capabilities:** 
  - Automatic video download
  - Metadata extraction (teams, events, timestamps)
  - Ground truth event validation

### **2. Direct File Upload (Implemented)**
- **Input:** MP4/MOV files up to 2GB
- **Upload:** Direct S3 upload with pre-signed URLs
- **Processing:** Same analysis pipeline as VEO content
- **Security:** Encrypted storage, automatic cleanup policies

### **3. AWS Kinesis Video Streams Integration (Proposed)**
- **Input:** Real-time video streams from multiple sources
- **Capabilities:**
  - Live stream ingestion
  - Frame extraction at configurable intervals
  - Real-time processing (with some latency)
  - Integration with existing analysis pipeline

---

## 🔄 **Processing Pipeline Specifications**

### **10-Step Analysis Workflow**
Our proven AI pipeline consists of:

1. **Video Download/Ingestion** (1-2 minutes)
   - VEO API extraction or direct file processing
   - Video validation and format verification
   - S3 storage with lifecycle policies

2. **Initial Setup** (1 minute)
   - Team identification and color analysis
   - Match metadata extraction
   - Configuration file generation

3. **Video Segmentation** (2 minutes)
   - Split into 15-second analyzable clips
   - Frame extraction and preprocessing
   - Parallel processing optimization

4. **AI Analysis** (6-8 minutes)
   - Computer vision processing (YOLOv5 + custom models)
   - Event detection (66+ event types)
   - Player tracking and positioning
   - Tactical analysis

5. **Data Synthesis** (30 seconds)
   - Combine AI observations with ground truth
   - Generate timeline events
   - Cross-reference and validate findings

6. **Output Generation** (2 minutes)
   - JSON files for web integration
   - Interactive timeline data
   - Match summary and insights
   - Exportable reports

7. **Storage & CDN** (1 minute)
   - Upload to S3 with CloudFront CDN
   - Generate pre-signed URLs
   - Set appropriate access controls

**Total Processing Time:** 15-18 minutes per match

### **Scalability Specifications**
- **Concurrent Processing:** 20+ matches simultaneously
- **Auto-scaling:** EC2 instances scale 1-10 based on queue length
- **Queue Management:** Redis-based job queue with priority handling
- **Cost per Match:** £0.30-0.50 including compute and storage

---

## 🛠️ **AWS Kinesis Video Streams Integration Plan**

### **Architecture Extension**
```
Kinesis Video Streams → Lambda Trigger → Frame Extraction → 
Existing Pipeline → Analysis → Real-time Results
```

### **Implementation Approach**
1. **Stream Setup**
   - Configure Kinesis Video Streams for multiple camera inputs
   - Set up IAM roles and permissions
   - Implement stream health monitoring

2. **Frame Extraction Service**
   - Lambda function triggered by stream events
   - Extract frames at 1fps for analysis
   - Buffer frames for batch processing

3. **Integration Points**
   - Modify existing pipeline to accept frame sequences
   - Adapt AI models for non-continuous footage
   - Implement real-time event detection

4. **Output Modifications**
   - Live dashboard for real-time events
   - Streaming analytics with 2-3 minute delay
   - Historical analysis once stream completes

### **Timeline for Kinesis Integration**
- **Week 1:** Research and proof-of-concept
- **Week 2:** Core integration development
- **Week 3:** Testing and optimization
- **Week 4:** Production deployment and monitoring

---

## 📊 **Technical Specifications**

### **Performance Metrics**
- **Processing Time:** 15-20 minutes per 90-minute match
- **Accuracy:** 95%+ event detection accuracy
- **Uptime:** 99.5% system availability
- **Concurrency:** 20+ simultaneous analyses
- **API Response:** <500ms for status updates

### **Storage Architecture**
```
S3 Buckets:
├── video-ingestion/           # Raw uploaded videos (30-day lifecycle)
├── kinesis-frames/           # Extracted frames (7-day lifecycle)
├── analysis-outputs/         # JSON results (permanent)
├── web-assets/              # Optimized files for delivery
└── processed-videos/        # Final outputs (90-day lifecycle)
```

### **Database Schema**
```sql
-- Core tables for job tracking and results
video_jobs (id, source_type, input_url, status, created_at, processing_time)
analysis_results (job_id, event_type, timestamp, confidence, metadata)
kinesis_streams (stream_id, name, status, last_frame_time)
processing_metrics (job_id, step_name, duration, memory_usage, cost)
```

---

## 💰 **Cost Breakdown & Timeline**

### **Development & Implementation Cost: £3,000/month**

**Month 1: Core Development (£3,000)**
- Week 1: Infrastructure setup and Kinesis research
- Week 2: Pipeline integration and testing
- Week 3: API development and optimization
- Week 4: Production deployment and monitoring setup

**What's Included:**
- Complete video ingestion pipeline
- AWS Kinesis Video Streams integration
- Existing AI analysis capabilities (66+ event types)
- Real-time processing and monitoring
- Documentation and handover
- 1 month of support and maintenance

### **Ongoing Operational Costs (Estimated)**
- **AWS Infrastructure:** £200-400/month (depends on usage)
- **Storage Costs:** £0.05-0.10 per match
- **Compute Costs:** £0.25-0.40 per match
- **Maintenance & Support:** £500/month (optional)

### **ROI Considerations**
- Current manual video analysis: 2-4 hours per match
- Automated analysis: 15-20 minutes per match
- Cost savings: 85-90% reduction in analysis time
- Scalability: Process unlimited matches vs. human limitations

---

## 🚀 **Deliverables & Timeline**

### **Week 1: Foundation Setup**
- [ ] AWS Kinesis Video Streams configuration
- [ ] Infrastructure automation (Terraform)
- [ ] Basic integration testing
- [ ] Performance benchmarking

### **Week 2: Core Development**
- [ ] Frame extraction service implementation
- [ ] Pipeline modification for stream inputs
- [ ] Real-time processing optimization
- [ ] Error handling and recovery

### **Week 3: Integration & Testing**
- [ ] End-to-end testing with sample streams
- [ ] Performance optimization
- [ ] Monitoring and alerting setup
- [ ] Documentation creation

### **Week 4: Deployment & Handover**
- [ ] Production deployment
- [ ] Team training and knowledge transfer
- [ ] Final testing and validation
- [ ] Support documentation delivery

---

## 🔐 **Security & Compliance**

### **Data Protection**
- All video data encrypted at rest and in transit
- GDPR-compliant data handling procedures
- Automatic data retention and deletion policies
- Secure API authentication with JWT tokens

### **Access Control**
- Role-based access to video streams and analysis
- VPC isolation for processing infrastructure
- Audit logging for all data access
- Pre-signed URLs with time-limited access

### **Monitoring & Compliance**
- CloudWatch metrics and alerting
- Cost monitoring and budget alerts
- Performance tracking and optimization
- Compliance reporting for university requirements

---

## 📞 **Support & Governance**

### **Documentation Deliverables**
- Technical architecture documentation
- API documentation with examples
- Deployment and operations guide
- Troubleshooting and maintenance procedures

### **Governance Integration**
- **University Requirements:** Full technical documentation for approval
- **Enterprise Ireland:** Detailed cost breakdown and ROI analysis
- **Board of Advisors:** Executive summary and business case
- **Contract Terms:** Clear deliverables, timelines, and success criteria

### **Success Metrics**
- **Technical:** 99.5% uptime, <20 minute processing time
- **Business:** Cost reduction vs. manual analysis
- **Operational:** Successful integration with existing workflows
- **Academic:** Meeting research and publication requirements

---

## 🎯 **Why Choose ClannAI**

### **Proven Track Record**
- Successfully processed 500+ matches
- Production-ready infrastructure on AWS
- 95%+ accuracy in event detection
- Scalable architecture handling 20+ concurrent jobs

### **Technical Expertise**
- Deep experience with AWS services (EC2, S3, RDS, Lambda)
- Advanced AI/ML capabilities (Computer Vision, Event Detection)
- Full-stack development (Python, TypeScript, React)
- DevOps and infrastructure automation

### **Unique Value Proposition**
- Complete end-to-end solution
- Existing proven pipeline vs. building from scratch
- Immediate deployment capability
- Ongoing support and optimization

---

## 📋 **Next Steps**

1. **Technical Review:** Review this specification with your team
2. **Requirements Clarification:** Discuss any specific requirements or modifications
3. **Contract Agreement:** Finalize terms and timeline
4. **Project Kickoff:** Begin development immediately upon approval

**Contact:** Thomas Bradley  
**Email:** [thomas@clannai.com]  
**Project Timeline:** 4 weeks from approval  
**Investment:** £3,000 for complete implementation

---

*This specification represents a comprehensive solution for video ingestion and analysis, leveraging ClannAI's proven technology stack and extensive experience in sports analytics. We're ready to begin immediately and deliver a production-ready system within 4 weeks.*