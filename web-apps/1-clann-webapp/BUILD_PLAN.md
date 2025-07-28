# 🔥 **TODAY BUILD PLAN - July 28th (REVISED)**
## **Meeting Tomorrow - Get Shit Working + File Upload**

---

## 🎯 **REVISED SCOPE - FULL FILE HANDLING**

### **IN SCOPE TODAY:**
✅ **Database setup** with demo data  
✅ **Backend API** (auth, teams, games, JSON upload)  
✅ **Frontend pages** (login, dashboard, game view)  
✅ **VEO URL upload** creates game records  
✅ **FILE UPLOAD** (MP4, MOV to S3) **← NEW**  
✅ **FILE DOWNLOAD** (signed S3 URLs) **← NEW**  
✅ **JSON file upload** (company analysts only)  
✅ **Team join codes** functionality  
✅ **Basic video player** with events timeline  
✅ **Company dashboard** (view all games + upload JSON)  

### **OUT OF SCOPE TODAY:**
❌ **Video encoding/compression** (store as-is)  
❌ **Chunked upload** (simple multipart)  
❌ **Upload progress bars** (basic only)  
❌ **Stripe payments** (add later)  
❌ **Mobile optimization** (desktop first)  
❌ **Email verification** (basic auth only)  

---

## 🔄 **REVISED DATA FLOW**

### **User Workflow:**
1. **Upload game** → Either VEO URL OR video file to S3
2. **View dashboard** → See uploaded games with download links
3. **Download original** → Signed S3 URL for file access
4. **Click game** → Video player + events (if JSON uploaded)

### **Company Workflow:**
1. **View ALL games** from ALL users (VEO + uploaded files)
2. **Upload JSON file** → VM analysis becomes visible
3. **Status changes** → "pending" → "analyzed"
4. **Download any file** → Access to all uploaded videos

### **File Storage:**
1. **Large video files** → S3 bucket storage
2. **VEO URLs** → PostgreSQL text field
3. **JSON analysis** → PostgreSQL JSONB column

---

## 📋 **EXACT PAGES TO BUILD (5 Pages)**

### **Frontend Pages (Next.js 15):**

#### **1. Landing Page (`/`)**
- Hero section with "Upload Game Footage" CTA
- Login/Register buttons
- **Time: 20 mins**

#### **2. Login Page (`/login`)**  
- Email/password form
- Toggle between login/register
- JWT token handling
- **Time: 30 mins**

#### **3. Dashboard (`/dashboard`)**
**Two tabs:**
- **Games Tab**: User's uploaded games (VEO + files) with download buttons
- **Team Tab**: Team join codes, team info  
- **Upload modal**: VEO URL OR file upload
- **Time: 90 mins** *(+30 for file handling)*

#### **4. Game View (`/games/[id]`)**
- **Video player** (VEO embed OR S3 file)
- **Download button** (if file upload)
- **Events timeline** (if JSON uploaded)
- **Events list** (click to jump to timestamp)
- **Time: 60 mins** *(+15 for download logic)*

#### **5. Company Dashboard (`/company`)**
- **List ALL games** from ALL users
- **[Upload JSON] button** for each game
- **[Download] button** for file uploads
- **Status indicators** (pending/analyzed)
- **Time: 45 mins** *(+15 for download access)*

---

## 🔌 **REVISED API ENDPOINTS**

### **Authentication (`/api/auth`)**
```
POST /api/auth/register    # Create user account
POST /api/auth/login       # Login with email/password  
GET  /api/auth/me          # Get current user
```

### **Games (`/api/games`)**
```
GET  /api/games            # Get user's games
POST /api/games            # Upload VEO URL → create game
POST /api/games/upload     # Upload video file to S3 ← NEW
GET  /api/games/:id        # Get game details + JSON events
GET  /api/games/:id/download # Get signed S3 download URL ← NEW
```

### **Analysis (`/api/analysis`)**
```
POST /api/games/:id/analysis # Upload JSON file (company only)
PUT  /api/games/:id/status   # Update status (company only)
```

### **Company (`/api/company`)**
```
GET  /api/company/games      # Get ALL games (all users)
GET  /api/games/:id/download # Download any file (company access)
```

### **Teams (`/api/teams`)**
```
POST /api/teams/join         # Join team by code
GET  /api/teams/:id          # Get team info
```

---

## 🗄️ **REVISED DATABASE STRUCTURE**

### **Games Table (Updated):**
```sql
games.video_url          -- VEO URL (if VEO upload)
games.s3_key            -- S3 file path (if file upload) ← NEW
games.original_filename  -- Original file name ← NEW
games.file_size         -- File size in bytes ← NEW
games.file_type         -- "veo" or "upload" ← NEW
games.status            -- 'pending' → 'analyzed'  
games.ai_analysis       -- JSONB from VM analysis
games.team_id           -- Team association
games.uploaded_by       -- User who uploaded
```

### **S3 Storage Structure:**
```
bucket-name/
├── games/
│   ├── uuid-1/
│   │   └── original.mp4     (2GB file)
│   ├── uuid-2/
│   │   └── original.mov     (1.5GB file)
│   └── uuid-3/
│       └── original.mp4     (3GB file)
```

