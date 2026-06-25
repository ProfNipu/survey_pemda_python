# Validasi Migrate + Seeder + Import Database (ESIMPEG-Python)

Dokumen ini adalah SOP singkat untuk memastikan **struktur tabel (migrations)** dan **data awal (seeders/import)** selalu konsisten, khususnya saat **deploy ke VPS**.

## Ruang Lingkup

- Django project: ESIMPEG-Python
- Database: MySQL (default di env project)
- Fokus utama: konsistensi antara:

1. **Schema** (Django migrations) di database
2. **Master data** hasil seeding (permissions/menus/default users)
3. **Import data** (contoh: `import_ms_unit_organisasi` dan import lain yang digunakan project)

## Prinsip

- **Migrations** adalah sumber kebenaran untuk schema.
- **Seeders** harus **idempotent** (aman dijalankan berulang) agar bisa dipakai sebagai proses sinkronisasi saat deploy.
- **Importers** adalah proses best-effort; untuk yang kritikal, wajib ada validasi hasilnya.

## A. Validasi Database (Service, Koneksi, dan Konfigurasi)

Bagian ini memastikan DB benar-benar siap sebelum menjalankan `migrate/seed/import`.

### A1. Pastikan service DB hidup (Docker)

Di host:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

Pastikan container MySQL (contoh: `mysql-main`) statusnya **healthy**.

### A2. Pastikan database target ada

Masuk ke MySQL dan cek database:

```sql
SHOW DATABASES;
```

Pastikan `DB_NAME` (contoh: `esimpeg_python_db`) ada.

Jika belum ada (opsional, hanya untuk setup awal):

```sql
CREATE DATABASE IF NOT EXISTS esimpeg_python_db;
```

### A3. Test koneksi dari container aplikasi

Tujuan: memastikan jaringan Docker + DNS service name (misal `mysql-main`) bisa di-resolve dari container aplikasi.

Di container app:

```bash
python manage.py dbshell
```

Atau test minimal (jika `dbshell` tidak tersedia):

- Pastikan `DB_HOST` sesuai (contoh: `mysql-main`)
- Pastikan `DB_PORT` sesuai (contoh: `3306`)

### A4. Validasi user & privileges

Pastikan user DB yang dipakai aplikasi punya hak yang cukup untuk:

- create/alter/drop table (untuk migrations)
- insert/update (untuk seeder/import)

Contoh cek privileges:

```sql
SHOW GRANTS FOR '<DB_USER>'@'%';
```

### A5. Validasi charset/collation database

Untuk menghindari masalah text search/sort/emoji/karakter khusus, pastikan charset sesuai.

```sql
SELECT @@character_set_server, @@collation_server;
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';
```

Rekomendasi umum MySQL 8:

- `utf8mb4`
- `utf8mb4_0900_ai_ci`

### A6. Validasi time zone (opsional tapi disarankan)

```sql
SELECT @@time_zone, @@system_time_zone, NOW();
```

Tujuan: menghindari kebingungan timestamp antara server/DB/app.

## B. Cek Konfigurasi Database yang Aktif

Di server/container aplikasi:

1. Pastikan file env yang dipakai.
2. Catat parameter koneksi:

- `DB_ENGINE`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`

Contoh dari `.env` ESIMPEG-Python:

- `DB_HOST=mysql-main`
- `DB_NAME=esimpeg_python_db`

## C. Validasi Migrations (Schema)

### C1. Cek status migrations via Django

Jalankan di container app:

```bash
python manage.py showmigrations
```

Atau fokus ke app tertentu:

```bash
python manage.py showmigrations manajemen_aplikasi
```

### C2. Pastikan migrate sudah dijalankan

```bash
python manage.py migrate
```

### C3. Validasi di database (langsung)

Masuk ke MySQL lalu cek:

```sql
USE <DB_NAME>;
SELECT app, name, applied
FROM django_migrations
ORDER BY applied DESC
LIMIT 50;
```

### C4. Validasi schema tabel via container aplikasi (tanpa login MySQL)

Jika dependencies Python hanya tersedia di container (umumnya begitu di setup Docker), gunakan cara ini untuk memastikan **tabel di DB benar-benar sesuai migration**.

1. Pastikan container app aktif (contoh nama: `esimpeg_python_app`).

2. Jalankan `manage.py shell` dari dalam container, lalu eksekusi `SHOW TABLES/COLUMNS/INDEX`.

Contoh validasi untuk tabel `permission_controls`:

```bash
docker exec -i esimpeg_python_app python manage.py shell -c "from django.db import connection; \
print('DB:', connection.settings_dict.get('NAME'), 'HOST:', connection.settings_dict.get('HOST'), 'PORT:', connection.settings_dict.get('PORT')); \
with connection.cursor() as c: \
    c.execute(\"SHOW TABLES LIKE 'permission_controls'\"); \
    print('TABLE_EXISTS:', bool(c.fetchone())); \
    c.execute(\"SHOW COLUMNS FROM permission_controls\"); \
    print('COLUMNS:'); \
    [print(row) for row in c.fetchall()]; \
    c.execute(\"SHOW INDEX FROM permission_controls\"); \
    print('INDEXES:'); \
    [print(row) for row in c.fetchall()];"
