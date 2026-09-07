#!/bin/bash
# AI Resume & Cover Letter Tailor Launcher
echo "========================================="
echo " Starting AI Resume & Cover Letter Tailor "
echo "========================================="

# Find Python executable
PYTHON_CMD="/Users/shrikar/anaconda3/bin/python"
if [ ! -f "$PYTHON_CMD" ]; then
    PYTHON_CMD="python3"
fi

cd "$(dirname "$0")"

LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")

echo "========================================="
echo " Starting AI Resume & Cover Letter Tailor "
echo " Local Access:   http://localhost:8000"
echo " Network/Phone:  http://${LOCAL_IP}:8000"
echo "========================================="

# Open browser after a brief delay
(sleep 1.5 && open "http://localhost:8000") &

$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

