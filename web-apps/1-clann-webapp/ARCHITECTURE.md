# 🏗️ System Architecture

## 🎯 **Overview**

ClannAI Football Analysis Platform - A unified system for uploading, analyzing, and viewing football game videos with event tracking and team management.

## 🏗️ **Technical Architecture**

### **Frontend (Next.js 15)**
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI
- **State Management**: React Query + Context API
- **Video Player**: HLS.js for streaming + custom event overlay
- **Authentication**: JWT tokens

### **Backend (Express.js)**
- **Framework**: Express.js
- **Database**: PostgreSQL
- **Authentication**: JWT with bcrypt
- **File Storage**: AWS S3
- **Video Processing**: HLS transcoding
- **API**: RESTful with JSON responses

### **Database (PostgreSQL)**
- **Users**: Account management
- **Teams**: Team management with flexible names
- **Games**: Video metadata and processing status
- **Events**: Flexible JSON structure for any sport
- **Team Members**: User-team relationships

---

## 🗄️ **Database Schema**

### **1. Users Table**
```sql
users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(500),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

### **2. Teams Table**
```sql
teams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  color VARCHAR(50) DEFAULT '#016F32',
  logo_url VARCHAR(500),
  team_code VARCHAR(50) UNIQUE, -- For invites
  owner_id UUID REFERENCES users(id),
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

### **3. Team Members Table**
```sql
team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(team_id, user_id)
)
```

### **4. Games Table**
```sql
games (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

### **5. Events Table**
```sql
events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  game_id UUID REFERENCES games(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL, -- goal, shot, pass, tackle, foul, etc.
  timestamp INTEGER NOT NULL, -- in seconds from video start
  team_id UUID REFERENCES teams(id),
  player_name VARCHAR(255),
  description TEXT,
  coordinates JSONB, -- {x: 0.5, y: 0.3} for pitch position
  metadata JSONB, -- flexible JSON for custom fields, tags, notes
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

---

## 🎬 **Video Processing Pipeline**

### **1. Upload Stage**
- **File Validation**: Type, size, duration
- **S3 Upload**: Store original file
- **Metadata Extraction**: Duration, resolution, codec
- **Status Update**: Set to 'processing'

### **2. Transcoding Stage**
- **HLS Conversion**: Convert to streaming format
- **Quality Variants**: Multiple bitrates for adaptive streaming
- **Thumbnail Generation**: Create video preview
- **Segment Creation**: Split into 10-second segments

### **3. Processing Stage**
- **AI Analysis**: Event detection (future)
- **Metadata Storage**: Store processing results
- **Status Update**: Set to 'ready'

### **4. Storage Structure**
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
│                       ├── segment_0.ts
│                       ├── segment_1.ts
│                       └── ...
└── public/
    └── assets/
        ├── logos/
        └── icons/
```

---

## 🔐 **Authentication & Authorization**

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

### **Authorization Levels**
- **Public**: Landing page, login, register
- **Authenticated**: Full access to all features (dashboard, upload, view games, manage teams, add events)

### **Session Management**
- **Token Storage**: localStorage (frontend)
- **Token Validation**: Middleware on protected routes
- **Token Refresh**: Automatic refresh before expiration
- **Logout**: Clear token, redirect to login

---

## 🎯 **Event JSON Structure**

### **Flexible Event Schema**
```json
{
  "id": "uuid",
  "game_id": "uuid",
  "event_type": "goal|shot|pass|tackle|foul|corner|free-kick|substitution|yellow-card|red-card",
  "timestamp": 120,
  "team_id": "uuid",
  "player_name": "Player Name",
  "description": "Custom description",
  "coordinates": {"x": 0.5, "y": 0.3},
  "metadata": {
    "confidence": 0.95,
    "custom_fields": {},
    "tags": ["important", "highlight"],
    "notes": "Coach's notes here"
  },
  "created_by": "uuid",
  "created_at": "timestamp"
}
```

### **Event Editing Capabilities**
- **Event Type**: Change from "shot" to "goal"
- **Timestamp**: Adjust when event happens
- **Team**: Change which team event belongs to
- **Player**: Update who did the action
- **Description**: Add/edit custom descriptions
- **Coordinates**: Adjust position on pitch
- **Tags**: Add/remove categorization tags
- **Notes**: Add coach's comments
- **Custom Fields**: Any additional data

---

## 🔄 **Data Flow**

### **1. User Registration**
```
Frontend → Backend → Database
User fills form → JWT created → User stored
```

### **2. Video Upload**
```
Frontend → Backend → S3 → Processing
File selected → Upload to S3 → Transcode → Ready
```

### **3. Event Creation**
```
Frontend → Backend → Database
User clicks timeline → Event saved → Timeline updates
```

### **4. Video Playback**
```
Database → Backend → Frontend → HLS.js
Load events → Stream video → Display with events
```

---

## 🛡️ **Error Handling Strategy**

### **Upload Errors**
- **File too large**: Show size limit message
- **Invalid file type**: Show supported formats
- **Upload timeout**: Retry with progress indicator
- **Processing failure**: Show error status

### **Authentication Errors**
- **Invalid credentials**: Clear error message
- **Token expired**: Automatic refresh or redirect
- **Permission denied**: Show appropriate message
- **Account not found**: Clear registration prompt

### **Video Playback Errors**
- **Video not found**: Show 404 with upload option
- **Streaming issues**: Retry with different quality
- **Browser compatibility**: Show fallback player
- **Network problems**: Offline indicator

### **Database Errors**
- **Connection issues**: Retry with exponential backoff
- **Constraint violations**: Clear validation messages
- **Transaction failures**: Rollback and retry
- **Performance issues**: Query optimization

---

## 🔧 **Performance Optimizations**

### **Frontend**
- **Code splitting**: Lazy load components
- **Image optimization**: Next.js Image component
- **Caching**: React Query for API responses
- **Bundle optimization**: Tree shaking, minification

### **Backend**
- **Database indexing**: Optimized queries
- **Connection pooling**: Efficient database connections
- **Caching**: Redis for frequently accessed data
- **Compression**: Gzip responses

### **Video Streaming**
- **HLS adaptive streaming**: Multiple quality levels
- **CDN integration**: Global content delivery
- **Caching headers**: Browser and CDN caching
- **Progressive loading**: Load segments on demand

---

## 🚀 **Scalability Considerations**

### **Database**
- **Read replicas**: For high read loads
- **Sharding**: If single database becomes bottleneck
- **Connection pooling**: Efficient resource usage
- **Query optimization**: Indexes and query tuning

### **Video Processing**
- **Queue system**: Background job processing
- **Multiple workers**: Parallel video processing
- **Auto-scaling**: Based on queue length
- **Storage optimization**: Lifecycle policies

### **API**
- **Rate limiting**: Prevent abuse
- **Load balancing**: Distribute traffic
- **Caching layers**: Reduce database load
- **Monitoring**: Track performance metrics

This architecture provides a solid foundation that's scalable, maintainable, and user-friendly! 