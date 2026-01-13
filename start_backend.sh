#!/bin/bash
# Start Backend Server
# Usage: ./start_backend.sh [port]

PORT=${1:-8000}

echo "Starting Cirujano Backend on port $PORT..."
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --reload
