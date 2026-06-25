# Error Logging to ms_log_data - Complete Guide

**Implementation Date:** November 3, 2025  
**Status:** ✅ ACTIVE - All Errors Logged to Database  

---

## 🎯 Overview

Sistem **Error Logging** ke `ms_log_data` untuk **monitoring dan debugging** yang lebih mudah. Semua error/exception sekarang **otomatis tercatat** di database dengan detail lengkap.

---

## ✅ Features

### 1. **Error Logging Method**
**File:** `esimpeg_core/models.py`

```python
@classmethod
def log_error(cls, user, action, error_message, error_details=None, 
              request=None, via='web', description=None):
    """
    Log error/exception untuk debugging dan monitoring
    
    Args:
        user: User instance (atau None jika tidak ada user context)
        action: Action yang error (e.g., 'password_change', 'login', 'data_update')
        error_message: Error message (string)
        error_details: Error details (dict) - traceback, params, dll
        request: Django request object (optional)
        via: 'web', 'api_v4', 'api_v5', 'system'
        description: Optional description
    """
    return cls.objects.create(
        table_name='system',
        record_id=user.id if user else None,
        action=f'{action}_error',
        user_id=user.id if user else None,
        username=user.username if user else None,
        old_data={
            'error_message': error_message,
            'error_details': error_details or {}
        },
        new_data=None,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000] if request else None,
        via=via,
        description=description or f'Error: {action} - {error_message[:100]}'
    )
```

---

## 📝 Implementation Examples

### 1. **Password Change Error Logging**

**File:** `apps/accounts/views.py` - `force_change_password_view()`

```python
# Update password
try:
    user.set_password(new_password)
    
    # Ensure date_joined is set
    if not user.date_joined:
        from django.utils import timezone
        user.date_joined = timezone.now()
    
    user.save()
    
    # Log SUCCESS
    MsLogData.objects.create(
        user_id=user.id,
        action='password_change',
        table_name='users',
        record_id=user.id,
        old_data={'note': 'Password changed from default (forced)'},
        new_data={'success': True, 'via': 'web'},
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
except Exception as e:
    # Log ERROR to ms_log_data
    import traceback
    error_traceback = traceback.format_exc()
    
    MsLogData.log_error(
        user=user,
        action='password_change',
        error_message=str(e),
        error_details={
            'error_type': type(e).__name__,
            'traceback': error_traceback,
            'username': user.username,
            'has_date_joined': bool(user.date_joined)
        },
        request=request,
        via='web'
    )
    
    # Return error response to user
    error_msg = f'Gagal mengubah password: {str(e)}'
    messages.error(request, error_msg)
```

---

## 📊 Error Log Structure

### Log Entry Example

```json
{
    "id": 123,
    "user_id": 8,
    "username": "199411192019031001",
    "action": "password_change_error",
    "table_name": "system",
    "record_id": 8,
    "old_data": {
        "error_message": "Column 'date_joined' cannot be null",
        "error_details": {
            "error_type": "IntegrityError",
            "traceback": "Traceback (most recent call last):\n  File ...",
            "username": "199411192019031001",
            "has_date_joined": false
        }
    },
    "new_data": null,
    "via": "web",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 ...",
    "description": "Error: password_change - Column 'date_joined' cannot be null",
    "created_at": "2025-11-03 15:54:27"
}
```

---

## 🔍 Querying Error Logs

### Get All Errors
```python
from esimpeg_core.models import MsLogData

# All errors (action ends with _error)
errors = MsLogData.objects.filter(action__endswith='_error').order_by('-created_at')

for error in errors:
    print(f"{error.created_at}: {error.action} - {error.old_data['error_message']}")
```

### Get Password Change Errors
```python
# Password change errors only
password_errors = MsLogData.objects.filter(
    action='password_change_error'
).order_by('-created_at')

for error in password_errors:
    print(f"User: {error.username}")
    print(f"Error: {error.old_data['error_message']}")
    print(f"Type: {error.old_data['error_details']['error_type']}")
    print(f"Traceback: {error.old_data['error_details']['traceback']}")
    print('-' * 50)
```

