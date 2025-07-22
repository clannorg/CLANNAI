# 🗄️ Schema Plan

## 🎯 **Database Schema Overview**

### **Core Tables:**
1. **users** - User accounts and authentication
2. **teams** - Team management
3. **games** - Video games and metadata
4. **events** - Game events and timestamps
5. **team_members** - User-team relationships

---

## 📊 **Detailed Schema**

### **1. Users Table**
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(500),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

**Purpose:** Store user accounts and authentication data
**Relationships:** One-to-many with teams, games

### **2. Teams Table**
```sql
teams (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  owner_id UUID REFERENCES users(id),
  logo_url VARCHAR(500),
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

**Purpose:** Store team information
**Relationships:** Many-to-one with users, one-to-many with games

### **3. Team Members Table**
```sql
team_members (
  id UUID PRIMARY KEY,
  team_id UUID REFERENCES teams(id),
  user_id UUID REFERENCES users(id),
  role VARCHAR(50) DEFAULT 'member', -- owner, admin, member
  joined_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(team_id, user_id)
)
```

**Purpose:** Manage user-team relationships and permissions
**Relationships:** Many-to-one with teams and users

### **4. Games Table**
```sql
games (
  id UUID PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  video_url VARCHAR(500) NOT NULL,
  thumbnail_url VARCHAR(500),
  duration INTEGER, -- in seconds
  file_size BIGINT, -- in bytes
  team_id UUID REFERENCES teams(id),
  uploaded_by UUID REFERENCES users(id),
  status VARCHAR(50) DEFAULT 'processing', -- processing, ready, error
  metadata JSONB, -- video metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

**Purpose:** Store video game information and metadata
**Relationships:** Many-to-one with teams and users, one-to-many with events

### **5. Events Table**
```sql
events (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  event_type VARCHAR(50) NOT NULL, -- goal, shot, pass, tackle, foul, etc.
  timestamp INTEGER NOT NULL, -- in seconds from video start
  team VARCHAR(50), -- red, blue, or null
  player_name VARCHAR(255),
  description TEXT,
  coordinates JSONB, -- {x: 0.5, y: 0.3} for pitch position
  confidence FLOAT, -- AI confidence score (0-1)
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

**Purpose:** Store game events and their timestamps
**Relationships:** Many-to-one with games and users

---

## 🔐 **Authentication Schema**

### **JWT Token Structure**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "iat": 1234567890,
  "exp": 1234567890
}
```

### **Session Management**
- **Token Storage:** localStorage (frontend)
- **Token Validation:** Middleware on protected routes
- **Token Refresh:** Automatic refresh before expiration

---

## 📁 **File Storage Schema**

### **S3 Bucket Structure**
```
clann-videos/
├── users/
│   └── {user_id}/
│       └── games/
│           └── {game_id}/
│               ├── original.mp4
│               ├── thumbnail.jpg
│               └── hls/
│                   ├── playlist.m3u8
│                   └── segments/
└── public/
    └── assets/
        ├── logos/
        └── icons/
```

### **Video Processing Pipeline**
1. **Upload** → S3 original bucket
2. **Transcode** → HLS format for streaming
3. **Generate** → Thumbnail and metadata
4. **Store** → Processed files in organized structure

---

## 🎬 **Video Player Schema**

### **Event Types**
```typescript
type EventType = 
  | 'goal' 
  | 'shot' 
  | 'pass' 
  | 'tackle' 
  | 'foul' 
  | 'corner' 
  | 'free-kick' 
  | 'substitution'
  | 'yellow-card'
  | 'red-card'
```

### **Event Coordinates**
```typescript
type Coordinates = {
  x: number; // 0-1 (left to right)
  y: number; // 0-1 (top to bottom)
}
```

### **Video Metadata**
```typescript
type VideoMetadata = {
  duration: number;
  resolution: {
    width: number;
    height: number;
  };
  fps: number;
  codec: string;
  fileSize: number;
}
```

---

## 🔄 **API Response Schemas**

### **User Response**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "avatar_url": "https://...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### **Team Response**
```json
{
  "id": "uuid",
  "name": "Team Name",
  "description": "Team description",
  "owner": { /* user object */ },
  "members": [ /* user objects */ ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### **Game Response**
```json
{
  "id": "uuid",
  "title": "Game Title",
  "description": "Game description",
  "video_url": "https://...",
  "thumbnail_url": "https://...",
  "duration": 3600,
  "team": { /* team object */ },
  "events": [ /* event objects */ ],
  "status": "ready",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### **Event Response**
```json
{
  "id": "uuid",
  "event_type": "goal",
  "timestamp": 120,
  "team": "red",
  "player_name": "Player Name",
  "description": "Goal scored",
  "coordinates": {"x": 0.5, "y": 0.3},
  "confidence": 0.95,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 🎯 **Data Validation Rules**

### **User Validation**
- Email: Valid email format, unique
- Password: Minimum 8 characters, hashed
- Name: Required, 1-255 characters

### **Team Validation**
- Name: Required, 1-255 characters
- Owner: Required, valid user ID
- Description: Optional, max 1000 characters

### **Game Validation**
- Title: Required, 1-255 characters
- Video URL: Required, valid URL
- File size: Maximum 4GB
- Duration: Maximum 2 hours (7200 seconds)

### **Event Validation**
- Event type: Required, valid enum value
- Timestamp: Required, 0 to video duration
- Team: Optional, 'red' or 'blue'
- Coordinates: Optional, valid 0-1 range

---

## 🔧 **Indexes for Performance**

### **Primary Indexes**
- `users(email)` - Fast login lookups
- `games(team_id)` - Fast team game queries
- `events(game_id, timestamp)` - Fast event queries
- `team_members(team_id, user_id)` - Fast permission checks

### **Secondary Indexes**
- `games(status)` - Filter by processing status
- `events(event_type)` - Filter by event type
- `games(created_at)` - Sort by upload date
- `events(created_at)` - Sort by event creation

This schema supports all the user flows while maintaining good performance and data integrity! 