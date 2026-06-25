#!/bin/bash

# Stop Tailwind Watch

PID_FILE="tailwind.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Tailwind watch tidak berjalan (PID file tidak ditemukan)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 Stopping Tailwind watch (PID: $PID)..."
    kill $PID
    rm "$PID_FILE"
    echo "✅ Tailwind watch stopped"
else
    echo "❌ Process PID $PID tidak ditemukan (mungkin sudah stop)"
    rm "$PID_FILE"
fi
