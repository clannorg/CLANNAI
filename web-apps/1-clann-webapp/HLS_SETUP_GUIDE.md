# HLS Streaming Setup Guide

## 🎬 What We Built

A complete HLS (HTTP Live Streaming) system that converts your MP4 videos into adaptive streaming format with multiple quality levels (360p, 720p, 1080p).

## 🏗️ Architecture

```
MP4 Video → AWS MediaConvert → HLS Segments → CloudFront CDN → Fast Streaming
```

## 📋 AWS Setup Required

### 1. MediaConvert IAM Role

You need to create an IAM role for MediaConvert to access your S3 bucket:

```bash
# Role name: MediaConvertRole
# Trust policy: MediaConvert service
# Permissions: S3 read/write access to your bucket
```

**Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "mediaconvert.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Permissions Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

### 2. Environment Variables

Add to your `.env` file:

```bash
# Existing AWS vars
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-west-1
AWS_BUCKET_NAME=your-bucket-name

# New MediaConvert role ARN
MEDIACONVERT_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/MediaConvertRole
```

## 🚀 How to Use

### 1. Run Database Migration

```bash
cd web-apps/1-clann-webapp/db
psql -d your_database -f migrations/006_add_hls_conversions.sql
```

### 2. Start HLS Conversion

```bash
# Convert a game video to HLS
POST /api/hls/convert/:gameId
```

### 3. Check Status

```bash
# Check conversion progress
GET /api/hls/status/:gameId

# Get HLS URL when ready
GET /api/hls/url/:gameId
```

## 📊 What Gets Created

For each video, MediaConvert creates:

```
s3://your-bucket/hls/gameId/
├── index.m3u8           # Master playlist
├── stream_360p.m3u8     # 360p playlist
├── stream_720p.m3u8     # 720p playlist  
├── stream_1080p.m3u8    # 1080p playlist
├── segment_360p_001.ts  # Video segments
├── segment_360p_002.ts
├── segment_720p_001.ts
└── ...
```

## ⚡ Benefits

- **Fast Seeking**: 6-second segments for instant jumps
- **Adaptive Quality**: Switches based on connection speed
- **Mobile Optimized**: Works perfectly on all devices
- **CDN Ready**: Designed for CloudFront delivery
- **Professional**: Same tech as YouTube/Netflix

## 🎯 Next Steps

1. **Test Conversion**: Try converting one game video
2. **Frontend Integration**: Update VideoPlayer to use HLS.js
3. **CloudFront Setup**: Add CDN for global delivery
4. **Monitoring**: Track conversion success rates

## 🔧 Troubleshooting

**Common Issues:**

1. **Role ARN Error**: Make sure MediaConvert role exists and has S3 permissions
2. **Region Mismatch**: MediaConvert and S3 bucket must be in same region
3. **Bucket Permissions**: Role needs read/write access to your S3 bucket

**Test MediaConvert Access:**
```bash
aws mediaconvert describe-endpoints --region eu-west-1
```

## 💰 Cost Estimate

- **MediaConvert**: ~$0.0075 per minute of video
- **S3 Storage**: ~$0.023 per GB per month  
- **CloudFront**: ~$0.085 per GB transferred

For a 90-minute game: ~$0.68 conversion + storage costs.