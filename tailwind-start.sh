#!/bin/bash

# Start Tailwind Watch in Background

PID_FILE="tailwind.pid"
LOG_FILE="tailwind-watch.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Tailwind watch sudah berjalan (PID: $PID)"
        echo "💡 Gunakan ./tailwind-stop.sh untuk stop"
        exit 1
    fi
fi

echo "🚀 Starting Tailwind CSS Watch Mode di background..."

cd "$(dirname "$0")"
nohup npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --watch > "$LOG_FILE" 2>&1 &
PID=$!

echo $PID > "$PID_FILE"
echo "✅ Tailwind watch started (PID: $PID)"
echo "📄 Log: $LOG_FILE"
echo "🛑 Stop dengan: ./tailwind-stop.sh"
