#!/bin/bash

# YouTube Downloader Pro - Setup Script

echo "🎬 YouTube Downloader Pro - Setup"
echo "=================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Installing packages individually..."
    pip install customtkinter>=5.2.0 yt-dlp>=2023.7.6 requests>=2.28.0 Pillow>=9.0.0 packaging>=21.0
fi

# Check for FFmpeg
echo "🔍 Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg found: $(ffmpeg -version | head -n 1)"
else
    echo "⚠️  FFmpeg not found!"
    echo "📥 Please install FFmpeg:"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   macOS: brew install ffmpeg"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   Ubuntu/Debian: sudo apt install ffmpeg"
        echo "   CentOS/RHEL: sudo yum install ffmpeg"
    else
        echo "   Download from: https://ffmpeg.org/download.html"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run YouTube Downloader Pro:"
echo "1. source venv/bin/activate"
echo "2. python3 main.py"
echo ""
echo "Or use the run script: ./run.sh"
