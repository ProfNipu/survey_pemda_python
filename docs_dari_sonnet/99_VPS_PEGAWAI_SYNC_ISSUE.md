# VPS Pegawai Sync Issue - ESIMPEG API Error 500

## Status: ⚠️ BLOCKED - ESIMPEG API Error

**Last Updated**: 8 April 2026, 08:00 WIB

## Problem Summary

Survey Pemda di VPS tidak bisa sync pegawai karena ESIMPEG API endpoint `/apisimpeg/5.0/pegawai/data/list` return HTTP 500 error.

### Error Message in UI

```
Gagal!
Gagal mengambil data dari API ESIMPEG
```

### Error in ESIMPEG Logs

```
django.urls.exceptions.NoReverseMatch: Reverse for 'login' not found. 'login' is not a valid view function or pattern name.
```

## Root Cause Analysis

### Issue 1: Django URL Reverse Error

ESIMPEG Python mengalami error saat render response karena Django tidak bisa reverse URL 'login'. Ini terjadi pada endpoint `/apisimpeg/5.0/pegawai/data/list`.

### Issue 2: Endpoint Works for Login, Fails for Data

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/apisimpeg/5.0/auth/login` | ✅ Works | Returns JWT tokens |
| `/apisimpeg/5.0/pegawai/data/list` | ❌ Error 500 | Django URL reverse error |
| `/apisimpeg/5.0/pegawai/data/nip/{nip}` | ❓ Unknown | Not tested yet |

## Testing Results

### Test 1: Login Endpoint (Public IP)

```bash
curl -X POST http://103.143.152.139:8005/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}'
```

**Result**: ✅ SUCCESS
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGc...",
    "user": {...}
  }
}
```

### Test 2: Pegawai List Endpoint (Public IP)

```bash
TOKEN="eyJhbGc..."
curl "http://103.143.152.139:8005/apisimpeg/5.0/pegawai/data/list?page=1&per_page=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Result**: ❌ ERROR 500
```html
<html>
  <head>
    <title>Internal Server Error</title>
  </head>
  <body>
    <h1><p>Internal Server Error</p></h1>
  </body>
</html>
```

### Test 3: From Survey Pemda Container (Docker Network)

```bash
docker exec survey-pemda-python python manage.py shell -c "
from apps.accounts.services import EsimpegAPIService

api_service = EsimpegAPIService()
login_result = api_service.login('Prakom@admin2025.com', 'Prakom@2025')
token = login_result['access_token']

pegawai_data = api_service.get_pegawai_list(token, page=1, per_page=5)
print('Result:', pegawai_data)
"
```

**Result**: ❌ ERROR - Returns None (API returned 500)

## Impact

### What Works
- ✅ Login via ESIMPEG API
- ✅ Token management
- ✅ Authentication backend
- ✅ Docker network connection

### What Doesn't Work
- ❌ Pegawai sync from ESIMPEG
- ❌ Get pegawai list
- ❌ Any endpoint that returns pegawai data

## Possible Causes

### 1. Missing URL Pattern

ESIMPEG Python might be missing URL pattern for 'login' in urls.py, causing Django to fail when trying to reverse the URL in templates or views.

### 2. Template Rendering Issue

The pegawai list endpoint might be trying to render a template that references `{% url 'login' %}`, which doesn't exist.

### 3. Middleware or Decorator Issue

Some middleware or decorator might be trying to redirect to login page, causing the URL reverse error.

## Recommended Solutions

### Solution 1: Check ESIMPEG URLs Configuration

Check if 'login' URL pattern exists in ESIMPEG Python:

```bash
ssh root@172.16.30.139 "docker exec esimpeg-python python manage.py show_urls | grep login"
```

### Solution 2: Check View Implementation

The pegawai list view might be using `@login_required` decorator or similar that tries to redirect to 'login' URL.

**File to check**: `projects/ESIMPEG-Python/apps/api/views.py` or similar

Look for:
```python
@login_required  # This might cause redirect to 'login' URL
def pegawai_list_api(request):
    ...
