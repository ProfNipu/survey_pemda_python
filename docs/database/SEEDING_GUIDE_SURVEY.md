# Survey Pemda Python — Seeding Guide

Dokumen ini untuk setup project Survey Pemda Python dengan sistem survey dinamis.

## 1) Jalankan project
```bash
docker compose up -d --build
```

## 2) Migration
```bash
docker exec survey_pemda_python_app python manage.py migrate
```

## 3) Seed core permissions + sidebar
Seeder utama (idempotent):
```bash
docker exec survey_pemda_python_app python manage.py seed_core_setup
```

Core setup ini mencakup:
- Permission modules/controls/functions/rules
- Sidebar menu items (Pengaturan Sistem → Pengaturan Aplikasi)

## 4) Buat user Super Admin
Kalau user sudah ada dan mau dijadikan Super Admin:
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin --user EMAIL_OR_USERNAME
```

Setelah itu jalankan:
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

## 5) Seed Survey JPT (Dynamic Survey System)

### 5a) Seed Jenis Survey & Pertanyaan
Seed data awal untuk survey JPT (7 pertanyaan):
```bash
docker exec survey_pemda_python_app python manage.py seed_survey_jpt
```

Data yang di-seed:
- **Jenis Survey**: JPT (Jabatan Pimpinan Tinggi)
- **Pertanyaan**: 7 pertanyaan (survey01 - survey07) dengan bobot masing-masing

### 5b) Seed Permissions Survey
Seed permissions untuk modul survey:
```bash
docker exec survey_pemda_python_app python manage.py seed_survey_permissions
```

Permissions yang dibuat:
- **Module**: survey
- **Controls**: jenis_survey, pertanyaan_survey
- **Functions**: view, create, edit, delete
- **Total Rules**: 8 permission rules

### 5c) Seed Menu Survey
Seed menu sidebar untuk modul survey:
```bash
docker exec survey_pemda_python_app python manage.py seed_survey_menu
```

Menu yang dibuat:
- **Kategori**: Survey (code 7)
- **Parent 1**: Penilaian JPT
  - Child: Daftar Penilaian (TODO)
  - Child: Tambah Penilaian (TODO)
  - Child: Laporan Hasil (TODO)
- **Parent 2**: Master Survey
  - Child: Jenis Survey (CRUD ✓)
  - Child: Pertanyaan Survey (CRUD ✓)

### 5d) Grant Permissions ke Superadmin
Berikan akses penuh ke superadmin:
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### 5e) Akses Menu Master Survey
Untuk mengelola jenis survey dan pertanyaan:
- **Jenis Survey**: `/survey/jenis-survey/`
- **Pertanyaan Survey**: `/survey/pertanyaan-survey/`

Atau akses via sidebar: Survey → Master Survey

**Fitur CRUD**:
- ✅ List dengan search & pagination
- ✅ Create dengan form validation
- ✅ Edit dengan HTMX support
- ✅ Delete dengan dependency check
- ✅ Filter by jenis survey (untuk pertanyaan)
- ✅ Permission-based access control

## 6) Seed API SIMPEG Integration

### 6a) Seed Menu API SIMPEG
Seed menu untuk integrasi API SIMPEG:
```bash
docker exec survey_pemda_python_app python manage.py seed_api_simpeg_menu
```

Menu yang dibuat:
- **Kategori**: Manajemen Integrasi (code 4)
- **Parent**: ESIMPEG
  - Child: Pegawai (URL: `/api-simpeg/pegawai/`)

### 6b) Import Data Pegawai dari BKPSDM
Jika ada database BKPSDM dengan tabel `pegawaiDataSementara`:
```bash
docker exec survey_pemda_python_app python manage.py import_pegawai_from_bkpsdm
```

Catatan:
- Pastikan koneksi database BKPSDM sudah dikonfigurasi di settings
- Data akan disimpan ke tabel `api_simpeg_pegawai`

## 7) Sistem Survey Dinamis

### Cara Kerja
Sistem survey ini dirancang **DINAMIS** sehingga:
- Bisa menambah jenis survey baru tanpa ubah kode
- Setiap jenis survey punya pertanyaan sendiri
- Pertanyaan bisa dikonfigurasi dengan bobot berbeda
- Sistem otomatis menghitung nilai terbobot

### Tabel Database
1. **survey_jenis**: Master jenis survey (JPT, 360, dll)
2. **survey_pertanyaan**: Pertanyaan per jenis survey (dengan bobot)
3. **survey_responden**: Data responden (penilai & yang dinilai)
4. **survey_jawaban**: Jawaban dengan nilai 1-5

### Interface CRUD (Custom Views)
Sistem menggunakan custom views dengan Tailwind CSS, bukan Django Admin:

**Jenis Survey** (`/survey/jenis-survey/`)
- List: Search, pagination (10/25/50/100), status badge
- Create: Form dengan validation
- Edit: HTMX support untuk smooth submission
- Delete: Dependency check (cek jumlah pertanyaan)

**Pertanyaan Survey** (`/survey/pertanyaan-survey/`)
- List: Search, filter by jenis survey, pagination
- Create: Form dengan dropdown jenis survey
- Edit: HTMX support
- Delete: Confirmation dengan SweetAlert2

### Menambah Jenis Survey Baru
1. Akses: Survey → Master Survey → Jenis Survey
2. Klik "Tambah Jenis Survey"
3. Isi form:
   - Kode: misal `SURVEY_360`
   - Nama: misal `Survey 360 Derajat`
   - Deskripsi: (opsional)
   - Is Active: ✓
4. Klik "Simpan"

### Menambah Pertanyaan untuk Survey
1. Akses: Survey → Master Survey → Pertanyaan Survey
2. Klik "Tambah Pertanyaan"
3. Isi form:
   - Jenis Survey: pilih dari dropdown
   - Kode Pertanyaan: misal `survey01`
   - Pertanyaan: teks pertanyaan
   - Urutan: nomor urut (untuk sorting)
   - Bobot: nilai bobot (default 1.0)
   - Is Active: ✓
4. Klik "Simpan"

### Perhitungan Nilai
Sistem otomatis menghitung:
- **Nilai Terbobot** = Nilai (1-5) × Bobot
- **Total Nilai** = Sum(Nilai Terbobot) untuk semua pertanyaan
- **Rata-rata** = Total Nilai / Sum(Bobot)

## 8) Restart Container
Setelah seeding, restart container untuk memastikan menu muncul:
```bash
docker restart survey_pemda_python_app
```

## 9) Akses Aplikasi
- **URL**: http://localhost:8006
- **Login**: gunakan user yang sudah dibuat di step 4

## 10) Troubleshooting

### Menu tidak muncul
```bash
docker exec survey_pemda_python_app python manage.py seed_survey_menu
docker restart survey_pemda_python_app
```

### Permission denied
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### Reset database
```bash
docker exec survey_pemda_python_app python manage.py flush --noinput
docker exec survey_pemda_python_app python manage.py migrate
# Lalu ulangi seeding dari step 3
```

## 11) Development Workflow

### Menambah Survey Baru (Contoh: Survey 360)
1. Buat jenis survey via Django Admin
2. Tambah pertanyaan untuk survey tersebut
3. Buat views/templates untuk form input (jika perlu custom UI)
4. Sistem sudah siap menerima data dan menghitung nilai

### Struktur Kode
- **Models**: `apps/survey_jpt/models.py`
- **Admin**: `apps/survey_jpt/admin.py`
- **Seeders**: `apps/survey_jpt/management/commands/`
- **Templates**: `apps/survey_jpt/templates/` (untuk custom UI)

## 12) Backup & Restore

### Backup Database
```bash
docker exec survey_pemda_python_mysql_check mysqldump -u root -p survey_pemda_python_db > backup.sql
```

### Restore Database
```bash
docker exec -i survey_pemda_python_mysql_check mysql -u root -p survey_pemda_python_db < backup.sql
```

## 13) Production Deployment

### Environment Variables
Pastikan set di `.env`:
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your-secret-key
DB_HOST=mysql-main
DB_NAME=survey_pemda_python_db
DB_USER=root
DB_PASSWORD=your-password
REDIS_HOST=redis-main
REDIS_DB=4
```

### Collect Static Files
```bash
docker exec survey_pemda_python_app python manage.py collectstatic --noinput
```

### Run Migrations
```bash
docker exec survey_pemda_python_app python manage.py migrate
```

### Seed Production Data
```bash
docker exec survey_pemda_python_app python manage.py seed_core_setup
docker exec survey_pemda_python_app python manage.py seed_survey_jpt
docker exec survey_pemda_python_app python manage.py seed_survey_permissions
docker exec survey_pemda_python_app python manage.py seed_survey_menu
docker exec survey_pemda_python_app python manage.py seed_superadmin --user admin@example.com
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

---

**Catatan**: Dokumen ini spesifik untuk project Survey Pemda Python. Untuk project ESIMPEG, lihat `SEEDING_GUIDE.md` yang terpisah.
