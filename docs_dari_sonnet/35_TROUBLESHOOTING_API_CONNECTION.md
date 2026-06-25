# 🔧 Troubleshooting - ESIMPEG API Connection

**Date**: 2026-03-31  
**Status**: ✅ RESOLVED

---

## ❌ Problem: "Gagal! Username atau password salah"

Saat login di Survey Pemda, muncul error "Gagal! Username atau password salah" padahal user baru (belum ada di database lokal).

---

## 🔍 Root Cause: RFC 1034/1035 Hostname Validation

**The Real Issue**: Django rejects hostnames with underscores (`_`) because they violate RFC 1034/1035 standards.

Container name `esimpeg_python_app` contains underscore, which is NOT a valid hostname according to RFC standards. Django's CommonMiddleware validates the `Host` header and rejects invalid hostnames BEFORE checking ALLOWED_HOSTS.

**Error Message**:
```
Invalid HTTP_HOST header: 'esimpeg_python_app:8000'. 
The domain name provided is not valid according to RFC 1034/1035.
```

---

## ✅ Solution: Use IP Address Instead of Hostname

Instead of using the container name with underscore, use the container's IP address directly.

### Step 1: Update Survey Pemda .env

```bash
# Edit .env
nano projects/survey_pemda_python/.env
```

Change:
```env
# OLD (doesn't work - underscore in hostname)
ESIMPEG_API_URL=http://esimpeg_python_app:8000

# NEW (works - IP address)
ESIMPEG_API_URL=http://172.21.0.2:8000
```

### Step 2: Restart Survey Pemda

```bash
docker restart survey_pemda_python_app
```

### Step 3: Test Connection

```bash
# Test health endpoint
docker exec survey_pemda_python_app curl -s http://172.21.0.2:8000/health/

# Should return:
# {"status": "healthy", "database": "connected", "cache": "connected", "message": "ESIMPEG Python is running"}
```

---

## 🎯 Expected Behavior After Fix

### Scenario 1: User NOT in Survey Pemda, EXISTS in ESIMPEG

```
1. User enters username + password
2. Survey Pemda checks local database → NOT FOUND
3. Survey Pemda calls ESIMPEG API at http://172.21.0.2:8000
4. ESIMPEG validates credentials → SUCCESS
5. Survey Pemda creates user with actual password
6. If password == 'Pegawai@Pessel' → Force change password
7. If password != 'Pegawai@Pessel' → Direct to dashboard
```

### Scenario 2: User EXISTS in Survey Pemda

```
1. User enters username + password
2. Survey Pemda checks local database → FOUND
3. Authenticate with local password → SUCCESS
4. Login successful (no API call needed)
```

---

## 📋 Configuration Summary

### Survey Pemda (.env)
```env
ESIMPEG_API_URL=http://172.21.0.2:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=
```

### ESIMPEG (.env)
```env
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,172.21.0.2,172.16.30.139,103.143.152.139,esimpeg-python.local,esimpeg-python.pesisirselatankab.go.id
```

---

## 🔍 Debugging Commands

### Check Survey Pemda Settings

```bash
docker exec survey_pemda_python_app python manage.py shell -c "
from django.conf import settings
print('ESIMPEG_API_URL:', getattr(settings, 'ESIMPEG_API_URL', 'NOT SET'))
"
```

### Check ESIMPEG ALLOWED_HOSTS

```bash
docker exec esimpeg_python_app python manage.py shell -c "
from django.conf import settings
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
"
```

### Test API Connection

```bash
# Health check
curl -s http://172.21.0.2:8000/health/

# Login test (will fail if user doesn't exist - that's OK)
curl -s -X POST http://172.21.0.2:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

---

## 📝 Lessons Learned

1. **RFC Compliance**: Docker container names with underscores are valid for Docker, but NOT valid as hostnames for HTTP requests
2. **Django Validation**: Django validates hostnames according to RFC 1034/1035 BEFORE checking ALLOWED_HOSTS
3. **Solution Options**:
   - ✅ Use IP address (172.21.0.2)
   - ✅ Use hostname without underscores (esimpeg-python-app)
   - ❌ Don't use hostname with underscores (esimpeg_python_app)

---

**Last Updated**: 2026-03-31  
**Version**: 2.0.0  
**Status**: ✅ RESOLVED
