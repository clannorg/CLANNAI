# 🎯 Frontend Development Plan

## 🏗️ **Target Architecture**

### **Tech Stack**
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI
- **State Management**: React Query + Context API
- **Authentication**: JWT with custom hooks
- **Video Player**: Custom component with event tagging
- **Charts**: Recharts or Chart.js
- **Maps**: React Leaflet for pitch visualization

---

## 📁 **Complete Folder Structure**

```
frontend/
├── public/
│   ├── clann-assets-package/
│   │   ├── clann-sliothar.png
│   │   ├── clann.ai-green.png
│   │   ├── clann.ai-white.png
│   │   └── [other brand assets]
│   ├── logo-white.png
│   ├── logo.png
│   └── favicon.ico
│
├── src/
│   ├── app/
│   │   ├── layout.tsx                    # Root layout with providers
│   │   ├── page.tsx                      # Landing page
│   │   ├── globals.css                   # Global styles
│   │   ├── favicon.ico
│   │   │
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx             # Login page
│   │   │   ├── register/
│   │   │   │   └── page.tsx             # Register page
│   │   │   └── forgot-password/
│   │   │       └── page.tsx             # Password reset
│   │   │
│   │   ├── dashboard/
│   │   │   ├── layout.tsx               # Dashboard layout
│   │   │   ├── page.tsx                 # Dashboard home
│   │   │   ├── loading.tsx              # Loading state
│   │   │   └── error.tsx                # Error boundary
│   │   │
│   │   ├── matches/
│   │   │   ├── page.tsx                 # Matches list
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx             # Match detail
│   │   │   │   ├── analysis/
│   │   │   │   │   └── page.tsx         # Match analysis
│   │   │   │   └── events/
│   │   │   │       └── page.tsx         # Events timeline
│   │   │   └── upload/
│   │   │       └── page.tsx             # Upload new match
│   │   │
│   │   ├── team/
│   │   │   ├── page.tsx                 # Team management
│   │   │   ├── members/
│   │   │   │   └── page.tsx             # Team members
│   │   │   └── settings/
│   │   │       └── page.tsx             # Team settings
│   │   │
│   │   ├── analytics/
│   │   │   ├── page.tsx                 # Analytics dashboard
│   │   │   ├── performance/
│   │   │   │   └── page.tsx             # Performance metrics
│   │   │   └── reports/
│   │   │       └── page.tsx             # Generated reports
│   │   │
│   │   └── settings/
│   │       ├── page.tsx                 # User settings
│   │       ├── profile/
│   │       │   └── page.tsx             # Profile settings
│   │       └── billing/
│   │           └── page.tsx             # Billing & subscription
│   │
│   ├── components/
│   │   ├── ui/                          # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── avatar.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── tooltip.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── table.tsx
│   │   │   ├── form.tsx
│   │   │   ├── calendar.tsx
│   │   │   ├── date-picker.tsx
│   │   │   ├── color-picker.tsx
│   │   │   └── [other UI components]
│   │   │
│   │   ├── providers/                   # Context providers
│   │   │   ├── query-provider.tsx       # React Query provider
│   │   │   ├── theme-provider.tsx       # Theme provider
│   │   │   ├── auth-provider.tsx        # Authentication context
│   │   │   └── team-provider.tsx        # Team context
│   │   │
│   │   ├── layout/                      # Layout components
│   │   │   ├── header.tsx               # Main header
│   │   │   ├── sidebar.tsx              # Dashboard sidebar
│   │   │   ├── footer.tsx               # Footer
│   │   │   ├── navigation.tsx           # Navigation menu
│   │   │   └── breadcrumb.tsx           # Breadcrumb navigation
│   │   │
│   │   ├── auth/                        # Authentication components
│   │   │   ├── login-form.tsx
│   │   │   ├── register-form.tsx
│   │   │   ├── forgot-password-form.tsx
│   │   │   ├── auth-guard.tsx           # Route protection
│   │   │   └── user-menu.tsx            # User dropdown menu
│   │   │
│   │   ├── dashboard/                   # Dashboard components
│   │   │   ├── dashboard.tsx            # Main dashboard
│   │   │   ├── stats-cards.tsx          # Statistics cards
│   │   │   ├── recent-activity.tsx      # Recent activity feed
│   │   │   ├── quick-actions.tsx        # Quick action buttons
│   │   │   └── tabs/
│   │   │       ├── matches-tab.tsx      # Matches tab content
│   │   │       ├── team-tab.tsx         # Team tab content
│   │   │       └── public-tab.tsx       # Public matches tab
│   │   │
│   │   ├── video-player/                # Video player components
│   │   │   ├── VideoPlayerWithEvents.tsx # Main video player
│   │   │   ├── VideoControls.tsx        # Playback controls
│   │   │   ├── TimelineOverlay.tsx      # Timeline with events
│   │   │   ├── EventsSidebar.tsx        # Events list sidebar
│   │   │   ├── EventMarker.tsx          # Individual event marker
│   │   │   ├── EventFilter.tsx          # Event filtering
│   │   │   ├── VideoUpload.tsx          # Video upload component
│   │   │   └── VideoThumbnail.tsx       # Video thumbnails
│   │   │
│   │   ├── matches/                     # Match-related components
│   │   │   ├── MatchCard.tsx            # Match card component
│   │   │   ├── MatchList.tsx            # Matches list
│   │   │   ├── MatchDetail.tsx          # Match detail view
│   │   │   ├── MatchStats.tsx           # Match statistics
│   │   │   ├── MatchEvents.tsx          # Match events list
│   │   │   ├── MatchUpload.tsx          # Match upload form
│   │   │   └── MatchActions.tsx         # Match action buttons
│   │   │
│   │   ├── team/                        # Team management components
│   │   │   ├── TeamCard.tsx             # Team card
│   │   │   ├── TeamList.tsx             # Teams list
│   │   │   ├── TeamMembers.tsx          # Team members list
│   │   │   ├── TeamInvite.tsx           # Team invitation
│   │   │   ├── TeamSettings.tsx         # Team settings form
│   │   │   └── TeamStats.tsx            # Team statistics
│   │   │
│   │   ├── analytics/                   # Analytics components
│   │   │   ├── PerformanceChart.tsx     # Performance charts
│   │   │   ├── Heatmap.tsx              # Heatmap visualization
│   │   │   ├── StatsOverview.tsx        # Statistics overview
│   │   │   ├── ReportGenerator.tsx      # Report generation
│   │   │   └── ExportOptions.tsx        # Export functionality
│   │   │
│   │   ├── forms/                       # Form components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── TeamForm.tsx
│   │   │   ├── MatchForm.tsx
│   │   │   ├── ProfileForm.tsx
│   │   │   └── SettingsForm.tsx
│   │   │
│   │   └── landing/                     # Landing page components
│   │       ├── HeroSection.tsx          # Hero section
│   │       ├── FeatureCards.tsx         # Feature highlights
│   │       ├── Testimonials.tsx         # Customer testimonials
│   │       ├── PricingSection.tsx       # Pricing plans
│   │       └── ContactSection.tsx       # Contact form
│   │
│   ├── hooks/                           # Custom React hooks
│   │   ├── use-auth.ts                  # Authentication hook
│   │   ├── use-team.ts                  # Team management hook
│   │   ├── use-matches.ts               # Matches data hook
│   │   ├── use-video-player.ts          # Video player hook
│   │   ├── use-api.ts                   # API calls hook
│   │   ├── use-upload.ts                # File upload hook
│   │   ├── use-analytics.ts             # Analytics hook
│   │   ├── use-local-storage.ts         # Local storage hook
│   │   └── use-debounce.ts              # Debounce utility hook
│   │
│   ├── lib/                             # Utility libraries
│   │   ├── utils.ts                     # General utilities
│   │   ├── api.ts                       # API client
│   │   ├── auth.ts                      # Authentication utilities
│   │   ├── validation.ts                # Form validation
│   │   ├── constants.ts                 # App constants
│   │   ├── types.ts                     # TypeScript types
│   │   ├── helpers.ts                   # Helper functions
│   │   └── config.ts                    # App configuration
│   │
│   ├── contexts/                        # React contexts
│   │   ├── auth-context.tsx             # Authentication context
│   │   ├── team-context.tsx             # Team context
│   │   ├── theme-context.tsx            # Theme context
│   │   └── app-context.tsx              # App-wide context
│   │
│   ├── types/                           # TypeScript type definitions
│   │   ├── api.ts                       # API response types
│   │   ├── auth.ts                      # Authentication types
│   │   ├── team.ts                      # Team types
│   │   ├── match.ts                     # Match types
│   │   ├── video.ts                     # Video player types
│   │   ├── analytics.ts                 # Analytics types
│   │   └── common.ts                    # Common types
│   │
│   └── styles/                          # Additional styles
│       ├── components.css               # Component-specific styles
│       ├── animations.css               # CSS animations
│       └── custom.css                   # Custom styles
│
├── package.json                         # Dependencies and scripts
├── next.config.js                       # Next.js configuration
├── tailwind.config.js                   # Tailwind CSS configuration
├── tsconfig.json                        # TypeScript configuration
├── postcss.config.js                    # PostCSS configuration
├── .eslintrc.js                         # ESLint configuration
├── .prettierrc                          # Prettier configuration
└── README.md                            # Frontend documentation
```

