# Test Video Player Guide

## Quick Setup (if database not set up yet)

1. **Set up PostgreSQL database:**
   ```bash
   # Create database
   createdb clannai_webapp
   
   # Run schema
   psql clannai_webapp < db/schema.sql
   
   # Load demo data
   psql clannai_webapp < db/seeds/demo_data.sql
   ```

2. **Start servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && npm run dev
   
   # Terminal 2 - Frontend  
   cd frontend && npm run dev
   ```

## Test the Video Player

1. **Login with demo user:**
   - Go to: http://localhost:3000
   - Email: `demo@clann.ai`
   - Password: `demo123`

2. **Access the test game:**
   - Go to Dashboard
   - Click on "Demo Video - Test Video Player" 
   - Or directly: http://localhost:3000/games/99999999-9999-9999-9999-999999999999

## Expected Video Player Features

✅ **Video playback** with Big Buck Bunny test video  
✅ **Event timeline** with colored dots on progress bar  
✅ **Events sidebar** with 13 test events (goals, shots, fouls, etc.)  
✅ **Click events** to jump to specific timestamps  
✅ **Playback controls** (play/pause, seek, volume)  
✅ **Event navigation** (previous/next event buttons)  
✅ **Auto-scroll** events sidebar to current event  
✅ **Fullscreen** support  

## Event Types with Colors

- 🟢 **Goals** - Green dots
- 🔵 **Shots** - Blue dots  
- 🔴 **Fouls** - Red dots
- 🟡 **Yellow Cards** - Yellow dots
- 🟣 **Substitutions** - Purple dots
- 🔄 **Corners** - Cyan dots

## Troubleshooting

- **Video not loading**: Check browser console for CORS errors
- **No events showing**: Verify game has `ai_analysis` data
- **Can't access game**: Make sure user is member of the team
- **Backend errors**: Check `localhost:3002/health` for status 