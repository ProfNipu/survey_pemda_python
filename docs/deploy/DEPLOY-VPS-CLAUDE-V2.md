# Panduan Deploy ke VPS (V2) - DEPRECATED

> **DEPRECATED:** Dokumen ini sudah tidak direkomendasikan.
>
> Gunakan panduan terbaru:
> - `docs/deploy/DEPLOY-VPS-CLAUDE-V3.md`

Dokumen ini berisi langkah-langkah *bulletproof* untuk deploy/upload ulang project ESIMPEG-Python ke VPS. Pipeline ini telah diperbarui untuk mencegah *crash database* yang disebabkan oleh asinkronisasi antara perintah migrate dan import data dari sistem Laravel lama.

## Prasyarat
- Akses SSH ke VPS (`root@103.143.152.139`)
- Docker dan Docker Compose (`mysql-main` sudah running)
- Project ESIMPEG-Python di local (`projects/ESIMPEG-Python/`)

Referensi:
- Tahap migrate + auto-seed yang benar: `docs/database/MIGRATE_AUTO_SEED_GUIDE.md`

---

## TAHAP 1: PREPARATION & UPLOAD

### 1. Stop Container Lama
Hentikan container agar tidak ada proses yang *nyangkut*.
```bash
ssh root@103.143.152.139 "cd /root/ESIMPEG-Python && docker compose -f docker-compose.prod.yml down"
```

### 2. Upload Project (Rsync)
Sinkronkan kode terbaru ke VPS. (Hindari cache & environment lokal).
```bash
rsync -avz --progress --delete \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='staticfiles' \
  --exclude='media' \
  --exclude='.env' \
  --exclude='node_modules' \
  projects/ESIMPEG-Python/ root@103.143.152.139:/root/ESIMPEG-Python/
```

### 3. Rebuild dan Start Container
Bangun ulang image dan jalankan di background.
```bash
ssh root@103.143.152.139 "cd /root/ESIMPEG-Python && docker compose -f docker-compose.prod.yml up -d --build"
```
 Tunggu sekitar 10 detik dan pastikan statusnya `(healthy)` via `docker ps`.

---

## TAHAP 2: DATABASE & BOOTSTRAP (URUTAN KRUSIAL)

> **⚠️ PERINGATAN KERAS:** Urutan di bawah ini **MUTLAK** tidak boleh dibalik! Jangan pernah menjalankan skrip Import Data sebelum perintah Migrate selesai, karena akan menyebabkan "Column Not Found Error" (contoh: field `is_opd_induk`).

### 1. Eksekusi Skema Database (MIGRATE) - WAJIB PERTAMA!
Membangun struktur/kerangka tabel terbaru di database (termasuk kolom-kolom baru).
```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py migrate"
```

 Copy-paste (recommended untuk DB baru):

 ```bash
 ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py migrate"
 ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py auto_seed"
 ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py seed_superadmin_full_access"
 ```

Catatan:
 - Setelah `migrate`, sistem akan menjalankan `auto_seed` otomatis (via Django `post_migrate`) jika database terlihat kosong.
 - Untuk database yang sudah terisi dan kamu hanya ingin sinkron perubahan permissions terbaru, gunakan:

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py auto_seed --sync --permissions-only"
```

### 2. Bersihkan Residu Menu (CLEANUP)
Mencegah seeder gagal karena constraint `MenuItem` yang double.
```bash
ssh root@103.143.152.139 "cat > /tmp/cleanup_menu_inline.py << 'PYEOF'
from apps.manajemen.models import MenuItem
from django.db.models import Count
duplicates = MenuItem.objects.values('name', 'parent_id').annotate(count=Count('id')).filter(count__gt=1)
for dup in duplicates:
    items = MenuItem.objects.filter(name=dup['name'], parent_id=dup['parent_id']).order_by('id')
    if items.count() > 1:
        for item in list(items)[1:]:
            item.delete()
