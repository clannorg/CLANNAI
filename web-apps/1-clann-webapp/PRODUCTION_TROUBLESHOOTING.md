# 🚨 Production Troubleshooting Guide

## 🎯 What We Learned from the AI Coach 500 Error Debug Session

This document captures the complete debugging process and lessons learned from resolving the AI Coach 500 error on production.

---

## 📋 The Problem We Solved

**Issue**: AI Coach returning 500 Internal Server Error on production while working perfectly locally.

**Root Cause**: Production server was using a different (invalid) Gemini API key than the local environment.

**Key Learning**: **Devopness Environment Variables override Configuration Files!**

---

## 🔍 How Devopness Environment Management Works

### **Two Layers of Configuration:**

#### **1. Configuration Files** (`.env` files)
- Located in: `Applications → clann-webapp-backend → Configuration Files`
- These are actual `.env` files deployed to the server
- Path on server: `/home/devopness/clann-webapp-backend/releases/[RELEASE]/web-apps/1-clann-webapp/backend/.env`

#### **2. Environment Variables** (Individual variables)
- Located in: `Applications → clann-webapp-backend → Variables`
- These are injected as `process.env.VARIABLE_NAME`
- **These OVERRIDE Configuration Files!**

### **Priority Order (Highest to Lowest):**
1. **Environment Variables** (Variables tab) ← **WINS**
2. Configuration Files (`.env` files)
3. Code defaults

---

## 🛠️ The Debug Process We Used

### **Step 1: Added Debug Endpoint**
Created `/api/ai-chat/debug` to inspect:
- Current working directory
- Environment variables loaded
- `.env` files found and their contents
- Which configuration source is active

### **Step 2: Enhanced Debug Information**
Added detailed logging to show:
- All environment variables containing "GEMINI", "API", or "KEY"
- Contents of all `.env` files found
- Which file/source contains the active Gemini key

### **Step 3: Traced the Source**
Discovered the production server was loading:
- **Wrong key**: `AIzaSyDyQM...` (from Environment Variables)
- **Right key**: `AIzaSyDDANEUFo2qDRgSdd2pv6Er78i0x0yu0y8` (from local `.env`)

---

## 🎯 How We Fixed It

### **The Solution:**
Updated the `GEMINI_API_KEY` Environment Variable in Devopness to match the working local key.

### **Why This Fixed It:**
- Environment Variables have higher priority than Configuration Files
- The server was loading the wrong key from Environment Variables
- Updating the Environment Variable immediately fixed the issue

---

## 🚀 Production Environment Architecture

### **Server Structure:**
```
/home/devopness/clann-webapp-backend/
├── releases/
│   └── 2025-08-28-06-48-12/          ← Current release
│       └── web-apps/1-clann-webapp/backend/
│           ├── .env                   ← Configuration File (if exists)
│           ├── routes/
│           ├── utils/
│           └── server.js
└── current → releases/[LATEST]/       ← Symlink to current
```

### **Environment Loading Order:**
1. Devopness injects Environment Variables into `process.env`
2. Node.js loads `.env` file (if exists) using dotenv
3. Environment Variables override `.env` file values
4. Application starts with final merged environment

---

## 🔧 Debugging Tools We Built

### **Debug Endpoint: `/api/ai-chat/debug`**

**Usage:**
```bash
curl https://api.clannai.com/api/ai-chat/debug
```

**Shows:**
- Current Gemini API key being used
- All relevant environment variables
- All `.env` files found on server
- Process information (working directory, Node version)
- Which configuration source is active

### **Key Debug Fields:**
```json
{
  "current_gemini_key": {
    "exists": true,
    "length": 39,
    "start": "AIzaSyDDAN",
    "full_key_for_debug": "AIzaSyDDANEUFo2qDRgSdd2pv6Er78i0x0yu0y8"
  },
  "all_relevant_env_vars": {
    "GEMINI_API_KEY": {
      "exists": true,
      "source": "environment_variable"
    }
  },
  "env_files_found": {
    "/path/to/.env": {
      "gemini_key_in_file": "AIzaSyDDAN...",
      "is_active_env_file": true
    }
  }
}
```

---

## 📚 Troubleshooting Playbook

