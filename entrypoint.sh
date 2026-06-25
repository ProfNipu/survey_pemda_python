#!/bin/bash

echo "======================================="
echo "🐍 Starting Django Application"
echo "======================================="

# Wait for MySQL
echo "⏳ Waiting for MySQL..."
while ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --silent --skip-ssl; do
    echo "⏳ MySQL is unavailable - sleeping..."
    sleep 2
done
echo "✅ MySQL is up and running!"

# Skip Redis check for now
echo "ℹ️ Skipping Redis check - will use database cache instead"

if [ "${CREATE_DB_IF_NOT_EXISTS:-0}" = "1" ]; then
    echo "🗄️ Setting up database (CREATE_DB_IF_NOT_EXISTS=1)..."
    mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --skip-ssl -e "
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
" 2>/dev/null || echo "⚠️ Database setup skipped (might already exist)"
else
    echo "ℹ️ Skipping DB create (CREATE_DB_IF_NOT_EXISTS!=1)"
fi

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    echo "🔄 Running database migrations (RUN_MIGRATIONS=1)..."
    python manage.py migrate --noinput
else
    echo "ℹ️ Skipping migrations (RUN_MIGRATIONS!=1)"
fi

if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
    echo "📁 Collecting static files (RUN_COLLECTSTATIC=1)..."
    python manage.py collectstatic --noinput
else
    echo "ℹ️ Skipping collectstatic (RUN_COLLECTSTATIC!=1)"
fi

# Create superuser if not exists and password is provided
if [ "${CREATE_SUPERUSER:-0}" = "1" ]; then
    echo "👤 Creating superuser (CREATE_SUPERUSER=1)..."
    python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    password = os.getenv('SUPERUSER_PASSWORD')
    if password:
        User.objects.create_superuser('admin', os.getenv('SUPERUSER_EMAIL', 'admin@example.com'), password)
        print('✅ Superuser created: admin')
    else:
        print('⚠️ SUPERUSER_PASSWORD not set - skipping superuser creation')
else:
    print('ℹ️ Superuser already exists')
"
else
    echo "ℹ️ Skipping superuser creation (CREATE_SUPERUSER!=1)"
fi

if [ "${LOAD_INITIAL_DATA:-0}" = "1" ]; then
    echo "📊 Loading initial data (LOAD_INITIAL_DATA=1)..."
    python manage.py loaddata initial_data.json 2>/dev/null || echo "ℹ️ No initial data to load"
else
    echo "ℹ️ Skipping initial data load (LOAD_INITIAL_DATA!=1)"
fi

echo "======================================="
echo "🚀 Starting server..."
echo "======================================="

# Start Django server
exec "$@"
