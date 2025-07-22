# 📁 Simple Backend Structure

```
backend/
├── src/
│   ├── index.js                          # Main server entry point
│   ├── config/
│   │   ├── database.js                   # PostgreSQL connection
│   │   └── auth.js                       # JWT configuration
│   │
│   ├── routes/
│   │   ├── auth.js                       # Login, register, logout
│   │   ├── games.js                      # Games CRUD operations
│   │   ├── teams.js                      # Team management
│   │   └── upload.js                     # File upload handling
│   │
│   ├── controllers/
│   │   ├── authController.js             # Authentication logic
│   │   ├── gamesController.js            # Games business logic
│   │   ├── teamsController.js            # Team business logic
│   │   └── uploadController.js           # File upload logic
│   │
│   ├── middleware/
│   │   ├── auth.js                       # JWT verification
│   │   ├── upload.js                     # File upload middleware
│   │   └── validation.js                 # Request validation
│   │
│   ├── models/
│   │   ├── User.js                       # User model
│   │   ├── Game.js                       # Game model
│   │   ├── Team.js                       # Team model
│   │   └── Event.js                      # Game events model
│   │
│   └── utils/
│       ├── database.js                   # Database utilities
│       ├── auth.js                       # JWT utilities
│       └── helpers.js                    # Helper functions
│
├── database/
│   ├── schema.sql                        # Database schema
│   └── migrations/                       # Database migrations
│
├── package.json
├── .env                                  # Environment variables
└── README.md
```

## 🎯 **Core API Endpoints**

### **Authentication**
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### **Games**
- `GET /api/games` - List all games
- `GET /api/games/:id` - Get specific game
- `POST /api/games` - Create new game
- `PUT /api/games/:id` - Update game
- `DELETE /api/games/:id` - Delete game

### **Teams**
- `GET /api/teams` - List user's teams
- `GET /api/teams/:id` - Get specific team
- `POST /api/teams` - Create new team
- `PUT /api/teams/:id` - Update team

### **Upload**
- `POST /api/upload/video` - Upload video file
- `POST /api/upload/thumbnail` - Upload thumbnail

## 🗄️ **Database Schema**

### **Users Table**
```sql
users (
  id, email, password_hash, name, 
  created_at, updated_at
)
```

### **Teams Table**
```sql
teams (
  id, name, description, owner_id,
  created_at, updated_at
)
```

### **Games Table**
```sql
games (
  id, title, description, video_url,
  team_id, user_id, status,
  created_at, updated_at
)
```

### **Events Table**
```sql
events (
  id, game_id, event_type, timestamp,
  team, description, coordinates,
  created_at
)
```

## 🔧 **Tech Stack**

- **Framework**: Express.js
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **File Upload**: Multer + S3 (later)
- **Validation**: Joi or Zod
- **CORS**: Enabled for frontend

## 📊 **Comparison Summary**

**Our Plan vs Existing Backends:**

| Feature | web-app-clannai | clannai-frontend | Our Plan |
|---------|----------------|------------------|----------|
| **Backend Control** | ✅ Full control | ❌ External | ✅ Full control |
| **Authentication** | ✅ JWT | ❌ AWS Cognito | ✅ JWT |
| **Database** | ✅ PostgreSQL | ❌ External | ✅ PostgreSQL |
| **Video Storage** | ✅ S3 | ❌ External | ✅ S3 |
| **Video Streaming** | ❌ Basic | ✅ HLS.js | ✅ HLS.js |
| **Video Player** | ❌ Basic | ✅ Advanced | ✅ Advanced |
| **Event Tracking** | ❌ None | ✅ Full events | ✅ Full events |

## 🎬 **Video Streaming Strategy**

### **The Challenge:**
- **1-hour videos** = large files (2-4GB)
- **Direct streaming** = slow loading, buffering
- **No optimization** = poor user experience

### **Our Solution:**
- **Phase 1**: S3 storage + basic React Player
- **Phase 2**: HLS.js streaming for optimized playback
- **Phase 3**: Advanced player with events and timeline

## 🚀 **Simple & Focused**

- ✅ **JWT authentication** (no AWS complexity)
- ✅ **Basic CRUD** operations
- ✅ **File upload** for videos
- ✅ **Clean structure** easy to understand
- ✅ **Ready to scale** when needed

## 📋 **Implementation Phases**

### **Phase 1: Foundation**
- [ ] Set up Express server
- [ ] Configure PostgreSQL
- [ ] Basic JWT authentication
- [ ] Simple API endpoints

### **Phase 2: Core Features**
- [ ] Games CRUD operations
- [ ] Team management
- [ ] File upload functionality
- [ ] Event tracking

### **Phase 3: Polish**
- [ ] Input validation
- [ ] Error handling
- [ ] API documentation
- [ ] Testing

This gives us a solid backend that matches our simple frontend structure! 