### **When AI Coach Returns 500 Error:**

#### **Step 1: Check Debug Endpoint**
```bash
curl https://api.clannai.com/api/ai-chat/debug | jq
```

#### **Step 2: Verify Gemini Key**
Look for `current_gemini_key.start` - should be `AIzaSyDDAN` (your working key)

#### **Step 3: Check Environment Variables**
- Go to Devopness → Applications → clann-webapp-backend → Variables
- Find `GEMINI_API_KEY`
- Verify it matches your working local key

#### **Step 4: Check Configuration Files**
- Go to Devopness → Applications → clann-webapp-backend → Configuration Files
- Check if `.env` file has conflicting Gemini key
- Remember: Environment Variables override Configuration Files

#### **Step 5: Update the Correct Source**
- If using Environment Variables: Update in Variables tab
- If using Configuration Files: Update `.env` file AND remove Environment Variable

#### **Step 6: Redeploy**
```bash
git push origin main  # Triggers auto-deployment
```

### **When Training Recommendations Show `null`:**

#### **Check S3 URLs in Database:**
```sql
SELECT id, team_name, training_url FROM games WHERE id = 'YOUR_GAME_ID';
```

#### **Verify S3 File Exists:**
```bash
curl -I "https://s3-url-from-database"
```

#### **Check API Response:**
```bash
curl https://api.clannai.com/api/games/YOUR_GAME_ID/training
```

---

## 🎯 Best Practices We Learned

### **1. Environment Management:**
- **Use EITHER Environment Variables OR Configuration Files, not both**
- **Document which approach you're using**
- **Keep local and production keys in sync**

### **2. Debugging Production:**
- **Always add debug endpoints for complex integrations**
- **Log environment variable sources**
- **Use temporary full key logging for debugging (remove after)**

### **3. Deployment Process:**
- **Test locally first**
- **Check debug endpoint after deployment**
- **Verify API keys are working**
- **Test end-to-end functionality**

### **4. Configuration File Strategy:**
```
Recommended: Use Configuration Files (.env) only
- Easier to manage
- Version controlled structure
- Clear file-based configuration
- Avoid Environment Variable overrides
```

---

## 🚨 Emergency Recovery

### **If Production Breaks:**

#### **Quick Fix:**
1. Go to Devopness Variables tab
2. Update `GEMINI_API_KEY` to working value
3. Redeploy immediately

#### **Permanent Fix:**
1. Decide on Environment Variables OR Configuration Files
2. Remove the unused configuration method
3. Document the chosen approach
4. Update this guide

---

## 📞 Debug Commands

### **Check Current Environment:**
```bash
# Via debug endpoint
curl https://api.clannai.com/api/ai-chat/debug

# Check specific variable
curl https://api.clannai.com/api/ai-chat/debug | jq '.current_gemini_key'
```

### **Test AI Chat:**
```bash
# Test endpoint directly
curl -X POST https://api.clannai.com/api/ai-chat/game/GAME_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Test message"}'
```

### **Check Database Connection:**
```bash
# Via any API endpoint
curl https://api.clannai.com/api/games
```

---

## 🔐 Security Notes

- **Remove `full_key_for_debug` from production after debugging**
- **Never commit actual API keys to Git**
- **Use secure environment variable management**
- **Rotate API keys regularly**

---

## 📝 Maintenance Checklist

### **Monthly:**
- [ ] Verify all API keys are working
- [ ] Check debug endpoint functionality
- [ ] Test AI Coach on production
- [ ] Review environment variable consistency

### **Before Major Deployments:**
- [ ] Test locally with production-like environment
- [ ] Verify all environment variables are set
- [ ] Check debug endpoint after deployment
- [ ] Test critical user flows

---

## 🎉 Success Indicators

### **AI Coach Working:**
- Debug endpoint shows correct Gemini key (`AIzaSyDDAN...`)
- AI chat returns responses (not 500 errors)
- Training recommendations display properly

### **Environment Healthy:**
- All environment variables loaded correctly
- Configuration files found and parsed
- No conflicting configuration sources

---

**Last Updated**: August 28, 2025  
**Debugged By**: Thomas Bradley  
**Status**: ✅ Production AI Coach Working  
**Next Review**: September 2025