```

Ekspektasi minimal (harus match dengan migration/model):

- kolom: `id`, `nama_kontrol` (unique), `label_kontrol`, `deskripsi_kontrol`, `created_at`, `updated_at`
- indexes: `PRIMARY(id)` dan unique untuk `nama_kontrol`

Jika ingin cek tabel lain, cukup ganti nama tabel di perintah di atas:

- `permission_functions`
- `permission_rules`
- `permission_modules`

## D. Validasi Seeders (Data Awal)

### D1. Seed awal untuk database kosong

Gunakan perintah:

```bash
python manage.py auto_seed
```

Perintah ini ditujukan untuk kondisi database baru (kosong).

### D2. Sinkronisasi seeder saat deploy (database sudah ada)

Jika ada perubahan (misalnya penambahan function baru seperti `move`), jalankan:

```bash
python manage.py auto_seed --sync --permissions-only
```

Atau jika ingin sync sekaligus menu & user (kalau semua seeders idempotent):

```bash
python manage.py auto_seed --sync
```

### D3. Validasi data hasil seeder (contoh: permission_functions)

Contoh verifikasi tabel **Manajemen Fungsi**:

```sql
USE <DB_NAME>;
SHOW COLUMNS FROM permission_functions;
SELECT COUNT(*) AS total_functions FROM permission_functions;
SELECT id, nama_fungsi, label_fungsi
FROM permission_functions
ORDER BY id DESC
LIMIT 20;
```

Ekspektasi minimal:

- `view`, `create`, `edit`, `delete`, `export`, `import`, `approve`, `reject`, `print`, `sync`
- `bulk_delete` (khusus untuk aksi hapus banyak / multi delete)
- Tambahan function lain sesuai modul (misal `move` untuk relasi organisasi)

### D4. Validasi permission terpisah: delete single vs bulk delete

Catatan:

- `delete` digunakan untuk **hapus satu data** (single delete)
- `bulk_delete` digunakan untuk **hapus banyak data sekaligus** (bulk/multi delete)

Langkah validasi:

1. Pastikan function `bulk_delete` ada (setelah seeding/sync):

```sql
USE <DB_NAME>;
SELECT nama_fungsi, label_fungsi
FROM permission_functions
WHERE nama_fungsi IN ('delete', 'bulk_delete')
ORDER BY nama_fungsi;
```

2. Pastikan rules untuk kontrol target sudah ada:

```sql
-- contoh untuk halaman Manajemen Fungsi (pengaturan.permission_function)
SELECT pm.nama_module, pc.nama_kontrol, pf.nama_fungsi, pr.is_active
FROM permission_rules pr
JOIN permission_modules pm ON pm.id = pr.module_id
JOIN permission_controls pc ON pc.id = pr.control_id
JOIN permission_functions pf ON pf.id = pr.function_id
WHERE pm.nama_module = 'pengaturan'
  AND pc.nama_kontrol = 'permission_function'
  AND pf.nama_fungsi IN ('delete', 'bulk_delete');
