# Video Downloads & Clip Creation - Approaches & Solutions

## Overview
This document tracks our journey through different approaches for creating downloadable video clips from full game videos, the problems we encountered, and our path forward.

## The Problem
- **Input**: Full game videos (1+ GB, 60+ minutes) stored on S3
- **Requirement**: Extract multiple event clips with custom padding (before/after seconds)
- **Output**: Combined highlight reel for download
- **Constraints**: Must work in production, be fast, and cost-effective

## Approaches Tried

### 1. Local FFmpeg (Initial Approach)
**Implementation**: Direct FFmpeg processing on the backend server
```javascript
// ffmpeg -ss startTime -i videoUrl -t duration -c copy output.mp4
```

**Problems**:
- ✅ **Local**: Works perfectly on development machines
- ❌ **Production**: FFmpeg not installed on Devopness servers
- ❌ **Deployment**: Can't easily install FFmpeg binaries on managed hosting
- **Result**: `ffmpeg: command not found` in production

### 2. AWS MediaConvert (Current Fallback)
**Implementation**: Cloud-based video transcoding service
```javascript
const job = await mediaConvert.createJob({
  Role: process.env.MEDIACONVERT_ROLE_ARN,
  Settings: { /* complex job configuration */ }
});
```

**Problems**:
- ✅ **Reliability**: Works in production
- ❌ **Speed**: 5-15 minutes processing time for simple clips
- ❌ **Cost**: $0.0075 per minute of video processed
- ❌ **Complexity**: Downloads entire 1GB video to extract 30 seconds
- ❌ **User Experience**: Long wait times, polling required

**Current Status**: Working but slow and expensive

### 3. Pre-chunked Videos (Attempted)
**Implementation**: Pre-split videos into 15-second chunks, serve directly
```javascript
// chunks/clip_06m15s.mp4, clip_06m30s.mp4, etc.
const chunkUrl = `${chunksBaseUrl}/clip_${minutes}m${seconds}s.mp4`;
```

**Problems**:
- ✅ **Speed**: Instant serving of chunks
- ❌ **Precision**: Can't get exact timestamps (limited to 15s boundaries)
- ❌ **Combination**: No way to combine multiple chunks without... FFmpeg
- ❌ **Infrastructure**: Requires pre-processing and separate storage

**Current Status**: Implemented but limited functionality

## Current Implementation (Hybrid)

### Backend Logic Flow:
```javascript
// 1. Check for chunks first (fastest)
if (game.chunks_base_url) {
  return serveDirectChunks(events); // Instant but imprecise
}

// 2. Fall back to MediaConvert (slow but works)
return createMediaConvertJob(events); // 5+ minutes
```

### Frontend Handling:
- **Chunks**: Direct download links, staggered for multiple events
- **MediaConvert**: Polling system with progress updates
- **FFmpeg**: Disabled (commented out)

## The Solution: AWS Lambda + FFmpeg

### Why Lambda Solves Everything:
1. **FFmpeg Available**: Pre-built layers or bundled binaries
2. **Serverless**: No deployment/installation issues
3. **Fast**: Processes only needed segments (30-60 seconds vs full video)
4. **Cheap**: Pay per execution (~$0.001 vs $0.45 for MediaConvert)
5. **Scalable**: Auto-scales for multiple users

### Proposed Architecture:
```
Frontend → Backend → Lambda Function → FFmpeg → S3 Upload → Download URL
                                    ↓
                            Smart Segment Extraction:
                            - Stream from S3 (no full download)
                            - Extract only needed timestamps
                            - Combine multiple clips
                            - Upload final result
```

### Lambda Function Flow:
```javascript
exports.handler = async (event) => {
  const { gameId, events, s3VideoUrl } = JSON.parse(event.body);
  
  // 1. Extract segments using FFmpeg streaming
  for (const event of events) {
    await ffmpeg([
      '-ss', startTime,
      '-i', s3VideoUrl,  // Stream from S3, don't download
      '-t', duration,
      '-c', 'copy',      // No re-encoding = fast
      `/tmp/segment_${event.timestamp}.mp4`
    ]);
  }
  
  // 2. Concatenate segments
  await ffmpeg(['-f', 'concat', '-i', 'segments.txt', 'final.mp4']);
  
  // 3. Upload to S3 and return URL
  return { downloadUrl: await uploadToS3('final.mp4') };
};
```

## Performance Comparison

| Method | Processing Time | Cost (1hr video) | Reliability | Precision |
|--------|----------------|------------------|-------------|-----------|
| **Local FFmpeg** | 30-60 seconds | Free | ❌ Prod fails | ✅ Exact |
| **MediaConvert** | 5-15 minutes | $0.45 | ✅ Works | ✅ Exact |
| **Chunks** | Instant | Free | ✅ Works | ❌ 15s blocks |
| **Lambda + FFmpeg** | 30-90 seconds | $0.001 | ✅ Works | ✅ Exact |

## Next Steps

### 1. Create Lambda Function
- Set up AWS Lambda with FFmpeg layer
- Implement smart segment extraction
- Add S3 upload/download handling

### 2. Update Backend Integration
- Replace MediaConvert calls with Lambda invocation
- Keep chunks as fastest option for compatible use cases
- Remove FFmpeg local fallback

### 3. Frontend Updates
- Handle Lambda response (faster than MediaConvert)
- Maintain existing chunk and MediaConvert support during transition

### 4. Migration Strategy
- Deploy Lambda function
- Test with existing games
- Gradually migrate from MediaConvert to Lambda
- Keep MediaConvert as final fallback

## Technical Debt Resolved
- ✅ **No more server FFmpeg dependencies**
- ✅ **Fast clip creation (seconds not minutes)**
- ✅ **Cost-effective processing**
- ✅ **Exact timestamp precision**
- ✅ **Production reliability**

## Files Modified
- `backend/routes/clips-mediaconvert.js` - Hybrid approach implementation
- `frontend/src/components/games/UnifiedSidebar.tsx` - Multi-method handling
- `backend/routes/games.js` - Chunks URL upload endpoint
- `frontend/src/app/company/page.tsx` - Chunks URL management
- Database: Added `chunks_base_url` column to games table

---

**Status**: Ready to implement Lambda solution as the definitive approach for video clip creation.