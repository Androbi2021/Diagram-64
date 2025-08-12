#!/bin/bash

# Exit on any error
set -e

# --- Backend Setup ---
echo "--- Setting up backend ---"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "--- Starting backend server ---"

python manage.py runserver > /tmp/backend.log 2>&1 &

# --- Frontend Setup ---
echo "--- Setting up frontend ---"
cd frontend
echo "--- Installing frontend dependencies ---"
npm install
echo "--- Starting frontend server ---"

npm run dev > /tmp/frontend.log 2>&1 &

cd ..
echo "--- Servers starting in the background ---"
echo "--- Logs available in /tmp/backend.log and /tmp/frontend.log ---"