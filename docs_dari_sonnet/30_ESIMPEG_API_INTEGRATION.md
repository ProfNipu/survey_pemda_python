# ESIMPEG API Integration - Login & Authentication

**Version**: 1.0.0  
**Date**: 2026-03-31  
**Status**: ✅ IMPLEMENTED

---

## Overview

Integrasi Survey Pemda dengan ESIMPEG API v5.0 untuk authentication dan data sync.

**Flow**:
```
User login → Check local database → If not found, try ESIMPEG API
  ↓
ESIMPEG API login successful → Create user in local database
  ↓
Set default password (Pegawai@Pessel) → Force change password
  ↓
User change password → Can access dashboard
```

---

## What's Implemented

### 1. ESIMPEG API Service (`apps/accounts/services.py`)

**Class**: `EsimpegAPIService`

**Methods**:
- `login(username, password)` - Login to ESIMPEG API
- `verify_token(token)` - Verify JWT token
- `refresh_token(refresh_token)` - Refresh access token
- `get_pegawai_list(token, ...)` - Get pegawai list
- `get_pegawai_by_nip(token, nip)` - Get pegawai detail
- `change_password(token, old, new)` - Change password via API
- `is_api_available()` - Check API availability

### 2. Login Flow Update (`core/views.py`)

**New Logic**:
```python
if user_not_exists_in_local_db:
    # Try login via ESIMPEG API
    api_response = esimpeg_api.login(username, password)
    
    if api_response:
        # Determine if password is default or custom
        is_default_password = (password == 'Pegawai@Pessel')
        
        # Create user in local database
        user = User.objects.create_user(
            username=api_user['username'],
            email=api_user['email'],
            name=api_user['name'],
            password=password,  # Use ACTUAL password from login
            id_pegawai=api_user['id_pegawai']
        )
        
        # Authenticate with actual password
        user = authenticate(username, password)
        
        # Continue to login flow
        # If password == 'Pegawai@Pessel' → Force change password
        # If password != 'Pegawai@Pessel' → Direct to dashboard
```

**CRITICAL CHANGE**: Password disimpan sesuai yang digunakan login, BUKAN selalu default!

- Password = `Pegawai@Pessel` → Force change password ⚠️
- Password = `CustomPass123` → Direct to dashboard ✅

### 3. Settings Configuration (`core/settings.py`)

**New Settings**:
```python
ESIMPEG_API_URL = config('ESIMPEG_API_URL', default='http://localhost:8000')
ESIMPEG_API_TIMEOUT = config('ESIMPEG_API_TIMEOUT', default=10, cast=int)
ESIMPEG_WEBHOOK_SECRET = config('ESIMPEG_WEBHOOK_SECRET', default='')
```

### 4. Environment Variables (`.env.example`)

**New Variables**:
```env
ESIMPEG_API_URL=http://localhost:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=
```

---

## Login Flow Diagram

### Scenario 1: User Exists in Local Database

```
User login (username + password)
  ↓
Check local database → User found
  ↓
Authenticate with local password
  ↓
✅ Login successful → Dashboard
```

### Scenario 2A: User NOT Exists + Default Password

```
User login (username + 'Pegawai@Pessel')
  ↓
Check local database → User NOT found
  ↓
Try ESIMPEG API login
  ↓
┌─────────────────────────────────────┐
│ ESIMPEG API: POST /apisimpeg/5.0/auth/login │
│ Body: {username, password: 'Pegawai@Pessel'} │
└─────────────────────────────────────┘
  ↓
API Response: {access_token, user: {...}}
  ↓
Create user in local database:
  - username: from API
  - email: from API
  - name: from API
  - password: 'Pegawai@Pessel' (ACTUAL password used)
  - id_pegawai: from API
  ↓
Authenticate with 'Pegawai@Pessel'
  ↓
✅ Login successful
  ↓
⚠️ Force change password (middleware detects default password)
  ↓
Redirect to /accounts/force-change-password/
  ↓
User change password
  ↓
✅ Can access dashboard
```

### Scenario 2B: User NOT Exists + Custom Password (NEW!)

```
User login (username + 'CustomPassword123')
  ↓
Check local database → User NOT found
  ↓
Try ESIMPEG API login
  ↓
┌─────────────────────────────────────┐
│ ESIMPEG API: POST /apisimpeg/5.0/auth/login │
│ Body: {username, password: 'CustomPassword123'} │
└─────────────────────────────────────┘
  ↓
API Response: {access_token, user: {...}}
  ↓
Create user in local database:
  - username: from API
  - email: from API
  - name: from API
  - password: 'CustomPassword123' (ACTUAL password used)
  - id_pegawai: from API
  ↓
Authenticate with 'CustomPassword123'
  ↓
✅ Login successful
  ↓
✅ NO force change password (not default)
  ↓
✅ Direct to dashboard
```

