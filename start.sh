#!/bin/bash
set -e

cd "$(dirname "$0")"
export PORT=5000
unset PIP_USER

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with system site packages..."
    python3 -m venv venv --system-site-packages
fi

# Activate
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Checking dependencies..."
    pip install -r requirements.txt
fi

echo "Starting application..."
python main.py
