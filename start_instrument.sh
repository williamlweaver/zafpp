#!/bin/bash
# ZAF++ Startup Script

# Navigate to project directory
cd "$(dirname "$0")"

# Activate Virtual Environment
source venv/bin/activate

# Start the Flask App
echo "Starting ZAF++ Touchscreen Interface..."
python3 app.py