print('Cleanup done')
PYEOF"
ssh root@103.143.152.139 "docker exec -i esimpeg-python python manage.py shell < /tmp/cleanup_menu_inline.py"
```

### 3. Eksekusi Seeder Inti (CORE SETUP)
Suntik default permissions, menu sidebar, dan Setup Admin.
```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py seed_core_setup"
```

### 4. Setup Super Admin
Pastikan akun superadmin tersedia.

Catatan:
 - Saat database kosong, `auto_seed` (otomatis setelah `migrate`) akan menjalankan `seed_default_users` dan membuat user superadmin:
   - username: `Prakom@admin2025.com`
   - password: `Prakom@2025`
 - Alternate superadmin (common):
   - username: `admin`
   - password: `admin123`

Jika kamu ingin memastikan akses full admin untuk superadmin existing, jalankan:
```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py seed_superadmin_full_access"
```

 Catatan model permission:
 - Project ini tidak memakai flag hardcode seperti `is_super_admin` untuk grant semua akses.
 - Akses ditentukan oleh data di database: `PermissionModule` → `PermissionControl` → `PermissionFunction` → `PermissionRule`, lalu di-assign ke role/group via `RoleRule`.
 - Group `Super Admin` dibuat lewat seeder, dan akses penuh diberikan lewat `seed_superadmin_full_access`.

---

## TAHAP 3: DATA MIGRATION (SYNC DARI LARAVEL)

Gunakan *Custom Command* yang sudah dilengkapi pre-flight check (menolak jalan jika masih ada migrations yang belum diterapkan). Command akan membatalkan diri jika Tahap 2.1 (Migrate) kamu lewati.

### Eksekusi Import Berurutan (Recommended)
Jalankan satu perintah ini untuk menarik SEMUA master data, hierarki OPD, jabatan struktural/non-struktural, referensi pendidikan, data pegawai, dan riwayat.
```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_laravel_all_ordered --include-deleted"
```

Catatan:
 - Import ini tidak membuat user login aplikasi.
 - User login default dibuat oleh `auto_seed` (via `seed_default_users`) pada tahap setelah `migrate`.

 **Kenapa pakai `import_laravel_all_ordered`?**
 - Mengecek status migrations. Menolak jalan jika ada skema menggantung.
 - Menjalankan import dalam urutan dependency yang aman (master → unit organisasi → jabatan → pendidikan → pegawai → riwayat).
 - Menjalankan `post_import_seed_flags` di akhir agar flag/penyesuaian internal tetap konsisten.

---

## TAHAP 4: VERIFIKASI & CRON JOB

### 1. Verifikasi Aplikasi
Pastikan respons aplikasi stabil (HTTP 200).
```bash
curl -I http://103.143.152.139:8005/
```

### 2. Verifikasi Dropdown OPD
Pastikan unit organisasi berhasil masuk dan terfilter dengan benar berdasarkan `is_opd_induk`.
```bash
curl -s http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/unit-kerja/ | head
```

### 3. Setup Cron Job SIASN (Background Sync)
Pasang auto-sync data berkala ke API SIASN BKN via *crontab* VPS.
```bash
ssh root@103.143.152.139 "cat > /tmp/esimpeg_siasn_cron.txt << 'EOF'
# ESIMPEG-Python SIASN Integration Cron Jobs
0 1 * * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --batch-size 50 --sleep-ms 150 >> /var/log/esimpeg_siasn_fetch.log 2>&1
10 3 * * * docker exec -i esimpeg-python python manage.py siasn_apply_data_utama --since-minutes 1440 >> /var/log/esimpeg_siasn_etl.log 2>&1
30 1 20 * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type integrasi --stale-hours 720 --batch-size 30 --sleep-ms 200 >> /var/log/esimpeg_siasn_integrasi.log 2>&1
EOF
(crontab -l 2>/dev/null; echo ''; cat /tmp/esimpeg_siasn_cron.txt) | crontab -"
```

✅ **DEPLOYMENT SELESAI & AMAN!**
