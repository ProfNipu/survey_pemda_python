# ESIMPEG Login Flow - Visual Guide

**Date**: 2026-03-31

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER LOGIN ATTEMPT                            │
│              (Username + Password di Survey Pemda)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Check Local Database │
                  └──────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌──────────────┐          ┌──────────────┐
        │ User EXISTS  │          │ User NOT     │
        │ in Local DB  │          │ EXISTS       │
        └──────┬───────┘          └──────┬───────┘
               │                         │
               │                         ▼
               │              ┌─────────────────────┐
               │              │ Call ESIMPEG API    │
               │              │ POST /auth/login    │
               │              └──────┬──────────────┘
               │                     │
               │          ┌──────────┴──────────┐
               │          │                     │
               │          ▼                     ▼
               │   ┌─────────────┐      ┌─────────────┐
               │   │ API SUCCESS │      │ API FAILED  │
               │   └──────┬──────┘      └──────┬──────┘
               │          │                    │
               │          ▼                    ▼
               │   ┌─────────────────┐  ┌──────────────┐
               │   │ Create User in  │  │ Show Error:  │
               │   │ Local Database  │  │ "User tidak  │
               │   │ with ACTUAL     │  │  ditemukan"  │
               │   │ password used   │  └──────────────┘
               │   └──────┬──────────┘
               │          │
               │          ▼
               │   ┌─────────────────────────┐
               │   │ Check Password Type:    │
               │   │ - Pegawai@Pessel?       │
               │   │ - Custom password?      │
               │   └──────┬──────────────────┘
               │          │
               └──────────┴──────────────────┐
                          │                  │
                          ▼                  │
                ┌──────────────────┐         │
                │ Authenticate     │         │
                │ with password    │         │
                └────────┬─────────┘         │
                         │                   │
                         ▼                   │
                ┌──────────────────┐         │
                │ Login Successful │         │
                │ (Create Session) │         │
                └────────┬─────────┘         │
                         │                   │
                         ▼                   │
              ┌──────────────────────┐       │
              │ Check Password:      │       │
              │ user.check_password  │       │
              │ ('Pegawai@Pessel')   │       │
              └──────┬───────────────┘       │
                     │                       │
        ┌────────────┴────────────┐          │
        │                         │          │
        ▼                         ▼          │
┌──────────────┐          ┌──────────────┐  │
│ Password =   │          │ Password ≠   │  │
│ Default      │          │ Default      │  │
│ (Pegawai@    │          │ (Custom)     │  │
│  Pessel)     │          │              │  │
└──────┬───────┘          └──────┬───────┘  │
       │                         │          │
       ▼                         ▼          │
┌──────────────┐          ┌──────────────┐  │
│ ⚠️ FORCE     │          │ ✅ DIRECT TO │  │
│ CHANGE       │          │ DASHBOARD    │  │
│ PASSWORD     │          │              │  │
└──────┬───────┘          └──────────────┘  │
       │                                     │
       ▼                                     │
┌──────────────┐                             │
│ Redirect to  │                             │
│ /accounts/   │                             │
│ force-change-│                             │
│ password/    │                             │
└──────┬───────┘                             │
       │                                     │
       ▼                                     │
┌──────────────┐                             │
│ User Change  │                             │
│ Password     │                             │
│ (Min 8 char) │                             │
└──────┬───────┘                             │
       │                                     │
       ▼                                     │
┌──────────────┐                             │
│ ✅ Can Access│                             │
│ Dashboard    │◄────────────────────────────┘
└──────────────┘
```

---

## Scenario Examples

### 📌 Scenario A: Default Password

```
Input:
  Username: pegawai@example.com
  Password: Pegawai@Pessel

Flow:
  1. Check local DB → NOT FOUND
  2. Call ESIMPEG API → SUCCESS
  3. Create user with password: "Pegawai@Pessel"
  4. Authenticate → SUCCESS
  5. Check password → IS DEFAULT
  6. Redirect → /accounts/force-change-password/
  
Result:
  ⚠️ User MUST change password before accessing dashboard
```

### 📌 Scenario B: Custom Password (NEW!)

```
Input:
  Username: pegawai@example.com
  Password: MySecurePass123

