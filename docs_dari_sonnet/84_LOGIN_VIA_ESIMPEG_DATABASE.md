# Login Survey Pemda via ESIMPEG Database

**Tanggal**: 6 April 2026  
**Status**: 🔄 ANALYSIS & SOLUTION

---

## 🎯 PERTANYAAN USER

"ini sudah terhubungan kedua api ini pada esimpeg_python dan survey_pemda_python apakah bisa login survey dari database via esimpeg python kah ini?"

---

## 📊 STATUS SAAT INI

### ✅ Yang Sudah Ada

1. **API Connection** - Survey Pemda bisa akses ESIMPEG API untuk data pegawai
2. **Password Sync Webhook** - Password otomatis sync saat user ganti password di ESIMPEG
3. **Import Command** - Ada command `import_users_from_esimpeg.py` untuk import users

### ❌ Yang Belum Ada

**Login langsung dari database ESIMPEG** - Saat ini Survey Pemda hanya bisa login dari database lokal (`survey_pemda_db.users`)

---

## 🔍 ANALISIS ARSITEKTUR

### Current Architecture (Login dari Database Lokal)

```
User Login di Survey Pemda
         ↓
FlexibleAuthBackend
         ↓
Query: survey_pemda_db.users
         ↓
✅ Login Success (jika user ada di database lokal)
❌ Login Failed (jika user TIDAK ada di database lokal)
```

**Problem**: User harus di-import dulu ke Survey Pemda database

---

## 💡 SOLUSI: 2 OPSI

### OPSI 1: Import Users dari ESIMPEG (Recommended)

**Cara Kerja**:
1. Import semua users dari ESIMPEG ke Survey Pemda
2. Login menggunakan database lokal Survey Pemda
3. Password sync otomatis via webhook

**Keuntungan**:
- ✅ Performance lebih cepat (query lokal)
- ✅ Tidak bergantung pada koneksi ESIMPEG
- ✅ Password sync otomatis sudah ada
- ✅ Command sudah tersedia

**Kekurangan**:
- ⚠️ Perlu sync manual untuk user baru
- ⚠️ Data user bisa out-of-sync

**Implementasi**:
```bash
# Import users dari ESIMPEG ke Survey Pemda
docker exec survey_pemda_python_app python manage.py import_users_from_esimpeg

# Atau dengan options
docker exec survey_pemda_python_app python manage.py import_users_from_esimpeg --dry-run
docker exec survey_pemda_python_app python manage.py import_users_from_esimpeg --include-inactive
```

---

### OPSI 2: Authentication Backend ke Database ESIMPEG (Real-time)

**Cara Kerja**:
1. User login di Survey Pemda
2. Backend query ke database ESIMPEG langsung
3. Jika valid, create/update user di Survey Pemda
4. Login success

**Keuntungan**:
- ✅ Selalu real-time (tidak perlu import)
- ✅ User baru otomatis bisa login
- ✅ Data selalu sync dengan ESIMPEG

**Kekurangan**:
- ⚠️ Bergantung pada koneksi database ESIMPEG
- ⚠️ Performance sedikit lebih lambat (query remote)
- ⚠️ Perlu setup database connection

**Implementasi**: Perlu buat custom authentication backend baru

---

## 🚀 IMPLEMENTASI OPSI 1 (Quick & Easy)

### Step 1: Update Database Connection

File: `projects/survey_pemda_python/core/settings.py`

**Current**:
```python
'esimpeg_source': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'esim_pegawai',  # ← Laravel database
    ...
}
```

**Update to**:
```python
'esimpeg_source': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'esimpeg_python_db',  # ← ESIMPEG Django database
    ...
}
```

### Step 2: Update Import Command

File: `projects/survey_pemda_python/apps/accounts/management/commands/import_users_from_esimpeg.py`

**Current**: Query dari `esim_pegawai.users` (Laravel)  
**Update**: Query dari `esimpeg_python_db.users` (ESIMPEG Django)

### Step 3: Run Import

```bash
# Dry run (preview)
docker exec survey_pemda_python_app python manage.py import_users_from_esimpeg --dry-run

# Actual import
docker exec survey_pemda_python_app python manage.py import_users_from_esimpeg

# Expected: Import 9703 users dari ESIMPEG
```

### Step 4: Test Login

```bash
# Test login dengan user dari ESIMPEG
# Buka: http://localhost:8005/
# Login dengan: prakom@admin.com / password
```

---

## 🚀 IMPLEMENTASI OPSI 2 (Advanced)

### Step 1: Create ESIMPEG Auth Backend

File: `projects/survey_pemda_python/apps/accounts/backends.py`

