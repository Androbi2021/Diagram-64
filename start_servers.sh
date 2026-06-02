#!/bin/bash

# Exit on any error
set -e

# Port the backend (Django) listens on. Override with: BACKEND_PORT=8001 ./start_servers.sh
# The frontend's Vite proxy reads the same variable, so both stay in sync automatically.
BACKEND_PORT="${BACKEND_PORT:-8000}"
export BACKEND_PORT

# --- Backend Setup ---
echo "--- Setting up backend ---"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "--- Starting backend server ---"

echo "--- Backend will listen on port ${BACKEND_PORT} ---"
python manage.py runserver "${BACKEND_PORT}" > /tmp/backend.log 2>&1 &

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