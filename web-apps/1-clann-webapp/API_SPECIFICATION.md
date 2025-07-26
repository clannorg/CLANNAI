# 📑 ClannAI API Specification

## Overview
This document defines the REST API contract for the ClannAI platform. All endpoints, request/response shapes, authentication, and error codes are specified here. This is the source of truth for frontend/backend integration.

---

## Authentication
- **JWT-based**: All protected endpoints require `Authorization: Bearer <token>`
- **Endpoints:**
  - `POST /api/auth/register` – Register new user
  - `POST /api/auth/login` – Login, returns JWT
  - `POST /api/auth/logout` – Logout (optional, for token blacklist)

---

## Users
- `GET /api/users/me` – Get current user profile
- `PATCH /api/users/me` – Update profile
- `GET /api/users/:id` – Get user by ID (admin only)


---

## Teams
- `GET /api/teams` – List teams user belongs to
- `POST /api/teams` – Create team
- `GET /api/teams/:id` – Get team details
- `PATCH /api/teams/:id` – Update team
- `DELETE /api/teams/:id` – Delete team (owner only)
- `POST /api/teams/:id/invite` – Invite user to team
- `GET /api/teams/:id/members` – List team members
- `PATCH /api/teams/:id/members/:userId` – Update member role
- `DELETE /api/teams/:id/members/:userId` – Remove member

---

## Games
- `GET /api/games` – List games (optionally filter by team)
- `POST /api/games` – Upload new game (metadata + video upload)
- `GET /api/games/:id` – Get game details
- `PATCH /api/games/:id` – Update game metadata
- `DELETE /api/games/:id` – Delete game

---

## Events
- `GET /api/games/:gameId/events` – List events for a game
- `POST /api/games/:gameId/events` – Create event
- `PATCH /api/events/:id` – Update event
- `DELETE /api/events/:id` – Delete event

---

## File Uploads
- `POST /api/uploads/video` – Get signed S3 URL for video upload
- `POST /api/uploads/complete` – Notify backend upload is complete

---

## Payments
- `POST /api/payments/create-checkout-session` – Create Stripe checkout session
- `POST /api/payments/webhook` – Stripe webhook endpoint
- `GET /api/payments/status` – Get user/team payment status

---

## Example Request/Response

### Register
```
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "hunter2",
  "name": "Jane Doe"
}

Response:
{
  "token": "<jwt>",
  "user": { ... }
}
```

### Create Team
```
POST /api/teams
{
  "name": "Galway United"
}

Response:
{
    "id": "uuid",
  "name": "Galway United",
  "owner_id": "uuid",
  ...
}
```

### Upload Video (S3 Signed URL)
```
POST /api/uploads/video
{
  "fileName": "match.mp4",
  "fileType": "video/mp4"
}

Response:
{
  "uploadUrl": "https://s3...",
  "fileUrl": "https://s3..."
}
```

---

## Error Codes
- `400 Bad Request` – Invalid input
- `401 Unauthorized` – Missing/invalid token
- `403 Forbidden` – Not allowed
- `404 Not Found` – Resource does not exist
- `409 Conflict` – Duplicate or conflicting resource
- `500 Internal Server Error` – Unexpected failure

---

## Notes
- All timestamps are ISO 8601 strings
- All IDs are UUIDs
- All responses are JSON
- Update this spec as the API evolves 