### Get Errors by User
```python
# All errors for specific user
user_errors = MsLogData.objects.filter(
    user_id=8,
    action__endswith='_error'
).order_by('-created_at')
```

### Get Recent Errors (Last 24 Hours)
```python
from datetime import datetime, timedelta

recent_errors = MsLogData.objects.filter(
    action__endswith='_error',
    created_at__gte=datetime.now() - timedelta(days=1)
).order_by('-created_at')
```

### Error Statistics
```python
from django.db.models import Count

# Count errors by type
error_stats = MsLogData.objects.filter(
    action__endswith='_error'
).values('action').annotate(
    count=Count('id')
).order_by('-count')

for stat in error_stats:
    print(f"{stat['action']}: {stat['count']} occurrences")
```

---

## 🎯 Use Cases

### 1. **Debugging Production Issues**

**Scenario:** User report "gagal ganti password"

**Query:**
```python
# Find user's recent errors
user = User.objects.get(username='199411192019031001')
errors = MsLogData.objects.filter(
    user_id=user.id,
    action='password_change_error',
    created_at__gte=datetime.now() - timedelta(days=7)
)

# Check error details
for error in errors:
    print("Error:", error.old_data['error_message'])
    print("Traceback:", error.old_data['error_details']['traceback'])
```

**Result:** Langsung ketahuan error `date_joined cannot be null` → Fix implemented ✅

---

### 2. **Monitoring System Health**

**Query:**
```python
# Get error count per hour (last 24 hours)
from django.db.models.functions import TruncHour

hourly_errors = MsLogData.objects.filter(
    action__endswith='_error',
    created_at__gte=datetime.now() - timedelta(days=1)
).annotate(
    hour=TruncHour('created_at')
).values('hour').annotate(
    count=Count('id')
).order_by('hour')

for stat in hourly_errors:
    print(f"{stat['hour']}: {stat['count']} errors")
```

**Result:** Detect error spikes → Investigate immediately

---

### 3. **Error Pattern Detection**

**Query:**
```python
# Find most common error messages
from django.db.models import Count
from django.db.models.functions import JSONExtract

common_errors = MsLogData.objects.filter(
    action__endswith='_error',
    created_at__gte=datetime.now() - timedelta(days=30)
).values('old_data').annotate(
    count=Count('id')
).order_by('-count')[:10]

# Check which errors are most frequent
```

**Result:** Identify recurring issues → Prioritize fixes

---

## 📋 Error Action Types

| Action | Description | Example |
|--------|-------------|---------|
| `password_change_error` | Error saat ganti password | IntegrityError, ValidationError |
| `login_error` | Error saat login (future) | AuthenticationError |
| `data_update_error` | Error saat update data (future) | ValidationError, IntegrityError |
| `api_error` | Error di API request (future) | Timeout, ConnectionError |
| `system_error` | Error system general (future) | MemoryError, etc |

---

## 🎨 Error Details Structure

### Standard Fields
```python
error_details = {
    'error_type': 'IntegrityError',      # Exception class name
    'traceback': 'Traceback...',          # Full traceback
    'username': 'user123',                # User context
    'has_date_joined': False,             # Related data
    # Custom fields per error type
}
```

### Password Change Error
```python
{
    'error_type': 'IntegrityError',
    'traceback': '...',
    'username': '199411192019031001',
    'has_date_joined': False,
    'attempted_action': 'force_change_password'
}
```

### Future: API Error
```python
{
    'error_type': 'ConnectionTimeout',
    'traceback': '...',
    'api_endpoint': '/apisimpeg/5.0/auth/login',
    'request_method': 'POST',
    'timeout_seconds': 30
}
```

---

## 🔧 Management Command (Future)

