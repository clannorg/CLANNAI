# 1-Clann-WebApp 🏈

A unified football analysis platform built with Next.js 15, combining the best features from both existing ClannAI applications into one modern, football-focused webapp.

## 🎯 **What This App Does**

### **Core Workflow**
```
User Uploads Football Video → AI Processing (VM) → JSON Stats → Video Player with Events
```

### **Key Features**
- **🎥 Advanced Video Player** with event tagging and timeline overlay
- **📤 Simple File Upload** for football game footage
- **🤖 AI Processing Integration** with your VM for automatic event detection
- **📊 Event Visualization** with color-coded timeline markers
- **👥 Team Management** with role-based access
- **💳 Payment Integration** for premium features
- **📱 Responsive Design** for mobile and desktop

## 🏗️ **Architecture**

### **Frontend (Next.js 15)**
```
/app
├── /dashboard
│   ├── /games (list of uploaded games)
│   ├── /games/[id] (game details)
│   └── /games/[id]/video (video player with events)
├── /upload (simple file upload)
├── /auth (login/register)
└── /teams (team management)
```

### **Backend (Express API)**
```
/api
├── /auth (login/register)
├── /games (CRUD for games)
├── /upload (file upload to S3)
├── /events (AI processing results)
├── /teams (team management)
└── /payments (Stripe integration)
```

### **Database (PostgreSQL)**
```sql
users (id, email, password_hash, role, created_at)
teams (id, name, invite_code, subscription_status, created_at)
games (id, team_id, user_id, video_url, status, created_at)
events (id, game_id, time, event_type, team, outcome, validated)
```

## 🚀 **Technology Stack**

### **Frontend**
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component primitives
- **Framer Motion** - Smooth animations
- **React Query** - Server state management

### **Backend**
- **Express.js** - Node.js web framework
- **PostgreSQL** - Reliable relational database
- **AWS S3** - File storage for videos
- **JWT** - Authentication tokens
- **Stripe** - Payment processing

### **AI Integration**
- **Custom VM** - AI processing for football events
- **JSON API** - Event data exchange
- **Real-time Updates** - Processing status updates

## 🎮 **User Experience**

### **For Regular Users**
1. **Upload** football game video
2. **Wait** for AI processing (5-10 minutes)
3. **View** analysis with event timeline
4. **Filter** and search events
5. **Export** reports and statistics

### **For Team Admins**
1. **Create** team and invite members
2. **Manage** team subscriptions
3. **Review** all team games
4. **Access** premium features

### **For Company Analysts**
1. **View** all games across teams
2. **Upload** additional analysis
3. **Update** game statuses
4. **Generate** comprehensive reports

## 🏈 **Football-Specific Features**

### **Event Types**
- **Goal** - Successful scoring attempts
- **Shot** - Attempts on goal
- **Pass** - Successful passes
- **Tackle** - Defensive actions
- **Foul** - Rule violations
- **Corner** - Corner kicks
- **Free Kick** - Set piece situations

### **Team Management**
- **Red vs Blue** - Color-coded teams
- **Player Tracking** - Individual performance
- **Possession Stats** - Ball control metrics
- **Formation Analysis** - Tactical insights

### **Video Player Features**
- **Timeline Overlay** - Visual event markers
- **Event Filtering** - Show/hide event types
- **Click to Seek** - Jump to specific events
- **Fullscreen Support** - Immersive viewing
- **Keyboard Shortcuts** - Quick navigation

## 🔧 **Development Setup**

### **Prerequisites**
- Node.js 18+
- PostgreSQL 14+
- AWS Account (for S3)
- Stripe Account (for payments)

### **Local Development**
```bash
# Clone and setup
cd web-apps/1-clann-webapp
npm install

# Start frontend
cd frontend
npm run dev

# Start backend
cd ../backend
npm run dev

# Setup database
cd ../database
npm run migrate
```

### **Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/clann_football

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# JWT
JWT_SECRET=your_jwt_secret
```

## 🚀 **Deployment**

### **Frontend (AWS Amplify)**
- Automatic deployments from Git
- Global CDN for fast loading
- SSL certificates included

### **Backend (AWS EC2)**
- Node.js server on EC2
- Load balancer for scaling
- Auto-scaling groups

### **Database (AWS RDS)**
- Managed PostgreSQL
- Automated backups
- Multi-AZ for reliability

## 📈 **Future Enhancements**

### **Phase 2 Features**
- **Real-time Processing** - Live event detection
- **Advanced Analytics** - Player performance metrics
- **Team Comparisons** - Head-to-head analysis
- **Mobile App** - Native iOS/Android

### **Phase 3 Features**
- **AI Coaching** - Automated insights
- **Social Features** - Team sharing
- **Advanced Export** - PDF reports
- **API Access** - Third-party integrations

## 🎯 **Why This Approach**

### **Advantages**
- ✅ **Modern Tech Stack** - Next.js 15, TypeScript, Tailwind
- ✅ **Football-Focused** - No unnecessary complexity
- ✅ **Scalable Architecture** - Can grow with your needs
- ✅ **Professional UX** - Clean, intuitive interface
- ✅ **Cost-Effective** - Start simple, add features

### **Learning from Existing Apps**
- ✅ **clannai-frontend** - Advanced video player and modern UI
- ✅ **web-app-clannai** - Complete backend and team management
- ✅ **Combined** - Best of both worlds

## 🏆 **Success Metrics**

- **User Engagement** - Time spent analyzing games
- **Processing Speed** - AI analysis completion time
- **User Retention** - Monthly active users
- **Feature Adoption** - Premium subscription rate
- **Technical Performance** - Page load times, API response times

---

**Built with ❤️ for football analysis and team improvement** 