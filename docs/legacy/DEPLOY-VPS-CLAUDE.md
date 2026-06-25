# Panduan Deploy ESIMPEG-Python ke VPS (untuk Claude AI)

Dokumen ini berisi langkah-langkah lengkap untuk deploy/upload ulang project ESIMPEG-Python ke VPS.

## Prasyarat

- Akses SSH ke VPS (root@103.143.152.139)
- Docker dan Docker Compose sudah terinstall di VPS
- MySQL container `mysql-main` sudah running di VPS
- Project ESIMPEG-Python sudah ada di local: `projects/ESIMPEG-Python/`

Referensi:
- Tahap migrate + auto-seed yang benar: `docs/database/MIGRATE_AUTO_SEED_GUIDE.md`

## Langkah 1: Stop Container yang Sedang Berjalan

```bash
ssh root@103.143.152.139 "cd /root/ESIMPEG-Python && docker compose -f docker-compose.prod.yml down"
```

## Langkah 2: Upload Project dengan Rsync

Upload semua file kecuali yang tidak diperlukan:

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

**Catatan:**
- `--delete` akan menghapus file di VPS yang tidak ada di local
- `.env` di-exclude karena config production berbeda dengan local

## Langkah 3: Rebuild dan Start Container

```bash
ssh root@103.143.152.139 "cd /root/ESIMPEG-Python && docker compose -f docker-compose.prod.yml up -d --build"
```

**Penting:** Gunakan `docker-compose.prod.yml` karena berisi konfigurasi production termasuk `ALLOWED_HOSTS`.

## Langkah 4: Tunggu Container Siap

```bash
sleep 10
```

Atau cek status container:

```bash
ssh root@103.143.152.139 "docker ps | grep esimpeg-python"
```

Container siap jika status menunjukkan `(healthy)`.

## Langkah 5: Jalankan Migration

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py migrate"
```

**Catatan:** Database menggunakan MySQL shared (`mysql-main`) dengan nama database `esimpeg_python_db`.

## Langkah 6: Import Master Data Laravel (Wajib untuk Dropdown OPD/Unit Kerja)

Beberapa fitur (contoh: filter `Unit Kerja/Sub Unit Kerja`) bergantung pada master data dari Laravel.
Jika import belum dijalankan atau urutannya salah, endpoint dropdown seperti `/manajemen-relasi-organisasi/ajax/unit-kerja/` bisa mengembalikan `results: []`.

Jalankan import berikut **dengan urutan ini**:

```bash
# 1) Jenis Organisasi (wajib karena flag is_opd_induk dipakai untuk filter Unit Kerja)
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_md_jenis_organisasi --include-deleted"

# 2) Unit Organisasi (ms_opd)
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_ms_unit_organisasi --include-deleted"
```

Catatan:
- `import_md_jenis_organisasi` harus dijalankan lebih dulu agar `is_opd_induk` tersinkron dan filter Unit Kerja bekerja.
- Import aman dijalankan ulang kapan saja (sync/update_or_create).

## Langkah 7: Cleanup Menu Duplikat (Jika Ada Error)

Jika `seed_core_setup` error karena duplikat menu, jalankan cleanup:

```bash
# Buat script cleanup
cat > /tmp/cleanup_menu.py << 'EOF'
from apps.manajemen.models import MenuItem
from django.db.models import Count

duplicates = MenuItem.objects.values('name', 'parent_id').annotate(count=Count('id')).filter(count__gt=1)
print('Duplicate menus:')
for dup in duplicates:
    print(f"  Name: {dup['name']}, Parent ID: {dup['parent_id']}, Count: {dup['count']}")
    items = MenuItem.objects.filter(name=dup['name'], parent_id=dup['parent_id']).order_by('id')
    for item in items:
        print(f"    - ID: {item.id}, Active: {item.is_active}, Order: {item.order}")
    if items.count() > 1:
        to_delete = list(items)[1:]
        for item in to_delete:
            print(f"    Deleting ID: {item.id}")
            item.delete()
print('Cleanup done!')
EOF

# Upload ke VPS
scp /tmp/cleanup_menu.py root@103.143.152.139:/tmp/

# Jalankan cleanup
ssh root@103.143.152.139 "docker exec -i esimpeg-python python manage.py shell < /tmp/cleanup_menu.py"
```

## Langkah 8: Seed Core Setup

Jalankan seeder untuk permissions dan menu:

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py seed_core_setup"
```

