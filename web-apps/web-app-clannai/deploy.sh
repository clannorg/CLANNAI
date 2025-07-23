#!/bin/bash

# ClannAI Web App Deployment Script
echo "🚀 Starting ClannAI deployment..."

# Install dependencies
echo "📦 Installing server dependencies..."
cd server && npm install && cd ..

echo "📦 Installing client dependencies..."
cd client && npm install && cd ..

# Build client for production
echo "🏗️ Building client for production..."
cd client && npm run build && cd ..

# Start server (for production, you'd use PM2 or similar)
echo "🖥️ Starting server..."
cd server && npm start 