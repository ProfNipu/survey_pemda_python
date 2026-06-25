# Deploy Survey Pemda ke VPS (Complete Guide)

**Tanggal**: 2026-04-08  
**Status**: Survey Pemda belum ada di VPS  
**Action**: Deploy lengkap dari laptop ke VPS

---

## 📋 Pre-requisites

- ✅ VPS: 103.143.152.139
- ✅ ESIMPEG sudah running di VPS port 8005
- ✅ MySQL sudah running di VPS
- ✅ Redis sudah running di VPS
- ⚠️ Survey Pemda belum di-deploy

---

## 🚀 Cara Deploy Survey Pemda ke VPS

### Opsi 1: Rsync dari Laptop (Recommended)

```bash
# Di laptop
cd ~/project-docker/all-projects-darireal/projects

# Rsync seluruh folder survey_pemda_python ke VPS
rsync -avz --progress \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'staticfiles' \
  --exclude 'media' \
  --exclude 'logs/*.log' \
  --exclude 'node_modules' \
  survey_pemda_python/ \
  root@103.143.152.139:/root/survey_pemda_python/
```

**Estimasi waktu**: 2-5 menit (tergantung koneksi)

### Opsi 2: Git Clone (Alternative)

```bash
# Di VPS
ssh root@103.143.152.139

# Clone dari repository (jika ada)
cd /root
git clone <repository-url> survey_pemda_python
cd survey_pemda_python
```

### Opsi 3: Zip & Upload (Jika Rsync Lambat)

```bash
# Di laptop
cd ~/project-docker/all-projects-darireal/projects
tar -czf survey_pemda_python.tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='staticfiles' \
  --exclude='node_modules' \
  survey_pemda_python/

# Upload ke VPS
scp survey_pemda_python.tar.gz root@103.143.152.139:/root/

# Di VPS
ssh root@103.143.152.139
cd /root
tar -xzf survey_pemda_python.tar.gz
```

---

## ⚙️ Konfigurasi di VPS

### 1. Update .env untuk Production

```bash
# Di VPS
cd /root/survey_pemda_python
cp .env.example .env
nano .env
```

**Update konfigurasi**:
```bash
# Django
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=103.143.152.139,localhost

# Database
DB_HOST=mysql-main
DB_PORT=3306
DB_NAME=survey_pemda_python_db
DB_USER=root
DB_PASSWORD=!23#

# Redis
REDIS_HOST=redis-main
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=4

# ESIMPEG API
ESIMPEG_API_URL=http://172.17.0.1:8005
ESIMPEG_API_TIMEOUT=10

# Session
SESSION_COOKIE_NAME=sessionid_survey_pemda_8006
CSRF_COOKIE_NAME=csrftoken_survey_pemda_8006
```

### 2. Update docker-compose.prod.yml

```bash
# Di VPS
cd /root/survey_pemda_python
nano docker-compose.prod.yml
```

**Isi**:
```yaml
version: '3.8'

services:
  survey-pemda-python:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: survey_pemda_python_app
    restart: unless-stopped
    ports:
      - "8006:8000"
    environment:
      - DEBUG=False
    env_file:
      - .env
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - mysql-main
      - redis-main
    networks:
      - esimpeg-network
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3

volumes:
  static_volume:
  media_volume:

networks:
  esimpeg-network:
    external: true
```

### 3. Build & Run Container

```bash
# Di VPS
cd /root/survey_pemda_python

# Build image
docker-compose -f docker-compose.prod.yml build

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm survey-pemda-python python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml run --rm survey-pemda-python python manage.py collectstatic --noinput

# Create superuser (optional)
docker-compose -f docker-compose.prod.yml run --rm survey-pemda-python python manage.py createsuperuser

# Start container
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker logs -f survey_pemda_python_app
```

---

## 🧪 Testing di VPS

### 1. Check Container Running

```bash
docker ps | grep survey
```

**Expected**:
```
survey_pemda_python_app   Up X minutes   0.0.0.0:8006->8000/tcp
```

### 2. Test HTTP Access

```bash
curl http://103.143.152.139:8006
```

**Expected**: HTML response (landing page)

### 3. Test Login

```
http://103.143.152.139:8006
```

Login dengan user yang ada di database.

### 4. Test API ESIMPEG Connection

