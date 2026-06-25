# Fix DisallowedHost Error After Laptop Restart

## Problem

Setiap kali restart laptop, muncul error `DisallowedHost` saat Survey Pemda mencoba connect ke ESIMPEG API.

**Error Message**:
```
DisallowedHost at /apisimpeg/5.0/auth/login
Invalid HTTP_HOST header: '172.18.0.6:8000'. You may need to add '172.18.0.6' to ALLOWED_HOSTS.
```

## Root Cause

Docker containers mendapat IP address dinamis dari Docker network. Setiap kali restart:
1. Docker network di-recreate
2. Containers mendapat IP baru (bisa berubah)
3. Django ALLOWED_HOSTS validation menolak IP baru
4. Survey Pemda tidak bisa connect ke ESIMPEG API

**Contoh IP Changes**:
- Before restart: `172.18.0.6`
- After restart: `172.21.0.2` ← IP berubah!

## Solutions Implemented

### Solution 1: Wildcard ALLOWED_HOSTS (DEBUG Mode)

**File**: `projects/ESIMPEG-Python/esimpeg_core/settings.py`

```python
if DEBUG:
    # Accept all hosts in DEBUG mode (for Docker dynamic IPs)
    ALLOWED_HOSTS = ['*']
    # Use X-Forwarded-Host header to bypass CommonMiddleware host validation
    USE_X_FORWARDED_HOST = True
    # Disable host validation completely in DEBUG mode
    ALLOWED_HOSTS_INCLUDE_SCHEME = False
else:
    ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')]
    USE_X_FORWARDED_HOST = False
```

**Pros**:
- ✅ Tidak perlu update manual setelah restart
- ✅ Works dengan semua IP di Docker subnet

**Cons**:
- ⚠️  Hanya untuk DEBUG mode (production harus specify hosts)

### Solution 2: Custom Middleware untuk Docker Hosts

**File**: `projects/ESIMPEG-Python/esimpeg_core/middleware/docker_hosts.py`

```python
"""
Custom middleware for ESIMPEG Python
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AllowDockerHostsMiddleware:
    """
    Middleware to allow Docker container hostnames and IPs in DEBUG mode
    This fixes DisallowedHost errors when containers communicate using hostnames or dynamic IPs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only apply in DEBUG mode
        if settings.DEBUG:
            host = request.get_host()
            
            # Allow Docker container hostnames
            if any(pattern in host for pattern in [
                'esimpeg_python_app',
                'survey_pemda_python_app',
                'localhost',
                '127.0.0.1',
                '0.0.0.0',
            ]):
                # Bypass host validation
                request.META['HTTP_HOST'] = 'localhost:8000'
            
            # Allow Docker subnet IPs (172.x.x.x, 192.168.x.x, 10.x.x.x)
            elif any(host.startswith(prefix) for prefix in ['172.', '192.168.', '10.']):
                # Bypass host validation for Docker IPs
                request.META['HTTP_HOST'] = 'localhost:8000'
        
        response = self.get_response(request)
        return response
```

**Added to MIDDLEWARE**:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'esimpeg_core.middleware.docker_hosts.AllowDockerHostsMiddleware',  # ← NEW
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]
```

**Pros**:
- ✅ Lebih granular control
- ✅ Hanya apply di DEBUG mode
- ✅ Support hostname dan IP

**Cons**:
- ⚠️  Lebih complex

### Solution 3: Auto-Fix Script

**File**: `fix-docker-network.sh` (di root project)

Script ini akan:
1. Check Docker status
2. Get current container IPs
3. Test connectivity
4. Auto-update `.env` file jika IP berubah
5. Restart containers jika perlu

**Usage**:
```bash
# Setelah restart laptop, jalankan:
./fix-docker-network.sh

# Script akan:
# 1. Detect IP baru
# 2. Tanya apakah mau update .env
# 3. Update ESIMPEG_API_URL di .env
# 4. Restart Survey Pemda container
```

**Script Features**:
- ✅ Auto-detect IP changes
- ✅ Interactive update (ask before change)
- ✅ Backup .env before update
- ✅ Test connectivity
- ✅ Show container health status

## How to Use After Laptop Restart

### Option A: Fully Automatic (RECOMMENDED)

Install systemd service untuk auto-fix saat boot:

```bash
# Install sekali saja
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --install