Command ini akan menjalankan:
- `seed_permissions` - Permission modules/controls/functions/rules
- `seed_menu_categories` - Kategori sidebar
- `seed_menus` - Menu items
- `seed_menus_extend` - Extended menus (Akun Saya, dll)
- `seed_admin_access` - Admin access rules
- Seeder permissions untuk Manajemen Data, Kepegawaian, Integrasi SIASN

## Opsional: Sekali jalan (migrate + seed + import berurutan)

Kalau kamu ingin proses yang lebih simpel dan menghindari salah urutan import (FK constraint / duplicate), gunakan script:

```bash
chmod +x vps-migrate-seed.sh
RUN_IMPORT_LARAVEL_ALL_ORDERED=1 ./vps-migrate-seed.sh
```

Catatan:
- `RUN_IMPORT_LARAVEL_ALL_ORDERED=1` akan menjalankan `import_laravel_all_ordered --include-deleted`.
  - Semua command master data yang tersedia: `import_md_*` dan `import_bkn_*`.
  - Unit organisasi + jabatan + pendidikan + pegawai sesuai urutan aman.
  - Semua riwayat yang tersedia: `import_mr_*`.
  - Command `import_ms_*` tambahan (jika ada) yang aman dijalankan setelah `ms_pegawai` (contoh: `import_ms_tata_naskah_pegawai`).
- Rekomendasi: Untuk deployment baru / database kosong: gunakan `RUN_IMPORT_LARAVEL_ALL_ORDERED=1` agar semua tabel tersinkron sekaligus.
- Untuk kebutuhan cepat (hanya dropdown OPD): cukup jalankan Langkah 6.

## Langkah 9: Seed Super Admin Full Access

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py seed_superadmin_full_access"
```

## Langkah 10: Verifikasi Deployment

### Cek Status Container

```bash
ssh root@103.143.152.139 "docker ps | grep esimpeg-python"
```

### Test Akses Aplikasi

```bash
curl -I http://103.143.152.139:8005/
```

Harus return `HTTP/1.1 200 OK`.

### Verifikasi Dropdown Unit Kerja (OPD)

Endpoint ini harus mengembalikan `results` tidak kosong jika master data sudah benar:

```bash
curl -s http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/unit-kerja/ | head
```

Verifikasi cepat flag `is_opd_induk` dari Django:

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py shell -c \"from apps.master_data.models import MdJenisOrganisasi; print('jenis_org_total=', MdJenisOrganisasi.objects.count()); print('is_opd_induk_true=', MdJenisOrganisasi.objects.filter(is_opd_induk=True).count())\""
```

### Cek Command SIASN Tersedia

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py help | grep siasn"
```

Harus menampilkan:
- `seed_siasn_endpoint_rules`
- `seed_siasn_tokens`
- `setup_siasn_roles`
- `siasn_apply_data_utama`
- `siasn_batch_sync`

## Langkah 11: Setup Cron Job SIASN (Opsional)

Jika belum ada, tambahkan cron job untuk integrasi SIASN otomatis:

```bash
ssh root@103.143.152.139 "cat > /tmp/esimpeg_siasn_cron.txt << 'EOF'
# ESIMPEG-Python SIASN Integration Cron Jobs

# 1. Fetch SIASN data (minimal) - Run daily at 01:00
0 1 * * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --batch-size 50 --sleep-ms 150 >> /var/log/esimpeg_siasn_fetch.log 2>&1

# 2. Apply ETL data_utama - Run daily at 03:10
10 3 * * * docker exec -i esimpeg-python python manage.py siasn_apply_data_utama --since-minutes 1440 >> /var/log/esimpeg_siasn_etl.log 2>&1

# 3. Fetch SIASN data (integrasi lengkap) - Run monthly on 20th at 01:30
30 1 20 * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type integrasi --stale-hours 720 --batch-size 30 --sleep-ms 200 >> /var/log/esimpeg_siasn_integrasi.log 2>&1
EOF
cat /tmp/esimpeg_siasn_cron.txt"

# Tambahkan ke crontab
ssh root@103.143.152.139 "(crontab -l 2>/dev/null; echo ''; cat /tmp/esimpeg_siasn_cron.txt) | crontab -"