```bash
docker exec survey_pemda_python_app python manage.py shell -c "
from apps.accounts.services import EsimpegAPIService
api = EsimpegAPIService()
result = api.login('Prakom@admin2025.com', 'Prakom@2025')
print('✅ SUCCESS!' if result else '❌ FAILED')
"
```

### 5. Test Sync Pegawai

1. Login ke http://103.143.152.139:8006
2. Akses menu "Data Pegawai ESIMPEG"
3. Klik "Sinkronisasi"
4. Popup password muncul
5. Masukkan password ESIMPEG
6. Sync berjalan
7. Data pegawai muncul

---

## 🔧 Troubleshooting

### Issue 1: Container Tidak Start

**Check logs**:
```bash
docker logs survey_pemda_python_app
```

**Common issues**:
- Database connection error → Check DB_HOST, DB_PASSWORD
- Redis connection error → Check REDIS_HOST
- Port already in use → Check port 8006 available

### Issue 2: Cannot Connect to ESIMPEG API

**Test connection**:
```bash
docker exec survey_pemda_python_app curl http://172.17.0.1:8005/apisimpeg/5.0/auth/login
```

**Solutions**:
- Check ESIMPEG container running: `docker ps | grep esimpeg`
- Check ESIMPEG_API_URL in .env
- Try different gateway IP: `172.18.0.1` or `172.21.0.1`

### Issue 3: Static Files Not Loading

**Collect static**:
```bash
docker exec survey_pemda_python_app python manage.py collectstatic --noinput
```

### Issue 4: Database Migration Error

**Run migrations**:
```bash
docker exec survey_pemda_python_app python manage.py migrate
```

---

## 📊 Deployment Checklist

### Pre-deployment
- [ ] Backup VPS data
- [ ] Check disk space: `df -h`
- [ ] Check Docker running: `docker ps`
- [ ] Check MySQL running
- [ ] Check Redis running

### Deployment
- [ ] Rsync/upload files ke VPS
- [ ] Update .env untuk production
- [ ] Build Docker image
- [ ] Run migrations
- [ ] Collect static files
- [ ] Start container
- [ ] Check logs

### Post-deployment
- [ ] Test HTTP access
- [ ] Test login
- [ ] Test ESIMPEG API connection
- [ ] Test sync pegawai
- [ ] Test password popup
- [ ] Monitor logs for errors

---

## 🎯 Quick Deploy Script

Buat script untuk deploy otomatis:

```bash
# Di laptop: deploy.sh
#!/bin/bash

echo "🚀 Deploying Survey Pemda to VPS..."

# 1. Rsync files
echo "📦 Syncing files..."
rsync -avz --progress \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'staticfiles' \
  --exclude 'media' \
  --exclude 'logs/*.log' \
  --exclude 'node_modules' \
  ~/project-docker/all-projects-darireal/projects/survey_pemda_python/ \
  root@103.143.152.139:/root/survey_pemda_python/

# 2. Deploy on VPS
echo "🔧 Deploying on VPS..."
ssh root@103.143.152.139 << 'EOF'
cd /root/survey_pemda_python

# Build and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker exec survey_pemda_python_app python manage.py migrate

# Collect static
docker exec survey_pemda_python_app python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
docker ps | grep survey
EOF

echo "🎉 Done! Access at http://103.143.152.139:8006"
```

**Usage**:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📝 Notes

**Network Configuration**:
- Survey Pemda: Port 8006
- ESIMPEG: Port 8005
- Survey Pemda → ESIMPEG: via `172.17.0.1:8005` (Docker gateway)

**Database**:
- Survey Pemda DB: `survey_pemda_python_db`
- ESIMPEG DB: `esimpeg_python_db` atau `esim_pegawai`
- Shared MySQL container

**Performance**:
- Sync 9,002 pegawai: 30-90 detik
- Default per_page: 200 (optimal)
- Database indexes applied

**Security**:
- DEBUG=False in production
- Strong SECRET_KEY
- ALLOWED_HOSTS configured
- Password not stored (only token in session)

---

## ✅ Kesimpulan

Survey Pemda siap di-deploy ke VPS dengan fitur:
- ✅ Login via ESIMPEG API
- ✅ Password popup untuk sync
- ✅ Real-time progress bar
- ✅ Optimal performance (per_page=200)
- ✅ Token management di session

Deploy dengan rsync atau script otomatis! 🚀
