# 🔒 HTTPS Deployment Guide - ESIMPEG Python

**Status:** ✅ **FULLY CONFIGURED FOR DYNAMIC HTTP/HTTPS DETECTION**

---

## ✅ Jawaban: Ya, Project Sudah Dinamis!

**Project Anda SUDAH BERSIFAT DINAMIS untuk HTTP/HTTPS detection!**

### 🎯 Yang Sudah Dikonfigurasi:

1. ✅ **SECURE_PROXY_SSL_HEADER** - Detect HTTPS behind proxy
2. ✅ **Relative URLs** - Static/Media files adapt otomatis
3. ✅ **Django template {% static %}** - Protocol-aware
4. ✅ **Security headers** - Auto-enable di production
5. ✅ **Secure cookies** - Auto HTTPS-only di production

---

## 🔧 Konfigurasi yang Ditambahkan

### File: `esimpeg_core/settings.py`

```python
# Security Settings (for production)
if not DEBUG:
    # Force HTTPS redirect
    SECURE_SSL_REDIRECT = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # ✅ CRITICAL: Detect HTTPS behind proxy/load balancer
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Secure cookies
    SESSION_COOKIE_SECURE = True  # HTTPS only
    CSRF_COOKIE_SECURE = True     # HTTPS only
    
    # Security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    # Development: Allow HTTP
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
```

---

## 📊 Bagaimana Protocol Detection Bekerja?

### Scenario 1: Development (HTTP)
```
Browser → http://localhost:8005
         ↓
Django DEBUG=True
         ↓
SECURE_SSL_REDIRECT = False (tidak redirect)
SESSION_COOKIE_SECURE = False (allow HTTP)
Static files: http://localhost:8005/static/
         ↓
✅ Works on HTTP
```

### Scenario 2: Production Behind Nginx (HTTPS)
```
Browser → https://esimpeg.com
         ↓
Nginx (SSL Termination)
   Sets: X-Forwarded-Proto: https
         ↓
Django (SECURE_PROXY_SSL_HEADER detects)
   Knows it's HTTPS!
         ↓
Django DEBUG=False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True (HTTPS only)
Static files: https://esimpeg.com/static/
         ↓
✅ Works on HTTPS
```

### Scenario 3: Direct HTTP Access in Production
```
User tries: http://esimpeg.com
         ↓
Django sees: DEBUG=False + SECURE_SSL_REDIRECT=True
         ↓
Django redirects: http → https
         ↓
✅ User lands on: https://esimpeg.com
```

---

## 🌐 Static & Media Files - Automatic Protocol

### Current Configuration:

```python
STATIC_URL = '/static/'  # ✅ Relative path
MEDIA_URL = '/media/'    # ✅ Relative path
```

### Why This Works:

**Relative URLs automatically adapt:**

```html
<!-- In template -->
{% load static %}
<link href="{% static 'css/tailwind.css' %}" rel="stylesheet">

<!-- On HTTP -->
→ http://localhost:8005/static/css/tailwind.css

<!-- On HTTPS -->
→ https://esimpeg.com/static/css/tailwind.css
```

**Django automatically uses current protocol!** ✅

---

## 🔐 Security Features by Environment

### Development (DEBUG=True):

| Feature | Value | Why |
|---------|-------|-----|
| HTTPS Required | ❌ No | Easy local testing |
| Secure Cookies | ❌ No | Allow HTTP cookies |
| SSL Redirect | ❌ No | No forced redirect |
| Protocol | HTTP | localhost:8005 |

### Production (DEBUG=False):

| Feature | Value | Why |
|---------|-------|-----|
| HTTPS Required | ✅ Yes | Security |
| Secure Cookies | ✅ Yes | Prevent theft |
| SSL Redirect | ✅ Yes | Auto redirect HTTP→HTTPS |
| HSTS | ✅ Yes | Force HTTPS for 1 year |
| Protocol Detection | ✅ Yes | Via X-Forwarded-Proto |
| Protocol | HTTPS | esimpeg.com |

---

## 🚀 Deployment Scenarios

### Scenario A: Behind Nginx/Apache (Recommended)

**Architecture:**
```
Internet → HTTPS → Nginx (SSL) → HTTP → Django
                    ↓
              Sets: X-Forwarded-Proto: https
```

**Nginx Config:**
```nginx
server {
    listen 443 ssl;
    server_name esimpeg.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;  # ← CRITICAL!
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name esimpeg.com;
    return 301 https://$host$request_uri;
}
```

**Django will:**
- ✅ Detect HTTPS via `X-Forwarded-Proto`
- ✅ Generate HTTPS URLs for assets
- ✅ Set secure cookies
- ✅ Enable all security headers

### Scenario B: Behind Load Balancer (AWS ALB, GCP LB)

**Architecture:**
```
Internet → HTTPS → Load Balancer → HTTP → Django
                        ↓
                  Sets: X-Forwarded-Proto: https
```

**Load Balancer Config:**
- Enable SSL termination
- Forward `X-Forwarded-Proto` header
- Health check: `/health/` or `/admin/`

**Django will:**
- ✅ Automatically detect HTTPS
- ✅ Work correctly

### Scenario C: Docker with Traefik

**docker-compose.yml:**
```yaml
services:
  django:
    image: esimpeg-python
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.django.rule=Host(`esimpeg.com`)"
      - "traefik.http.routers.django.entrypoints=websecure"
      - "traefik.http.routers.django.tls.certresolver=letsencrypt"
      - "traefik.http.middlewares.django-headers.headers.customrequestheaders.X-Forwarded-Proto=https"
```

