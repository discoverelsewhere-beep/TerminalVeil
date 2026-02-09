#!/bin/bash
# Terminal Veil Web Server
# Runs on http://0.0.0.0:5000

cd "$(dirname "$0")"

echo "Starting Terminal Veil Web Edition..."
echo "Access at: http://$(ifconfig | grep -E "inet .*broadcast" | head -1 | awk '{print $2}'):5000"
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