### Scenario 3: ESIMPEG API Down

```
User login (username + password)
  ↓
Check local database → User NOT found
  ↓
Try ESIMPEG API login
  ↓
❌ API Connection Error (timeout/down)
  ↓
Show error: "Sistem ESIMPEG sedang tidak tersedia"
  ↓
User cannot login (must wait for API)
```

---

## Force Change Password Flow

### Middleware: `ForceChangePasswordMiddleware`

**Location**: `core/middleware/session.py`

**Logic**:
```python
if user.check_password('Pegawai@Pessel'):
    # User still using default password
    # Redirect to force change password page
    return redirect('accounts:force_change_password')
```

**Allowed Paths** (can access even with default password):
- `/accounts/force-change-password/`
- `/accounts/logout/`
- `/static/`
- `/media/`

### Force Change Password View

**Location**: `apps/accounts/views.py::force_change_password_view`

**Form Fields**:
- `old_password` - Must be `Pegawai@Pessel`
- `new_password` - Min 8 characters
- `confirm_password` - Must match new_password

**Validation**:
- ✅ Old password must be `Pegawai@Pessel`
- ✅ New password != `Pegawai@Pessel`
- ✅ New password min 8 characters
- ✅ New password == confirm_password

**After Success**:
- Password updated in local database
- Redirect to dashboard
- Can access all pages

---

## API Endpoints Used

### 1. Login

**Endpoint**: `POST /apisimpeg/5.0/auth/login`

**Request**:
```json
{
  "username": "prakom@admin.com",
  "password": "Pegawai@Pessel"
}
```

**Response** (Success):
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "user_id": 1,
      "username": "prakom@admin.com",
      "name": "Prakom Admin",
      "email": "prakom@admin.com",
      "id_pegawai": 12345,
      "is_active": true
    }
  },
  "version": "5.0"
}
```

**Response** (Failed):
```json
{
  "status": "error",
  "message": "Invalid credentials",
  "code": "INVALID_CREDENTIALS",
  "version": "5.0"
}
```

---

## Testing

### Test 1: First Time Login with Default Password

```bash
# 1. Make sure user NOT exists in Survey Pemda database
docker exec -it survey_pemda_python_app python manage.py shell
>>> from apps.accounts.models import User
>>> User.objects.filter(username='test@example.com').delete()
>>> exit()

# 2. Make sure user EXISTS in ESIMPEG with default password
# (Create via ESIMPEG admin or seeder with password: Pegawai@Pessel)

# 3. Try login at Survey Pemda
# URL: http://localhost:8006/
# Username: test@example.com
# Password: Pegawai@Pessel

# Expected:
# - Login successful
# - User created in Survey Pemda database with password 'Pegawai@Pessel'
# - Redirected to /accounts/force-change-password/
```

### Test 2: First Time Login with Custom Password (NEW!)

```bash
# 1. Make sure user NOT exists in Survey Pemda database
docker exec -it survey_pemda_python_app python manage.py shell
>>> from apps.accounts.models import User
>>> User.objects.filter(username='user2@example.com').delete()
>>> exit()

# 2. Make sure user EXISTS in ESIMPEG with custom password
# (Create via ESIMPEG admin with password: CustomPass123)

# 3. Try login at Survey Pemda
# URL: http://localhost:8006/
# Username: user2@example.com
# Password: CustomPass123

# Expected:
# - Login successful
# - User created in Survey Pemda database with password 'CustomPass123'
# - NO force change password
# - Direct to dashboard ✅
```

### Test 3: Force Change Password (Only for Default)

```bash
# After first login (redirected to force change password)

# Form:
# Old Password: Pegawai@Pessel
# New Password: NewPassword123
# Confirm Password: NewPassword123

# Expected:
# - Password changed successfully
# - Redirected to dashboard
# - Can access all pages
```

### Test 3: Login with New Password

```bash
# Logout and login again

# Username: test@example.com
# Password: NewPassword123

# Expected:
# - Login successful (using local database)
# - No force change password
# - Direct to dashboard
```

### Test 4: ESIMPEG API Down

```bash
# 1. Stop ESIMPEG API
docker stop esimpeg_python_app

# 2. Try login with new user (not exists in Survey Pemda)
# Username: newuser@example.com
# Password: anything

# Expected:
# - Error: "Sistem ESIMPEG sedang tidak tersedia"
# - Cannot login

