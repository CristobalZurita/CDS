#!/bin/bash
# Start Backend and Frontend Together
# Usage: ./start_all.sh

echo "=== Cirujano de Sintetizadores ==="
echo "Starting all services..."
echo ""

# Start backend in background
echo "Starting backend on port 8000..."
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✓ Backend started successfully"
else
    echo "✗ Backend failed to start. Check /tmp/backend.log"
    exit 1
fi

# Start frontend
echo ""
echo "Starting frontend on port 5173..."
echo "Open browser: http://localhost:5173"
echo ""
npm run dev

# Cleanup on exit
trap "echo ''; echo 'Stopping backend...'; kill $BACKEND_PID 2>/dev/null" EXIT
