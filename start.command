#!/usr/bin/env bash
# Double-clickable macOS launcher for CASE CLOSED
cd "$(dirname "$0")"
echo "=========================================================="
echo " Starting CASE CLOSED — Classified Investigation Bureau"
echo " Open http://127.0.0.1:8000 in your web browser"
echo " Press Ctrl+C in this terminal window to stop the server"
echo "=========================================================="
./manage.py runserver 127.0.0.1:8000
