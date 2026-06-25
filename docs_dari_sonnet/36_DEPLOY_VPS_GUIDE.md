# 🚀 Deploy ke VPS - ESIMPEG API Integration

**Date**: 2026-03-31  
**Status**: DEPLOYMENT GUIDE

---

## 📋 Prerequisites

Sebelum deploy, pastikan:

- ✅ ESIMPEG Python sudah running di VPS
- ✅ Survey Pemda Python sudah running di VPS
- ✅ Kedua container dalam network yang sama (atau bisa saling akses)
- ✅ Port 8005 (ESIMPEG) dan 8006 (Survey Pemda) sudah di-expose

---

## 🎯 Skenario Deploy

### Skenario 1: Kedua Container di VPS yang Sama (Recommended) ✅

Ini adalah setup yang paling umum dan mudah.

```
┌─────────────────────────────────────────────────────────┐
│ VPS (103.143.152.139)                                   │
│                                                          │
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ Survey Pemda       │  │ ESIMPEG Python           │  │
│  │ Container          │  │ Container                │  │
│  │ Port: 8006         │  │ Port: 8005               │  │
│  │                    │  │                          │  │
│  │ Internal: 8000     │  │ Internal: 8000           │  │
│  │ IP: 172.21.0.3     │  │ IP: 172.21.0.2           │  │
│  └────────────────────┘  └──────────────────────────┘  │
│           │                         ▲                   │
│           └─────────────────────────┘                   │
│              Network: esimpeg-python_default            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Step-by-Step Deploy

### Step 1: Cek Network Setup di VPS

```bash
# SSH ke VPS
ssh root@103.143.152.139

# Cek network ESIMPEG
docker network inspect esimpeg-python_default

# Cek apakah Survey Pemda sudah dalam network yang sama
docker network inspect esimpeg-python_default | grep survey_pemda_python_app

# Kalau belum, connect manual:
docker network connect esimpeg-python_default survey_pemda_python_app
```

---

### Step 2: Cek IP Container ESIMPEG di VPS

```bash
# Cek IP ESIMPEG
docker inspect esimpeg_python_app | grep IPAddress

# Output contoh:
# "IPAddress": "172.21.0.2"
```

**PENTING**: Catat IP ini! Akan digunakan di Step 3.

---

### Step 3: Update Survey Pemda .env di VPS

```bash
# Edit .env
cd /path/to/survey_pemda_python
nano .env
```

Update atau tambahkan:

```env
# ESIMPEG API Configuration
# Ganti IP sesuai hasil Step 2
ESIMPEG_API_URL=http://172.21.0.2:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=
```

**Alternatif (Pakai Service Name)**:
```env
# Kalau pakai service name (lebih stabil)
ESIMPEG_API_URL=http://esimpeg-python:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=
```

Save dan exit (Ctrl+X, Y, Enter)

---

### Step 4: Update ESIMPEG ALLOWED_HOSTS di VPS

```bash
# Edit ESIMPEG .env
cd /path/to/ESIMPEG-Python
nano .env
```

Pastikan ALLOWED_HOSTS include IP internal Survey Pemda:

```env
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,172.16.30.139,103.143.152.139,esimpeg-python.local,esimpeg-python.pesisirselatankab.go.id,172.21.0.2,172.21.0.3
```

**Penjelasan**:
- `172.21.0.2` = IP ESIMPEG sendiri
- `172.21.0.3` = IP Survey Pemda (sesuaikan dengan IP sebenarnya)
- `103.143.152.139` = IP public VPS
- `esimpeg-python.pesisirselatankab.go.id` = Domain public

Save dan exit

---

### Step 5: Restart Kedua Container

```bash
# Restart ESIMPEG
docker restart esimpeg_python_app

# Wait
sleep 15

# Restart Survey Pemda
docker restart survey_pemda_python_app

# Wait
sleep 10
```

---

### Step 6: Test Connection di VPS

```bash
# Test dari container Survey Pemda ke ESIMPEG
docker exec survey_pemda_python_app curl -s http://172.21.0.2:8000/health/

# Harus return JSON:
# {"status": "healthy", "database": "connected", "cache": "connected", "message": "ESIMPEG Python is running"}
```

**Kalau gagal**, cek:
1. IP ESIMPEG benar?
2. Network connection OK?
3. ALLOWED_HOSTS sudah include IP Survey Pemda?

---

### Step 7: Test Login API

```bash
# Test login endpoint (akan error kalau user tidak ada - itu normal)
docker exec survey_pemda_python_app curl -s -X POST \
  http://172.21.0.2:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Expected response:
