#!/bin/bash
# Terminal Veil Launcher
# Sets required library paths and starts the server

cd "$(dirname "$0")"

# Set library path for zbar (macOS)
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH

echo "========================================"
echo "  TERMINAL VEIL v2.0"
echo "========================================"
echo ""

# Get IP for mobile testing
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

echo "Starting server..."
echo ""
echo "Desktop:    http://localhost:5495"
echo "Mobile:     http://$IP:5495"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

python3 app.py
