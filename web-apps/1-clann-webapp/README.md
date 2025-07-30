# 🔥 ClannAI Football Analysis MVP

**Professional football analysis platform with AI-powered event detection**

## 🚀 Quick Start (Local Development)

```bash
# 1. Setup database
cd db && createdb clann_mvp && psql clann_mvp < schema.sql && psql clann_mvp < seeds/demo_data.sql

# 2. Start backend  
cd backend && npm install && npm start

# 3. Start frontend
cd frontend && npm install && npm run dev
```

## 🌐 Production Deployment (AWS)

```bash
# Full AWS production deployment
# See aws-setup.md for complete guide

# 1. Deploy to AWS (RDS + S3 + ECS)
./deploy-aws.sh

# 2. Deploy frontend to Vercel
cd frontend && vercel --prod

# Result: https://clannai.com LIVE!
```

## 📁 Structure

```
├── BUILD_PLAN.md       # 🔥 Complete build plan & specifications
├── backend/            # Express.js API server (port 3002)
├── frontend/           # Next.js 15 app (port 3000)  
└── db/                 # PostgreSQL schema & demo data
```

## 📋 Full Plan

**👉 See [BUILD_PLAN.md](BUILD_PLAN.md) for complete build specifications**

## 🎯 Goal

**LIVE WEBSITE at clannai.com → 5 paying customers at $5/game**

**Professional production demo → Meeting tomorrow ✅** 