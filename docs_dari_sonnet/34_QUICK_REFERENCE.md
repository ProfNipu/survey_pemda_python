# 🚀 ESIMPEG Integration - Quick Reference

**Status**: ✅ READY FOR TESTING  
**Date**: 2026-03-31

---

## 📋 Quick Facts

### What's New?
✅ Login via ESIMPEG API for new users  
✅ Password disimpan sesuai yang digunakan login  
✅ Force change HANYA untuk password default  
✅ Custom password langsung ke dashboard  

### Key Files
- `apps/accounts/services.py` - ESIMPEG API Service
- `core/views.py` - Login flow (Line 168-350)
- `core/settings.py` - Settings
- `.env` - Configuration

---

## 🔑 Password Logic

```
Password = "Pegawai@Pessel"  → ⚠️ Force change password
Password = "CustomPass123"   → ✅ Direct to dashboard
Password = "ApaAja789"       → ✅ Direct to dashboard
```

**Rule**: Hanya password default yang harus diganti!

---

## 🧪 Quick Test

### Test 1: Default Password
```bash
# Login di http://localhost:8006/
Username: test@example.com
Password: Pegawai@Pessel

Expected: ⚠️ Redirect to force change password
```

### Test 2: Custom Password
```bash
# Login di http://localhost:8006/
Username: user2@example.com
Password: CustomPass123

Expected: ✅ Direct to dashboard (no force change!)
```

---

## ⚙️ Configuration

### .env File
```env
ESIMPEG_API_URL=http://esimpeg_python_app:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=
```

### Production
```env
ESIMPEG_API_URL=https://esimpeg.pesisirselatankab.go.id
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=your-secret-key
```

---

## 🔍 Verification Commands

### Check User Password
```bash
docker exec -it survey_pemda_python_app python manage.py shell

from apps.accounts.models import User
user = User.objects.get(username='test@example.com')

# Check password type
print(user.check_password('Pegawai@Pessel'))  # True = default
print(user.check_password('CustomPass123'))   # True = custom
```

### Check Logs
```bash
docker exec -it survey_pemda_python_app python manage.py shell

from core.models import MsLogData

# User creation logs
MsLogData.objects.filter(action='user_created_from_api').last()

# Check is_default_password flag
log = MsLogData.objects.filter(action='user_created_from_api').last()
print(log.new_data['is_default_password'])  # True/False
```

### Test API
```bash
# Health check
curl http://localhost:8000/health

# Login test
curl -X POST http://localhost:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"Pegawai@Pessel"}'
```

---

## 🐛 Troubleshooting

### Problem: API Connection Error
```bash
# Check ESIMPEG is running
docker ps | grep esimpeg

# Test connection
docker exec -it survey_pemda_python_app curl http://esimpeg_python_app:8000/health
```

### Problem: User Created but Can't Login
```bash
# Reset password
docker exec -it survey_pemda_python_app python manage.py shell

from apps.accounts.models import User
user = User.objects.get(username='test@example.com')
user.set_password('Pegawai@Pessel')
user.save()
```

### Problem: Force Change Password Loop
```bash
# Clear sessions
docker exec -it survey_pemda_python_app python manage.py clearsessions

# Verify password changed
docker exec -it survey_pemda_python_app python manage.py shell
from apps.accounts.models import User
user = User.objects.get(username='test@example.com')
print(user.check_password('Pegawai@Pessel'))  # Should be False
```

---

## 📚 Full Documentation

1. **IMPLEMENTATION_COMPLETE.md** - Complete implementation summary
2. **TEST_ESIMPEG_INTEGRATION.md** - Detailed test scenarios
3. **ESIMPEG_LOGIN_FLOW.md** - Visual flow diagram
4. **docs_dari_sonnet/30_ESIMPEG_API_INTEGRATION.md** - Technical guide

---

## ✅ Checklist

Before testing:
- [ ] Update `.env` with ESIMPEG_API_URL
- [ ] Ensure ESIMPEG API is running
- [ ] Check Docker network connection
- [ ] Create test users in ESIMPEG

Testing:
- [ ] Test default password login → Force change
- [ ] Test custom password login → Direct dashboard
- [ ] Test password change → Can access dashboard
- [ ] Test API down → Error message
- [ ] Test existing user → Normal login

After testing:
- [ ] Verify logs in `ms_log_data`
- [ ] Check user passwords in database
- [ ] Test logout and re-login
- [ ] Test multiple users

---

## 🎯 Key Points

1. **Password disimpan sesuai yang digunakan login** (bukan selalu default)
2. **Force change HANYA untuk password default** (`Pegawai@Pessel`)
3. **Custom password langsung ke dashboard** (no force change)
4. **API down = error message** (existing users still work)
5. **All actions logged** to `ms_log_data`

---

## 💡 User Question Answered

**Q**: "klw passworednya di api bukan pegawai@pessel kan tidak dia set password defaultkan, password tetap simpan jika dia beda kan dan bisa masuk kan gitu , paham kah ?"

**A**: ✅ **YA BENAR!** Password disimpan sesuai yang digunakan login. Jika password bukan default, user bisa langsung masuk ke dashboard tanpa perlu ganti password!

**Proof**: Check `core/views.py` Line 195:
```python
password=password,  # ← Use ACTUAL password from login
```

---

**Last Updated**: 2026-03-31  
**Version**: 1.0.0