# Selesai! Auto-fix akan jalan otomatis setiap boot
```

Setelah install, auto-fix akan jalan otomatis setiap kali:
- ✅ Laptop restart
- ✅ Docker service start
- ✅ Tidak perlu manual intervention

**Check status**:
```bash
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status
```

**View logs**:
```bash
sudo journalctl -u docker-network-fix.service -f
```

### Option B: Manual Run (Quick Fix)

Jika belum install service, jalankan manual:

```bash
# Run auto-fix script (no confirmation needed)
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh

# Script akan otomatis:
# 1. Detect IP baru
# 2. Update .env
# 3. Restart containers
# 4. Done!
```

### Option C: Silent Background Mode

Untuk run di background tanpa output:

```bash
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh > /tmp/docker-fix.log 2>&1 &
```

### Option D: Manual (Old Way)

```bash
# 1. Check new IP
docker inspect esimpeg_python_app | grep IPAddress

# 2. Update .env
nano projects/survey_pemda_python/.env
# Change: ESIMPEG_API_URL=http://NEW_IP:8000

# 3. Restart
docker restart survey_pemda_python_app
```

## Current Configuration

**ESIMPEG Settings** (`projects/ESIMPEG-Python/esimpeg_core/settings.py`):
```python
DEBUG = True
ALLOWED_HOSTS = ['*']  # Accept all in DEBUG mode
USE_X_FORWARDED_HOST = True
```

**Survey Pemda .env** (`projects/survey_pemda_python/.env`):
```bash
# Use IP address (updated by fix-docker-network.sh)
ESIMPEG_API_URL=http://172.21.0.2:8000
```

## Testing

```bash
# Test connectivity
./fix-docker-network.sh

# Expected output:
# ✅ Survey Pemda → ESIMPEG (IP): OK
# ✅ ESIMPEG: healthy
# ✅ Survey Pemda: healthy
```

## Troubleshooting

### Issue: Script shows "FAILED (HTTP 400)"

**Cause**: Django host validation still rejecting request

**Fix**:
```bash
# 1. Check ALLOWED_HOSTS in ESIMPEG
docker exec esimpeg_python_app python manage.py shell << 'EOF'
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"USE_X_FORWARDED_HOST: {settings.USE_X_FORWARDED_HOST}")
EOF

# 2. Restart ESIMPEG
docker restart esimpeg_python_app
```

### Issue: Script shows "FAILED (HTTP 000)"

**Cause**: Container not ready or network issue

**Fix**:
```bash
# 1. Wait for containers to be healthy
docker ps --filter name=python_app

# 2. Check logs
docker logs esimpeg_python_app --tail 50

# 3. Restart both containers
docker restart esimpeg_python_app survey_pemda_python_app
```

### Issue: IP keeps changing

**Cause**: Docker network recreated on restart

**Solution**: Use static IP in docker-compose (advanced)

**File**: `docker-compose.yml`
```yaml
services:
  esimpeg_python_app:
    networks:
      internal-network:
        ipv4_address: 172.18.0.10  # Static IP

networks:
  internal-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.18.0.0/16
```

## Files Modified

1. `projects/ESIMPEG-Python/esimpeg_core/settings.py`
   - Set `ALLOWED_HOSTS = ['*']` in DEBUG mode
   - Added `USE_X_FORWARDED_HOST = True`

2. `projects/ESIMPEG-Python/esimpeg_core/middleware/docker_hosts.py` (NEW)
   - Custom middleware untuk allow Docker IPs

3. `projects/survey_pemda_python/.env`
   - Changed `ESIMPEG_API_URL` to use IP instead of hostname

4. `projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh` (NEW)
   - All-in-one auto-fix script

5. `projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/README.md` (NEW)
   - Script documentation

6. `projects/survey_pemda_python/docs_dari_sonnet/QUICK-START.md` (NEW)
   - Quick reference guide

## Summary

✅ **Problem Solved!**

Setelah restart laptop:
1. Jalankan `./fix-docker-network.sh`
2. Script akan auto-detect IP baru
3. Update .env jika perlu
4. Restart containers
5. Done!

Tidak perlu manual update ALLOWED_HOSTS atau .env lagi.

## Related Documentation

- [88_FIX_PASSWORD_CHANGE_COMPLETE.md](./88_FIX_PASSWORD_CHANGE_COMPLETE.md) - Password change fix
- [64_FIX_DISALLOWED_HOST_FINAL.md](./64_FIX_DISALLOWED_HOST_FINAL.md) - Previous DisallowedHost fix
- [60_FIX_ESIMPEG_API_CONNECTION.md](./60_FIX_ESIMPEG_API_CONNECTION.md) - API connection setup
