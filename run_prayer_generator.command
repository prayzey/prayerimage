#!/bin/bash

# Script to run the Prayer Image Generator
# This script includes error handling and environment checks

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if the main script exists
if [ ! -f "prayer_image.py" ]; then
    echo "Error: prayer_image.py not found in $(pwd)"
    exit 1
fi

# Run the prayer image generator
echo "Starting Prayer Image Generator..."
python3 prayer_image.py

# Keep the terminal window open if there's an error
read -p "Press Enter to exit..."