# 3. Start ESIMPEG API again
docker start esimpeg_python_app
```

---

## Configuration

### 1. Update `.env`

```env
# ESIMPEG API Configuration
ESIMPEG_API_URL=http://esimpeg_python_app:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=
```

**Production**:
```env
ESIMPEG_API_URL=https://esimpeg.pesisirselatankab.go.id
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=abc123xyz...
```

### 2. Docker Network

Make sure Survey Pemda and ESIMPEG are in the same Docker network:

```yaml
# docker-compose.yml (Survey Pemda)
services:
  app:
    networks:
      - esimpeg_network

networks:
  esimpeg_network:
    external: true
```

Or use host network:

```yaml
services:
  app:
    network_mode: "host"
```

---

## Security Considerations

### 1. Default Password

**Default**: `Pegawai@Pessel`

**Security**:
- ✅ User MUST change on first login (middleware enforced)
- ✅ Cannot use default password as new password
- ✅ Min 8 characters for new password
- ✅ All password changes logged to `ms_log_data`

### 2. API Communication

**Security**:
- ✅ Use HTTPS in production
- ✅ Timeout 10 seconds (prevent hanging)
- ✅ Connection error handling
- ✅ API availability check (cached 1 minute)

### 3. Password Storage

**Local Database**:
- ✅ Argon2 hashing (OWASP recommended)
- ✅ Laravel Bcrypt compatibility (for old passwords)
- ✅ Password never stored in plain text

---

## Logging

### 1. User Creation from API

**Table**: `ms_log_data`

**Action**: `user_created_from_api`

**Data**:
```json
{
  "username": "test@example.com",
  "name": "Test User",
  "source": "esimpeg_api",
  "api_user_id": 123
}
```

### 2. Login Failed (API)

**Action**: `login_failed`

**Reason**: `API login failed - user not found`

### 3. Password Change

**Action**: `password_change`

**Data**:
```json
{
  "note": "Password changed from default (forced)",
  "success": true,
  "via": "web"
}
```

---

## Troubleshooting

### Problem 1: API Connection Error

**Symptoms**:
- Error: "Sistem ESIMPEG sedang tidak tersedia"
- Cannot login with new user

**Solutions**:
1. Check ESIMPEG API is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check Docker network:
   ```bash
   docker network inspect esimpeg_network
   ```

3. Check `.env` configuration:
   ```bash
   cat .env | grep ESIMPEG_API_URL
   ```

### Problem 2: User Created but Cannot Login

**Symptoms**:
- User exists in database
- Login failed with "Password salah"

**Solutions**:
1. Check if password is set correctly:
   ```python
   user = User.objects.get(username='test@example.com')
   print(user.check_password('Pegawai@Pessel'))  # Should be True
   ```

2. Reset password manually:
   ```python
   user.set_password('Pegawai@Pessel')
   user.save()
   ```

### Problem 3: Force Change Password Loop

**Symptoms**:
- After changing password, still redirected to force change password

**Solutions**:
1. Check if password actually changed:
   ```python
   user = User.objects.get(username='test@example.com')
   print(user.check_password('Pegawai@Pessel'))  # Should be False
   print(user.check_password('NewPassword123'))  # Should be True
   ```

2. Clear sessions:
   ```bash
   docker exec -it survey_pemda_python_app python manage.py clearsessions
   ```

---

## Next Steps

### 1. Webhook Integration (Password Sync)

When user changes password in ESIMPEG, sync to Survey Pemda automatically.

**See**: `27_SURVEY_PEMDA_WEBHOOK_IMPLEMENTATION.md` (from ESIMPEG docs)

### 2. Token Management

Store ESIMPEG API token in session for future API calls.

### 3. Data Sync

Sync pegawai data from ESIMPEG API to Survey Pemda.

---

## Files Created/Modified

### Created:
- `apps/accounts/services.py` - ESIMPEG API Service

### Modified:
- `core/views.py` - Login flow with API integration
- `core/settings.py` - ESIMPEG API settings
- `.env.example` - ESIMPEG API environment variables

### Documentation:
- `docs_dari_sonnet/30_ESIMPEG_API_INTEGRATION.md` - This file

---

## Summary

✅ **Implemented**:
1. ESIMPEG API Service (login, verify, refresh, get data)
2. Login flow with API fallback
3. Auto user creation from API
4. Force change password (default: `Pegawai@Pessel`)
5. Settings configuration
6. Environment variables
7. Logging & error handling

✅ **Benefits**:
- User can login with ESIMPEG credentials
- No manual user creation needed
- Secure default password (must change)
- Fallback to local database if API down
- All actions logged

⏳ **TODO**:
- Webhook integration (password sync)
- Token management (session storage)
- Data sync (pegawai data)

---

**Last Updated**: 2026-03-31  
**Version**: 1.0.0  
**Status**: Implemented ✓