# Verifikasi cron terpasang
ssh root@103.143.152.139 "crontab -l | tail -10"
```

## Troubleshooting

### Error: "Invalid HTTP_HOST header"

Pastikan `ALLOWED_HOSTS` di `docker-compose.prod.yml` sudah include IP VPS:

```yaml
- ALLOWED_HOSTS=esimpeg-python.pesisirselatankab.go.id,172.16.30.139,103.143.152.139,localhost
```

Lalu restart container:

```bash
ssh root@103.143.152.139 "cd /root/ESIMPEG-Python && docker compose -f docker-compose.prod.yml restart esimpeg-python"
```

### Error: "MultipleObjectsReturned" saat Seeding

Jalankan cleanup menu duplikat (Langkah 6).

### Container Tidak Healthy

Cek logs:

```bash
ssh root@103.143.152.139 "docker logs esimpeg-python --tail 50"
```

### Dropdown Unit Kerja Kosong (results: [])

Jika endpoint `/manajemen-relasi-organisasi/ajax/unit-kerja/` mengembalikan:

```json
{ "results": [], "has_more": false }
```

Checklist:
- Pastikan import master data sudah dijalankan:
  - `import_md_jenis_organisasi --include-deleted`
  - `import_ms_unit_organisasi --include-deleted`
- Pastikan nilai `is_opd_induk_true` tidak 0 (lihat perintah verifikasi di atas).
- Pastikan koneksi `DATABASES['laravel']` valid di environment production.

### Masalah & Solusi: Field `is_opd_induk` (MdJenisOrganisasi)

Masalah:
- Field `is_opd_induk` ada di model Django `MdJenisOrganisasi`, tetapi pada beberapa database Laravel lama kolom tersebut tidak ada.
- Saat import dari Laravel dijalankan ulang, `is_opd_induk` bisa kembali `False` untuk semua record sehingga filter Unit Kerja (OPD induk) tidak bekerja.

Penyebab:
- Import command dibuat *backward compatible*: ia akan tetap jalan walaupun kolom baru tidak ada di database sumber.
- Import command mengecek kolom sumber lewat `INFORMATION_SCHEMA`.
  - Jika kolom `is_opd_induk` ada: nilai diambil dari database sumber.
  - Jika kolom tidak ada: import menggunakan default (mis. `False`) agar tidak error.

Solusi:
- Setelah import, lakukan seeding/penandaan ulang `is_opd_induk` untuk jenis organisasi yang termasuk OPD induk.
- Rekomendasi: pastikan proses seeding `is_opd_induk` dijalankan setelah import (terutama jika `is_opd_induk` tidak ada di database sumber).

## Daftar Endpoint AJAX (Internal)

Semua endpoint di bawah ini dipakai oleh komponen *remote searchable select* (`static/js/app.js` / `initSearchableSelect`) dan umumnya mengembalikan format JSON yang sama:

```json
{ "results": [{"value": "...", "label": "..."}], "has_more": false }
```

Parameter query yang umum:
- `q`: kata kunci pencarian
- `page`: halaman (1-based)
- `page_size`: jumlah item per halaman

### Manajemen Relasi Organisasi

Base path (sesuai routing): `/manajemen-relasi-organisasi/`

Panduan import cepat (rekomendasi untuk VPS):

```bash
# Sync seeder permissions/config dulu (agar perubahan terbaru ikut ke-deploy)
docker exec esimpeg-python python manage.py auto_seed --sync --permissions-only

# All-in-one (paling aman karena urutan dependency)
docker exec esimpeg-python python manage.py import_laravel_all_ordered --include-deleted