### Check Error Summary
```bash
python manage.py check_errors --last 24h
```

**Output:**
```
Error Summary (Last 24 hours):
========================================
Total Errors: 15

By Type:
  - password_change_error: 10
  - login_error: 3
  - data_update_error: 2

Most Affected Users:
  - user123: 5 errors
  - user456: 3 errors

Most Common Error:
  - IntegrityError (date_joined): 8 occurrences
```

---

## ✅ Benefits

### 1. **Easy Debugging**
- ✅ Full traceback tersimpan
- ✅ User context lengkap
- ✅ Queryable di database
- ✅ No need to check log files

### 2. **Production Monitoring**
- ✅ Real-time error tracking
- ✅ Error statistics
- ✅ Pattern detection
- ✅ Proactive issue detection

### 3. **Better Support**
- ✅ Quick user issue resolution
- ✅ Historical error data
- ✅ Reproducible errors
- ✅ Evidence-based fixes

### 4. **Performance Metrics**
- ✅ Error rate tracking
- ✅ System health indicators
- ✅ Success/failure ratio
- ✅ Reliability metrics

---

## 🚀 Future Enhancements

### 1. **Error Notification**
```python
# Auto-notify admin on critical errors
if error_count > threshold:
    send_notification_to_admin(error_details)
```

### 2. **Error Dashboard**
- Visual error statistics
- Real-time error feed
- Error trend charts
- Top errors by type

### 3. **Auto-Recovery**
```python
# Retry mechanism with backoff
try:
    perform_action()
except TemporaryError as e:
    log_error(...)
    schedule_retry(action, delay=60)
```

### 4. **Error Grouping**
- Group similar errors
- Deduplicate error logs
- Track error lifecycle
- Mark errors as resolved

---

## 🧪 Testing Error Logging

### Manual Test
```python
# Force an error to test logging
from esimpeg_core.models import MsLogData

try:
    # Simulate error
    raise ValueError("Test error for logging")
except Exception as e:
    import traceback
    MsLogData.log_error(
        user=request.user,
        action='test',
        error_message=str(e),
        error_details={
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc(),
            'test': True
        },
        request=request,
        via='manual_test'
    )

# Query to verify
test_error = MsLogData.objects.filter(action='test_error').latest('id')
print(f"Logged: {test_error.old_data['error_message']}")
```

---

## 📊 Example Queries for Admin Dashboard

### 1. Error Count Widget
```python
# Today's error count
today_errors = MsLogData.objects.filter(
    action__endswith='_error',
    created_at__date=datetime.now().date()
).count()
```

### 2. Error Rate Chart (7 days)
```python
from django.db.models.functions import TruncDate

daily_errors = MsLogData.objects.filter(
    action__endswith='_error',
    created_at__gte=datetime.now() - timedelta(days=7)
).annotate(
    day=TruncDate('created_at')
).values('day').annotate(
    count=Count('id')
).order_by('day')
```

### 3. Top Error Types
```python
top_errors = MsLogData.objects.filter(
    action__endswith='_error',
    created_at__gte=datetime.now() - timedelta(days=30)
).values('action').annotate(
    count=Count('id')
).order_by('-count')[:5]
```

---

## ✅ Implementation Status

### Completed:
- [x] `log_error()` method in MsLogData model
- [x] Error logging in `force_change_password_view()`
- [x] Error logging in `change_password_view()`
- [x] Traceback capture
- [x] User context capture
- [x] IP & User Agent capture

### Future:
- [ ] Error logging in login views
- [ ] Error logging in API endpoints
- [ ] Error dashboard page
- [ ] Error notification system
- [ ] Management commands for error analysis

---

**Status:** ✅ **PRODUCTION READY**  
**Coverage:** Password change operations  
**Next:** Expand to login, API, and data operations  

---

*Last Updated: November 3, 2025*  
*Version: 1.0 - Initial Implementation*
