# PostHog Analytics Setup

## Overview
PostHog is set up to track user behavior across the ClannAI platform. This includes page views, user interactions, sign-ups, and custom events.

## Current Configuration

### Development
- **Local URL**: `http://localhost:3000`
- **PostHog Host**: `https://eu.i.posthog.com` (EU region)
- **Project Key**: `phc_MjxvlfdE9tTYe0ivfFbNhrbEaHcSX2HhaYNe30C8HpK`

### Production 
- **Production URL**: `https://clannai.com`
- **Same PostHog configuration**

## Files Modified
- `instrumentation-client.ts` - PostHog initialization
- `next.config.ts` - Reverse proxy setup to avoid ad blockers
- `.env.local` - Environment variables (local only)

## Deployment Steps

### 1. Add Environment Variables to Production
Add these to your hosting provider (Vercel/Netlify/etc.):

```bash
NEXT_PUBLIC_POSTHOG_KEY=phc_MjxvlfdE9tTYe0ivfFbNhrbEaHcSX2HhaYNe30C8HpK
NEXT_PUBLIC_POSTHOG_HOST=https://eu.i.posthog.com
```

### 2. Add Production Domain to PostHog
1. Go to https://eu.posthog.com/settings/project
2. Click "Authorized domains"
3. Add: `https://clannai.com`
4. Add: `http://localhost:3000` (for development)

### 3. Deploy Changes
```bash
git add .
git commit -m "Add PostHog analytics"
git push origin main
```

## What's Being Tracked

### Automatic Events
- ✅ Page views
- ✅ User sessions  
- ✅ Time on page
- ✅ Geographic data
- ✅ Device/browser info

### Custom Events (To Add)
- [ ] User registration
- [ ] Game uploads
- [ ] AI coach interactions
- [ ] Video plays
- [ ] Download actions

## Testing
1. Visit your site (local or production)
2. Check PostHog dashboard: https://eu.posthog.com/project/[PROJECT_ID]/web-analytics
3. Should see events within 30 seconds

## Troubleshooting
- **No events?** Check authorized domains
- **Events delayed?** Normal up to 60 seconds
- **Ad blockers?** Reverse proxy should handle this

## Dashboard Access
- **URL**: https://eu.posthog.com/
- **Project**: Default project
- **Key**: `phc_MjxvlfdE9tTYe0ivfFbNhrbEaHcSX2HhaYNe30C8HpK`