# {"status": "error", "message": "Username tidak ditemukan", "code": "USER_NOT_FOUND", "version": "5.0"}
```

---

### Step 8: Test dari Browser

1. Buka Survey Pemda: `http://103.143.152.139:8006/` atau `https://survey-pemda.pesisirselatankab.go.id/`
2. Login dengan user yang **ADA di ESIMPEG** tapi **BELUM ADA di Survey Pemda**
3. Harusnya:
   - ✅ Berhasil login
   - ✅ User otomatis dibuat di Survey Pemda
   - ✅ Redirect ke force change password (kalau password default)
   - ✅ Redirect ke dashboard (kalau password custom)

---

## 🔍 Troubleshooting di VPS

### Problem 1: Connection Refused

```bash
# Cek apakah ESIMPEG running
docker ps | grep esimpeg

# Cek logs ESIMPEG
docker logs esimpeg_python_app --tail 50

# Cek network
docker exec survey_pemda_python_app ping -c 2 172.21.0.2
```

### Problem 2: DisallowedHost Error

```bash
# Cek ALLOWED_HOSTS di ESIMPEG
docker exec esimpeg_python_app python manage.py shell -c "
from django.conf import settings
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
"

# Pastikan include IP Survey Pemda
```

### Problem 3: Invalid HTTP_HOST (RFC Error)

**Jangan pakai hostname dengan underscore!**

```env
# ❌ SALAH
ESIMPEG_API_URL=http://esimpeg_python_app:8000

# ✅ BENAR
ESIMPEG_API_URL=http://172.21.0.2:8000
# ATAU
ESIMPEG_API_URL=http://esimpeg-python:8000
```

---

## 🚀 Script Auto-Deploy

Buat script untuk memudahkan deploy:

```bash
#!/bin/bash
# deploy_esimpeg_integration.sh

echo "🚀 Deploying ESIMPEG Integration to VPS..."

# 1. Cek IP ESIMPEG
echo "📍 Checking ESIMPEG IP..."
ESIMPEG_IP=$(docker inspect esimpeg_python_app | grep -oP '(?<="IPAddress": ")[^"]*' | head -1)

if [ -z "$ESIMPEG_IP" ]; then
    echo "❌ Error: Cannot find ESIMPEG IP"
    exit 1
fi

echo "✅ ESIMPEG IP: $ESIMPEG_IP"

# 2. Cek IP Survey Pemda
echo "📍 Checking Survey Pemda IP..."
SURVEY_IP=$(docker inspect survey_pemda_python_app | grep -oP '(?<="IPAddress": ")[^"]*' | head -1)

if [ -z "$SURVEY_IP" ]; then
    echo "❌ Error: Cannot find Survey Pemda IP"
    exit 1
fi

echo "✅ Survey Pemda IP: $SURVEY_IP"

# 3. Update Survey Pemda .env
echo "📝 Updating Survey Pemda .env..."
cd /path/to/survey_pemda_python
sed -i "s|ESIMPEG_API_URL=.*|ESIMPEG_API_URL=http://$ESIMPEG_IP:8000|" .env

# 4. Update ESIMPEG ALLOWED_HOSTS
echo "📝 Updating ESIMPEG ALLOWED_HOSTS..."
cd /path/to/ESIMPEG-Python
# Backup current .env
cp .env .env.backup

# Add Survey Pemda IP to ALLOWED_HOSTS if not exists
if ! grep -q "$SURVEY_IP" .env; then
    sed -i "s|ALLOWED_HOSTS=\(.*\)|ALLOWED_HOSTS=\1,$SURVEY_IP|" .env
    echo "✅ Added $SURVEY_IP to ALLOWED_HOSTS"
fi

# 5. Restart containers
echo "🔄 Restarting containers..."
docker restart esimpeg_python_app
sleep 15
docker restart survey_pemda_python_app
sleep 10

# 6. Test connection
echo "🧪 Testing connection..."
HEALTH_CHECK=$(docker exec survey_pemda_python_app curl -s http://$ESIMPEG_IP:8000/health/)

if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "✅ Connection test PASSED!"
    echo "$HEALTH_CHECK"
else
    echo "❌ Connection test FAILED!"
    echo "$HEALTH_CHECK"
    exit 1
fi

# 7. Test login API
echo "🧪 Testing login API..."
LOGIN_TEST=$(docker exec survey_pemda_python_app curl -s -X POST \
  http://$ESIMPEG_IP:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}')

if echo "$LOGIN_TEST" | grep -q "version"; then
    echo "✅ Login API test PASSED!"
    echo "$LOGIN_TEST"
else
    echo "❌ Login API test FAILED!"
    echo "$LOGIN_TEST"
    exit 1
fi

echo ""
echo "🎉 Deploy complete!"
echo "📍 ESIMPEG IP: $ESIMPEG_IP"
echo "📍 Survey Pemda IP: $SURVEY_IP"
echo "🌐 Test at: http://103.143.152.139:8006/"
```

