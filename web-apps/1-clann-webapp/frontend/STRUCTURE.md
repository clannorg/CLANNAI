# 📁 Frontend Structure

## 🎯 **Overview**

Next.js 15 frontend with modal-based forms and component-driven architecture. All forms appear as modals on the current page, keeping the user experience seamless.

---

## 📂 **Folder Structure**

```
frontend/
├── public/
│   ├── clann-sliothar.png
│   ├── clann.ai-green.png
│   ├── clann.ai-white.png
│   ├── favicon.ico
│   └── videos/
│       └── hero-video.mp4
│
├── src/
│   ├── app/
│   │   ├── layout.tsx                  # Root layout with providers
│   │   ├── page.tsx                    # Landing page (hero + modals)
│   │   ├── globals.css                 # Global styles
│   │   │
│   │   ├── dashboard/
│   │   │   └── page.tsx                # Dashboard with Teams/Games toggle
│   │   │
│   │   └── games/
│   │       └── [id]/
│   │           └── page.tsx            # Game detail with video player
│   │
│   ├── components/
│   │   ├── ui/                         # Base UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── modal.tsx               # Reusable modal wrapper
│   │   │   ├── card.tsx
│   │   │   └── ...
│   │   │
│   │   ├── auth/                       # Authentication components
│   │   │   ├── AuthModal.tsx           # Login/Register modal
│   │   │   ├── LoginForm.tsx           # Login form component
│   │   │   ├── RegisterForm.tsx        # Register form component
│   │   │   └── AuthProvider.tsx        # Auth context provider
│   │   │
│   │   ├── dashboard/                  # Dashboard components
│   │   │   ├── DashboardHeader.tsx     # User info, logout, team selector
│   │   │   ├── TeamsTab.tsx            # Teams list and management
│   │   │   ├── GamesTab.tsx            # Games list and upload
│   │   │   ├── TeamCard.tsx            # Individual team card
│   │   │   ├── GameCard.tsx            # Individual game card
│   │   │   └── EmptyState.tsx          # Empty state for tabs
│   │   │
│   │   ├── modals/                     # Modal form components
│   │   │   ├── TeamModal.tsx           # Create/Edit team modal
│   │   │   ├── UploadModal.tsx         # Video upload modal
│   │   │   ├── EventModal.tsx          # Create/Edit event modal
│   │   │   └── SettingsModal.tsx       # User settings modal
│   │   │
│   │   ├── video-player/               # Video player components
│   │   │   ├── VideoPlayer.tsx         # Main video player
│   │   │   ├── Timeline.tsx            # Timeline with event markers
│   │   │   ├── EventSidebar.tsx        # Event list and filters
│   │   │   ├── EventMarker.tsx         # Individual event marker
│   │   │   └── Controls.tsx            # Playback controls
│   │   │
│   │   ├── landing/                    # Landing page components
│   │   │   ├── HeroSection.tsx         # Hero with video background
│   │   │   ├── DemoMetrics.tsx         # Spider chart comparison
│   │   │   ├── AnalysisShowcase.tsx    # Feature cards
│   │   │   ├── PricingTiers.tsx        # Pricing display
│   │   │   ├── UrlInput.tsx            # URL input with analyze button
│   │   │   └── TopNav.tsx              # Navigation bar
│   │   │
│   │   └── shared/                     # Shared components
│   │       ├── LoadingSpinner.tsx      # Loading indicators
│   │       ├── ErrorBoundary.tsx       # Error handling
│   │       ├── Notification.tsx        # Success/error messages
│   │       └── ...
│   │
│   ├── hooks/                          # Custom React hooks
│   │   ├── useAuth.ts                  # Authentication hook
│   │   ├── useTeams.ts                 # Teams management
│   │   ├── useGames.ts                 # Games management
│   │   ├── useEvents.ts                # Events management
│   │   ├── useUpload.ts                # File upload hook
│   │   └── useVideoPlayer.ts           # Video player state
│   │
│   ├── lib/                            # Utilities and configuration
│   │   ├── api.ts                      # API client
│   │   ├── auth.ts                     # Authentication utilities
│   │   ├── utils.ts                    # Helper functions
│   │   ├── constants.ts                # App constants
│   │   └── types.ts                    # TypeScript types
│   │
│   └── types/                          # TypeScript type definitions
│       ├── auth.ts                     # Authentication types
│       ├── teams.ts                    # Team types
│       ├── games.ts                    # Game types
│       ├── events.ts                   # Event types
│       └── api.ts                      # API response types
│
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

---

## 🎨 **Component Architecture**

### **Modal System**
All forms use a consistent modal approach:

```typescript
// Base Modal Component
<Modal isOpen={showModal} onClose={handleClose}>
  <ModalHeader title="Create Team" onClose={handleClose} />
  <ModalBody>
    <TeamForm onSubmit={handleSubmit} />
  </ModalBody>
</Modal>
```

### **Modal Types**
1. **AuthModal** - Login/Register toggle
2. **TeamModal** - Create/Edit team
3. **UploadModal** - Video upload with progress
4. **EventModal** - Create/Edit events
5. **SettingsModal** - User preferences

### **Page Structure**
- **Landing Page** - Hero + modals (no separate auth pages)
- **Dashboard** - Teams/Games tabs + modals
- **Game Detail** - Video player + event modals

---

## 🔄 **State Management**

### **Context Providers**
- **AuthProvider** - User authentication state
- **TeamProvider** - Teams and team selection
- **GameProvider** - Games and current game
- **EventProvider** - Events for current game

### **Custom Hooks**
- **useAuth** - Login, logout, user state
- **useTeams** - CRUD operations for teams
- **useGames** - CRUD operations for games
- **useEvents** - CRUD operations for events
- **useUpload** - File upload with progress

---

## 🎯 **Key Features**

### **Landing Page**
- Hero video background with animated text
- Demo metrics comparison (spider chart)
- Analysis showcase (3 feature cards)
- Pricing tiers display
- URL input with "Analyze" button
- Auth modal triggered by "Analyze" or nav

### **Dashboard**
- Teams/Games toggle tabs
- Create team modal
- Upload video modal
- Games list with status indicators
- Search and filter options

### **Video Player**
- HLS.js streaming player
- Timeline with event markers
- Event creation sidebar
- Event editing modal
- Filter and search events
- Fullscreen support

---

## 📱 **Responsive Design**

### **Desktop (1200px+)**
- Full layout with sidebar
- Large video player
- Modal forms centered

### **Tablet (768px - 1199px)**
- Adaptive grid layout
- Collapsible sidebar
- Modal forms full-width

### **Mobile (320px - 767px)**
- Stacked single column
- Hidden sidebar (bottom sheet)
- Modal forms full-screen

---

## 🎨 **Design System**

### **Colors**
- Primary: `#016F32` (ClannAI green)
- Secondary: `#4EC2CA` (Cyan)
- Accent: `#D1FB7A` (Light green)
- Background: `#111827` (Dark gray)
- Text: `#FFFFFF` (White)

### **Typography**
- Headings: Inter (Bold)
- Body: Inter (Regular)
- Monospace: JetBrains Mono (Code)

### **Components**
- Consistent button styles
- Form inputs with validation
- Modal backdrop and animations
- Loading states and spinners
- Error messages and notifications

This structure ensures a clean, maintainable codebase with reusable components and a consistent user experience! 