```

### Solution 3: Add Missing URL Pattern

If 'login' URL is missing, add it to urls.py:

```python
# In ESIMPEG-Python urls.py
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    ...
    path('login/', auth_views.LoginView.as_view(), name='login'),
    ...
]
```

### Solution 4: Use API-Only Response (No Template)

Ensure pegawai list endpoint returns JSON response without rendering templates:

```python
from django.http import JsonResponse

def pegawai_list_api(request):
    # Don't use render() or render_to_response()
    # Use JsonResponse directly
    data = {...}
    return JsonResponse(data)
```

## Workaround (Temporary)

### Option 1: Use ESIMPEG Database Directly

Instead of calling ESIMPEG API, Survey Pemda can read directly from ESIMPEG database:

**Pros**:
- No API dependency
- Faster data access
- No token management needed

**Cons**:
- Tight coupling with ESIMPEG database
- Need to handle database schema changes
- No API abstraction layer

### Option 2: Fix ESIMPEG Python First

Fix the URL reverse error in ESIMPEG Python, then retry sync.

**Steps**:
1. SSH to VPS
2. Check ESIMPEG Python logs for exact error
3. Fix URL configuration or view implementation
4. Restart ESIMPEG container
5. Test pegawai list endpoint
6. Retry sync from Survey Pemda

## Files to Investigate (ESIMPEG Python)

1. **URLs Configuration**:
   - `projects/ESIMPEG-Python/esimpeg_core/urls.py`
   - `projects/ESIMPEG-Python/apps/api/urls.py`

2. **Views**:
   - `projects/ESIMPEG-Python/apps/api/views.py`
   - Look for pegawai list view

3. **Middleware**:
   - `projects/ESIMPEG-Python/esimpeg_core/settings.py`
   - Check MIDDLEWARE configuration

4. **Templates** (if used):
   - Any template that might reference `{% url 'login' %}`

## Survey Pemda Code (Already Fixed)

Survey Pemda code is correct and includes Host header fix:

**File**: `projects/survey_pemda_python/apps/accounts/services.py`

```python
class EsimpegAPIService:
    def __init__(self):
        self.base_url = getattr(settings, 'ESIMPEG_API_URL', 'http://localhost:8000')
        self.host_header = getattr(settings, 'ESIMPEG_API_HOST_HEADER', None)
    
    def get_pegawai_list(self, token, page=1, per_page=50, search=None, id_opd=None):
        url = f"{self.base_url}/apisimpeg/5.0/pegawai/data/list"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        if self.host_header:
            headers['Host'] = self.host_header  # ✅ Host header included
        
        response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        # ... handle response
```

## Next Steps

1. **Investigate ESIMPEG Python**:
   - Check URL configuration
   - Check view implementation
   - Check middleware

2. **Fix URL Reverse Error**:
   - Add missing 'login' URL pattern, OR
   - Remove template rendering from API endpoint, OR
   - Fix decorator/middleware that causes redirect

3. **Test Fix**:
   - Test pegawai list endpoint from public IP
   - Test from Survey Pemda container
   - Verify sync works end-to-end

4. **Document Fix**:
   - Update this document with solution
   - Add to ESIMPEG Python documentation

## Related Documentation

- `98_VPS_LOGIN_VIA_API_SUCCESS.md` - Login via API (works)
- `97_VPS_DOCKER_NETWORK_FIX.md` - Docker network fix
- `96_SIASN_IP_WHITELIST_ISSUE.md` - SIASN IP whitelist
- `94_VPS_DEPLOYMENT_SUMMARY.md` - VPS deployment

## Summary

✅ **Survey Pemda code is correct**
- Login via API works
- Host header fix applied
- Token management works

❌ **ESIMPEG Python has issue**
- Pegawai list endpoint returns 500 error
- Django URL reverse error for 'login'
- Needs investigation and fix in ESIMPEG Python

⏳ **Waiting for ESIMPEG fix**
- Survey Pemda cannot sync pegawai until ESIMPEG API is fixed
- Workaround: Use database direct access (if needed urgently)

---

**Action Required**: Fix ESIMPEG Python `/apisimpeg/5.0/pegawai/data/list` endpoint to return JSON response without Django URL reverse error.