# Pastikan flag hasil import (mis. MdJenisOrganisasi.is_opd_induk) sudah benar,
# terutama jika kolomnya tidak ada di DB Laravel lama.
docker exec esimpeg-python python manage.py post_import_seed_flags
```

Catatan penting:

- Jangan menjalankan `import_ms_unit_organisasi` saja tanpa master import (`import_md_jenis_organisasi`).
  Banyak filter/relasi bergantung ke master flags (mis. `MdJenisOrganisasi.is_opd_induk`).
- Hindari menjalankan `import_laravel_all_ordered` dengan `--skip-master` kecuali kamu benar-benar paham dampaknya.

- **Jenis Organisasi (untuk filtering/OPD)**
  - URL: `/manajemen-relasi-organisasi/ajax/jenis-organisasi/`
  - Params:
    - `q`, `page`, `page_size`
    - `only_opd` (default `1`) untuk filter `is_opd_induk=True`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_jenis_organisasi_list`
  - Model: `MdJenisOrganisasi`
  - Import/seed guide:
    - Import:

      ```bash
      docker exec esimpeg-python python manage.py import_md_jenis_organisasi --include-deleted
      ```

    - Post-import seed (jika kolom `is_opd_induk` tidak ada di DB Laravel / nilainya semua `False`):

      ```bash
      docker exec esimpeg-python python manage.py post_import_seed_flags
      ```

    - Verify (Django shell):

      ```bash
      docker exec esimpeg-python python manage.py shell -c "from apps.master_data.models import MdJenisOrganisasi; print('total=',MdJenisOrganisasi.objects.count()); print('opd_induk_true=',MdJenisOrganisasi.objects.filter(is_opd_induk=True, deleted_at__isnull=True).count())"
      ```

    - Verify (SQL) (opsional):

      ```bash
      docker exec -i mysql-main mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e "USE esimpeg_python_db; SELECT COUNT(*) total, SUM(CASE WHEN is_opd_induk=1 THEN 1 ELSE 0 END) AS opd_induk_true FROM Md_jenis_organisasi WHERE deleted_at IS NULL;"
      ```

    - Verify (curl):

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/jenis-organisasi/?page_size=5" | head
      ```
 

- **Unit Kerja (OPD induk)**
  - URL: `/manajemen-relasi-organisasi/ajax/unit-kerja/`
  - Params: `q`, `page`, `page_size`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_unit_kerja_list`
  - Model: `MsUnitOrganisasi` (filter via relasi `type_opd__is_opd_induk` atau `id_unit__is_opd_induk`)
  - Import/seed guide:
    - Import (unit organisasi):

      ```bash
      docker exec esimpeg-python python manage.py import_ms_unit_organisasi --include-deleted
      ```

    - Dependency:
      - Pastikan `MdJenisOrganisasi.is_opd_induk=True` untuk OPD induk (lihat endpoint di atas).
    - Verify (Django shell):

      ```bash
      docker exec esimpeg-python python manage.py shell -c "from apps.master_data.models import MsUnitOrganisasi; print('total=',MsUnitOrganisasi.objects.count()); print('active=',MsUnitOrganisasi.objects.filter(deleted_at__isnull=True).exclude(status=0).count())"
      ```

    - Verify (curl):

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/unit-kerja/?page_size=5" | head
      ```

- **Sub Unit Kerja (tree, berdasarkan parent)**
  - URL: `/manajemen-relasi-organisasi/ajax/sub-unit-kerja/`
  - Params: `parent_id` (wajib), `q`, `page`, `page_size`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_sub_unit_kerja_list`
  - Model: `MsUnitOrganisasi`
  - Import/seed guide:
    - Import: sama dengan Unit Kerja (`import_ms_unit_organisasi`).
    - Verify (curl) contoh:

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/sub-unit-kerja/?parent_id=1&page_size=5" | head
      ```
 

- **Jabatan Struktural (berdasarkan OPD/Sub OPD)**
  - URL: `/manajemen-relasi-organisasi/ajax/jabatan-struktural/`
  - Params: `id_opd` (wajib), `id_sub_opd` (opsional), `q`, `page`, `page_size`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_jabatan_struktural_list`
  - Model: `MsJabatanStruktural`
  - Import/seed guide:
    - Import:

      ```bash
      docker exec esimpeg-python python manage.py import_ms_jabatan_struktural --include-deleted
      ```

    - Verify (curl) contoh:

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/jabatan-struktural/?id_opd=1&page_size=5" | head
      ```

- **Jabatan Non Struktural (fungsional umum)**
  - URL: `/manajemen-relasi-organisasi/ajax/jabatan-non-struktural/`
  - Params: `id_jenis_jabatan` (wajib), `q`, `page`, `page_size`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_jabatan_non_struktural_list`
  - Model: `MsJabatanNonStruktural`
  - Import/seed guide:
    - Import:

      ```bash
      docker exec esimpeg-python python manage.py import_ms_jabatan_non_struktural --include-deleted
      ```

    - Dependency:
      - Pastikan master `MdJenisJabatan` dan `MdKategoriJabatan` sudah ada (biasanya dari `import_laravel_all_ordered`).
    - Verify (curl) contoh:

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/jabatan-non-struktural/?id_jenis_jabatan=2&page_size=5" | head
      ```

- **BKN Jabatan Fungsional (untuk Jenis Jabatan=3)**
  - URL: `/manajemen-relasi-organisasi/ajax/bkn-jabatan-fungsional/`
  - Params: `q`, `page`, `page_size`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_bkn_jabatan_fungsional_list`
  - Model: `BknJabatanFungsional` (filter `deleted_at__isnull=True`)
  - Import/seed guide:
    - Import:

      ```bash
      docker exec esimpeg-python python manage.py import_bkn_jabatan_fungsional --include-deleted
      ```

    - Troubleshooting hasil kosong:
      - Cek jumlah row yang `deleted_at IS NULL` (di Django). Jika 0, biasanya data hasil import menyimpan `deleted_at='0000-00-00 00:00:00'`.
      - Solusi: jalankan ulang import setelah update code importer.
    - Verify (Django shell):

      ```bash
      docker exec esimpeg-python python manage.py shell -c "from apps.master_data.models import BknJabatanFungsional; print('total=',BknJabatanFungsional.objects.count()); print('deleted_null=',BknJabatanFungsional.objects.filter(deleted_at__isnull=True).count())"
      ```

    - Verify (curl):

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/bkn-jabatan-fungsional/?page_size=5" | head
      ```

- **BKN Sub Jabatan (berdasarkan Jabatan fungsional terpilih)**
  - URL: `/manajemen-relasi-organisasi/ajax/bkn-sub-jabatan/`
  - Params: `id_jabatan` (list; minimal 1), `q`, `page`, `page_size`
  - View: `apps.manajemen.manajemen_relasi_organisasi.ajax_bkn_sub_jabatan_list`
  - Model: `BknSubJabatan` (filter via `kel_jabatan_id` turunan dari `BknJabatanFungsional`)
  - Import/seed guide:
    - Import:

      ```bash
      docker exec esimpeg-python python manage.py import_bkn_sub_jabatan --include-deleted
      ```

    - Dependency:
      - Pastikan `import_bkn_jabatan_fungsional` sudah dijalankan dulu.
    - Verify (curl) contoh (isi `id_jabatan` dengan id BKN jabatan yang valid):

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-relasi-organisasi/ajax/bkn-sub-jabatan/?id_jabatan=1&page_size=5" | head
      ```