```

3. Smoke test UI (tanpa reset DB):

- Login sebagai role yang **punya** `delete` tapi **tidak punya** `bulk_delete`
  - Icon delete per-row harus muncul
  - Tombol bulk delete harus tidak muncul
  - Jika user memaksa request `action=bulk_delete`, harus ditolak (403/redirect + error)

4. Smoke test UI untuk role yang punya `bulk_delete`:

- Login sebagai role yang **punya** `bulk_delete`
  - Tombol bulk delete harus muncul
  - Bulk delete harus berhasil

### D5. Catatan perubahan UI/UX granular (button hidden) + validasi

Tujuan: memastikan perubahan seeder/permission tidak hanya aman di backend, tapi juga rapi di UI (tombol tidak tampil jika user tidak punya akses).

Perubahan yang harus diperhatikan:

- Bulk delete dipisah menjadi permission khusus `bulk_delete` (tidak otomatis sama dengan `delete`).
- Tombol Create/Edit/Delete/Bulk actions disembunyikan (hidden) jika user tidak punya permission terkait.
- Tombol navigasi `Kembali`/`Batal` disembunyikan jika user tidak punya permission untuk membuka halaman tujuan (menghindari tombol yang mengarah ke 403).

Validasi yang disarankan:

1. Jalankan sinkronisasi permission saat deploy/update:

```bash
python manage.py auto_seed --sync --permissions-only
```

2. Pastikan function minimal berikut ada (termasuk yang baru):

```sql
USE <DB_NAME>;
SELECT nama_fungsi
FROM permission_functions
WHERE nama_fungsi IN ('view','create','edit','delete','bulk_delete','export')
ORDER BY nama_fungsi;
```

3. Smoke test UI (contoh di halaman Manajemen Fungsi / Kontrol):

- Role hanya punya `view`
  - List halaman harus bisa dibuka
  - Tombol `Tambah`, icon `Edit/Delete`, tombol `Bulk Delete`, dan `Export` tidak tampil
- Role punya `delete` tapi tidak punya `bulk_delete`
  - Icon delete per-row tampil
  - Tombol bulk delete tidak tampil
- Role punya `bulk_delete`
  - Tombol bulk delete tampil dan bisa dipakai

4. Smoke test navigasi:

- Jika user tidak punya akses ke dashboard granular (`pengaturan.permission_dashboard.view`)
  - Tombol `Kembali` di halaman list granular tidak tampil
- Jika user tidak punya akses `view` ke halaman list tujuan
  - Tombol `Kembali` dan `Batal` di form (Tambah/Edit) tidak tampil

Catatan: meskipun tombol disembunyikan, backend tetap wajib menolak action tanpa permission (anti tembak request).

### D6. Catatan route canonical untuk dashboard granular

Untuk menghindari URL legacy membingungkan, route canonical dashboard granular adalah:

- `/manajemen-aplikasi/akses-granular/`

Dan route legacy tetap tersedia sebagai redirect:

- `/manajemen-aplikasi/permissions-roles/` → redirect ke `/manajemen-aplikasi/akses-granular/`
- `/permissions/` → redirect ke `/manajemen-aplikasi/akses-granular/`

### D7. Validasi Manajemen Module (permission_modules)

Tujuan: memastikan tabel `permission_modules` sesuai migrate dan perubahan permission/UI pada halaman **Manajemen Module** aman.

1. Validasi schema table (dari dalam container):

```bash
docker exec -i esimpeg_python_app python manage.py shell -c "from django.db import connection; \
with connection.cursor() as c: \
    c.execute(\"SHOW COLUMNS FROM permission_modules\"); \
    print('COLUMNS:'); [print(r) for r in c.fetchall()]; \
    c.execute(\"SHOW INDEX FROM permission_modules\"); \
    print('INDEXES:'); [print(r) for r in c.fetchall()]"
