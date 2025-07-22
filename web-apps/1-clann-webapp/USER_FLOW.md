# 👤 Intended User Flow

## 🎯 **User Journey Overview**

### **New User Flow:**
1. **Landing Page** → Learn about the platform
2. **Modal Sign Up** → Create account (popup on same page)
3. **Dashboard** → See empty state, create first team
4. **Modal Upload** → Upload first game (popup on dashboard)
5. **View Analysis** → See video with events

### **Returning User Flow:**
1. **Landing Page** → Login modal (popup on same page)
2. **Dashboard** → Toggle between Teams/Games
3. **View Games** → Browse uploaded games
4. **Watch Analysis** → View video with events

---

## 📋 **Detailed User Flows**

### **1. Landing Page Experience**
**Goal:** Convert visitors to users

**Steps:**
1. **Land on homepage** → See hero video, animated text, demo metrics
2. **Paste video URL** → Enter Veo/Trace/Spiideo URL in input box
3. **Click "Analyze"** → Triggers login modal if not authenticated
4. **Sign up/Login** → Modal appears on same page
5. **Redirect to dashboard** → After successful authentication

**Key Features:**
- Hero video background with animated text
- Demo metrics comparison (spider chart)
- Analysis showcase (position tracking, heat mapping, sprint analysis)
- Pricing tiers display
- URL input with "Analyze" button

### **2. Authentication Flow**
**Goal:** Seamless sign up/login experience

**Steps:**
1. **Trigger auth modal** → From "Analyze" button or nav links
2. **Choose mode** → Toggle between Login/Register
3. **Fill form** → Email, password, terms (for register)
4. **Submit** → API call with loading state
5. **Success** → Store token, redirect to dashboard
6. **Error** → Show error message in modal

**Modal Features:**
- Toggle between Login/Register
- Form validation
- Password visibility toggle
- Terms checkbox (register only)
- Error message display
- Loading states

### **3. Dashboard Experience**
**Goal:** Manage teams and games

**Steps:**
1. **Land on dashboard** → See teams and games tabs
2. **Toggle view** → Switch between Teams/Games
3. **Create team** → Modal form for new team
4. **Upload game** → Modal form for video upload
5. **View games** → List of uploaded games with status

**Dashboard Features:**
- Teams/Games toggle tabs
- Create team modal
- Upload video modal
- Games list with status indicators
- Search and filter options

### **4. Video Upload Flow**
**Goal:** Upload and process game videos

**Steps:**
1. **Click "Upload"** → Opens upload modal
2. **Select file** → Drag & drop or file picker
3. **Add metadata** → Title, description, team
4. **Submit** → Upload to S3 with progress
5. **Processing** → Show status updates
6. **Complete** → Game appears in list

**Upload Modal Features:**
- Drag & drop file upload
- File validation (type, size)
- Progress indicator
- Metadata form (title, description, team)
- Error handling and retry

### **5. Video Analysis View**
**Goal:** Watch videos with event tracking

**Steps:**
1. **Click game** → Navigate to video player
2. **Load video** → HLS streaming with events
3. **View timeline** → See event markers
4. **Add events** → Click timeline or use sidebar
5. **Edit events** → Modal form for event editing
6. **Filter events** → By type, team, player

**Video Player Features:**
- HLS.js streaming player
- Timeline with event markers
- Event creation sidebar
- Event editing modal
- Filter and search events
- Fullscreen support

### **6. Event Management Flow**
**Goal:** Create and edit game events

**Steps:**
1. **Click timeline** → Opens event creation modal
2. **Fill event form** → Type, timestamp, team, player, description
3. **Add coordinates** → Click on pitch or enter manually
4. **Add metadata** → Tags, notes, custom fields
5. **Save** → Event appears on timeline
6. **Edit/Delete** → Right-click or use sidebar

**Event Modal Features:**
- Event type selection
- Timestamp input
- Team and player selection
- Description field
- Coordinate picker
- Metadata fields (tags, notes)
- Preview of event on timeline

