#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Print start message
echo "Starting Image Downloader..."
echo "Working directory: $DIR"

# Check for virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment (.venv) not found!"
    echo "Attempting to use system python3..."
fi

# Run the script
echo "Running imagedownloader.py..."
echo "----------------------------------------"
python3 imagedownloader.py

# Keep window open
echo "----------------------------------------"
echo "Script finished. Press any key to close this window."
read -n 1
