# Login Survey Pemda via ESIMPEG API (Fallback Authentication)

**Tanggal**: 6 April 2026  
**Status**: ✅ IMPLEMENTED

---

## 🎯 REQUIREMENT

User ingin login di Survey Pemda dengan flow:
1. **Coba login via ESIMPEG API dulu** (PRIORITY)
2. Jika berhasil, create/update user di database lokal Survey Pemda
3. Jika gagal, fallback ke database lokal Survey Pemda

---

## 🏗️ ARCHITECTURE

### Authentication Flow

```
User Login di Survey Pemda
         ↓
┌────────────────────────────────────────────────┐
│ 1. EsimpegAPIAuthBackend (PRIORITY)            │
│    ↓                                            │
│    POST /apisimpeg/5.0/auth/login              │
│    ↓                                            │
│    ✅ Success?                                  │
│       ↓ YES                                     │
│       Create/Update user di database lokal     │
│       Store token di session                   │
│       Return user → LOGIN SUCCESS              │
│       ↓ NO                                      │
│       Return None → Try next backend           │
└────────────────────────────────────────────────┘
         ↓ (if API failed)
┌────────────────────────────────────────────────┐
│ 2. FlexibleAuthBackend (Fallback)              │
│    ↓                                            │
│    Query database lokal Survey Pemda           │
│    ↓                                            │
│    ✅ User found & password valid?             │
│       ↓ YES                                     │
│       Return user → LOGIN SUCCESS              │
│       ↓ NO                                      │
│       Return None → Try next backend           │
└────────────────────────────────────────────────┘
         ↓ (if local DB failed)
┌────────────────────────────────────────────────┐
│ 3. ModelBackend (Final Fallback)               │
│    ↓                                            │
│    Standard Django authentication              │
│    ↓                                            │
│    Return user or None                         │
└────────────────────────────────────────────────┘
         ↓
    LOGIN RESULT
```

---

## 📝 IMPLEMENTATION

### 1. Authentication Backend

**File**: `apps/accounts/backends.py`

```python
class EsimpegAPIAuthBackend(ModelBackend):
    """
    Login via ESIMPEG API
    Jika berhasil, create/update user di database lokal
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1. Login via ESIMPEG API
        api_service = EsimpegAPIService()
        login_result = api_service.login(username, password)
        
        if not login_result:
            return None  # Try next backend
        
        # 2. Extract user data
        user_data = login_result.get('user', {})
        
        # 3. Create/update user di database lokal
        user, created = User.objects.update_or_create(
            username=user_data.get('username'),
            defaults={
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'id_pegawai': user_data.get('id_pegawai'),
                'user_id_opd': user_data.get('user_id_opd'),
                'is_active': user_data.get('is_active', True),
            }
        )
        
        # 4. Set password (hash)
        user.set_password(password)
        user.save()
        
        # 5. Store token di session
        request.session['esimpeg_access_token'] = login_result.get('access_token')
        request.session['esimpeg_refresh_token'] = login_result.get('refresh_token')
        
        return user
```

### 2. Settings Configuration

**File**: `core/settings.py`

```python
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EsimpegAPIAuthBackend',   # 1. ESIMPEG API (PRIORITY)
    'apps.accounts.backends.FlexibleAuthBackend',     # 2. Local database
    'django.contrib.auth.backends.ModelBackend',      # 3. Standard Django
]
```

**Priority Order**:
- Django akan coba backend dari atas ke bawah
- Jika backend return `None`, coba backend berikutnya
- Jika backend return `User`, login success

---

## ✅ BENEFITS

### 1. Centralized User Management
- User data di-manage di ESIMPEG
- Survey Pemda otomatis sync user dari ESIMPEG
- Tidak perlu import manual

### 2. Always Up-to-Date
- Setiap login, user data di-update dari ESIMPEG
- Password selalu sync dengan ESIMPEG
- User baru otomatis bisa login

### 3. Offline Fallback
- Jika ESIMPEG API down, masih bisa login dari database lokal
- User yang pernah login akan tersimpan di database lokal
- Tidak bergantung 100% pada ESIMPEG

### 4. Token Management
- Token ESIMPEG disimpan di session
- Bisa digunakan untuk API calls ke ESIMPEG
- Auto-refresh token jika expired

---

## 🧪 TESTING

### Test 1: Login User Baru (Belum Ada di Database Lokal)

```bash
# User: prakom@admin.com (ada di ESIMPEG, belum ada di Survey Pemda)
# Expected: Login via API, create user di database lokal

# 1. Cek user belum ada di database lokal
docker exec survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print('User exists:', User.objects.filter(username='prakom@admin.com').exists())
"
# Output: User exists: False

# 2. Login via web browser
# URL: http://localhost:8005/
# Username: prakom@admin.com
# Password: [password_esimpeg]
# Expected: ✅ Login success

# 3. Cek user sudah dibuat di database lokal
docker exec survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='prakom@admin.com')
print(f'User created: {u.username}')
print(f'Name: {u.name}')
print(f'Email: {u.email}')
print(f'ID Pegawai: {u.id_pegawai}')
"
# Output: User created, dengan data dari ESIMPEG
```

### Test 2: Login User Existing (Sudah Ada di Database Lokal)

```bash
# User: prakom@admin.com (sudah ada di database lokal)
# Expected: Login via API, update user data

# 1. Login via web browser
# Expected: ✅ Login success, data user di-update dari ESIMPEG
```

### Test 3: ESIMPEG API Down (Fallback ke Database Lokal)

```bash
# 1. Stop ESIMPEG container
docker stop esimpeg_python_app

# 2. Login via web browser
# Username: prakom@admin.com (yang sudah pernah login sebelumnya)
# Password: [password_lokal]
# Expected: ✅ Login success dari database lokal

# 3. Start ESIMPEG container kembali
docker start esimpeg_python_app
```

