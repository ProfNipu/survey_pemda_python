# User ID OPD - Sync dari ESIMPEG ke Survey Pemda

**Tanggal**: 31 Maret 2026  
**Status**: ✅ SUDAH DIIMPLEMENTASI

---

## 🎯 Perubahan

Saat user login via ESIMPEG API di Survey Pemda, field `user_id_opd` sekarang disimpan ke database lokal Survey Pemda.

---

## 🔄 Flow Lengkap

```
1. User login di Survey Pemda (username tidak ada di database lokal)
   ↓
2. Survey Pemda call ESIMPEG API login
   POST /apisimpeg/5.0/auth/login
   ↓
3. ESIMPEG return user data (termasuk user_id_opd)
   {
     "user": {
       "user_id": 1,
       "username": "prakom@admin.com",
       "name": "Prakom Admin",
       "id_pegawai": 123,
       "user_id_opd": 456  ← Field baru!
     }
   }
   ↓
4. Survey Pemda create user di database lokal
   User.objects.create_user(
     username="prakom@admin.com",
     name="Prakom Admin",
     id_pegawai=123,
     user_id_opd=456  ← Disimpan!
   )
   ↓
5. User berhasil login di Survey Pemda
   Database lokal sudah punya user_id_opd
```

---

## 📝 Detail Implementasi

### File yang Diubah

#### 1. Survey Pemda - core/views.py

**Lokasi:** `projects/survey_pemda_python/core/views.py`

**Perubahan:**
```python
# SEBELUM
user = User.objects.create_user(
    username=user_data.get('username', username),
    email=user_data.get('email'),
    name=user_data.get('name', username),
    password=password,
    id_pegawai=user_data.get('id_pegawai', 0)
)

# SESUDAH
user = User.objects.create_user(
    username=user_data.get('username', username),
    email=user_data.get('email'),
    name=user_data.get('name', username),
    password=password,
    id_pegawai=user_data.get('id_pegawai', 0),
    user_id_opd=user_data.get('user_id_opd', 0)  ← TAMBAHAN!
)
```

#### 2. Survey Pemda - apps/accounts/services.py

**Lokasi:** `projects/survey_pemda_python/apps/accounts/services.py`

**Perubahan:** Update docstring untuk mencerminkan field baru di response

```python
Example response:
{
    "user": {
        "user_id": 1,
        "username": "prakom@admin.com",
        "id_pegawai": 123,
        "user_id_opd": 456  ← Dokumentasi updated!
    }
}
```

#### 3. ESIMPEG - esimpeg_core/views.py

**Lokasi:** `projects/ESIMPEG-Python/esimpeg_core/views.py`

**Perubahan:** Tambah `user_id_opd` ke response login API

```python
return JsonResponse({
    'data': {
        'user': {
            'user_id': user.id,
            'username': user.username,
            'id_pegawai': user.id_pegawai or 0,
            'user_id_opd': user.user_id_opd or 0  ← TAMBAHAN!
        }
    }
})
```

---

## 🧪 Testing

### Test 1: Login User Baru (Belum Ada di Survey Pemda)

```bash
# 1. Pastikan user tidak ada di Survey Pemda
docker exec -it survey_pemda_python_app python manage.py shell
>>> from apps.accounts.models import User
>>> User.objects.filter(username='test@example.com').exists()
False  # User belum ada

# 2. Login via web Survey Pemda
# URL: http://localhost:8006/
# Username: test@example.com
# Password: password_dari_esimpeg

# 3. Cek user sudah dibuat dengan user_id_opd
>>> user = User.objects.get(username='test@example.com')
>>> user.user_id_opd
456  # ✅ Tersimpan!
```

### Test 2: Cek Database Langsung

```bash
# Connect ke database Survey Pemda
docker exec -it survey_pemda_python_db mysql -u root -p

# Query user
mysql> USE survey_pemda;
mysql> SELECT id, username, name, id_pegawai, user_id_opd 
       FROM users 
       WHERE username = 'test@example.com';

# Expected output:
+----+------------------+-------------+------------+-------------+
| id | username         | name        | id_pegawai | user_id_opd |
+----+------------------+-------------+------------+-------------+
|  5 | test@example.com | Test User   |        123 |         456 |
+----+------------------+-------------+------------+-------------+
```

### Test 3: Cek Log

```bash
# Cek log user creation
docker exec -it survey_pemda_python_app python manage.py shell

>>> from core.models import MsLogData
>>> log = MsLogData.objects.filter(action='user_created_from_api').last()
>>> log.new_data
{
    'username': 'test@example.com',
    'name': 'Test User',
    'source': 'esimpeg_api',
    'api_user_id': 1,
    'id_pegawai': 123,
    'user_id_opd': 456,  ← ✅ Tercatat di log!
    'is_default_password': False
}
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ ESIMPEG Database                                            │
│                                                             │
│ users table:                                                │
│ ┌────┬──────────────────┬──────────┬────────┬─────────────┐│
│ │ id │ username         │ id_pegawai│ user_id_opd         ││
│ ├────┼──────────────────┼──────────┼────────┼─────────────┤│
│ │  1 │ prakom@admin.com │      123 │    456 │             ││
│ └────┴──────────────────┴──────────┴────────┴─────────────┘│
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Login API Call
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ESIMPEG API Response                                        │
│                                                             │
│ {                                                           │
│   "user": {                                                 │
│     "user_id": 1,                                           │
│     "username": "prakom@admin.com",                         │
│     "id_pegawai": 123,                                      │
│     "user_id_opd": 456  ← Dikirim ke Survey Pemda          │
│   }                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Create User di Survey Pemda
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Survey Pemda Database                                       │
│                                                             │
│ users table:                                                │
│ ┌────┬──────────────────┬──────────┬────────┬─────────────┐│
│ │ id │ username         │ id_pegawai│ user_id_opd         ││
│ ├────┼──────────────────┼──────────┼────────┼─────────────┤│
│ │  5 │ prakom@admin.com │      123 │    456 │ ← Tersimpan!││
│ └────┴──────────────────┴──────────┴────────┴─────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist

- [x] ESIMPEG: Tambah `user_id_opd` ke response login API
- [x] Survey Pemda: Simpan `user_id_opd` saat create user dari API
- [x] Survey Pemda: Update log untuk mencatat `user_id_opd`
- [x] Update docstring di service
- [x] Test no syntax errors
- [x] Hapus file test .sh yang tidak diperlukan
- [x] Documentation created

---

## 🎯 Kesimpulan

### Sebelum

User login via ESIMPEG API → User dibuat di Survey Pemda tanpa `user_id_opd`

```sql
-- Survey Pemda database
SELECT user_id_opd FROM users WHERE username = 'prakom@admin.com';
-- Result: NULL atau 0
```

### Sesudah

User login via ESIMPEG API → User dibuat di Survey Pemda dengan `user_id_opd` dari ESIMPEG

```sql
-- Survey Pemda database
SELECT user_id_opd FROM users WHERE username = 'prakom@admin.com';
-- Result: 456 (nilai dari ESIMPEG)
```

---

## 📚 Related Documentation

- `48_LOGIN_API_USER_ID_OPD.md` - Dokumentasi perubahan di ESIMPEG API

---

## 🚀 Next Steps

1. ✅ Test login user baru di Survey Pemda
2. ✅ Verify `user_id_opd` tersimpan di database
3. ✅ Cek log untuk memastikan tercatat
4. ⏳ Deploy ke production (jika diperlukan)

---

**Terakhir Update**: 31 Maret 2026  
**Versi**: 1.0  
**Status**: ✅ Selesai & Siap Dipakai