---

## 🎯 **User Personas**

### **Team Manager**
- **Goal:** Analyze team performance
- **Pain Points:** Manual video analysis, no metrics
- **Solution:** Automated tracking and insights
- **Key Features:** Team management, game uploads, performance metrics

### **Coach**
- **Goal:** Improve team tactics
- **Pain Points:** Limited tactical insights
- **Solution:** Position tracking and formation analysis
- **Key Features:** Video player with events, tactical overlays

### **Player**
- **Goal:** Review personal performance
- **Pain Points:** No individual metrics
- **Solution:** Player-specific tracking
- **Key Features:** Individual player stats, highlight reels

---

## 📊 **User Interface Requirements**

### **Landing Page**
- **Hero Section:** Video background with animated text
- **Demo Metrics:** Spider chart comparison
- **Analysis Showcase:** Three feature cards
- **Pricing Tiers:** Three-column layout
- **URL Input:** Prominent input with analyze button
- **Navigation:** Clean top nav with auth buttons

### **Dashboard**
- **Header:** User info, logout, team selector
- **Tabs:** Teams/Games toggle
- **Content Area:** Dynamic based on selected tab
- **Action Buttons:** Create team, upload video
- **Search/Filter:** For games and teams

### **Video Player**
- **Player:** Full-width video with controls
- **Timeline:** Below video with event markers
- **Sidebar:** Event list and filters
- **Toolbar:** Playback controls and fullscreen
- **Event Modal:** Overlay for event creation/editing

### **Forms (All Modals)**
- **Consistent Design:** Same styling across all modals
- **Validation:** Real-time form validation
- **Loading States:** Spinners and progress indicators
- **Error Handling:** Clear error messages
- **Responsive:** Work on mobile and desktop

---

## 🔄 **Error Handling**

### **Upload Errors**
- **File too large:** Show size limit message
- **Invalid file type:** Show supported formats
- **Upload timeout:** Retry with progress indicator
- **Processing failure:** Show error status

### **Authentication Errors**
- **Invalid credentials:** Clear error message in modal
- **Account not found:** Clear registration prompt
- **Network issues:** Retry with exponential backoff
- **Token expired:** Automatic refresh or redirect

### **Video Playback Errors**
- **Video not found:** Show 404 with upload option
- **Streaming issues:** Retry with different quality
- **Browser compatibility:** Show fallback player
- **Network problems:** Offline indicator

---

## 📱 **Responsive Design**

### **Desktop (1200px+)**
- **Full layout:** All features visible
- **Sidebar:** Event management panel
- **Large video player:** Full-width with controls
- **Modal forms:** Centered with backdrop

### **Tablet (768px - 1199px)**
- **Adaptive layout:** Responsive grid
- **Collapsible sidebar:** Toggle for events
- **Medium video player:** Responsive sizing
- **Modal forms:** Full-width on tablet

### **Mobile (320px - 767px)**
- **Stacked layout:** Single column
- **Hidden sidebar:** Events in bottom sheet
- **Small video player:** Optimized for mobile
- **Modal forms:** Full-screen on mobile

---

## 🎨 **Modal Form Strategy**

### **Consistent Modal Design**
- **Backdrop:** Semi-transparent overlay
- **Container:** Centered with rounded corners
- **Header:** Title and close button
- **Form:** Consistent input styling
- **Actions:** Primary and secondary buttons

### **Modal Types**
1. **Auth Modal:** Login/Register toggle
2. **Team Modal:** Create/Edit team
3. **Upload Modal:** Video upload with progress
4. **Event Modal:** Create/Edit events
5. **Settings Modal:** User preferences

### **Modal Behavior**
- **Open:** Smooth fade-in animation
- **Close:** Click backdrop, escape key, or X button
- **Form submission:** Loading state with spinner
- **Success:** Close modal and update parent
- **Error:** Show error message in modal

This user flow ensures we build exactly what users need with a consistent, modal-based experience! 