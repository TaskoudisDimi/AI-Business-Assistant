#!/bin/bash

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$REPO_ROOT/wms/backend"
FRONTEND_DIR="$REPO_ROOT/wms/frontend/ui"
VENV_ACTIVATE="$BACKEND_DIR/ai-bus-assistant/bin/activate"

echo "Starting WMS..."

# Backend terminal
osascript <<EOF
tell application "Terminal"
    do script "source '$VENV_ACTIVATE' && cd '$BACKEND_DIR' && uvicorn main:app --reload"
    set custom title of front window to "Backend - FastAPI"
end tell
EOF

# Frontend terminal
osascript <<EOF
tell application "Terminal"
    do script "cd '$FRONTEND_DIR' && npm run dev"
    set custom title of front window to "Frontend - Vue"
end tell
EOF

echo "Opened Backend and Frontend terminals."