---

## 🎯 **Key Features to Implement**

### **1. Authentication System**
- JWT-based authentication
- Login/Register forms
- Password reset functionality
- Route protection
- User session management

### **2. Advanced Video Player**
- Custom video player with controls
- Event tagging and timeline overlay
- Click-to-seek functionality
- Event filtering by team/type
- Video upload with progress

### **3. Dashboard**
- Statistics cards
- Recent activity feed
- Quick action buttons
- Tabbed interface (Matches, Team, Public)

### **4. Match Management**
- Match list with filtering
- Match detail view
- Event timeline
- Upload new matches
- Match statistics

### **5. Team Management**
- Team creation and settings
- Member invitations
- Team statistics
- Role-based permissions

### **6. Analytics**
- Performance charts
- Heatmap visualizations
- Report generation
- Export functionality

---

## 🚀 **Implementation Phases**

### **Phase 1: Foundation (Week 1)**
- [ ] Set up Next.js 15 with TypeScript
- [ ] Configure Tailwind CSS and Radix UI
- [ ] Create basic layout components
- [ ] Set up authentication context
- [ ] Create landing page

### **Phase 2: Core Features (Week 2)**
- [ ] Implement authentication pages
- [ ] Create dashboard structure
- [ ] Build video player component
- [ ] Set up API integration
- [ ] Add basic match management

