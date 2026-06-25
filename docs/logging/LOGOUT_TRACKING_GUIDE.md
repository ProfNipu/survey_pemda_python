# Logout Tracking - Complete Guide

**Implementation Date:** November 3, 2025  
**Status:** ✅ IMPLEMENTED & WORKING

---

## 🎯 Overview

**Logout tracking** sekarang mencatat **SEMUA jenis logout**:
- ✅ Manual logout via web
- ✅ Manual logout via API (v4.0 & v5.0)
- ✅ **Auto-logout karena session expired** ⭐

Semua tercatat di **ms_log_data** dengan detail lengkap!

---

## 📊 Jenis Logout yang Tracked

| Jenis | Via | Description | Auto/Manual |
|-------|-----|-------------|-------------|
| **Web Logout** | web | Manual logout via aplikasi web | Manual |
| **API v4.0 Logout** | api_v4 | Manual logout via API v4.0 | Manual |
| **API v5.0 Logout** | api_v5 | Manual logout via API v5.0 | Manual |
| **Session Expired** | web | Auto-logout: Session expired after X minutes inactive | **Auto** ⭐ |

---

## 🔍 Auto-Logout Detection

### **How It Works:**

```python
# SessionInactivityMiddleware
SESSION_INACTIVITY_TIMEOUT = 1800  # 30 minutes (default)

# Every request:
1. Check last_activity time
2. If inactive > 30 minutes:
   ├── Log logout to ms_log_data (BEFORE logout)
   ├── Set description: "Auto-logout: Session expired after 32 minutes inactive"
   └── Then logout user
3. Update last_activity time
```

### **Log Entry Example:**

```json
{
  "action": "logout",
  "table_name": "users",
  "username": "admin",
  "via": "web",
  "description": "Auto-logout: Session expired after 32 minutes inactive",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "old_data": {
    "logout_time": "2025-11-03T11:45:00"
  }
}
```

---

## 📝 Implementation Details

### **1. Web Manual Logout**

**File:** `apps/accounts/views.py`

```python
def logout_view(request):
    """Logout user and log to ms_log_data"""
    if request.user.is_authenticated:
        # Log BEFORE logout
        MsLogData.log_logout(
            user=request.user,
            request=request,
            via='web',
            description='Manual logout via aplikasi web'
        )
        
        auth_logout(request)
```

**URL:** `/accounts/logout/`

---

### **2. Auto-Logout (Session Expired)**

**File:** `esimpeg_core/middleware/session.py`

```python
class SessionInactivityMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            inactive_time = current_time - last_activity
            
            if inactive_time > self.timeout:
                # Log auto-logout
                MsLogData.log_logout(
                    user=request.user,
                    request=request,
                    via='web',
                    description=f'Auto-logout: Session expired after {int(inactive_time/60)} minutes inactive'
                )
                
                logout(request)
```

**Triggered:** Automatically when session timeout

---

### **3. API v4.0 Manual Logout**

**File:** `esimpeg_core/views.py`

```python
@csrf_exempt
def api_logout_v4(request):
    """Logout via API v4.0"""
    # Verify token & get user
    user = get_user_from_token(request)
    
    # Log logout
    MsLogData.log_logout(
        user=user,
        request=request,
        via='api_v4',
        description='Manual logout via API v4.0'
    )
    
    # Blacklist token
    TokenBlacklist.blacklist_token(token)
```

**URL:** `/apisimpeg/4.0/logout`  
**Method:** POST  
**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "data": {
    "message": "Logout successful",
    "username": "user@example.com"
  },
  "success_message": "Logout berhasil",
  "errors": [],
  "error_message": null
}
```

---

### **4. API v5.0 Manual Logout**

**File:** `esimpeg_core/views.py`

```python
@csrf_exempt
def api_logout_v5(request):
    """Logout via API v5.0"""
    # Verify token & get user
    user = get_user_from_token(request)
    
    # Log logout
    MsLogData.log_logout(
        user=user,
        request=request,
        via='api_v5',
        description='Manual logout via API v5.0'
    )
    
    # Blacklist token
    TokenBlacklist.blacklist_token(token)
```

**URL:** `/apisimpeg/5.0/auth/logout`  
**Method:** POST  
**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "status": "success",
  "message": "Logout successful",
  "data": {
    "username": "user@example.com",
    "logout_at": "2025-11-03T11:45:00"
  },
  "version": "5.0"
}
```

---

## 🔍 Query Examples

### **All Logout Activities:**
```sql
SELECT 
    username,
    via,
    description,
    ip_address,
    created_at
FROM ms_log_data
WHERE action = 'logout'
ORDER BY created_at DESC;
```

### **Auto-Logout Only (Session Expired):**
```sql
SELECT 
    username,
    description,
    ip_address,
    created_at
FROM ms_log_data
WHERE action = 'logout'
AND description LIKE '%Auto-logout%'
ORDER BY created_at DESC;
```

### **Manual Logout Only:**
```sql
SELECT 
    username,
    via,
    description,
    created_at
FROM ms_log_data
WHERE action = 'logout'
AND description LIKE '%Manual%'
ORDER BY created_at DESC;
```

### **Logout by Via (Web vs API):**
```sql
SELECT 
    via,
    COUNT(*) as logout_count,
    COUNT(CASE WHEN description LIKE '%Auto%' THEN 1 END) as auto_logout,
    COUNT(CASE WHEN description LIKE '%Manual%' THEN 1 END) as manual_logout
FROM ms_log_data
WHERE action = 'logout'
GROUP BY via;
```

---

## 📊 Python Queries

