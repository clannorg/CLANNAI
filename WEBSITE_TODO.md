## ClannAI Website To‑Do (Unified)

Source of truth for landing and site UX polish. Links to prior plans:
- `web-apps/1-clann-webapp/FEATURE_FINALIZATION_PLAN.md`
- `web-apps/1-clann-webapp/VIDEO_UI_REWORK.md`
- `web-apps/1-clann-webapp/MOBILE_VIDEO_LAYOUT_PLAN.md`
- `0-to-1-project-plan/0-to-1-project-plan.md`

### Goals
- Clear messaging for clubs: upload → AI insights → watch/share.
- Fast, mobile-first landing that converts (90+ Lighthouse on mobile).
- Seamless handoff from landing CTA to upload/auth and into the analyzed game.

---

### Landing Page (MVP rework)
1) Messaging/copy
   - Headline: “Instant match insights for your club.”
   - Sub: “Upload your game video to get events, tactical analysis and downloadable clips.”
   - 3 bullets: Events timeline • Tactical insights • Download highlights.
   - Primary CTA: Analyze my match → opens auth/upload.

2) Hero
   - Desktop: light poster with play button (no auto-play on mobile).
   - Mobile: static poster (skip heavy video). Preload poster.
   - Replace current full-screen background video on mobile.

3) Social proof (optional, placeholder)
   - Row for partner/club logos or single testimonial.

4) How it works (3 steps)
   - Upload → AI analyzes → Watch & share.

5) Product strip
   - Real screenshots: Events, Insights, Downloads cards.
   - Use current app UI to keep truthfulness.

6) CTAs
   - Sticky top CTA on mobile.
   - Repeat CTA near footer.

7) Performance
   - Remove blocking assets, compress hero, lazy-load heavy sections.
   - Target: Lighthouse ≥ 90 mobile.

8) Mobile polish
   - Safe-area insets, 44px tap targets, font scaling.
   - Ensure navbar + CTA don’t overlap iOS bars.

9) Analytics
   - Track: hero CTA click, start upload, sign up.

10) Footer
   - Privacy/Terms links; contact.

Acceptance
- Copy passes the “who/what/value/CTA” test.
- TTI < 2.5s on mid-range mobile; LCP < 2.5s.
- All CTAs route to auth/upload and on success go straight to game view.

---

### Pipeline–Website Integration
- Ensure upload flow returns user to analyzed game with Events/Insights visible.
- Auto-open AI Coach/Insights when invoked from landing CTA (session hint).
- Align landing screenshots with current UI (no mocked states).

---

### Tasks (Actionable)
- [ ] Copy draft for headline, sub, bullets, CTAs (owner: TB)
- [ ] Replace hero section in `web-apps/1-clann-webapp/frontend/src/app/page.tsx` (owner: dev)
- [ ] Add lightweight product strip component with real screenshots (owner: dev)
- [ ] Add sticky mobile CTA and safe-area padding (owner: dev)
- [ ] Swap mobile video for poster, preload poster (owner: dev)
- [ ] Add analytics events to CTA/auth/upload (owner: dev)
- [ ] Route: CTA → auth/upload → analyzed game (owner: dev)
- [ ] Lighthouse pass ≥ 90 mobile (owner: dev)
- [ ] Update assets in `public/` (owner: design)

---

### References (Current Code)
- Landing: `web-apps/1-clann-webapp/frontend/src/app/page.tsx`
- Assets: `web-apps/1-clann-webapp/frontend/public/`
- Auth/upload: `web-apps/1-clann-webapp/frontend/src/app/dashboard/page.tsx` (entry points)
- Game view (target after upload): `web-apps/1-clann-webapp/frontend/src/app/games/[id]/page.tsx`