**Cara pakai**:
```bash
# Buat file
nano deploy_esimpeg_integration.sh

# Paste script di atas, edit path sesuai VPS

# Beri permission
chmod +x deploy_esimpeg_integration.sh

# Run
./deploy_esimpeg_integration.sh
```

---

## 📋 Checklist Deploy

Sebelum deploy, pastikan:

- [ ] ESIMPEG sudah running di VPS
- [ ] Survey Pemda sudah running di VPS
- [ ] Kedua container dalam network yang sama
- [ ] IP ESIMPEG sudah dicatat
- [ ] IP Survey Pemda sudah dicatat
- [ ] `.env` Survey Pemda sudah di-update
- [ ] `.env` ESIMPEG ALLOWED_HOSTS sudah di-update
- [ ] Kedua container sudah di-restart
- [ ] Health check berhasil
- [ ] Login API test berhasil
- [ ] Test login dari browser berhasil

---

## 🔐 Security Notes untuk Production

### 1. Gunakan HTTPS

```env
# Production .env
ESIMPEG_API_URL=https://esimpeg-python.pesisirselatankab.go.id
```

### 2. Set WEBHOOK_SECRET

```env
# Generate secret key
ESIMPEG_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

### 3. Restrict ALLOWED_HOSTS

```env
# Hanya allow IP/domain yang diperlukan
ALLOWED_HOSTS=esimpeg-python.pesisirselatankab.go.id,172.21.0.2,172.21.0.3
```

### 4. Enable Firewall

```bash
# Allow only necessary ports
ufw allow 8005/tcp  # ESIMPEG
ufw allow 8006/tcp  # Survey Pemda
ufw allow 22/tcp    # SSH
ufw enable
```

---

## 📊 Monitoring

### Check Logs

```bash
# Survey Pemda logs
docker logs survey_pemda_python_app --tail 100 -f

# ESIMPEG logs
docker logs esimpeg_python_app --tail 100 -f

# Filter API calls
docker logs survey_pemda_python_app 2>&1 | grep "ESIMPEG API"
```

### Check Connection Status

```bash
# Create monitoring script
cat > check_esimpeg_status.sh << 'EOF'
#!/bin/bash
ESIMPEG_IP=$(docker inspect esimpeg_python_app | grep -oP '(?<="IPAddress": ")[^"]*' | head -1)
HEALTH=$(docker exec survey_pemda_python_app curl -s http://$ESIMPEG_IP:8000/health/)

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ ESIMPEG API: OK"
else
    echo "❌ ESIMPEG API: DOWN"
    echo "$HEALTH"
fi
EOF

chmod +x check_esimpeg_status.sh

# Run periodically
watch -n 60 ./check_esimpeg_status.sh
```

---

## 🆘 Rollback Plan

Kalau ada masalah setelah deploy:

```bash
# 1. Restore backup .env
cd /path/to/survey_pemda_python
cp .env.backup .env

cd /path/to/ESIMPEG-Python
cp .env.backup .env

# 2. Restart containers
docker restart esimpeg_python_app
docker restart survey_pemda_python_app

# 3. Check logs
docker logs survey_pemda_python_app --tail 50
docker logs esimpeg_python_app --tail 50
```

---

## 📞 Support

Kalau masih ada masalah:

1. Cek logs kedua container
2. Cek network connectivity
3. Cek ALLOWED_HOSTS
4. Cek IP address tidak berubah
5. Test dengan script monitoring

---

**Last Updated**: 2026-03-31  
**Version**: 1.0.0  
**Status**: PRODUCTION READY ✅
