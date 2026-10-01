#!/bin/bash
# Starts the AI Resume & Cover Letter Tailor on http://localhost:8000
# It reads the CV sources from the repository root (one level up).
cd "$(dirname "$0")"

PYTHON_CMD="/Users/shrikar/anaconda3/bin/python"
[ -x "$PYTHON_CMD" ] || PYTHON_CMD="python3"

LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")
echo "========================================="
echo " AI Resume & Cover Letter Tailor"
echo " Local Access:   http://localhost:8000"
echo " Network/Phone:  http://${LOCAL_IP}:8000"
echo "========================================="

(sleep 1.5 && open "http://localhost:8000") &
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
