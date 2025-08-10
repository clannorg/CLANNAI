# 🚀 ClannAI - Football Analysis Platform

**Professional video analysis platform for football teams** - Live at [clannai.com](https://clannai.com)

## ✨ **Features**

- 🎯 **Video Analysis** - Upload VEO URLs, get AI-powered tactical insights
- 👥 **Team Management** - Join teams with invite codes, manage multiple teams
- 🤖 **AI Coach** - Chat with AI about match analysis and tactical advice
- 📊 **Event Timeline** - Interactive match events with timestamps
- 🏢 **Company Dashboard** - Admin view for all teams and games
- 🎮 **Demo Content** - Rich demo games for immediate onboarding

## 🚀 **Quick Start**

### **Local Development:**
```bash
# 1. Start Backend (connects to AWS RDS)
cd backend && node server.js

# 2. Start Frontend  
cd frontend && npm run dev

# 3. Visit: http://localhost:3000
```

<!-- Demo access and public join links removed → focus on real uploads and team membership flows -->

## 🏗️ **Tech Stack**

- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **Backend**: Express.js + PostgreSQL (AWS RDS)
- **Infrastructure**: AWS (RDS, S3) + Devopness deployment
- **Authentication**: JWT tokens with bcrypt

## 🌍 **Deployment**

- **Production**: https://clannai.com (auto-deployed via Devopness)
- **API**: https://api.clannai.com
- **Database**: AWS RDS PostgreSQL (production)

## 📊 **Current Status**

✅ **Live Production Platform**  
✅ **Demo Content Access** - New users see rich content immediately  
✅ **Direct Join Links** - One-click team joining  
✅ **AWS Database** - Production-ready PostgreSQL with SSL  
🔄 **Enhanced Event Timeline** - In progress  
⏳ **User Video Upload** - Next feature  

---

**🎯 Production-ready SaaS platform for football analysis**

---

## 📚 Product Flows (Concise)

### Company Uploads (current)
- Video URL → `POST /api/games/:id/upload-video` → saves `game.video_url`
- Events URL → `POST /api/games/:id/upload-events` → saves `game.events`
- Analysis (tactical) URL → `POST /api/games/:id/upload-tactical` → fetch+transform → saves `game.tactical_analysis`; also stores canonical link at `metadata.tactical_files.latest.url`
- Metadata URL (single file) → `POST /api/games/:id/upload-metadata` → applies video+events+tactical+team_identity in one step and sets canonical links

### Game Page consumption
- Video player reads `game.video_url`
- Events tab reads `game.events`
- Insights tab reads `game.tactical_analysis`
- Team names (planned): read `metadata.team_identity` and map any color tokens to `home/away` names

### Mobile portrait behavior
- Video + tab bar stay pinned; overlays auto-hide on tap/after 4s
- Mobile controls: single “Next” button (Prev hidden on phones), safe‑area bottom spacing so controls don’t slip off‑screen

### Recent changes (high‑signal)
- Company → Analysis “Save” updates Insights and shows the exact tactical S3 URL (`metadata.tactical_files.latest.url`)
- Metadata single‑upload added (`/upload-metadata`) to set video, events, tactical, team identity in one step
- Insights renderer made robust to v2 JSON (object or array shapes)
- Portrait mode finalized: pinned tabs + 4s auto‑hide overlays; safe‑area fix for iOS
- Landing: upload box restyled black; demo codes removed

## 🧾 Metadata.json (single upload)
- Keys: `video_url`, `events_url`, `tactical_url`, `team_identity { home, away, mapping }`
- Upload via Company → Metadata → Save (calls `/upload-metadata`)
- Sets canonical URLs for display and marks analyzed when video + (events or tactical) present

## 🔍 Search & Request to Join (planned)
- UX: search club → request to join (or add new club) → approval → access to Company dashboard
- Backend: `GET /api/clubs?query` (search), `POST /api/clubs/requests` (create), `POST /api/clubs/requests/:id/approve` (admin), optional `POST /api/clubs` (add)
- Data: `clubs`, `club_memberships`, `club_join_requests`
- Frontend: `app/join-club/` page; redirect users without approved membership to join flow
- Seed: import clubs from `crm/` CSVs (aliases for fuzzy search)

### Join flow acceptance (MVP)
- Logged‑in users without membership are redirected to `/join-club`
- Search returns seeded clubs and alias matches
- Request creates a pending membership; manual approve path exists; optional email‑domain auto‑approve later
- Once approved → user sees Company dashboard for that club

## 🗺️ File Map (where things live)
- Frontend
  - `frontend/src/app/company/page.tsx` → upload inputs (Video/Events/Analysis/Metadata)
  - `frontend/src/lib/api-client.ts` → API calls (upload video/events/tactical/metadata)
  - `frontend/src/app/games/[id]/page.tsx` → game layout
  - `frontend/src/components/games/FifaStyleInsights.tsx` → Insights renderer
  - `frontend/src/components/games/UnifiedSidebar.tsx` + `VideoPlayer.tsx` → portrait behaviors
- Backend
  - `backend/routes/games.js` → upload routes (video/events/tactical/metadata)
  - `backend/routes/company.js` → list games with canonical URLs
  - `db/` → migrations/seeds (clubs/memberships planned)

## ⚙️ Rough edges (to tighten for MVP)
- Add success/error toasts on Company uploads; show last-applied Metadata URL/time
- Validate metadata schema (client hint + backend checks)
- Surface team identity in header/events (map color tokens → club names)
- Events: “Recent” jump to latest 5
- Auto-toggle analyzed when metadata includes video + (events or tactical)
- Better error text/timeouts when fetching S3 JSON

## ✅ Acceptance (Game page)
- Header shows real club names (from `metadata.team_identity`)
- Events list uses those names and supports a “Recent” jump
- Insights renders without shape errors (recommendations, strengths/weaknesses)
- Portrait: video + tabs pinned; overlays auto‑hide; single Next button visible on phones

---

## 📝 Next steps (one‑liners)
- **Company uploads: toasts + timestamp** — show success/failure and last applied metadata URL/time.
- **Auto‑analyzed toggle** — set analyzed=true when video + (events or tactical) present.
- **Metadata schema checks** — friendly server errors for missing/invalid keys.
- **Team identity everywhere** — use `team_identity` for header/events; map color tokens → names.
- **Events “Recent”** — jump to latest 5; keep filters sticky under tabs.
- **Canonical links** — always display video/events/tactical URLs from metadata on Company rows.
- **Reapply metadata** — one click to re-run `/upload-metadata` with the same URL.
- **Join by search** — search clubs, request to join, approve flow; seed from CRM.
- **Landing tighten** — clear hero copy + CTA; mobile poster image; three “what you get” cards.
- **Downloads tab** — show generated clips/bundles; one‑click download when available.

### Sprint acceptance
- Paste metadata → toast appears → row shows canonical URLs and analyzed=true.
- Game page shows real club names; “Recent” works; Insights OK; mobile shows single Next.

## ✅ Next Steps (short list)
- [ ] Company: toasts + show last Metadata URL/time
- [ ] Backend: schema checks for `/upload-metadata`
- [ ] UI: use `metadata.team_identity` in header/events
- [ ] Events: add “Recent” jump
- [ ] Mark analyzed on successful metadata apply