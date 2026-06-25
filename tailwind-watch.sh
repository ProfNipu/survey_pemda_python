#!/bin/bash

# Tailwind CSS Watch Mode Helper
# Auto-rebuild Tailwind saat file template berubah

echo "🚀 Starting Tailwind CSS Watch Mode..."
echo "📂 Watching: templates/**/*.html, apps/**/templates/**/*.html"
echo ""
echo "⚡ Tailwind akan auto-rebuild saat file berubah"
echo "❌ Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --watch
