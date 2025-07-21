#!/bin/bash

# CLANNAI Unified Environment Setup Script
# For Ram and John's Bangalore VMs

echo "🚀 Setting up CLANNAI unified environment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install conda if not present
if ! command -v conda &> /dev/null; then
    echo "📦 Installing Anaconda..."
    wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh
    bash Anaconda3-2024.02-1-Linux-x86_64.sh -b -p $HOME/anaconda3
    echo 'export PATH="$HOME/anaconda3/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi

# Clone CLANNAI repo
if [ ! -d "CLANNAI" ]; then
    echo "📥 Cloning CLANNAI repository..."
    git clone https://github.com/clannorg/CLANNAI.git
fi

cd CLANNAI

# Create unified environment
echo "🐍 Creating clann-unified environment..."
conda env create -f clann-unified.yml

# Activate environment
echo "✅ Activating clann-unified environment..."
conda activate clann-unified

# Install additional dependencies
echo "📚 Installing additional dependencies..."
pip install -r requirements.txt

# Install ffmpeg for video processing
echo "🎬 Installing ffmpeg..."
sudo apt install ffmpeg -y

# Test environment
echo "🧪 Testing environment..."
python -c "import torch; import opencv; import google.generativeai; print('✅ Environment setup complete!')"

echo "🎉 CLANNAI environment ready!"
echo "📝 To activate: conda activate clann-unified"
echo "📁 Repository: $(pwd)"
echo "🚀 Ready for sprint work!" 