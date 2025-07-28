# 🔥 **BUILD PLAN - July 28th (HYBRID APPROACH)**
## **Meeting Tomorrow - Modern Frontend + Simple Backend**

### **💡 HYBRID STRATEGY:**
✅ **Modern Frontend** → Copy components from clannai-frontend (Next.js 15, TypeScript, shadcn/ui)  
✅ **Simple Backend** → Express.js + PostgreSQL (no AWS complexity)  
✅ **Best of Both** → Professional UI + Reliable backend + Fast build time

---

## 🎯 **SIMPLIFIED SCOPE**

### **IN SCOPE TODAY:**
✅ **Database setup** with demo data  
✅ **Backend API** (auth, teams, games, JSON upload)  
✅ **Frontend pages** (login, dashboard, game view)  
✅ **VEO URL upload** creates game records  
✅ **Company S3 upload** (manual process) 
✅ **JSON analysis upload** (company analysts only)  
✅ **Team join codes** functionality  
✅ **Basic video player** with events timeline  
✅ **Company dashboard** (view all games + upload)  

### **OUT OF SCOPE TODAY:**
❌ **Direct file upload** from users (VEO URLs only)  
❌ **Download functionality** (no user downloads)  
❌ **Automated VM integration** (manual company process)  
❌ **Stripe payments** (add later)  
❌ **Mobile optimization** (desktop first)  
❌ **Email verification** (basic auth only)  

---

## 🔄 **SIMPLIFIED DATA FLOW**

### **User Workflow:**
1. **Upload VEO URL** → Creates game record (status: "pending")
2. **View dashboard** → See uploaded games with status
3. **Wait for processing** → Company handles manually
4. **View analyzed game** → S3 video + events timeline

### **Company Workflow:**
1. **View ALL VEO URLs** from all users
2. **Manual process** → Download VEO on VM → Upload to S3  
3. **Upload JSON analysis** → From VM processing
4. **Mark as analyzed** → Status changes to "analyzed"

### **Storage:**
- **VEO URLs** → PostgreSQL text field
- **S3 videos** → Company uploads after manual processing
- **JSON analysis** → PostgreSQL JSONB column

---

## 📋 **PAGES TO BUILD (4 Simple Pages)**

### **Frontend Pages (Next.js 15):**

#### **1. Landing/Login Page (`/`)** *(Combined like existing app)*
- **Hero section** with background video + "Upload Game Footage" 
- **Features showcase** (3 analysis examples with demo data)
- **Login/Register forms** (toggle when user clicks CTA)
- **JWT token** storage → Redirect dashboard
- **Time: 40 mins**

#### **2. Dashboard (`/dashboard`)**
**Two tabs:**
- **Games Tab**: User's uploaded VEO URLs with status badges
- **Team Tab**: Team join codes, team info  
- **Upload VEO URL modal**
- **Time: 60 mins**

#### **3. Game View (`/games/[id]`)**
- **S3 video player** (if analyzed)
- **Events timeline** (from JSON analysis)
- **Events list** (click to jump to timestamp)
- **Status display** (pending/analyzed)
- **Time: 45 mins**

#### **4. Company Dashboard (`/company`)**
- **List ALL VEO URLs** from all users
- **[Upload Video to S3] button** for each pending game
- **[Upload JSON] button** for analysis
- **[Mark Analyzed] button** to change status
- **Status indicators** (pending/analyzed)
- **Time: 40 mins**

---

