# 🧠 Existing Apps Analysis

## Overview
This document summarizes lessons learned from previous ClannAI apps and guides migration to the new stack.

---

## What Worked Well
- Express.js backend with JWT auth and Postgres
- S3 file uploads for video storage
- Modular React components for UI
- Stripe integration for payments
- Clear API endpoints for teams, games, events
- Video player with event tagging

---

## What Didn’t Work
- Monorepo coupling (frontend/backend tightly linked)
- No ORM (raw SQL made migrations and queries harder)
- Devopness env var issues (injection problems)
- Limited automated testing
- Error handling/logging gaps
- Scaling and deployment friction

---

## Features to Keep
- JWT auth, modular API, S3 uploads, Stripe payments
- Modern UI/UX, event tagging, dashboard tabs
- Responsive design, clear user flows

---

## Features to Drop or Improve
- Monorepo structure (move to separate frontend/backend)
- Add ORM (Prisma) for DB
- Dockerize for local dev and deployment
- Add automated tests (unit/integration/e2e)
- Improve error handling and logging
- Use modern CI/CD and env var management

---

## Migration Notes
- Use `/clannai-frontend` for UI/component reference
- Use this doc and all planning docs as source of truth
- Migrate only what fits new architecture—avoid legacy hacks
- Update docs as you go 