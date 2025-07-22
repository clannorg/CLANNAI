# 🔌 API Specification

## 🎯 **Overview**

Complete API specification for the ClannAI Football Analysis Platform. All endpoints return JSON responses and use JWT authentication for protected routes.

---

## 🔐 **Authentication**

### **JWT Token Format**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "iat": 1234567890,
  "exp": 1234567890
}
```

### **Authorization Headers**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## 👤 **Authentication Endpoints**

### **POST /api/auth/register**
**Register a new user**

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "jwt_token_here"
}
```

### **POST /api/auth/login**
**Login user**

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "jwt_token_here"
}
```

### **POST /api/auth/logout**
**Logout user (clear token)**

**Request:** `{}`

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### **GET /api/auth/me**
**Get current user info**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "avatar_url": "https://...",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 👥 **Team Management Endpoints**

### **GET /api/teams**
**Get user's teams**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "teams": [
    {
      "id": "uuid",
      "name": "Manchester United",
      "description": "Team description",
      "color": "#016F32",
      "logo_url": "https://...",
      "team_code": "MUFC123",
      "owner": {
        "id": "uuid",
        "name": "Owner Name"
      },
      "members": [
        {
          "id": "uuid",
          "name": "Member Name"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### **POST /api/teams**
**Create new team**

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Manchester United",
  "description": "Team description",
  "color": "#016F32"
}
```

**Response:**
```json
{
  "success": true,
  "team": {
    "id": "uuid",
    "name": "Manchester United",
    "description": "Team description",
    "color": "#016F32",
    "team_code": "MUFC123",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### **GET /api/teams/:id**
**Get specific team**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "team": {
    "id": "uuid",
    "name": "Manchester United",
    "description": "Team description",
    "color": "#016F32",
    "logo_url": "https://...",
    "team_code": "MUFC123",
    "owner": {
      "id": "uuid",
      "name": "Owner Name"
    },
    "members": [
      {
        "id": "uuid",
        "name": "Member Name"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### **PUT /api/teams/:id**
**Update team**

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Updated Team Name",
  "description": "Updated description",
  "color": "#FF0000"
}
```

**Response:**
```json
{
  "success": true,
  "team": {
    "id": "uuid",
    "name": "Updated Team Name",
    "description": "Updated description",
    "color": "#FF0000",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### **POST /api/teams/:id/invite**
**Invite user to team**

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "email": "invite@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Invitation sent successfully"
}
```

---

## 🎮 **Games Management Endpoints**

### **GET /api/games**
**Get user's games**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `team_id` (optional): Filter by team
- `status` (optional): Filter by status (processing, ready, error)
- `page` (optional): Page number for pagination
- `limit` (optional): Items per page