## 🔌 **SIMPLIFIED API ENDPOINTS**

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
GET  /api/games/:id        # Get game details + JSON events
```

### **Company (`/api/company`)**
```
GET  /api/company/games           # Get ALL games (all users)
POST /api/games/:id/upload-video  # Upload S3 video (company only)
POST /api/games/:id/analysis      # Upload JSON analysis (company only)
PUT  /api/games/:id/status        # Mark as analyzed (company only)
```

### **Teams (`/api/teams`)**
```
POST /api/teams/join         # Join team by code
GET  /api/teams/:id          # Get team info
```

---

## 🗄️ **SIMPLIFIED DATABASE STRUCTURE**

### **Games Table:**
```sql
games.video_url          -- VEO URL (user uploads)
games.s3_key            -- S3 video path (company uploads)
games.status            -- 'pending' or 'analyzed'
games.ai_analysis       -- JSON from VM analysis
games.team_id           -- Team association
games.uploaded_by       -- User who uploaded VEO URL
```

---

## 🎨 **MODERN UI COMPONENTS** *(Taken from clannai-frontend)*

### **From shadcn/ui (Ready-Made):**
✅ **Button, Card, Dialog, Dropdown, Form**  
✅ **Input, Label, Select, Table, Tabs**  
✅ **Badge, Avatar, Progress, Skeleton**  
✅ **Sidebar, Sheet, Drawer, Tooltip**  

### **Advanced Video Player (Copy from clannai-frontend):**
✅ **VideoPlayerWithEvents** - 16KB component with HLS.js  
✅ **adaptive-video-player** - Smart resolution switching  
✅ **video-overlay-timeline** - Events timeline on video  
✅ **sidebar-events-list** - Filterable events with click-to-jump  

### **Auth Components (Copy from clannai-frontend):**
✅ **sign-in-form** - Professional login with validation  
✅ **sign-up-form** - Registration with form validation  

### **Landing Components (Copy from clannai-frontend):**
✅ **hero-section** - Professional hero with animations  
✅ **TypingEffect** - Dynamic text animation  

### **Custom Components (Build New - 15 mins total):**
1. **VEOUploadModal** - Simple URL input dialog  
2. **S3UploadButton** - Company file upload  
3. **JSONUploadButton** - Analysis upload  

**Result: Professional UI in 1.5 hours instead of 2+ hours!**

---

## ⚡ **SIMPLIFIED BUILD ORDER & TIMING**

### **Phase 1: Foundation (30 mins)**
1. **Database setup** (15 mins)
   - Run schema.sql
   - Load demo data with 5 teams

2. **Backend core** (15 mins)
   - Express server setup
   - Database connection
   - Basic auth middleware

### **Phase 2: Core APIs (60 mins)**
1. **Auth endpoints** (15 mins)
   - POST /auth/register, /auth/login
   - GET /auth/me

2. **Games endpoints** (25 mins)
   - GET /games (user's games)
   - POST /games (VEO URL upload)
   - GET /games/:id (with JSON)

3. **Company endpoints** (20 mins)
   - GET /company/games (all games)
   - POST /games/:id/upload-video (S3 upload)
   - POST /games/:id/analysis (JSON upload)

### **Phase 3: Modern Frontend (90 mins)**
1. **Copy clannai-frontend components** (15 mins)
   - Video player + auth forms + hero section
   - shadcn/ui setup + TypeScript config

2. **Landing/Login page** (25 mins)
   - Copy hero-section + sign-in/up-form components
   - Adapt to simple JWT backend

3. **Dashboard** (30 mins)
   - Games tab with copied UI components
   - Team tab + VEO upload modal

4. **Game view** (20 mins)
   - Copy VideoPlayerWithEvents component
   - Connect to PostgreSQL JSON data

### **Phase 4: Company Features (40 mins)**
1. **Company dashboard** (40 mins)
   - List all VEO URLs
   - S3 upload + JSON upload buttons
   - Status management

### **Phase 5: AWS Production Deploy (45 mins)**
1. **AWS RDS setup** (15 mins)
   - Create PostgreSQL RDS instance
   - Load schema + demo data
   - Configure security groups

2. **S3 bucket setup** (10 mins)
   - Create S3 bucket for videos
   - Configure CORS + public read access
   - Upload demo video files

3. **Backend deploy** (15 mins)
   - Container build + push to ECR
   - Deploy to ECS/Fargate
   - Configure environment variables

4. **Frontend deploy** (5 mins)
   - Deploy to Vercel
   - Configure API endpoint URLs

---

## 🎯 **SUCCESS CRITERIA**

### **End of Today Demo Flow:**
1. **Landing page** → professional, clean
2. **Register/Login** → works smoothly
3. **Upload VEO URL** → creates pending game
4. **Company dashboard** → sees all VEO URLs
5. **Company uploads** → S3 video + JSON analysis
6. **User views** → analyzed game with events
7. **Team join codes** → ARS269, CHE277, etc. work

### **Must Work For Meeting:**
✅ **VEO URL upload** workflow  
✅ **Company S3 upload** (manual)  
✅ **JSON analysis upload** (company only)  
✅ **Events timeline** display  
✅ **Team join codes** functionality  
✅ **Clean, professional** UI  

---

## 🛠️ **MODERN TECH STACK**

### **Frontend (Modern):**
✅ **Next.js 15.3.4** + **React 19** + **TypeScript**  
✅ **Tailwind CSS v4** (latest)  
✅ **shadcn/ui** (29 ready-made components)  
✅ **Advanced video player** with HLS.js + events timeline  
✅ **React Query** for API state management  
✅ **React Hook Form** + **Zod** validation  
✅ **Framer Motion** animations  
✅ **Hero section** with typing effects  

### **Backend (Simple & Reliable):**
✅ **Express.js** + **Node.js** (proven, fast)  
✅ **PostgreSQL** (reliable SQL database)  
✅ **JWT authentication** (no AWS dependency)  
✅ **bcrypt** password hashing  
✅ **Raw SQL queries** (no ORM complexity)  
✅ **Simple file uploads** to S3  

### **Deployment (FULL AWS PRODUCTION):**
✅ **Frontend**: Vercel (Next.js optimized)  
✅ **Backend**: AWS ECS/Fargate (containerized)  
✅ **Database**: AWS RDS PostgreSQL (managed)  
✅ **Storage**: AWS S3 (video files)  
✅ **Domain**: Live production URL  

---

## 🚀 **PRODUCTION TIME ESTIMATE**

**Backend: 1.5 hours** (Express + PostgreSQL - proven approach)  
**Frontend: 1.5 hours** (using clannai-frontend components saves 30 mins)  
**AWS Production Deploy: 45 mins** (RDS + S3 + ECS + Vercel)  
**Integration: 30 mins** (test + polish)  
**Total: 4.25 hours** (LIVE production website!)

**Start Time: Now**  
**End Time: ~4:15pm**  
**LIVE Website: Tonight → clannai.com**  

---

## 🔥 **HYBRID PLAN LOCKED**

**Modern VEO URL workflow:**

**Frontend:** Next.js 15 + clannai-frontend components (professional UI)  
**Backend:** Express.js + PostgreSQL (simple, reliable)  
**User:** Upload VEO URL only  
**Company:** Manual VM process → S3 upload → JSON upload  
**Result:** Advanced video player + events timeline + professional UI  

**Modern frontend + Simple backend = Fast build + Professional demo! 🚀** 