### Test 4: User Tidak Ada di ESIMPEG & Database Lokal

```bash
# Username: usertest@test.com (tidak ada di ESIMPEG & Survey Pemda)
# Expected: ❌ Login failed
```

---

## 📊 USER SCENARIOS

### Scenario 1: User Baru (First Time Login)

```
User: john@example.com
Status: Belum pernah login di Survey Pemda

Flow:
1. User input username & password
2. EsimpegAPIAuthBackend → Login via ESIMPEG API
3. ✅ API Success → Create user di database lokal
4. Store token di session
5. ✅ LOGIN SUCCESS
```

### Scenario 2: User Existing (Regular Login)

```
User: prakom@admin.com
Status: Sudah pernah login di Survey Pemda

Flow:
1. User input username & password
2. EsimpegAPIAuthBackend → Login via ESIMPEG API
3. ✅ API Success → Update user data di database lokal
4. Store token di session
5. ✅ LOGIN SUCCESS
```

### Scenario 3: ESIMPEG API Down (Offline Mode)

```
User: prakom@admin.com
Status: Sudah pernah login di Survey Pemda
ESIMPEG: DOWN

Flow:
1. User input username & password
2. EsimpegAPIAuthBackend → Login via ESIMPEG API
3. ❌ API Failed (connection error)
4. FlexibleAuthBackend → Query database lokal
5. ✅ User found & password valid
6. ✅ LOGIN SUCCESS (dari database lokal)
```

### Scenario 4: Password Salah

```
User: prakom@admin.com
Password: SALAH

Flow:
1. User input username & password salah
2. EsimpegAPIAuthBackend → Login via ESIMPEG API
3. ❌ API Failed (invalid credentials)
4. FlexibleAuthBackend → Query database lokal
5. ❌ Password tidak match
6. ModelBackend → Standard Django auth
7. ❌ Failed
8. ❌ LOGIN FAILED
```

---

## 🔍 LOGGING

### Check Authentication Logs

```bash
# Survey Pemda logs
docker logs -f survey_pemda_python_app | grep -i "auth\|login"

# Expected output:
# INFO: ESIMPEG API login successful for user: prakom@admin.com
# INFO: User created from ESIMPEG API: prakom@admin.com
# or
# INFO: User updated from ESIMPEG API: prakom@admin.com
```

### Check User Creation

```bash
docker exec survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

# List users created today
from django.utils import timezone
from datetime import timedelta
today = timezone.now() - timedelta(days=1)
users = User.objects.filter(date_joined__gte=today)

for u in users:
    print(f'{u.username} - {u.name} - {u.date_joined}')
"
```

---

## ⚙️ CONFIGURATION

### Environment Variables

**File**: `.env`

```bash
# ESIMPEG API Configuration
ESIMPEG_API_URL=http://172.21.0.3:8000
ESIMPEG_API_TIMEOUT=10
```

**Notes**:
- `ESIMPEG_API_URL`: URL ESIMPEG API (internal Docker network)
- `ESIMPEG_API_TIMEOUT`: Timeout untuk API calls (seconds)

---

## 🚨 TROUBLESHOOTING

### Problem 1: Login Gagal - "Username atau password salah"

**Possible Causes**:
1. ESIMPEG API down
2. Password salah
3. User tidak ada di ESIMPEG

**Solution**:
```bash
# 1. Check ESIMPEG API status
curl http://172.21.0.3:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"prakom@admin.com","password":"test"}'

# 2. Check logs
docker logs survey_pemda_python_app | tail -50

# 3. Try login with different user
```

### Problem 2: User Created but Cannot Login

**Possible Causes**:
1. User is_active = False
2. Password tidak tersimpan dengan benar

**Solution**:
```bash
# Check user status
docker exec survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='prakom@admin.com')
print(f'Is Active: {u.is_active}')
print(f'Password: {u.password[:50]}...')
"

# Activate user if needed
docker exec survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='prakom@admin.com')
u.is_active = True
u.save()
print('User activated')
"
```

### Problem 3: ESIMPEG Token Not Stored in Session

**Possible Causes**:
1. Session middleware tidak aktif
2. Request object tidak diteruskan ke backend

**Solution**:
```bash
# Check session
# Login via browser, then check:
docker exec survey_pemda_python_app python manage.py shell -c "
from django.contrib.sessions.models import Session
from django.utils import timezone

# Get active sessions
sessions = Session.objects.filter(expire_date__gte=timezone.now())
for s in sessions:
    data = s.get_decoded()
    print(f'Session: {s.session_key}')
    print(f'Token: {data.get(\"esimpeg_access_token\", \"NOT FOUND\")[:50]}...')
"
```

---

## 📋 FILES MODIFIED

### New/Modified Files

1. ✅ `apps/accounts/backends.py`
   - Added `EsimpegAPIAuthBackend` class

2. ✅ `core/settings.py`
   - Updated `AUTHENTICATION_BACKENDS` order

3. ✅ `docs_dari_sonnet/85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md`
   - This documentation

---

## ✅ SUMMARY

**Implementasi**: ✅ COMPLETE

**Flow**:
1. ✅ Login via ESIMPEG API (PRIORITY)
2. ✅ Create/update user di database lokal
3. ✅ Store token di session
4. ✅ Fallback ke database lokal jika API down

**Benefits**:
- ✅ Centralized user management
- ✅ Always up-to-date user data
- ✅ Offline fallback support
- ✅ Auto token management

**Testing**: Ready for testing

---

**Status**: ✅ **READY TO TEST**

Silakan test login dengan user ESIMPEG di Survey Pemda!

