#!/bin/bash

# Install FFmpeg on Ubuntu/Debian server
echo "🎬 Installing FFmpeg for video processing..."

# Update package list
sudo apt-get update

# Install FFmpeg
sudo apt-get install -y ffmpeg

# Verify installation
ffmpeg -version

echo "✅ FFmpeg installation complete!"
