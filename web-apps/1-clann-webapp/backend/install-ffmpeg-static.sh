#!/bin/bash

# Download static FFmpeg binary (no sudo required)
echo "🎬 Downloading static FFmpeg binary..."

# Create bin directory
mkdir -p ./bin

# Download static FFmpeg for Linux x64
wget -O ./bin/ffmpeg https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
if [ $? -ne 0 ]; then
    echo "❌ Failed to download FFmpeg"
    exit 1
fi

# Extract the binary
cd ./bin
tar -xf ffmpeg-release-amd64-static.tar.xz --strip-components=1
rm ffmpeg-release-amd64-static.tar.xz

# Make executable
chmod +x ffmpeg

# Verify installation
./ffmpeg -version

echo "✅ Static FFmpeg installation complete!"
echo "📍 FFmpeg location: $(pwd)/ffmpeg"
