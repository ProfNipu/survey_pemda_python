# Test Guide - ESIMPEG API Integration

**Date**: 2026-03-31  
**Status**: Ready for Testing

---

## Quick Test Scenarios

### ✅ Scenario 1: Login dengan Password Default

**Kondisi**:
- User TIDAK ada di Survey Pemda database
- User ADA di ESIMPEG dengan password: `Pegawai@Pessel`

**Steps**:
1. Buka: http://localhost:8006/
2. Login dengan:
   - Username: `test@example.com`
   - Password: `Pegawai@Pessel`

**Expected Result**:
- ✅ Login berhasil
- ✅ User dibuat di Survey Pemda database
- ✅ Redirect ke `/accounts/force-change-password/`
- ✅ User HARUS ganti password sebelum akses dashboard

---

### ✅ Scenario 2: Login dengan Password Custom (BARU!)

**Kondisi**:
- User TIDAK ada di Survey Pemda database
- User ADA di ESIMPEG dengan password custom: `CustomPass123`

**Steps**:
1. Buka: http://localhost:8006/
2. Login dengan:
   - Username: `user2@example.com`
   - Password: `CustomPass123`

**Expected Result**:
- ✅ Login berhasil
- ✅ User dibuat di Survey Pemda database dengan password `CustomPass123`
- ✅ TIDAK ada force change password
- ✅ Langsung redirect ke `/dashboard/` ✨

**Ini yang dimaksud user**: Password disimpan sesuai yang digunakan login, bukan selalu default!

---

### ✅ Scenario 3: Ganti Password (Hanya untuk Default)

**Kondisi**:
- User login dengan password default (Scenario 1)
- Berada di halaman force change password

**Steps**:
1. Isi form:
   - Old Password: `Pegawai@Pessel`
   - New Password: `NewPassword123`
   - Confirm Password: `NewPassword123`
2. Submit

**Expected Result**:
- ✅ Password berhasil diubah
- ✅ Redirect ke dashboard
- ✅ Bisa akses semua halaman

---

### ✅ Scenario 4: Login Ulang dengan Password Baru

**Kondisi**:
- User sudah ganti password (Scenario 3)

**Steps**:
1. Logout
2. Login dengan:
   - Username: `test@example.com`
   - Password: `NewPassword123`

**Expected Result**:
- ✅ Login berhasil (pakai local database)
- ✅ TIDAK ada force change password
- ✅ Langsung ke dashboard

---

### ✅ Scenario 5: ESIMPEG API Down

**Kondisi**:
- ESIMPEG API tidak bisa diakses
- User baru (belum ada di Survey Pemda)

**Steps**:
1. Stop ESIMPEG: `docker stop esimpeg_python_app`
2. Login dengan user baru

**Expected Result**:
- ❌ Error: "Sistem ESIMPEG sedang tidak tersedia"
- ❌ Tidak bisa login
- ✅ User yang sudah ada tetap bisa login (pakai local database)

---

## Verification Commands

### Check User in Database

```bash
# Masuk ke container
docker exec -it survey_pemda_python_app python manage.py shell

# Check user
from apps.accounts.models import User
user = User.objects.get(username='test@example.com')

# Check password
print(user.check_password('Pegawai@Pessel'))  # True = masih default
print(user.check_password('CustomPass123'))   # True = password custom
print(user.check_password('NewPassword123'))  # True = sudah ganti

# Check user data
print(f"Username: {user.username}")
print(f"Name: {user.name}")
print(f"Email: {user.email}")
print(f"ID Pegawai: {user.id_pegawai}")
```

### Check Logs

```bash
# Check login logs
docker exec -it survey_pemda_python_app python manage.py shell

from core.models import MsLogData

# Login logs
MsLogData.objects.filter(action='login').order_by('-created_at')[:5]

# User creation logs
MsLogData.objects.filter(action='user_created_from_api').order_by('-created_at')[:5]

# Password change logs
MsLogData.objects.filter(action='password_change').order_by('-created_at')[:5]
```

### Test API Connection

```bash
# Test ESIMPEG API
curl http://localhost:8000/health

# Test login API
curl -X POST http://localhost:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"Pegawai@Pessel"}'
```

---

## Configuration Check

### 1. Environment Variables

```bash
# Check .env
cat projects/survey_pemda_python/.env | grep ESIMPEG

# Should show:
# ESIMPEG_API_URL=http://esimpeg_python_app:8000
# ESIMPEG_API_TIMEOUT=10
# ESIMPEG_WEBHOOK_SECRET=
```

### 2. Docker Network

```bash
# Check if both containers in same network
docker network inspect esimpeg_network

# Should show both:
# - esimpeg_python_app
# - survey_pemda_python_app
```

---

## Key Points (Jawaban untuk User)

### ❓ "klw passworednya di api bukan pegawai@pessel kan tidak dia set password defaultkan, password tetap simpan jika dia beda kan dan bisa masuk kan gitu"

**Jawaban**: ✅ BENAR! Sudah diimplementasikan!

**Cara Kerja**:
```python
# Di core/views.py line 193-195
is_default_password = (password == 'Pegawai@Pessel')

# Create user dengan password ACTUAL dari login
user = User.objects.create_user(
    username=user_data.get('username', username),
    email=user_data.get('email'),
    name=user_data.get('name', username),
    password=password,  # ← Ini password ASLI yang dipakai login!
    id_pegawai=user_data.get('id_pegawai', 0)
)
```

**Hasil**:
- Password = `Pegawai@Pessel` → Force change password ⚠️
- Password = `CustomPass123` → Langsung dashboard ✅
- Password = `ApaAja789` → Langsung dashboard ✅

**Kesimpulan**: Password disimpan sesuai yang digunakan saat login, BUKAN selalu default!

---

## Troubleshooting

### Problem: User dibuat tapi tidak bisa login

**Solution**:
```bash
# Reset password manual
docker exec -it survey_pemda_python_app python manage.py shell

from apps.accounts.models import User
user = User.objects.get(username='test@example.com')
user.set_password('Pegawai@Pessel')
user.save()
```

### Problem: Force change password loop

**Solution**:
```bash
# Clear sessions
docker exec -it survey_pemda_python_app python manage.py clearsessions

# Check password
docker exec -it survey_pemda_python_app python manage.py shell
from apps.accounts.models import User
user = User.objects.get(username='test@example.com')
print(user.check_password('Pegawai@Pessel'))  # Should be False after change
```

### Problem: API connection error

**Solution**:
```bash
# Check ESIMPEG is running
docker ps | grep esimpeg

# Check network
docker network inspect esimpeg_network

# Test connection from Survey Pemda container
docker exec -it survey_pemda_python_app curl http://esimpeg_python_app:8000/health
```

---

## Summary

✅ **Implemented**:
1. Login via ESIMPEG API jika user tidak ada di local database
2. Password disimpan sesuai yang digunakan login (bukan selalu default)
3. Force change password HANYA untuk password default (`Pegawai@Pessel`)
4. Password custom langsung bisa akses dashboard
5. Fallback ke local database jika API down
6. Logging lengkap untuk semua action

✅ **Benefits**:
- User bisa login dengan kredensial ESIMPEG
- Tidak perlu create user manual
- Password custom tidak perlu ganti lagi
- Secure (default password harus diganti)

⏳ **Next Steps** (Optional):
- Webhook untuk sync password dari ESIMPEG ke Survey Pemda
- Token management untuk API calls
- Data sync pegawai

---

**Last Updated**: 2026-03-31  
**Version**: 1.0.0  
**Status**: Ready for Testing ✓
