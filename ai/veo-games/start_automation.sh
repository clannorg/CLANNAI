#!/bin/bash

# AI Pipeline → Website Automation Startup Script

echo "🚀 AI Pipeline → Website Automation"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "automation_config.yaml" ]; then
    echo "❌ Error: automation_config.yaml not found"
    echo "Please run this script from the ai/veo-games/ directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 to continue"
    exit 1
fi

# Check/install dependencies
echo "📦 Checking dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Install dependencies if needed
pip3 install -r requirements.txt --quiet

echo "✅ Dependencies ready"

# Check if setup has been run
if [ ! -f "processed_games.json" ]; then
    echo ""
    echo "🔧 First time setup detected"
    echo "Running setup wizard..."
    python3 setup_automation.py
else
    echo ""
    echo "⚡ Starting automation monitor..."
    echo "Press Ctrl+C to stop"
    echo ""
    python3 pipeline_automation.py
fi