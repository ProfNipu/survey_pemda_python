#!/bin/bash

echo "🔄 Reloading Static Files untuk ESIMPEG-Python..."
echo ""

# Step 1: Collect static files
echo "📦 Step 1: Collecting static files..."
docker exec esimpeg_python_app python manage.py collectstatic --noinput --clear

# Step 2: Restart container (untuk refresh gunicorn)
echo ""
echo "🔄 Step 2: Restarting container..."
docker restart esimpeg_python_app

# Step 3: Wait for health check
echo ""
echo "⏳ Step 3: Waiting for container to be healthy..."
sleep 5

# Step 4: Check status
echo ""
echo "✅ Container status:"
docker ps --filter "name=esimpeg_python" --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "✨ Done! Sekarang:"
echo "   1. Buka browser"
echo "   2. Tekan Ctrl+Shift+R (hard refresh) atau Ctrl+F5"
echo "   3. Test ganti password"
echo ""
echo "🌐 URL: http://localhost:8005"
echo ""
