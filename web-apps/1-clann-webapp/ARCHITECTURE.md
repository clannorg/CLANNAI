# 🏗️ ClannAI Architecture

## Overview
This document describes the system design, stack choices, deployment, security, and scaling strategy for the ClannAI platform.

---

## System Design
- **Frontend:** Next.js 15+, TypeScript, Tailwind CSS, React Query, modular components
- **Backend:** Node.js, Express, Prisma ORM, PostgreSQL, JWT auth, Stripe, AWS S3
- **API:** RESTful, documented in API_SPECIFICATION.md
- **Database:** PostgreSQL, see DATABASE_SCHEMA.md
- **Storage:** AWS S3 for video/files
- **Auth:** JWT, NextAuth.js (or custom)
- **Payments:** Stripe

---

## Deployment
- **Frontend:** Vercel or similar (static/SSR hosting)
- **Backend:** Cloud VM (AWS EC2, GCP, etc.), Dockerized, managed with PM2 or similar
- **Database:** Managed Postgres (AWS RDS, Supabase, etc.)
- **Storage:** AWS S3 buckets
- **CI/CD:** GitHub Actions or similar for automated deploys
- **Env Vars:** Managed via host dashboards, never committed

---

## Security
- Use HTTPS everywhere
- Store secrets in env vars, not code
- Hash passwords with bcrypt
- Validate all input (backend and frontend)
- Use CORS to restrict API access
- Implement rate limiting and security headers
- Monitor for suspicious activity

---

## Scaling
- Stateless backend (easy to scale horizontally)
- Use managed DB and S3 for storage
- CDN for static assets
- Optimize queries and add DB indexes
- Monitor performance and errors

---

## Notes
- Update this doc as the system evolves
- See all referenced docs for details on API, DB, user flows, and implementation 