### **Get User's Logout History:**
```python
from esimpeg_core.models import MsLogData

# All logout for user
logouts = MsLogData.objects.filter(
    username='admin',
    action='logout'
).order_by('-created_at')

for logout in logouts:
    print(f"{logout.created_at}: {logout.description}")
```

### **Auto-Logout Statistics:**
```python
from django.db.models import Count, Q

stats = MsLogData.objects.filter(
    action='logout'
).aggregate(
    total=Count('id'),
    auto=Count('id', filter=Q(description__contains='Auto-logout')),
    manual=Count('id', filter=Q(description__contains='Manual'))
)

print(f"Total: {stats['total']}")
print(f"Auto-logout: {stats['auto']}")
print(f"Manual: {stats['manual']}")
```

---

## 🧪 Testing

### **Test 1: Manual Web Logout**
```bash
# Login first (via browser)
# Then click logout button

# Check log:
docker compose exec -T esimpeg-python python manage.py shell -c \
  "from esimpeg_core.models import MsLogData; \
   log = MsLogData.objects.filter(action='logout').latest('created_at'); \
   print(f'Via: {log.via}'); \
   print(f'Description: {log.description}')"

# Output:
# Via: web
# Description: Manual logout via aplikasi web
```

### **Test 2: Auto-Logout (Session Expired)**
```bash
# Login and wait 30+ minutes (or set shorter timeout for testing)
# Session will expire automatically

# Check log:
docker compose exec -T esimpeg-python python manage.py shell -c \
  "from esimpeg_core.models import MsLogData; \
   log = MsLogData.objects.filter(action='logout', description__contains='Auto-logout').latest('created_at'); \
   print(f'Description: {log.description}')"

# Output:
# Description: Auto-logout: Session expired after 32 minutes inactive
```

### **Test 3: API Logout**
```bash
# Get token first
TOKEN=$(curl -s -X POST http://localhost:8005/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.data.access_token')

# Logout
curl -X POST http://localhost:8005/apisimpeg/5.0/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# Check log
docker compose exec -T esimpeg-python python manage.py shell -c \
  "from esimpeg_core.models import MsLogData; \
   log = MsLogData.objects.filter(action='logout').latest('created_at'); \
   print(f'Via: {log.via}'); \
   print(f'Description: {log.description}')"

# Output:
# Via: api_v5
# Description: Manual logout via API v5.0
```

---

## 📈 Statistics Dashboard

### **Logout Summary (Last 7 Days):**
```python
from esimpeg_core.models import MsLogData
from django.utils import timezone
from datetime import timedelta

since = timezone.now() - timedelta(days=7)

logouts = MsLogData.objects.filter(
    action='logout',
    created_at__gte=since
)

print(f"Total logouts: {logouts.count()}")
print(f"Web: {logouts.filter(via='web').count()}")
print(f"API v4: {logouts.filter(via='api_v4').count()}")
print(f"API v5: {logouts.filter(via='api_v5').count()}")
print(f"Auto-logout: {logouts.filter(description__contains='Auto-logout').count()}")
print(f"Manual: {logouts.filter(description__contains='Manual').count()}")
```

---

## ⚙️ Configuration

### **Change Session Timeout:**

**File:** `esimpeg_core/settings.py`

```python
# Default: 30 minutes (1800 seconds)
SESSION_INACTIVITY_TIMEOUT = 1800

# Change to 1 hour:
SESSION_INACTIVITY_TIMEOUT = 3600

# Change to 15 minutes:
SESSION_INACTIVITY_TIMEOUT = 900
```

---

## 🔐 Security Benefits

| Feature | Benefit |
|---------|---------|
| **Track auto-logout** | Detect unusual session timeouts |
| **Track manual logout** | Know when users explicitly logout |
| **IP & user agent** | Detect suspicious logout patterns |
| **Timestamp** | Timeline analysis |
| **Via tracking** | Distinguish web vs API logout |

---

## 📊 Sample Data

### **Auto-Logout:**
```json
{
  "id": 123,
  "action": "logout",
  "table_name": "users",
  "record_id": 1,
  "username": "admin",
  "via": "web",
  "description": "Auto-logout: Session expired after 32 minutes inactive",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (X11; Linux x86_64)...",
  "created_at": "2025-11-03 11:45:00"
}
```

### **Manual Logout (Web):**
```json
{
  "id": 124,
  "action": "logout",
  "table_name": "users",
  "record_id": 1,
  "username": "admin",
  "via": "web",
  "description": "Manual logout via aplikasi web",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (X11; Linux x86_64)...",
  "created_at": "2025-11-03 12:00:00"
}
```

### **Manual Logout (API):**
```json
{
  "id": 125,
  "action": "logout",
  "table_name": "users",
  "record_id": 1,
  "username": "admin",
  "via": "api_v5",
  "description": "Manual logout via API v5.0",
  "ip_address": "172.21.0.1",
  "user_agent": "curl/8.16.0",
  "created_at": "2025-11-03 12:15:00"
}
```

---

## ✅ Implementation Checklist

- [x] Auto-logout tracking (session expired)
- [x] Web manual logout tracking
- [x] API v4.0 logout endpoint
- [x] API v5.0 logout endpoint
- [x] IP address tracking
- [x] User agent tracking
- [x] Via tracking (web/api_v4/api_v5)
- [x] Custom descriptions
- [x] URL routes configured
- [x] Tested and working

---

## 📞 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/accounts/logout/` | Web logout |
| POST | `/apisimpeg/4.0/logout` | API v4.0 logout |
| POST | `/apisimpeg/5.0/auth/logout` | API v5.0 logout |

---

**Status: ✅ PRODUCTION READY**  
**Last Updated: November 3, 2025, 11:40 AM UTC+7**