---

## 🎨 **REVISED UI COMPONENTS**

### **Core Components (9 Total):**
1. **Header** - Navigation with auth state
2. **GameCard** - Display game with download button  
3. **UploadModal** - VEO URL OR file upload tabs **← UPDATED**
4. **FileUpload** - Drag/drop file upload component **← NEW**
5. **VideoPlayer** - VEO embed OR S3 video with events timeline
6. **EventsList** - Click to jump to timestamp
7. **StatusBadge** - PENDING/ANALYZED pills
8. **DownloadButton** - S3 signed URL download **← NEW**
9. **JSONUpload** - Company file upload button

### **Upload Modal Design:**
```
┌─────────────────────────────────────┐
│ Upload Game Footage                 │
├─────────────────────────────────────┤
│ [VEO URL] [File Upload]             │
├─────────────────────────────────────┤
│ VEO: Paste URL here                 │
│ File: [Drag files here] Max 5GB     │
│ Supported: MP4, MOV, AVI            │
├─────────────────────────────────────┤
│ [Cancel] [Upload]                   │
└─────────────────────────────────────┘
```

---

## ⚡ **REVISED BUILD ORDER & TIMING**

### **Phase 1: Foundation (45 mins)**
1. **Database setup** (15 mins)
   - Run schema.sql (updated with file fields)
   - Load demo data with 5 teams

2. **Backend core + S3** (30 mins)
   - Express server setup
   - Database connection
   - S3 SDK configuration
   - Basic auth middleware

### **Phase 2: Core APIs (90 mins)** *(+30 for S3)*
1. **Auth endpoints** (20 mins)
   - POST /auth/register, /auth/login
   - GET /auth/me

2. **Games endpoints** (35 mins) *(+10 for files)*
   - GET /games (user's games)
   - POST /games (VEO upload)
   - GET /games/:id (with JSON)

3. **File upload endpoints** (35 mins) **← NEW**
   - POST /games/upload (multipart to S3)
   - GET /games/:id/download (signed URLs)
   - File validation (size, type)

### **Phase 3: Frontend Core (120 mins)** *(+30 for file handling)*
1. **Auth pages** (30 mins)
   - Landing page + login/register

2. **Dashboard** (60 mins) *(+20 for file features)*
   - Games tab + upload modal (VEO + file)
   - Download buttons on game cards
   - Team tab + join codes

3. **Game view** (30 mins) *(+10 for download)*
   - Video player (VEO or S3)
   - Events display + download button

### **Phase 4: Company Features (45 mins)** *(+15 for file access)*
1. **Company dashboard** (30 mins)
   - List all games (VEO + files)
   - JSON upload button
   - Download access for all files

2. **Integration test** (15 mins)
   - Full workflow test (VEO + file)

### **Phase 5: Demo Data (15 mins)**
1. **Load demo data** (10 mins)
   - 5 teams with mixed VEO + uploaded files
   - Test download functionality

2. **Final polish** (5 mins)
   - Fix obvious bugs

---

## 🎯 **SUCCESS CRITERIA**

### **End of Today Demo Flow:**
1. **Landing page** → professional, clean
2. **Register/Login** → works smoothly
3. **Upload VEO URL** → creates game (pending)
4. **Upload video file** → stores in S3, creates game **← NEW**
5. **Download original** → signed S3 URL works **← NEW**
6. **Company uploads JSON** → game becomes analyzed
7. **View game** → video + events timeline
8. **5 demo teams** → mix of VEO + uploaded files

### **Must Work For Meeting:**
✅ **VEO URL upload** workflow  
✅ **Video file upload** to S3 **← NEW**  
✅ **File download** functionality **← NEW**  
✅ **JSON analysis upload** (company only)  
✅ **Events timeline** display  
✅ **Team join codes** functionality  
✅ **Company can see/download all**  

---

## 💰 **INFRASTRUCTURE NEEDED**

### **AWS S3 Setup:**
```bash
# Create S3 bucket
aws s3 mb s3://clann-game-videos

# Set CORS for uploads
aws s3api put-bucket-cors --bucket clann-game-videos

# Environment variables
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx  
AWS_REGION=us-east-1
S3_BUCKET=clann-game-videos
```

### **File Limits:**
- **Max file size**: 5GB per upload
- **Allowed formats**: MP4, MOV, AVI, MKV
- **Storage**: Pay per GB (starts cheap)

---

## 🚀 **REVISED TIME ESTIMATE**

**Backend: 2.5 hours** *(+1 for S3 integration)*  
**Frontend: 3 hours** *(+1 for file handling)*  
**Integration: 45 mins** *(+15 for file testing)*  
**Total: 6.25 hours** *(realistic with file features)*

**Start Time: Now**  
**End Time: ~7pm** *(later finish)*  
**Demo Ready: Tonight**  

---

## 🔥 **REVISED PLAN LOCKED**

**Full file handling + VEO support**

**User can:** Upload VEO OR video file, download originals  
**Company can:** Access all files, upload analysis  
**Demo shows:** Complete file management system  

**More complex, longer timeline, but full feature set! 🚀** 