#!/bin/bash

# Create FFmpeg layer for Lambda
set -e

echo "🎬 Creating FFmpeg Lambda Layer..."

# Create layer structure
mkdir -p bin
cd bin

# Download static FFmpeg binary for Lambda (Amazon Linux 2)
echo "📥 Downloading FFmpeg static binary..."
curl -L -o ffmpeg.tar.xz "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

# Extract FFmpeg
echo "📦 Extracting FFmpeg..."
tar -xf ffmpeg.tar.xz --strip-components=1
rm ffmpeg.tar.xz

# Keep only ffmpeg binary (remove ffprobe and other files to reduce size)
ls -la
chmod +x ffmpeg
rm -f ffprobe qt-faststart

cd ..

# Create layer zip
echo "🗜️ Creating layer package..."
zip -r ffmpeg-layer.zip bin/

# Upload layer
echo "☁️ Uploading to AWS Lambda..."
aws lambda publish-layer-version \
    --layer-name "clann-ffmpeg" \
    --description "FFmpeg static binary for ClannAI clip processing" \
    --zip-file fileb://ffmpeg-layer.zip \
    --compatible-runtimes nodejs18.x \
    --region eu-west-1

echo "✅ FFmpeg layer created successfully!"
echo "🧹 Cleaning up..."
rm -rf bin ffmpeg-layer.zip

echo "📋 Layer is ready to use in Lambda functions"