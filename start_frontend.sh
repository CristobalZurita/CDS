#!/bin/bash
# Start Frontend Development Server
# Usage: ./start_frontend.sh [port]

PORT=${1:-5173}

echo "Starting Cirujano Frontend on port $PORT..."
npm run dev -- --port $PORT --host 0.0.0.0
