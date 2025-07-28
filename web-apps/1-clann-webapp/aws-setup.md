# 🚀 AWS Production Deployment Guide

## 🎯 Goal: Live Website at clannai.com Tomorrow

**Complete AWS production deployment for professional demo**

---

## 📋 AWS Services We'll Use

- **RDS PostgreSQL** → Production database
- **S3** → Video file storage + static assets
- **ECS/Fargate** → Containerized backend API
- **ECR** → Container registry
- **VPC** → Network security
- **CloudFront** → CDN (optional)
- **Route 53** → Domain management

---

## 🔧 AWS Setup Commands

### 1. RDS PostgreSQL Database (15 mins)

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier clannai-prod-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username clannai_admin \
  --master-user-password "ClannAI_2024_Secure!" \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-name clann_mvp \
  --backup-retention-period 7 \
  --multi-az false \
  --publicly-accessible true \
  --storage-encrypted true

# Wait for RDS to be available (5-10 mins)
aws rds wait db-instance-available --db-instance-identifier clannai-prod-db

# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier clannai-prod-db \
  --query 'DBInstances[0].Endpoint.Address'
```

### 2. Load Database Schema & Data

```bash
# Set database URL
export DATABASE_URL="postgresql://clannai_admin:ClannAI_2024_Secure!@clannai-prod-db.xxxxxxxxx.eu-west-1.rds.amazonaws.com:5432/clann_mvp"

# Load schema
psql $DATABASE_URL < db/schema.sql

# Load demo data
psql $DATABASE_URL < db/seeds/demo_data.sql

# Verify data loaded
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM games;"
```

### 3. S3 Bucket Setup (10 mins)

```bash
# Create S3 bucket
aws s3 mb s3://clannai-video-storage-prod

# Configure bucket for public read access
aws s3api put-bucket-cors \
  --bucket clannai-video-storage-prod \
  --cors-configuration file://s3-cors.json

# Upload demo videos (if we have any)
aws s3 sync ./demo-videos/ s3://clannai-video-storage-prod/videos/ --acl public-read
```

**Create s3-cors.json:**
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

### 4. Container Setup (15 mins)

```bash
# Create ECR repository
aws ecr create-repository --repository-name clannai-backend-prod

# Get ECR login token
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.eu-west-1.amazonaws.com

# Build and tag Docker image
cd backend
docker build -t clannai-backend .
docker tag clannai-backend:latest 123456789012.dkr.ecr.eu-west-1.amazonaws.com/clannai-backend-prod:latest

# Push to ECR
docker push 123456789012.dkr.ecr.eu-west-1.amazonaws.com/clannai-backend-prod:latest
```

### 5. ECS/Fargate Deployment

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name clannai-prod-cluster

# Register task definition (see ecs-task-definition.json)
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create ECS service
aws ecs create-service \
  --cluster clannai-prod-cluster \
  --service-name clannai-backend-service \
  --task-definition clannai-backend-prod:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxxx],securityGroups=[sg-xxxxxxxxx],assignPublicIp=ENABLED}"
```

---

## 🌐 Frontend Deployment (Vercel)

### 1. Deploy to Vercel (5 mins)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://clannai-backend-prod.xxxxxxxxx.amazonaws.com

vercel env add NEXT_PUBLIC_S3_BUCKET production  
# Enter: clannai-video-storage-prod
```

### 2. Custom Domain Setup

```bash
# Add domain to Vercel project
vercel domains add clannai.com

# Configure DNS (in your domain registrar):
# CNAME: www.clannai.com → cname.vercel-dns.com
# A: clannai.com → 76.76.19.19
```

---

## 🔑 Environment Variables

### Backend (.env.production)
```env
NODE_ENV=production
PORT=3002

# Database
DATABASE_URL=postgresql://clannai_admin:ClannAI_2024_Secure!@clannai-prod-db.xxxxxxxxx.eu-west-1.rds.amazonaws.com:5432/clann_mvp

# JWT
JWT_SECRET=your_super_secret_jwt_key_here

# AWS S3
AWS_REGION=eu-west-1
S3_BUCKET=clannai-video-storage-prod
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# CORS
CORS_ORIGIN=https://clannai.com
```

### Frontend (.env.production)
```env
NEXT_PUBLIC_API_URL=https://clannai-backend-prod.xxxxxxxxx.amazonaws.com
NEXT_PUBLIC_S3_BUCKET=clannai-video-storage-prod
NEXT_PUBLIC_APP_ENV=production
```

---

## ✅ Production Checklist

### Before Deployment:
- [ ] AWS CLI configured with credentials
- [ ] Docker installed and running
- [ ] Domain purchased and ready
- [ ] SSL certificates configured
- [ ] Environment variables set

### After Deployment:
- [ ] RDS database accessible
- [ ] S3 bucket configured and accessible
- [ ] ECS service running (1/1 tasks)
- [ ] Vercel deployment successful
- [ ] Domain pointing to Vercel
- [ ] SSL certificate valid
- [ ] API endpoints responding
- [ ] Demo data loaded and accessible

### Test URLs:
- [ ] https://clannai.com → Frontend works
- [ ] https://clannai-backend-prod.xxxxxxxxx.amazonaws.com/health → API health check
- [ ] https://clannai.com/login → Login page loads
- [ ] https://clannai.com/dashboard → Dashboard (after login)

---

## 🚨 If Something Goes Wrong

### Quick Fixes:
```bash
# Check ECS service status
aws ecs describe-services --cluster clannai-prod-cluster --services clannai-backend-service

# Check RDS status
aws rds describe-db-instances --db-instance-identifier clannai-prod-db

# Check S3 bucket
aws s3 ls s3://clannai-video-storage-prod

# Restart ECS service
aws ecs update-service --cluster clannai-prod-cluster --service clannai-backend-service --force-new-deployment

# Redeploy frontend
cd frontend && vercel --prod
```

---

## 💰 AWS Costs (Estimate)

**Monthly costs for MVP:**
- RDS t3.micro: ~$13/month
- ECS Fargate: ~$10/month  
- S3 storage (10GB): ~$0.25/month
- Data transfer: ~$5/month
- **Total: ~$30/month**

**Demo period (1 week): ~$7**

---

## 🔥 READY FOR PRODUCTION!

**End result: clannai.com live with:**
- ✅ Professional domain
- ✅ SSL certificate  
- ✅ AWS RDS database
- ✅ S3 video storage
- ✅ Containerized backend
- ✅ CDN-optimized frontend
- ✅ Ready for 5 paying customers! 