# 👤 Intended User Flow

## 🎯 User Journey Overview

### New User Flow
1. Landing Page → Learn about the platform
2. Modal Sign Up → Create account (popup on same page)
3. Dashboard → See empty state, create first team
4. Modal Upload → Upload first game (popup on dashboard)
5. View Analysis → See video with events

### Returning User Flow
1. Landing Page → Login modal (popup on same page)
2. Dashboard → Toggle between Teams/Games
3. View Games → Browse uploaded games
4. Watch Analysis → View video with events

---

## 📋 Detailed User Flows

### 1. Landing Page Experience
- Hero video, animated text, demo metrics
- Paste video URL, click "Analyze"
- Triggers login modal if not authenticated
- Sign up/login modal
- Redirect to dashboard after auth

### 2. Authentication Flow
- Modal-based login/register
- Toggle between Login/Register
- Form validation, password visibility, terms checkbox
- API call with loading state
- Store token, redirect to dashboard
- Error message in modal

### 3. Dashboard Experience
- Tabs: Teams/Games
- Create team (modal)
- Upload game (modal)
- List of games with status, search/filter
- Toggle between teams/games

### 4. Video Upload Flow
- Upload modal: drag & drop, file validation, progress
- Metadata: title, description, team
- Status updates for processing

### 5. Video Analysis View
- Video player (HLS streaming)
- Timeline with event markers
- Sidebar for events (add/edit/filter)
- Event modals for creation/editing

### 6. Event Management Flow
- Create/edit/delete events (modal)
- Event type, timestamp, team, player, description, coordinates, tags
- Filter/search events

---

## 🧑‍💻 User Personas
- Team Manager: Analyze team performance
- Coach: Improve tactics
- Player: Review personal performance

---

## 🖥️ User Interface Requirements
- Consistent modals, validation, loading states
- Responsive design (desktop, tablet, mobile)
- Error handling for uploads, auth, playback

---

## 🔄 Error Handling
- Upload errors: file size/type, timeout, processing failure
- Auth errors: invalid credentials, account not found, network issues, token expired
- Video errors: not found, streaming issues, browser compatibility

---

## 📱 Responsive Design
- Desktop: full layout, sidebar, large video
- Tablet: adaptive grid, collapsible sidebar
- Mobile: stacked layout, bottom sheet for events

---

## 📝 Modal Form Strategy
- Consistent modal design, validation, loading, error states
- Auth, team, upload, event, settings modals
- Smooth open/close, success/error feedback 