**Django will:**
- ✅ Detect HTTPS from Traefik
- ✅ Work automatically

---

## ✅ Verification Checklist

### After Deployment, Verify:

**1. HTTPS Detection:**
```python
# In Django shell
from django.contrib.sites.requests import RequestSite
request.is_secure()  # Should return True in production
```

**2. Static Files:**
```bash
# Check static URL in production
curl -I https://esimpeg.com/static/css/tailwind.css
# Should return: HTTP/2 200 (with HTTPS)
```

**3. Security Headers:**
```bash
# Check response headers
curl -I https://esimpeg.com

# Should see:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
```

**4. Cookie Security:**
```bash
# Check Set-Cookie headers
curl -v https://esimpeg.com/login/

# Should see:
# Set-Cookie: sessionid=...; secure; httponly
# Set-Cookie: csrftoken=...; secure
```

**5. HTTP → HTTPS Redirect:**
```bash
curl -I http://esimpeg.com

# Should see:
# HTTP/1.1 301 Moved Permanently
# Location: https://esimpeg.com/
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Insecure assets" warning

**Problem:** Mixed content (HTTPS page loads HTTP resources)

**Solution:**
```python
# ✅ Already fixed - using relative URLs
STATIC_URL = '/static/'  # NOT 'http://...'
MEDIA_URL = '/media/'    # NOT 'http://...'
```

### Issue 2: "Cookie not sent over HTTPS"

**Problem:** `SECURE_PROXY_SSL_HEADER` not set

**Solution:**
```python
# ✅ Already added
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Issue 3: "Redirect loop"

**Problem:** Nginx/LB not setting `X-Forwarded-Proto`

**Solution:**
```nginx
# Add to Nginx config
proxy_set_header X-Forwarded-Proto https;
```

### Issue 4: Static files 404 on HTTPS

**Problem:** Static files not collected

**Solution:**
```bash
# Collect static files
docker exec esimpeg_python_app python manage.py collectstatic --noinput

# Check STATIC_ROOT
ls -la /path/to/staticfiles/
```

---

## 🎯 Environment Variables for Production

**Required .env settings:**

```bash
# Production mode
DEBUG=False

# Security
SECRET_KEY=<strong-random-key-min-50-chars>

# Allowed hosts
ALLOWED_HOSTS=esimpeg.com,www.esimpeg.com,<server-ip>

# Database (production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=esimpeg_prod
DB_USER=esimpeg_user
DB_PASSWORD=<strong-password>
DB_HOST=db
DB_PORT=5432

# Redis (production)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<app-password>
```

---

## 📋 Pre-Deployment Checklist

**Security:**
- [x] SECURE_PROXY_SSL_HEADER configured ✅
- [x] SECURE_SSL_REDIRECT enabled (production) ✅
- [x] HSTS configured ✅
- [x] Secure cookies enabled (production) ✅
- [x] Security headers configured ✅
- [ ] SECRET_KEY changed (generate new for production)
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured for domain

**Static Files:**
- [x] STATIC_URL relative path ✅
- [x] MEDIA_URL relative path ✅
- [x] {% static %} tags used in templates ✅
- [ ] collectstatic ran
- [ ] Nginx/server configured to serve static files

**SSL Certificate:**
- [ ] SSL certificate installed (Let's Encrypt, etc)
- [ ] Certificate valid and not expired
- [ ] Auto-renewal configured (certbot, etc)

**Nginx/Proxy:**
- [ ] X-Forwarded-Proto header set
- [ ] HTTP → HTTPS redirect configured
- [ ] Static/media file serving configured
- [ ] Gzip compression enabled
- [ ] Security headers added

---

## ✅ Final Answer

### **YA, PROJECT SUDAH 100% DINAMIS!** 🎉

**Protocol detection akan otomatis:**

| Akses Via | Protocol Detected | Static Files | Cookies | Redirect |
|-----------|-------------------|--------------|---------|----------|
| localhost:8005 (dev) | HTTP | http://... | HTTP OK | No |
| esimpeg.com (prod) | HTTPS | https://... | HTTPS only | Yes |
| http://esimpeg.com | HTTP → HTTPS | https://... | HTTPS only | Auto |

**Tidak perlu hardcode protocol apapun - semua automatic! ✅**

---

## 📞 Testing Commands

### Local Development (HTTP):
```bash
# Start server
docker-compose up

# Access
http://localhost:8005/

# Expected:
✅ Works on HTTP
✅ No HTTPS redirect
✅ No secure cookie requirement
```

### Production Staging (HTTPS):
```bash
# Set environment
DEBUG=False
ALLOWED_HOSTS=staging.esimpeg.com

# Start with SSL proxy
# Access via Nginx/Traefik with SSL

# Expected:
✅ Works on HTTPS
✅ HTTP redirects to HTTPS
✅ Secure cookies only
✅ Security headers present
```

---

## 🚀 Ready for Production!

**Status:** ✅ **CONFIGURED AND READY**

Project Anda sudah siap untuk:
- ✅ HTTP (development)
- ✅ HTTPS (production)
- ✅ Behind proxy/load balancer
- ✅ Dynamic protocol detection
- ✅ Secure cookies in production
- ✅ All security headers

**Tinggal deploy dan configure SSL certificate di Nginx/load balancer!**

---

**Last Updated:** November 11, 2025  
**Status:** 🟢 PRODUCTION READY FOR HTTP/HTTPS