```python
class EsimpegDatabaseAuthBackend(ModelBackend):
    """
    Authentication backend yang query langsung ke database ESIMPEG
    Jika user valid, create/update di database lokal Survey Pemda
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # 1. Query ke database ESIMPEG
        from django.db import connections
        with connections['esimpeg_source'].cursor() as cursor:
            cursor.execute("""
                SELECT id, username, password, email, name, 
                       is_active, id_pegawai, user_id_opd
                FROM users
                WHERE username = %s OR email = %s
                LIMIT 1
            """, [username, username])
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Parse data
            user_data = {
                'id': row[0],
                'username': row[1],
                'password_hash': row[2],
                'email': row[3],
                'name': row[4],
                'is_active': row[5],
                'id_pegawai': row[6],
                'user_id_opd': row[7],
            }
        
        # 2. Verify password
        from django.contrib.auth.hashers import check_password
        if not check_password(password, user_data['password_hash']):
            return None
        
        # 3. Create or update user di database lokal
        user, created = User.objects.update_or_create(
            id=user_data['id'],
            defaults={
                'username': user_data['username'],
                'password': user_data['password_hash'],
                'email': user_data['email'],
                'name': user_data['name'],
                'is_active': user_data['is_active'],
                'id_pegawai': user_data['id_pegawai'],
                'user_id_opd': user_data['user_id_opd'],
            }
        )
        
        return user if user.is_active else None
```

### Step 2: Update Settings

File: `projects/survey_pemda_python/core/settings.py`

```python
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EsimpegDatabaseAuthBackend',  # ← NEW: Query ESIMPEG first
    'apps.accounts.backends.FlexibleAuthBackend',         # Fallback: Local database
    'django.contrib.auth.backends.ModelBackend',          # Fallback: Standard Django
]
```

### Step 3: Test

```bash
# Restart container
docker restart survey_pemda_python_app

# Test login
# User akan di-query dari ESIMPEG database
# Jika valid, otomatis create/update di Survey Pemda
```

---

## 📊 PERBANDINGAN OPSI

| Aspek | Opsi 1: Import | Opsi 2: Real-time Auth |
|-------|----------------|------------------------|
| **Setup** | ✅ Mudah (command sudah ada) | ⚠️ Perlu coding |
| **Performance** | ✅ Cepat (query lokal) | ⚠️ Sedikit lambat (query remote) |
| **Dependency** | ✅ Tidak bergantung ESIMPEG | ⚠️ Bergantung koneksi ESIMPEG |
| **Sync** | ⚠️ Manual (perlu re-import) | ✅ Otomatis real-time |
| **User Baru** | ⚠️ Perlu import dulu | ✅ Langsung bisa login |
| **Maintenance** | ✅ Minimal | ⚠️ Perlu monitor koneksi |

---

## 🎯 REKOMENDASI

### Untuk Development/Testing
**Gunakan OPSI 1** (Import Users)
- Lebih mudah setup
- Tidak perlu coding tambahan
- Command sudah tersedia

### Untuk Production
**Gunakan OPSI 1 + Scheduled Sync**
- Import users sekali
- Setup cron job untuk sync berkala (misal setiap hari)
- Password sync otomatis via webhook

```bash
# Cron job example (di container)
0 2 * * * cd /app && python manage.py import_users_from_esimpeg
```

---

## ✅ KESIMPULAN

**Jawaban untuk pertanyaan user**:

> "apakah bisa login survey dari database via esimpeg python kah ini?"

**Ya, BISA!** Ada 2 cara:

1. **OPSI 1 (Recommended)**: Import users dari ESIMPEG ke Survey Pemda
   - Command: `python manage.py import_users_from_esimpeg`
   - Setelah import, user bisa login di Survey Pemda
   - Password sync otomatis via webhook

2. **OPSI 2 (Advanced)**: Buat authentication backend yang query langsung ke ESIMPEG
   - Perlu coding custom backend
   - Login real-time dari database ESIMPEG
   - Auto create/update user di Survey Pemda

**Rekomendasi**: Gunakan OPSI 1 karena:
- ✅ Lebih mudah (command sudah ada)
- ✅ Performance lebih baik
- ✅ Password sync sudah otomatis via webhook
- ✅ Tidak bergantung pada koneksi ESIMPEG

---

## 📝 NEXT STEPS

Jika user mau implementasi OPSI 1:

1. Update database connection (esimpeg_source → esimpeg_python_db)
2. Update import command (query dari Django users table)
3. Run import command
4. Test login

Jika user mau implementasi OPSI 2:

1. Create EsimpegDatabaseAuthBackend
2. Update AUTHENTICATION_BACKENDS
3. Test login

---

**Status**: 📋 Menunggu konfirmasi user mau pakai opsi mana