### **Phase 3: Advanced Features (Week 3)**
- [ ] Complete video player with events
- [ ] Add team management
- [ ] Implement analytics dashboard
- [ ] Add file upload functionality
- [ ] Create settings pages

### **Phase 4: Polish (Week 4)**
- [ ] Add animations and transitions
- [ ] Implement error handling
- [ ] Add loading states
- [ ] Optimize performance
- [ ] Add tests

---

## 🔧 **Dependencies to Install**

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@radix-ui/react-*": "^1.0.0",
    "tailwindcss": "^3.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.300.0",
    "sonner": "^1.0.0",
    "next-themes": "^0.2.0",
    "framer-motion": "^10.0.0",
    "recharts": "^2.0.0",
    "react-leaflet": "^4.0.0",
    "leaflet": "^1.9.0",
    "date-fns": "^2.30.0",
    "zod": "^3.22.0",
    "react-hook-form": "^7.0.0",
    "@hookform/resolvers": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0"
  }
}
```

---

## 📋 **Next Steps**

1. **Initialize Next.js project** with TypeScript
2. **Install dependencies** and configure tools
3. **Set up folder structure** as outlined above
4. **Create basic components** starting with UI components
5. **Implement authentication** flow
6. **Build video player** component
7. **Create dashboard** with tabs
8. **Connect to backend** APIs
9. **Add advanced features** progressively

This structure gives us a solid foundation that combines the best of both existing apps while maintaining clean architecture and scalability. 