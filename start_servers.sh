#!/bin/bash

# Exit on any error
set -e

# --- Backend Setup ---
echo "--- Setting up backend ---"
cd /app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "--- Starting backend server ---"
python manage.py runserver > /tmp/backend.log 2>&1 &

# --- Frontend Setup ---
echo "--- Setting up frontend ---"
cd /app/frontend
echo "--- Installing frontend dependencies ---"
npm install
echo "--- Starting frontend server ---"
/app/frontend/node_modules/.bin/vite > /tmp/frontend.log 2>&1 &

echo "--- Servers starting in the background ---"
