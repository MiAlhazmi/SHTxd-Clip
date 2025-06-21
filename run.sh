#!/bin/bash

# SHTxd Clip - Run Script

echo "🎬 Starting SHTxd Clip..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "🔧 Please run setup first: ./setup.sh"
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in current directory!"
    exit 1
fi

# Activate virtual environment and run app
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "🚀 Launching application..."
python3 main.py
