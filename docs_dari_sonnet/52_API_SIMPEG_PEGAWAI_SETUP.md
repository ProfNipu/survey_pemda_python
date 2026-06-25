# API SIMPEG Pegawai - Setup Guide

**Tanggal**: 31 Maret 2026  
**Status**: ✅ SIAP DIAKTIFKAN

---

## 🎯 Apa Ini?

Menu dan permission untuk akses data pegawai dari ESIMPEG API di Survey Pemda.

---

## ✅ Yang Sudah Ada

1. ✅ **Route**: `/api-simpeg/pegawai/` sudah ada
2. ✅ **View**: `pegawai_list` sudah ada
3. ✅ **Seeder Menu**: `seed_api_simpeg_menu.py` (BARU!)
4. ✅ **Seeder Permission**: `seed_api_simpeg_permissions.py` (BARU!)

---

## 🔧 Cara Aktivasi

### Step 1: Seed Menu

```bash
docker exec survey_pemda_python_app python manage.py seed_api_simpeg_menu
```

**Output:**
```
✓ Created category: Manajemen Integrasi
✓ Created parent menu: ESIMPEG
✓ Created child menu: Pegawai
```

**Menu yang dibuat:**
- Kategori: Manajemen Integrasi (code 4)
- Parent: ESIMPEG
  - Child: Pegawai → `/api-simpeg/pegawai/`

---

### Step 2: Seed Permissions

```bash
docker exec survey_pemda_python_app python manage.py seed_api_simpeg_permissions
```

**Output:**
```
✓ Created module: API SIMPEG
✓ Created control: Pegawai
✓ Created function: View
✓ Created function: Sync
✓ Created function: Export
✓ Created rule: api_simpeg.pegawai.view
✓ Created rule: api_simpeg.pegawai.sync
✓ Created rule: api_simpeg.pegawai.export
```

**Permissions yang dibuat:**
- Module: `api_simpeg`
- Control: `pegawai`
- Functions: `view`, `sync`, `export`
- Rules: 3 permission rules

---

### Step 3: Grant ke Super Admin

```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

**Output:**
```
✓ Granted all permissions to superadmin
```

---

### Step 4: Restart Container

```bash
docker restart survey_pemda_python_app
```

---

### Step 5: Akses Menu

**URL:** http://localhost:8006/api-simpeg/pegawai/

**Via Sidebar:**
```
Manajemen Integrasi
└─ ESIMPEG
   └─ Pegawai
```

---

## 📊 Permission Rules

| Rule Code | Description |
|-----------|-------------|
| `api_simpeg.pegawai.view` | Lihat daftar pegawai |
| `api_simpeg.pegawai.sync` | Sinkronisasi data pegawai dari ESIMPEG |
| `api_simpeg.pegawai.export` | Export data pegawai |

---

## 🧪 Testing

### Test 1: Cek Menu Muncul

```bash
# Login sebagai superadmin
# Buka: http://localhost:8006/
# Cek sidebar: Manajemen Integrasi → ESIMPEG → Pegawai
```

**Expected:** Menu muncul di sidebar ✅

---

### Test 2: Akses Halaman Pegawai

```bash
# Buka: http://localhost:8006/api-simpeg/pegawai/
```

**Expected:** Halaman list pegawai muncul ✅

---

### Test 3: Cek Permission

```bash
docker exec survey_pemda_python_app python manage.py shell

>>> from apps.manajemen.models import MsPermissionRule
>>> rules = MsPermissionRule.objects.filter(module__code='api_simpeg')
>>> for rule in rules:
...     print(rule.code)
api_simpeg.pegawai.view
api_simpeg.pegawai.sync
api_simpeg.pegawai.export
```

**Expected:** 3 permission rules ✅

---

## 🔍 Troubleshooting

### Menu Tidak Muncul

```bash
# Re-seed menu
docker exec survey_pemda_python_app python manage.py seed_api_simpeg_menu

# Restart
docker restart survey_pemda_python_app

# Clear cache
docker exec survey_pemda_python_app python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

### Permission Denied

```bash
# Re-grant permissions
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

---

### Cek Superadmin Punya Permission

```bash
docker exec survey_pemda_python_app python manage.py shell

>>> from apps.accounts.models import User
>>> from apps.manajemen.models import MsRole
>>> 
>>> # Cek superadmin role
>>> superadmin_role = MsRole.objects.get(code='superadmin')
>>> print(f"Superadmin role: {superadmin_role.name}")
>>> 
>>> # Cek permissions
>>> permissions = superadmin_role.permissions.filter(module__code='api_simpeg')
>>> print(f"API SIMPEG permissions: {permissions.count()}")
>>> for perm in permissions:
...     print(f"  - {perm.code}")
```

**Expected:**
```
Superadmin role: Super Admin
API SIMPEG permissions: 3
  - api_simpeg.pegawai.view
  - api_simpeg.pegawai.sync
  - api_simpeg.pegawai.export
```

---

## 📝 Summary

### Sebelum

❌ Menu API SIMPEG tidak ada di sidebar  
❌ Permission tidak ada  
❌ Superadmin tidak bisa akses

### Sesudah

✅ Menu API SIMPEG muncul di sidebar  
✅ Permission sudah dibuat (3 rules)  
✅ Superadmin bisa akses halaman pegawai

---

## 🎯 Next Steps

1. ✅ Seed menu
2. ✅ Seed permissions
3. ✅ Grant ke superadmin
4. ✅ Restart container
5. ✅ Test akses halaman

**Sekarang superadmin bisa akses:** http://localhost:8006/api-simpeg/pegawai/

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `apps/api_simpeg/urls.py` | Route definition |
| `apps/api_simpeg/views.py` | View function |
| `apps/api_simpeg/management/commands/seed_api_simpeg_menu.py` | Menu seeder |
| `apps/api_simpeg/management/commands/seed_api_simpeg_permissions.py` | Permission seeder |
| `docs_dari_sonnet/03_SEEDING_GUIDE_SURVEY.md` | Updated seeding guide |

---

**Terakhir Update**: 31 Maret 2026  
**Versi**: 1.0  
**Status**: ✅ Siap Diaktifkan