Flow:
  1. Check local DB → NOT FOUND
  2. Call ESIMPEG API → SUCCESS
  3. Create user with password: "MySecurePass123"
  4. Authenticate → SUCCESS
  5. Check password → NOT DEFAULT
  6. Redirect → /dashboard/
  
Result:
  ✅ User can access dashboard immediately!
```

### 📌 Scenario C: Existing User

```
Input:
  Username: existing@example.com
  Password: AnyPassword

Flow:
  1. Check local DB → FOUND
  2. Authenticate with local password → SUCCESS
  3. Check password → NOT DEFAULT (already changed)
  4. Redirect → /dashboard/
  
Result:
  ✅ Normal login (no API call needed)
```

### 📌 Scenario D: API Down

```
Input:
  Username: newuser@example.com
  Password: AnyPassword

Flow:
  1. Check local DB → NOT FOUND
  2. Call ESIMPEG API → CONNECTION ERROR
  3. Show error message
  
Result:
  ❌ Cannot login (API required for new users)
  ✅ Existing users can still login (use local DB)
```

---

## Code References

### 1. Check Local Database
**File**: `core/views.py` (Line 168-170)
```python
user_exists = User.objects.filter(
    Q(username=username) | Q(email=username)
).exists()
```

### 2. Call ESIMPEG API
**File**: `core/views.py` (Line 176-178)
```python
from apps.accounts.services import EsimpegAPIService
esimpeg_api = EsimpegAPIService()
api_response = esimpeg_api.login(username, password)
```

### 3. Create User with Actual Password
**File**: `core/views.py` (Line 188-198)
```python
# Determine if password is default or custom
is_default_password = (password == 'Pegawai@Pessel')

# Create user with the password used for login
user = User.objects.create_user(
    username=user_data.get('username', username),
    email=user_data.get('email'),
    name=user_data.get('name', username),
    password=password,  # ← ACTUAL password from login!
    id_pegawai=user_data.get('id_pegawai', 0)
)
```

### 4. Check Default Password
**File**: `core/views.py` (Line 318-320)
```python
if user.check_password('Pegawai@Pessel'):
    logger.info(f"User {user.username} using default password")
    return redirect('accounts:force_change_password')
```

### 5. Force Change Password View
**File**: `apps/accounts/views.py` (Line 52+)
```python
def force_change_password_view(request):
    # Check if user still has default password
    if not user.check_password('Pegawai@Pessel'):
        return redirect('dashboard:index')
    
    # Validate and change password
    # ...
```

---

## Key Implementation Details

### ✅ Password Storage Logic

```python
# BEFORE (Wrong - always default):
user = User.objects.create_user(
    username=username,
    password='Pegawai@Pessel'  # ❌ Always default
)

# AFTER (Correct - actual password):
user = User.objects.create_user(
    username=username,
    password=password  # ✅ Use actual password from login
)
```

### ✅ Force Change Logic

```python
# Check if password is default
if user.check_password('Pegawai@Pessel'):
    # Force change password
    return redirect('accounts:force_change_password')
else:
    # Direct to dashboard
    return redirect('/dashboard/')
```

### ✅ Middleware Check

**File**: `core/middleware/session.py`

```python
class ForceChangePasswordMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.check_password('Pegawai@Pessel'):
                # Redirect to force change password
                if request.path not in ALLOWED_PATHS:
                    return redirect('accounts:force_change_password')
        
        return self.get_response(request)
```

---

## Summary

**Key Points**:
1. ✅ Password disimpan sesuai yang digunakan saat login
2. ✅ Default password (`Pegawai@Pessel`) → Force change
3. ✅ Custom password → Direct to dashboard
4. ✅ Existing users → Normal login (no API call)
5. ✅ API down → Error message (new users cannot login)

**User Question Answered**:
> "klw passworednya di api bukan pegawai@pessel kan tidak dia set password defaultkan, password tetap simpan jika dia beda kan dan bisa masuk kan gitu"

**Answer**: ✅ YA BENAR! Password disimpan sesuai yang digunakan login. Jika password bukan default, user bisa langsung masuk ke dashboard tanpa perlu ganti password!

---

**Last Updated**: 2026-03-31  
**Version**: 1.0.0