### Manajemen Aplikasi (Rules)

Base path (sesuai routing): `/manajemen-aplikasi/`

- **Rules: Controls search**
  - URL: `/manajemen-aplikasi/rules/ajax/controls/`
  - Params: `q`, `page`, `page_size`
  - View: `apps.manajemen.rules.ajax_controls_search`
  - Model: `PermissionControl`
  - Seed guide:
    - Data sumber: tabel internal Django (bukan import Laravel)
    - Pastikan seeding awal permission/rules sudah dijalankan (sesuai langkah deploy/seed proyek).
    - Verify (curl):

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-aplikasi/rules/ajax/controls/?page_size=5" | head
      ```

- **Rules: Functions search**
  - URL: `/manajemen-aplikasi/rules/ajax/functions/`
  - Params: `q`, `page`, `page_size`
  - View: `apps.manajemen.rules.ajax_functions_search`
  - Model: `PermissionFunction`
  - Seed guide:
    - Data sumber: tabel internal Django (bukan import Laravel)
    - Pastikan seeding awal permission/rules sudah dijalankan (sesuai langkah deploy/seed proyek).
    - Verify (curl):

      ```bash
      curl -s "http://103.143.152.139:8005/manajemen-aplikasi/rules/ajax/functions/?page_size=5" | head
      ```

### Command SIASN Tidak Ditemukan

Pastikan file command sudah ter-upload dan container sudah di-rebuild:

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python ls -la /app/apps/integrations/management/commands/ | grep siasn"
```

Jika tidak ada, ulangi Langkah 2 dan 3.

## Informasi Penting

### Nama Container

- Container name: `esimpeg-python`
- Service name di docker-compose: `esimpeg-python`

### Database

- Host: `mysql-main` (container MySQL shared)
- Database name: `esimpeg_python_db`
- User: sesuai environment variable di docker-compose.prod.yml
- Password: sesuai environment variable di docker-compose.prod.yml

### Port

- Application: `8005` (host) → `8000` (container)
- URL: http://103.143.152.139:8005/

### File Penting

- Docker Compose: `/root/ESIMPEG-Python/docker-compose.prod.yml`
- Logs: `/var/log/esimpeg_siasn_*.log`

## Seeder Tambahan (Opsional)

### Import Data dari Laravel

Jika perlu import data dari database Laravel:

```bash
# Import Unit Organisasi
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_ms_unit_organisasi --include-deleted"

# Import Pegawai
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_ms_pegawai --include-deleted"

# Import Riwayat (Pangkat, Jabatan, Pendidikan)
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_mr_pangkat --include-deleted"
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_mr_jabatan --include-deleted"
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_mr_pendidikan --include-deleted"

# Atau gunakan command komposit (all-in-one)
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_laravel_data --include-deleted"

# Rekomendasi (lebih aman): import berurutan sesuai dependency
# Ini menghindari error umum seperti:
# - Md_jenjang_pendidikan: duplicate id_bkn=0
# - Ms_daftar_pendidikan: foreign key constraint (kode_tingkat)
# - Ms_pegawai: foreign key/dirty 0 values
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_laravel_all_ordered --include-deleted"
```

### Seed Master Data

```bash
# Kategori Pegawai
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py seed_kategori_pegawai"

# Import Master Data dari Laravel
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_md_agama"
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_md_status_perkawinan"
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_md_jenjang_pendidikan"
```

## Checklist Deployment

- [ ] Stop container lama
- [ ] Upload project dengan rsync
- [ ] Rebuild container
- [ ] Tunggu container healthy
- [ ] Jalankan migrate
- [ ] Cleanup menu duplikat (jika perlu)
- [ ] Seed core setup
- [ ] Seed superadmin full access
- [ ] Verifikasi akses aplikasi (HTTP 200)
- [ ] Verifikasi command SIASN tersedia
- [ ] Setup cron job SIASN (jika belum)
- [ ] Import data dari Laravel (opsional)
- [ ] Test login dan akses menu

## Kontak

Jika ada masalah, cek:
1. Logs container: `docker logs esimpeg-python`
2. Logs aplikasi: `/app/logs/` di dalam container
3. Logs cron: `/var/log/esimpeg_siasn_*.log`


## Hasil Import Data (Status Terakhir)

### ✅ Berhasil Diimport

**Data BKN:**
- Bkn_lokasi_kerja: 28,761 rows
- Bkn_jabatan_fungsional: 1,520 rows
- Bkn_sub_jabatan: 2,521 rows
- Bkn_jenis_penugasan: 5 rows
- Bkn_jenis_mutasi: 2 rows
- Bkn_jenis_diklat: 25 rows
- Bkn_jenis_hukuman: 21 rows
- Bkn_alasan_hukuman: 45 rows
- Bkn_tingkat_hukdis: 3 rows
- Bkn_jenis_kenaikan_pangkat: 12 rows
- Bkn_jenis_penghargaan: 29 rows

**Master Data:**
- Md_agama: 13 rows
- Md_status_perkawinan: 4 rows
- Md_pangkat: 17 rows
- Md_eselon: 10 rows
- Md_jenjang_jabatan: 14 rows
- Md_jenis_jabatan: 3 rows
- Md_kategori_jabatan: 7 rows
- Md_kedudukan_pegawai: 23 rows
- Md_pejabat_menetapkan: 22 rows
- Md_jenis_surat: 14 rows
- Md_diklat_struktural: 8 rows

**Unit Organisasi & Jabatan:**
- Ms_unit_organisasi: 3,090 rows
- Ms_jabatan_struktural: 2,157 rows
- Ms_jabatan_non_struktural: 7,870 rows

### ⚠️ Error/Skip

- Jika ada error import, biasanya sumbernya adalah data legacy di Laravel (contoh duplikat pada kolom unik) atau referensi master yang belum ter-import.
- Jalankan ulang `import_laravel_all_ordered --include-deleted` setelah perbaikan/patch; command ini idempotent (upsert) dan aman diulang.

### Solusi untuk Error

Untuk memperbaiki error import, lakukan:
1. Identifikasi tabel/kolom yang menyebabkan error (lihat traceback).
2. Patch importer terkait agar robust terhadap data legacy (contoh: dedupe/merge untuk kolom unik) atau perbaiki data sumber.
3. Jalankan ulang `import_laravel_all_ordered --include-deleted`.

## Command Import Data Lengkap (One-liner)

Untuk import semua data sekaligus (gunakan dengan hati-hati):

```bash
ssh root@103.143.152.139 "docker exec esimpeg-python python manage.py import_laravel_data --include-deleted"
```

Command ini akan menjalankan import berurutan:
- import_ms_unit_organisasi
- import_ms_pegawai
- import_mr_pangkat
- import_mr_jabatan
- import_mr_pendidikan

Atau import manual satu per satu untuk kontrol lebih baik.