```

Minimal yang harus ada:

- Kolom: `id`, `nama_module`, `label_module`, `deskripsi_module`, `icon`, `order`, `is_active`, `created_at`, `updated_at`
- Index/unique: `nama_module` unique

2. Validasi seed permission (pastikan rule untuk `pengaturan.permission_module.*` ada):

```bash
python manage.py auto_seed --sync --permissions-only
```

3. Smoke test permission di UI Manajemen Module:

- Role hanya `view`
  - Bisa buka list
  - Tombol `Tambah Module`, bulk export, bulk delete tidak tampil
  - Icon aksi Edit/Delete per row tidak tampil
- Role punya `export` saja
  - Tombol bulk export tampil dan bisa export
  - Jika memaksa request export tanpa permission → harus 403
- Role punya `delete` tapi tidak punya `bulk_delete`
  - Delete per row tampil
  - Bulk delete tidak tampil
- Role punya `bulk_delete`
  - Bulk delete tampil dan bisa dipakai

## E. Validasi Import (ETL / Sinkronisasi)

### E1. Jalankan import yang diperlukan (Ordered Import)

Direkomendasikan menggunakan import berurutan untuk menjamin konsistensi relasi master data dan organisasi:

```bash
python manage.py import_laravel_all_ordered --include-deleted
```

Catatan:

- Import ini membutuhkan konektivitas ke database sumber (jika ada multi-DB).
- Jika import ini wajib untuk produksi, jalankan manual dan pastikan tidak di-skip.

### E2. Validasi hasil import

Lakukan pengecekan minimal:

- Tabel target terisi
- Jumlah record masuk sesuai ekspektasi
- Tidak ada error fatal di log

Contoh (sesuaikan dengan tabel target import):

```sql
SELECT COUNT(*) FROM <tabel_target>;
SELECT * FROM <tabel_target> LIMIT 5;
```

## F. Checklist Deploy (Local/VPS) — End-to-End

### F1. Checklist database (wajib)

1. Pastikan container DB hidup/healthy.
2. Pastikan `DB_NAME` ada.
3. Pastikan user DB punya privileges yang cukup.
4. Pastikan charset/collation sesuai.
5. Pastikan container app bisa konek ke DB host (`mysql-main`).

### F2. Jalankan migrations

```bash
python manage.py migrate
```

### F3. Jalankan seeder

- Setup awal (DB kosong):

```bash
python manage.py auto_seed
```

- Deploy update (DB sudah ada, tapi ada perubahan seeder/permissions):

```bash
python manage.py auto_seed --sync --permissions-only
```

### F4. Jalankan import data utuh (Data Migration)

```bash
python manage.py import_laravel_all_ordered --include-deleted
```

### F5. Validasi cepat via SQL (smoke test)

```sql
USE <DB_NAME>;

-- 1) migration terbaru tercatat
SELECT app, name, applied
FROM django_migrations
ORDER BY applied DESC
LIMIT 20;

-- 2) validasi hasil explicit seeding OPD Induk (SANGAT PENTING!)
SELECT jo_01, is_opd_induk FROM Md_jenis_organisasi WHERE is_opd_induk = 1 LIMIT 10;

-- 3) contoh validasi Manajemen Fungsi
SELECT COUNT(*) AS total_functions FROM permission_functions;

-- 3) cek sample data
SELECT id, nama_fungsi, label_fungsi
FROM permission_functions
ORDER BY id DESC
LIMIT 20;
```

### F6. Validasi aplikasi (smoke test UI)

1. Login sebagai Super Admin.
2. Buka halaman:

- Manajemen Aplikasi → Manajemen Fungsi
- Manajemen Aplikasi → Rules

3. Pastikan:

- List tampil
- Create/Edit/Delete sesuai permission
- Tidak ada error 500

## G. Checklist Deploy VPS (Ringkas)

1. Pastikan env DB benar (host, nama DB, user/pass).
2. Jalankan migrations:

```bash
python manage.py migrate
```

3. Sync seeder permissions (agar perubahan terbaru masuk):

```bash
python manage.py auto_seed --sync --permissions-only
```

4. Jalankan Ordered Import Data:

```bash
python manage.py import_laravel_all_ordered --include-deleted
```

5. Validasi cepat via SQL:

- `django_migrations` terbaru ada
- `permission_functions` berisi function terbaru
- nilai kolom `is_opd_induk` pada `Md_jenis_organisasi` terisi `1` untuk organisasi terkait (Dinas/Badan/dsb).
- tabel import unit organisasi dan pegawai telah terisi

## F. Troubleshooting

- Jika seeder tidak menambah data baru:
  - pastikan seeder menggunakan `get_or_create` / update jika label berubah
  - jalankan `auto_seed --sync --permissions-only`

- Jika migration tidak tercatat:
  - cek apakah app label migration sesuai (`showmigrations`)
  - pastikan container menjalankan kode versi terbaru