**Response:**
```json
{
  "success": true,
  "games": [
    {
      "id": "uuid",
      "title": "Manchester United vs Liverpool",
      "description": "Game description",
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "duration": 3600,
      "file_size": 2147483648,
      "status": "ready",
      "team": {
        "id": "uuid",
        "name": "Manchester United",
        "color": "#016F32"
      },
      "uploaded_by": {
        "id": "uuid",
        "name": "User Name"
      },
      "event_count": 15,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

### **GET /api/games/:id**
**Get specific game with events**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "game": {
    "id": "uuid",
    "title": "Manchester United vs Liverpool",
    "description": "Game description",
    "video_url": "https://...",
    "thumbnail_url": "https://...",
    "duration": 3600,
    "file_size": 2147483648,
    "status": "ready",
    "metadata": {
      "resolution": {"width": 1920, "height": 1080},
      "fps": 30,
      "codec": "h264"
    },
    "team": {
      "id": "uuid",
      "name": "Manchester United",
      "color": "#016F32"
    },
    "uploaded_by": {
      "id": "uuid",
      "name": "User Name"
    },
    "events": [
      {
        "id": "uuid",
        "event_type": "goal",
        "timestamp": 120,
        "team": {
          "id": "uuid",
          "name": "Manchester United",
          "color": "#016F32"
        },
        "player_name": "Ronaldo",
        "description": "Amazing goal!",
        "coordinates": {"x": 0.5, "y": 0.3},
        "metadata": {
          "confidence": 0.95,
          "tags": ["highlight"],
          "notes": "Coach's comment"
        },
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### **POST /api/games**
**Upload new game**

**Headers:** `Authorization: Bearer <token>`

**Request:** `multipart/form-data`
- `video`: Video file (MP4, MOV, AVI)
- `title`: Game title
- `description`: Game description
- `team_id`: Team ID

**Response:**
```json
{
  "success": true,
  "game": {
    "id": "uuid",
    "title": "Manchester United vs Liverpool",
    "status": "processing",
    "upload_progress": 0,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### **DELETE /api/games/:id**
**Delete game**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Game deleted successfully"
}
```

---

## 🎯 **Events Management Endpoints**

### **GET /api/games/:id/events**
**Get events for a game**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `event_type` (optional): Filter by event type
- `team_id` (optional): Filter by team
- `player_name` (optional): Filter by player

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "uuid",
      "event_type": "goal",
      "timestamp": 120,
      "team": {
        "id": "uuid",
        "name": "Manchester United",
        "color": "#016F32"
      },
      "player_name": "Ronaldo",
      "description": "Amazing goal!",
      "coordinates": {"x": 0.5, "y": 0.3},
      "metadata": {
        "confidence": 0.95,
        "tags": ["highlight"],
        "notes": "Coach's comment"
      },
      "created_by": {
        "id": "uuid",
        "name": "User Name"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### **POST /api/games/:id/events**
**Create new event**

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "event_type": "goal",
  "timestamp": 120,
  "team_id": "uuid",
  "player_name": "Ronaldo",
  "description": "Amazing goal!",
  "coordinates": {"x": 0.5, "y": 0.3},
  "metadata": {
    "confidence": 0.95,
    "tags": ["highlight"],
    "notes": "Coach's comment"
  }
}
```

**Response:**
```json
{
  "success": true,
  "event": {
    "id": "uuid",
    "event_type": "goal",
    "timestamp": 120,
    "team": {
      "id": "uuid",
      "name": "Manchester United",
      "color": "#016F32"
    },
    "player_name": "Ronaldo",
    "description": "Amazing goal!",
    "coordinates": {"x": 0.5, "y": 0.3},
    "metadata": {
      "confidence": 0.95,
      "tags": ["highlight"],
      "notes": "Coach's comment"
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### **PUT /api/events/:id**
**Update event**

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "event_type": "shot",
  "timestamp": 125,
  "team_id": "uuid",
  "player_name": "Ronaldo",
  "description": "Updated description",
  "coordinates": {"x": 0.6, "y": 0.4},
  "metadata": {
    "confidence": 0.90,
    "tags": ["highlight", "important"],
    "notes": "Updated coach's comment"
  }
}
```

**Response:**
```json
{
  "success": true,
  "event": {
    "id": "uuid",
    "event_type": "shot",
    "timestamp": 125,
    "team": {
      "id": "uuid",
      "name": "Manchester United",
      "color": "#016F32"
    },
    "player_name": "Ronaldo",
    "description": "Updated description",
    "coordinates": {"x": 0.6, "y": 0.4},
    "metadata": {
      "confidence": 0.90,
      "tags": ["highlight", "important"],
      "notes": "Updated coach's comment"
    },
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### **DELETE /api/events/:id**
**Delete event**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Event deleted successfully"
}
```

---

## 📤 **Upload Endpoints**

### **POST /api/upload/video**
**Upload video file**

**Headers:** `Authorization: Bearer <token>`

**Request:** `multipart/form-data`
- `video`: Video file
- `title`: Video title
- `description`: Video description
- `team_id`: Team ID

**Response:**
```json
{
  "success": true,
  "upload": {
    "id": "uuid",
    "filename": "game_video.mp4",
    "size": 2147483648,
    "progress": 0,
    "status": "uploading"
  }
}
```

### **GET /api/upload/:id/status**
**Get upload status**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "upload": {
    "id": "uuid",
    "status": "processing",
    "progress": 75,
    "message": "Transcoding video..."
  }
}
```

---

## 🛡️ **Error Responses**

### **Authentication Error**
```json
{
  "success": false,
  "error": "UNAUTHORIZED",
  "message": "Invalid or missing token"
}
```

### **Validation Error**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

### **Not Found Error**
```json
{
  "success": false,
  "error": "NOT_FOUND",
  "message": "Resource not found"
}
```

### **Server Error**
```json
{
  "success": false,
  "error": "INTERNAL_ERROR",
  "message": "Something went wrong"
}
```

---

## 📊 **Status Codes**

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Validation Error
- **500**: Internal Server Error

---

## 🔧 **Rate Limiting**

- **Authentication endpoints**: 5 requests per minute
- **Upload endpoints**: 10 requests per hour
- **Other endpoints**: 100 requests per minute

---

## 📈 **Pagination**

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

**Response Format:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10
  }
}
```

This API specification provides a complete interface for the ClannAI platform! 