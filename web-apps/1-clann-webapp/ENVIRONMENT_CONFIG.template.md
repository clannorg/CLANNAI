# 🌍 Environment Configuration Guide

This document explains the environment setup for the ClannAI web application across different environments.

## 📋 Environment Overview

We have **two main environments**:
- **Local Development** (your machine)
- **Production** (live site at clannai.com)

Both environments use the **same AWS resources** (database, S3 buckets) to avoid data inconsistencies.

---

## 🖥️ Local Development Environment

### Backend (.env)
```env
# Local Development Environment Variables - Connected to AWS RDS

# Database Configuration (AWS RDS with SSL)
DATABASE_URL=postgresql://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]

# Fallback individual DB settings
DB_HOST=[RDS_ENDPOINT]
DB_PORT=5432
DB_NAME=postgres
DB_USER=[DB_USERNAME]
DB_PASSWORD=[DB_PASSWORD]

# Server Configuration
PORT=3002

# JWT Secret
JWT_SECRET=[YOUR_JWT_SECRET]

# Environment
NODE_ENV=development

# CORS Configuration (for local frontend)
CORS_ORIGIN=http://localhost:3000

# AI Configuration  
GEMINI_API_KEY=[YOUR_GEMINI_API_KEY]

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=[YOUR_AWS_ACCESS_KEY]
AWS_SECRET_ACCESS_KEY=[YOUR_AWS_SECRET_KEY]
AWS_REGION=eu-west-1
AWS_BUCKET_NAME=[YOUR_S3_BUCKET]

# Debug
DEBUG=true
```

### Frontend (.env.local)
```env
# Local frontend points to local backend
NEXT_PUBLIC_API_URL=http://localhost:3002
NEXT_PUBLIC_API_BASE_URL=http://localhost:3002/api

# App Configuration
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_NAME=ClannAI
NEXT_PUBLIC_APP_VERSION=1.0.0

# Video Storage
NEXT_PUBLIC_S3_BUCKET=[YOUR_S3_BUCKET]

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=true
```

---

## 🌐 Production Environment (clannai.com)

### Backend (Devopness Config)
```env
# Production Environment Variables

# Database Configuration (AWS RDS with SSL)
DATABASE_URL=postgresql://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]

# Server Configuration
PORT=3002

# JWT Secret
JWT_SECRET=[STRONG_PRODUCTION_JWT_SECRET]

# Environment
NODE_ENV=production

# CORS Configuration (for production frontend)
CORS_ORIGIN=https://clannai.com

# AI Configuration  
GEMINI_API_KEY=[YOUR_GEMINI_API_KEY]

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=[YOUR_AWS_ACCESS_KEY]
AWS_SECRET_ACCESS_KEY=[YOUR_AWS_SECRET_KEY]
AWS_REGION=eu-west-1
AWS_BUCKET_NAME=[YOUR_S3_BUCKET]

# Debug
DEBUG=false

# Stripe Configuration
STRIPE_SECRET_KEY=[YOUR_STRIPE_SECRET_KEY]
STRIPE_WEBHOOK_SECRET=[YOUR_STRIPE_WEBHOOK_SECRET]
STRIPE_PRICE_ID=[YOUR_STRIPE_PRICE_ID]
```

### Frontend (Devopness Config)
```env
# Production frontend points to production API
NEXT_PUBLIC_API_URL=https://api.clannai.com
NEXT_PUBLIC_API_BASE_URL=https://api.clannai.com/api

# App Configuration
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_APP_NAME=ClannAI
NEXT_PUBLIC_APP_VERSION=1.0.0

# Video Storage
NEXT_PUBLIC_S3_BUCKET=[YOUR_S3_BUCKET]

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_DEBUG=false
```

---

## 🔑 Key Differences

| Setting | Local Development | Production |
|---------|------------------|------------|
| **Backend URL** | `http://localhost:3002` | `https://api.clannai.com` |
| **Frontend URL** | `http://localhost:3000` | `https://clannai.com` |
| **CORS Origin** | `http://localhost:3000` | `https://clannai.com` |
| **NODE_ENV** | `development` | `production` |
| **Debug** | `true` | `false` |
| **Analytics** | `false` | `true` |
| **Database** | ✅ Same AWS RDS | ✅ Same AWS RDS |
| **S3 Bucket** | ✅ Same bucket | ✅ Same bucket |
| **JWT Secret** | Simple dev key | Strong production key |

---

## 🚨 Common Issues & Solutions

### Clips Not Working on Production
**Problem**: 500 errors when creating video clips

**Likely Causes**:
1. Missing environment variables in Devopness
2. S3 bucket permissions
3. FFmpeg not installed on production server

**Solution**: Ensure all AWS variables are set in Devopness config.

### CORS Errors
**Problem**: Frontend can't connect to backend

**Solution**: Verify `CORS_ORIGIN` matches your frontend URL exactly.

### Database Connection Issues
**Problem**: Backend can't connect to PostgreSQL

**Solution**: Check `DATABASE_URL` format and SSL settings.

---

## 📝 Deployment Checklist

### Before Deploying:
- [ ] Update Devopness environment variables
- [ ] Verify CORS_ORIGIN matches frontend domain
- [ ] Check S3 bucket name consistency
- [ ] Ensure all secrets are properly set
- [ ] Test database connection

### After Deploying:
- [ ] Verify frontend loads at clannai.com
- [ ] Test API connection at api.clannai.com
- [ ] Check video upload/analysis works
- [ ] Test clip creation functionality
- [ ] Verify user authentication

---

## 🔧 Quick Commands

### Local Development
```bash
# Start backend
cd backend && npm start

# Start frontend  
cd frontend && npm run dev
```

### Production Deployment
```bash
# Deploy via Devopness (auto-triggered on git push)
git push origin main
```

---

## 📞 Troubleshooting

If something breaks:

1. **Check logs** in Devopness dashboard
2. **Verify environment variables** are set correctly
3. **Test API endpoints** manually
4. **Check database connection** with psql
5. **Verify S3 permissions** in AWS console

---

## 🔐 Security Notes

- **Never commit** actual API keys or passwords to Git
- Use `ENVIRONMENT_CONFIG.md` (gitignored) for actual values
- This template shows the structure only
- Replace `[PLACEHOLDER]` values with real credentials

---

**Last Updated**: December 2024  
**Maintainer**: Thomas Bradley