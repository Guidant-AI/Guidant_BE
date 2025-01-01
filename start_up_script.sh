#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI application using PM2
pm2 start uvicorn --name "fastapi-app" -- main:app --host 0.0.0.0 --port 8000

# Save PM2 process list for startup
pm2 save

# Set PM2 to start on system reboot
pm2 startup
