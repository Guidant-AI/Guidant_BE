#!/bin/bash

# Exit the script on any error
set -e

# Navigate to the project directory
cd "$(dirname "$0")" || exit

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start the FastAPI application with PM2
echo "Starting the FastAPI application with PM2..."
pm2 start uvicorn --name "fastapi-app" -- main:app --host 0.0.0.0 --port 8000

# Save the PM2 process list
echo "Saving PM2 process list..."
pm2 save

# Set PM2 to start on system reboot
echo "Configuring PM2 to start on system reboot..."
pm2 startup --silent

echo "FastAPI app deployed and managed with PM2!"
