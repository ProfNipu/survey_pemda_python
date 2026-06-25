# ESIMPEG-Python — Seeding Guide (Reusable)

Dokumen ini untuk setup ulang project (instansi/data berbeda) dengan metode yang sama.

## 1) Jalankan project
- `docker compose up -d --build`

## 2) Migration
- `docker exec esimpeg_python_app python manage.py migrate`

## 3) Seed core permissions + sidebar
Seeder utama (idempotent):
- `docker exec esimpeg_python_app python manage.py seed_core_setup`

Core setup ini mencakup:
- Permission modules/controls/functions/rules (termasuk Manajemen Aplikasi + Master Data)
- Sidebar menu items (termasuk Pengaturan Sistem → Pengaturan Aplikasi)

### Cara pakai (VPS / server): script sekali jalan (migrate + seed)

File:
- `vps-migrate-seed.sh`

Tujuan:
- Menjalankan `migrate` lalu `seed_core_setup` dalam urutan aman.
- Opsional menjalankan import unit organisasi dari DB Laravel dan/atau `collectstatic`.

#### Jalankan (mode Docker container)

Jika container Django bernama `esimpeg_python_app`:

```bash
chmod +x vps-migrate-seed.sh
./vps-migrate-seed.sh
```

Jika nama container berbeda:

```bash
ESIMPEG_PYTHON_CONTAINER=nama_container ./vps-migrate-seed.sh
```

#### Jalankan (mode venv / non-docker)

Kalau kamu tidak pakai Docker dan `python manage.py ...` bisa jalan langsung di host (venv sudah aktif), script ini tetap akan jalan:

```bash
chmod +x vps-migrate-seed.sh
./vps-migrate-seed.sh
```

#### Opsi (environment variables)

- `RUN_IMPORT_MS_UNIT_ORG=1`
  - Akan menjalankan:
    - `python manage.py import_ms_unit_organisasi --include-deleted`
- `RUN_COLLECTSTATIC=1`
  - Akan menjalankan:
    - `python manage.py collectstatic --noinput`

Contoh:

```bash
RUN_IMPORT_MS_UNIT_ORG=1 RUN_COLLECTSTATIC=1 ./vps-migrate-seed.sh
```

#### Catatan: mana yang offline vs butuh koneksi

- **Offline (DB lokal saja):**
  - `migrate`
  - `seed_core_setup` (permissions, menu, integrations permissions, dll)
- **Butuh koneksi DB Laravel:**
  - `import_ms_unit_organisasi --include-deleted`
- **Butuh koneksi DB Laravel (sekali jalan untuk unit + pegawai + riwayat):**
  - `import_laravel_data --include-deleted`
- **Butuh akses internet + credential:**
  - Fetch SIASN (API BKN)

## 3b) Import data dari DB Laravel (Unit Organisasi + Pegawai + Riwayat)

Jika kamu ingin menyiapkan data **Relasi Unit Kerja**, **Tabel Pegawai**, dan **Riwayat** dari database Laravel (bukan dari SIASN), gunakan command komposit:

```bash
docker exec -i esimpeg_python_app python manage.py import_laravel_data --include-deleted
```

Command ini akan memanggil (berurutan):
- `import_ms_unit_organisasi`
- `import_ms_pegawai`
- `import_mr_pangkat`
- `import_mr_jabatan`
- `import_mr_pendidikan`

## 3c) Import data dari DB Laravel (Lengkap & Berurutan — Recommended)

Jika kamu ingin import yang lebih lengkap dan menghindari masalah urutan dependency (FK/relasi) gunakan command komposit:

```bash
docker exec -i esimpeg_python_app python manage.py import_laravel_all_ordered --include-deleted
```

Perilaku command ini (one-shot):
- Import master/reference yang tersedia: `import_md_*` dan `import_bkn_*`.
- Import unit organisasi + jabatan + pendidikan + pegawai dalam urutan aman.
- Import riwayat yang tersedia: `import_mr_*`.
- Menjalankan `import_ms_*` tambahan (jika ada) yang aman dijalankan setelah `ms_pegawai` (contoh: `import_ms_tata_naskah_pegawai`).

Catatan:
- Command ini idempotent (upsert) dan aman dijalankan ulang.
- Jika ada error, biasanya karena data legacy di Laravel (contoh duplikat kolom unik) atau ada master data yang belum ter-import.

### Opsi flags

- `--skip-unit`
- `--skip-pegawai`
- `--skip-riwayat`

### Catatan koneksi database

Semua command `import_*` yang mengambil data dari Laravel memakai koneksi:
- `DATABASES['laravel']`

Jadi **cukup set 1 kali** koneksi `laravel` (host/user/password/db) di `.env`/settings server, maka seluruh import (unit organisasi, pegawai, riwayat) akan bisa jalan.

## 4) Jadwal Integrasi SIASN Otomatis (Cron) - Pegawai Aktif

Command batch (baru):
- `docker exec -i esimpeg_python_app python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24`

Penting:
- Setelah deploy ke VPS, job ini **tidak jalan otomatis** kalau kamu belum pasang scheduler (cron/systemd timer).
- Jadi kamu perlu menambahkan entry cron di VPS supaya jalan otomatis mulai jam tertentu (mis. jam 01:00).

Definisi *pegawai aktif* mengikuti halaman **Tabel Pegawai** (ms_pegawai_list):
- `deleted_at IS NULL`
- exclude `A_01 = 99`
- exclude `B_11__status_hitung = 2`

Cache freshness memakai `SiasnPegawai.updated_at`.

### Konfigurasi dinamis endpoint berdasarkan Kategori Pegawai (B_09)

Beberapa endpoint SIASN (contoh: `data_utama`) bisa berbeda path tergantung kategori pegawai (field `MsPegawai.B_09`).

Solusi di project ini:
- Tabel config: `siasn_endpoint_rule`
- UI pengaturan: **Integrasi SIASN → Konfigurasi Endpoint SIASN**
- Saat fetch berjalan, endpoint `data_utama` akan memakai template dari tabel tersebut jika ada.

Template memakai placeholder `{nip}`.

Contoh default yang umum:
- Kategori 1/2/3 (CPNS/PNS/PPPK):
  - `/pns/data-utama/{nip}`
- Kategori 4 (Paruh Waktu):
  - `/pns/data-utama/paruhwaktu/{nip}`

Catatan:
- Kalau rule kosong, sistem fallback ke endpoint default (hardcoded) `/pns/data-utama/`.
- Jika ada kategori baru, cukup tambah/ubah template via UI (tanpa edit code).

### Rekomendasi jadwal

- **Harian (nightly) 01:00**: `minimal` (cepat) untuk menjaga cache 1 hari.
- **Bulanan tgl 20 01:30**: `integrasi` (lengkap) untuk refresh data lengkap.

### Cara pasang cron di VPS (host)

1) Buka editor crontab:

```bash
crontab -e
```

2) Tambahkan baris cron (contoh di bawah).

3) Simpan & keluar, lalu cek list cron:

```bash
crontab -l
```

### Contoh cron di VPS (host)

Nightly minimal:

```bash
0 1 * * * docker exec -i esimpeg_python_app python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --batch-size 50 --sleep-ms 150 >> /var/log/esimpeg_siasn_minimal.log 2>&1
```

Bulanan integrasi (tgl 20):

```bash
30 1 20 * * docker exec -i esimpeg_python_app python manage.py siasn_batch_sync --fetch-type integrasi --stale-hours 720 --batch-size 30 --sleep-ms 200 >> /var/log/esimpeg_siasn_integrasi.log 2>&1
```

Catatan:
- Gunakan `--limit` jika ingin uji coba dulu (mis. `--limit 100`).
- Command memakai lock file default `/tmp/esimpeg_siasn_batch_sync.lock` supaya tidak jalan dobel.
- Untuk mode bulanan integrasi, `--stale-hours 720` (30 hari) direkomendasikan supaya tidak “ulang full integrasi” untuk pegawai yang baru saja diproses.

### Cara test sekarang (manual)

Test cepat (ambil 10 pegawai aktif pertama yang cache-nya stale > 24 jam):

```bash
docker exec -i esimpeg_python_app python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --limit 10
```

Test integrasi lengkap (lebih lama):

```bash
docker exec -i esimpeg_python_app python manage.py siasn_batch_sync --fetch-type integrasi --stale-hours 24 --limit 3
```

Jika output menunjukkan `total=0`, artinya semua cache masih fresh (updated_at < 24 jam). Kamu bisa:
- turunkan `--stale-hours` (mis. `--stale-hours 1`), atau
- hapus beberapa record cache `siasn_pegawai` untuk uji.

### Cara test lewat tombol UI

Di halaman **Integrasi SIASN → Dokumentasi Fetch SIASN**, ada tombol:
- **Test Batch Sync (10 pegawai aktif)**

Tombol ini menjalankan batch kecil (limit 10) dan menampilkan ringkasan hasil lewat SweetAlert.

Jika kamu ingin memastikan kategori sidebar sesuai label terbaru (Pengaturan Sistem + Master Data + Data Induk), jalankan:
- `docker exec esimpeg_python_app python manage.py seed_menu_categories`
- `docker exec esimpeg_python_app python manage.py seed_menus`

Catatan:
- Menu `Dashboard` ditampilkan sebagai `Beranda` dan berada di kategori sidebar `Beranda`.
- Kategori sidebar `Master Data` berisi group utama `Data Induk` (tanpa nested `Data Induk`).

Jika kamu ingin memastikan **Super Admin** punya akses penuh (disarankan):
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

## 4) Buat user Super Admin / set user jadi Super Admin
Kalau user sudah ada dan mau dijadikan Super Admin:
- `docker exec esimpeg_python_app python manage.py seed_superadmin --user EMAIL_OR_USERNAME`

Jika command menolak argumen (mis. `--user` tidak dikenali), cek command yang terdaftar:
- `docker exec esimpeg_python_app python manage.py help seed_superadmin`

Setelah itu jalankan:
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

## 4b) Dokumentasi API (Manajemen Aplikasi)
Menu:
- Pengaturan Sistem → Pengaturan Aplikasi → Dokumentasi API

Sumber data:
- Dokumentasi API disimpan di database Python pada tabel `api_documentation`
- Data awal/sinkronisasi berasal dari file: `docs/API-ENDPOINTS.md` (di repo ESIMPEG-Python)

Jika ada penambahan / perubahan endpoint API:
- Update isi file: `docs/API-ENDPOINTS.md`
- Format yang dipakai (per endpoint):
  - Header: `#### <nomor>. <judul>`
  - Baris URL: `**URL:** `<path>``
  - Baris Method: `**Method:** `GET` atau `GET` or `POST``
  - Parameters (optional):
    - `**Parameters:**`
    - `- param_name - keterangan`

- Jalankan sync ke database (idempotent/upsert):
  - `docker exec esimpeg_python_app python manage.py migrate manajemen_aplikasi`
  - `docker exec esimpeg_python_app python manage.py seed_api_documentation`

- Jika ingin menonaktifkan record lama yang sudah tidak ada di markdown:
  - `docker exec esimpeg_python_app python manage.py seed_api_documentation --deactivate-missing`

- Setelah sync, refresh halaman:
  - `/manajemen-aplikasi/api-documentation/`

Catatan seeding untuk instance baru:
- Jika di instance baru menu/permission belum muncul, jalankan:
  - `docker exec esimpeg_python_app python manage.py seed_core_setup`
  - `docker exec esimpeg_python_app python manage.py seed_api_documentation`
  - `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

## 5) Seed master data (contoh)
Contoh master data `Md_kategori_pegawai`:
- `docker exec esimpeg_python_app python manage.py migrate master_data`
- `docker exec esimpeg_python_app python manage.py seed_kategori_pegawai`

Import master data dari database Laravel `esim_pegawai` (contoh: `Md_agama`):
- Pastikan koneksi DB Laravel (default akan memakai host/user/password yang sama dengan DB utama):
  - `LARAVEL_DB_HOST` (default: `DB_HOST`)
  - `LARAVEL_DB_NAME` (default: `esim_pegawai`)
  - `LARAVEL_DB_USER` (default: `DB_USER`)
  - `LARAVEL_DB_PASSWORD` (default: `DB_PASSWORD`)
  - `LARAVEL_DB_PORT` (default: `DB_PORT`)
- Jalankan migration (membuat tabel `Md_agama` di DB Python jika belum ada):
  - `docker exec esimpeg_python_app python manage.py migrate master_data`
- Jalankan import (idempotent/upsert):
  - `docker exec esimpeg_python_app python manage.py import_md_agama`

## 6) CRUD Manajemen Data: Kategori Pegawai
URL:
- List: `/manajemen-data/kategori-pegawai/`
- Create: `/manajemen-data/kategori-pegawai/create/`
- Edit: `/manajemen-data/kategori-pegawai/<id>/edit/`
- Delete: `/manajemen-data/kategori-pegawai/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_kategori_pegawai/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_kategori_pegawai.view`
- `manajemen_data.md_kategori_pegawai.create`
- `manajemen_data.md_kategori_pegawai.edit`
- `manajemen_data.md_kategori_pegawai.delete`

Status field:
- `Aktif` = `1`
- `Non Aktif` = `0`

Catatan UX:
- Saat submit form Create/Edit via HTMX, sukses akan menampilkan SweetAlert terlebih dahulu.
- Redirect ke halaman list dilakukan setelah user klik tombol `OK`.

Sidebar:
- Master Data → Data Induk → Kategori Pegawai

## 6b) CRUD Manajemen Data: Agama
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_agama`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/agama/`
- Create: `/manajemen-data/agama/create/`
- Edit: `/manajemen-data/agama/<id>/edit/`
- Delete: `/manajemen-data/agama/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_agama/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_agama.view`
- `manajemen_data.md_agama.create`
- `manajemen_data.md_agama.edit`
- `manajemen_data.md_agama.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Agama

## 6c) CRUD Manajemen Data: Status Perkawinan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_status_perkawinan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/status-perkawinan/`
- Create: `/manajemen-data/status-perkawinan/create/`
- Edit: `/manajemen-data/status-perkawinan/<id>/edit/`
- Delete: `/manajemen-data/status-perkawinan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_status_perkawinan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_status_perkawinan.view`
- `manajemen_data.md_status_perkawinan.create`
- `manajemen_data.md_status_perkawinan.edit`
- `manajemen_data.md_status_perkawinan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Status Perkawinan

## 6d) CRUD Manajemen Data: Jenjang Pendidikan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_jenjang_pendidikan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/jenjang-pendidikan/`
- Create: `/manajemen-data/jenjang-pendidikan/create/`
- Edit: `/manajemen-data/jenjang-pendidikan/<id>/edit/`
- Delete: `/manajemen-data/jenjang-pendidikan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_jenjang_pendidikan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_jenjang_pendidikan.view`
- `manajemen_data.md_jenjang_pendidikan.create`
- `manajemen_data.md_jenjang_pendidikan.edit`
- `manajemen_data.md_jenjang_pendidikan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Jenjang Pendidikan

## 6d-2) Master Data Import: Daftar Pendidikan (`Ms_daftar_pendidikan`)
Sumber data:
- DB Laravel (`DATABASES['laravel']` / default DB name: `esim_pegawai`)
- Tabel sumber: `Ms_pendidikan`

Target di ESIMPEG-Python:
- App: `apps.master_data`
- Model: `MsDaftarPendidikan`
- Tabel target (DB default): `Ms_daftar_pendidikan`

Langkah:
- Jalankan migration (create + rename table jika belum ada):
  - `docker exec esimpeg_python_app python manage.py migrate master_data`
- Jalankan import (idempotent/upsert):
  - `docker exec esimpeg_python_app python manage.py import_ms_daftar_pendidikan`

Opsi:
- Include soft-deleted rows:
  - `docker exec esimpeg_python_app python manage.py import_ms_daftar_pendidikan --include-deleted`
- Skip jika ID sudah ada:
  - `docker exec esimpeg_python_app python manage.py import_ms_daftar_pendidikan --skip-existing`

Catatan kompatibilitas:
- Command lama masih tersedia sebagai alias:
  - `docker exec esimpeg_python_app python manage.py import_ms_pendidikan`

## 6d-3) CRUD Manajemen Data: Daftar Pendidikan
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/daftar-pendidikan/`
- Create: `/manajemen-data/daftar-pendidikan/create/`
- Edit: `/manajemen-data/daftar-pendidikan/<id>/edit/`
- Delete: `/manajemen-data/daftar-pendidikan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_daftar_pendidikan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.ms_daftar_pendidikan.view`
- `manajemen_data.ms_daftar_pendidikan.create`
- `manajemen_data.ms_daftar_pendidikan.edit`
- `manajemen_data.ms_daftar_pendidikan.delete`

## 7) Data Pegawai: Kepegawaian → Riwayat → Tabel Pegawai (`ms_pegawai`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data pegawai dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_ms_pegawai`
- Include soft-deleted rows (jika perlu):
  - `docker exec esimpeg_python_app python manage.py import_ms_pegawai --include-deleted`

URL:
- List (baru): `/manajemen-data-kepegawaian/ms-pegawai/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Ms_pegawai/`
  - `list.html`
  - `partials/_table.html`

Permission keys:
- `kepegawaian.Ms_pegawai.view`
- `kepegawaian.Ms_pegawai.create`
- `kepegawaian.Ms_pegawai.edit`
- `kepegawaian.Ms_pegawai.delete`

Relasi & aturan penting (MsPegawai / `Ms_pegawai`):
- Relasi Master Data (ORM):
  - `id_opd`, `id_sub_opd` → `master_data.MsUnitOrganisasi(id_opd)`
  - `id_jenis_jabatan` → `master_data.MdJenisJabatan(id)`
  - `id_jabatan` → `master_data.MsJabatanStruktural(id_jabatan)`
  - `id_jfu_jft` → `master_data.MsJabatanNonStruktural(id_jabatan_fungsional)`
  - `id_sub_jabatan` → `master_data.BknJabatanFungsional(id)`
  - `id_lokasi` → `master_data.BknLokasiKerja(id)`
  - `B_07` → `master_data.MdAgama(id)`
  - `B_09` → `master_data.MdKategoriPegawai(id)`
  - `B_11` → `master_data.MdKedudukanPegawai(id)`
  - `D_05` (Pangkat CPNS) → `master_data.MdPangkat(id)`
  - `E_05` (Pangkat PNS) → `master_data.MdPangkat(id)`
  - `I_06` (Eselon) → `master_data.MdEselon(id)`
  - `I_07` (Jenjang Jabatan) → `master_data.MdJenjangJabatan(id)`
  - `J_01` (Status Perkawinan) → `master_data.MdStatusPerkawinan(id)`
  - `id_penjabat` (jenis penugasan) → `master_data.BknJenisPenugasan(id)`
  - `id_opd_rangkap` → `master_data.MsUnitOrganisasi(id_opd)`
  - `id_sub_opd_rangkap` → `master_data.MsUnitOrganisasi(id_opd)`
  - `id_jabatan_rangkap` → `master_data.MsJabatanStruktural(id_jabatan)`
- Aturan filter list “Aktif/Non Aktif”:
  - Aktif: `A_01 != 99` dan `B_11.status_hitung != 2`
  - Non Aktif: `A_01 == 99` atau `B_11.status_hitung == 2`
- Aturan “Pangkat Terakhir” (berdasarkan `F_03`):
  - Kategori pegawai `B_09` id `1/2` (CPNS/PNS): `F_03` di-resolve ke `MdPangkat`.
  - Selain itu (PPPK/paruh waktu/dll): `F_03` ditampilkan sebagai angka romawi berdasarkan urutan `MdPangkat.order_by('id')`.
  - Nilai `F_03` kosong/0 akan ditampilkan `-`.
- Format masa kerja:
  - `F_04` (Masa Kerja pangkat) dan `G_02` (Masa Kerja gaji) memakai format `0000` (2 digit tahun + 2 digit bulan) dan ditampilkan menjadi `YY tahun MM bulan`.
- Catatan integritas relasi:
  - Relasi dibuat dengan `db_constraint=False` agar aman walau ada data yang belum punya master.
  - Jika master data belum di-seed/import, relasi akan tampil kosong (`-`) dan tidak memblokir halaman.

## 7b) Data Pegawai: Kepegawaian → Riwayat → Riwayat Pangkat (`Mr_pangkat`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Catatan menu (Opsi A / recommended):
- Struktur sidebar untuk modul ini dibuat 3 level: `Kepegawaian → Riwayat → Riwayat Pangkat`.
- Menu bisa diatur lewat UI Manajemen Menu: `/manajemen-aplikasi/menu/` (ubah parent, order, icon, active).
- `seed_menus` akan memastikan struktur default tetap konsisten dan melakukan cleanup menu duplikat legacy (contoh: menonaktifkan `Tabel Pegawai` yang tidak sengaja berada di bawah `Kepegawaian → Riwayat`).

Import data riwayat pangkat dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_pangkat`
- Include soft-deleted rows (jika perlu):
  - `docker exec esimpeg_python_app python manage.py import_mr_pangkat --include-deleted`

URL:
- List: `/manajemen-data-kepegawaian/mr-pangkat/`
- Detail: `/manajemen-data-kepegawaian/mr-pangkat/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_pangkat/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_pangkat.view`
- `kepegawaian.Mr_pangkat.create`
- `kepegawaian.Mr_pangkat.edit`
- `kepegawaian.Mr_pangkat.delete`

## 7c) Data Pegawai: Kepegawaian → Riwayat → Riwayat Jabatan (`Mr_jabatan`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Catatan menu (Opsi A / recommended):
- Struktur sidebar untuk modul ini dibuat 3 level: `Kepegawaian → Riwayat → Riwayat Jabatan`.
- Menu bisa diatur lewat UI Manajemen Menu: `/manajemen-aplikasi/menu/`.

Import data riwayat jabatan dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_jabatan`
- Include soft-deleted rows (jika perlu):
  - `docker exec esimpeg_python_app python manage.py import_mr_jabatan --include-deleted`

Catatan mapping field (penting):
- `id_jabatan` di tabel legacy bersifat "polymorphic" (1 kolom, 2 sumber master data), sehingga **tidak bisa** dibuat 1 `ForeignKey` langsung di Django.
  - Jika `id_jenis_jabatan == 1`:
    - `id_jabatan` merefer ke `MsJabatanStruktural.id_jabatan`
    - Di Django di-resolve ke `MrJabatan.id_jabatan_struktural`
  - Jika `id_jenis_jabatan != 1`:
    - `id_jabatan` merefer ke `MsJabatanNonStruktural.id_jabatan_fungsional`
    - Di Django di-resolve ke `MrJabatan.id_jabatan_non_struktural`
- `JF_01` (legacy char) tetap disimpan, namun untuk relasi master digunakan:
  - `MrJabatan.JF_01_ref` → `MdPejabatMenetapkan.id` (nullable)
- `JF_02` (legacy char) tetap disimpan, namun untuk relasi master digunakan:
  - `MrJabatan.JF_02_ref` → `MdJenjangJabatan.id` (nullable)

Ringkasan relasi/ForeignKey yang sudah dibuat di Django (semua `db_constraint=False`):
- `MrJabatan.id_pegawai` → `MsPegawai.id`
- `MrJabatan.id_jenis_jabatan` → `MdJenisJabatan.id`
- `MrJabatan.id_opd` → `MsUnitOrganisasi.id_opd` (to_field)
- `MrJabatan.id_sub_opd` → `MsUnitOrganisasi.id_opd` (to_field)
- `MrJabatan.JF_04` → `MdEselon.id`
- `MrJabatan.JF_01_ref` → `MdPejabatMenetapkan.id` (sementara `JF_01` tetap legacy char)
- `MrJabatan.JF_02_ref` → `MdJenjangJabatan.id` (sementara `JF_02` tetap legacy char)
- `MrJabatan.id_jabatan_struktural` → `MsJabatanStruktural.id_jabatan` (to_field)
- `MrJabatan.id_jabatan_non_struktural` → `MsJabatanNonStruktural.id_jabatan_fungsional` (to_field)
- `MrJabatan.JF_23` → `BknJenisMutasi.id`
- `MrJabatan.JF_24` → `BknJenisPenugasan.id`
- `MrJabatan.JF_25_ref` → `BknSubJabatan.id` (sementara `JF_25` tetap legacy `varchar`)
- `MrJabatan.MM_07` → `MdJenisSurat.id` (Jenis Surat Keputusan)

Panduan tampilan (UI) disarankan:
- Tampilkan "Jabatan" dengan prioritas:
  - `id_jabatan_struktural` jika ada
  - else `id_jabatan_non_struktural` jika ada
  - else fallback ke `JF_03` atau `id_jabatan`
- Tampilkan "Nama Jabatan" dengan prioritas:
  - `JF_03A` jika ada
  - else `JF_03`
- Tampilkan "Pejabat Menetapkan" dengan prioritas:
  - `JF_01_ref` jika ada, else fallback ke `JF_01`
- Tampilkan "Jenjang" dengan prioritas:
  - `JF_02_ref` jika ada, else fallback ke `JF_02`

URL:
- List: `/manajemen-data-kepegawaian/mr-jabatan/`
- Detail: `/manajemen-data-kepegawaian/mr-jabatan/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_jabatan/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_jabatan.view`
- `kepegawaian.Mr_jabatan.create`
- `kepegawaian.Mr_jabatan.edit`
- `kepegawaian.Mr_jabatan.delete`

## 7d) Data Pegawai: Kepegawaian → Riwayat → Riwayat Pendidikan (`Mr_pendidikan`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Catatan menu (Opsi A / recommended):
- Struktur sidebar untuk modul ini dibuat 3 level: `Kepegawaian → Riwayat → Riwayat Pendidikan`.
- Menu bisa diatur lewat UI Manajemen Menu: `/manajemen-aplikasi/menu/`.

Import data riwayat pendidikan dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_pendidikan`
- Include soft-deleted rows (jika perlu):
  - `docker exec esimpeg_python_app python manage.py import_mr_pendidikan --include-deleted`

URL:
- List: `/manajemen-data-kepegawaian/mr-pendidikan/`
- Detail: `/manajemen-data-kepegawaian/mr-pendidikan/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_pendidikan/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_pendidikan.view`
- `kepegawaian.Mr_pendidikan.create`
- `kepegawaian.Mr_pendidikan.edit`
- `kepegawaian.Mr_pendidikan.delete`

## 7e) Data Pegawai: Kepegawaian → Tata Naskah Pegawai (`ms_tata_naskah_pegawai`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Catatan menu:
- Modul ini ditempatkan langsung di bawah `Kepegawaian` (sejajar dengan `Tabel Pegawai` dan group `Riwayat`).
- Menu bisa diatur lewat UI Manajemen Menu: `/manajemen-aplikasi/menu/`.

Import data dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_ms_tata_naskah_pegawai`
- Include soft-deleted rows (jika perlu):
  - `docker exec esimpeg_python_app python manage.py import_ms_tata_naskah_pegawai --include-deleted`

URL:
- List: `/manajemen-data-kepegawaian/ms-tata-naskah-pegawai/`
- Detail: `/manajemen-data-kepegawaian/ms-tata-naskah-pegawai/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Ms_tata_naskah_pegawai/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Ms_tata_naskah_pegawai.view`
- `kepegawaian.Ms_tata_naskah_pegawai.create`
- `kepegawaian.Ms_tata_naskah_pegawai.edit`
- `kepegawaian.Ms_tata_naskah_pegawai.delete`

## 7f) Data Pegawai: Kepegawaian → Riwayat → Riwayat Ortu (`Mr_ortu`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat ortu dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_ortu`
- Include soft-deleted rows (jika perlu):
  - `docker exec esimpeg_python_app python manage.py import_mr_ortu --include-deleted`

URL:
- List: `/manajemen-data-kepegawaian/mr-ortu/`
- Detail: `/manajemen-data-kepegawaian/mr-ortu/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_ortu/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_ortu.view`
- `kepegawaian.Mr_ortu.create`
- `kepegawaian.Mr_ortu.edit`
- `kepegawaian.Mr_ortu.delete`

## 7g) Data Pegawai: Kepegawaian → Riwayat → Riwayat Pasangan (`Mr_pasangan` dari `Mr_keluarga`)
Catatan:
- Data pasangan & anak berasal dari tabel yang sama: `Mr_keluarga`.
- Filter pasangan: `KF_02 = 1`.

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data keluarga (1x untuk pasangan+anak):
- `docker exec esimpeg_python_app python manage.py import_mr_keluarga`

URL:
- List: `/manajemen-data-kepegawaian/mr-pasangan/`
- Detail: `/manajemen-data-kepegawaian/mr-pasangan/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_pasangan/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_pasangan.view`
- `kepegawaian.Mr_pasangan.create`
- `kepegawaian.Mr_pasangan.edit`
- `kepegawaian.Mr_pasangan.delete`

## 7h) Data Pegawai: Kepegawaian → Riwayat → Riwayat Anak (`Mr_anak` dari `Mr_keluarga`)
Catatan:
- Data pasangan & anak berasal dari tabel yang sama: `Mr_keluarga`.
- Filter anak: `KF_02 = 2`.

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data keluarga (1x untuk pasangan+anak):
- `docker exec esimpeg_python_app python manage.py import_mr_keluarga`

URL:
- List: `/manajemen-data-kepegawaian/mr-anak/`
- Detail: `/manajemen-data-kepegawaian/mr-anak/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_anak/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_anak.view`
- `kepegawaian.Mr_anak.create`
- `kepegawaian.Mr_anak.edit`
- `kepegawaian.Mr_anak.delete`

## 7i) Data Pegawai: Kepegawaian → Riwayat → Diklat Struktural (`Mr_diklat_struktural`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat diklat struktural dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_diklat_struktural`

URL:
- List: `/manajemen-data-kepegawaian/mr-diklat-struktural/`
- Detail: `/manajemen-data-kepegawaian/mr-diklat-struktural/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_diklat_struktural/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_diklat_struktural.view`
- `kepegawaian.Mr_diklat_struktural.create`
- `kepegawaian.Mr_diklat_struktural.edit`
- `kepegawaian.Mr_diklat_struktural.delete`

## 7j) Data Pegawai: Kepegawaian → Riwayat → Diklat Fungsional (`Mr_diklat_fungsional`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat diklat fungsional dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_diklat_fungsional`

URL:
- List: `/manajemen-data-kepegawaian/mr-diklat-fungsional/`
- Detail: `/manajemen-data-kepegawaian/mr-diklat-fungsional/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_diklat_fungsional/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_diklat_fungsional.view`
- `kepegawaian.Mr_diklat_fungsional.create`
- `kepegawaian.Mr_diklat_fungsional.edit`
- `kepegawaian.Mr_diklat_fungsional.delete`

## 7k) Data Pegawai: Kepegawaian → Riwayat → Diklat Teknis (`Mr_diklat_teknis`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat diklat teknis dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_diklat_teknis`

URL:
- List: `/manajemen-data-kepegawaian/mr-diklat-teknis/`
- Detail: `/manajemen-data-kepegawaian/mr-diklat-teknis/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_diklat_teknis/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_diklat_teknis.view`
- `kepegawaian.Mr_diklat_teknis.create`
- `kepegawaian.Mr_diklat_teknis.edit`
- `kepegawaian.Mr_diklat_teknis.delete`

## 7l) Data Pegawai: Kepegawaian → Riwayat → Seminar (`Mr_seminar`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat seminar dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_seminar`

URL:
- List: `/manajemen-data-kepegawaian/mr-seminar/`
- Detail: `/manajemen-data-kepegawaian/mr-seminar/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_seminar/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_seminar.view`
- `kepegawaian.Mr_seminar.create`
- `kepegawaian.Mr_seminar.edit`
- `kepegawaian.Mr_seminar.delete`

## 7m) Data Pegawai: Kepegawaian → Riwayat → Angka Kredit (`Mr_angka_kredit`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat angka kredit dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_angka_kredit`

URL:
- List: `/manajemen-data-kepegawaian/mr-angka-kredit/`
- Detail: `/manajemen-data-kepegawaian/mr-angka-kredit/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_angka_kredit/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_angka_kredit.view`
- `kepegawaian.Mr_angka_kredit.create`
- `kepegawaian.Mr_angka_kredit.edit`
- `kepegawaian.Mr_angka_kredit.delete`

## 7n) Data Pegawai: Kepegawaian → Riwayat → Hukuman Disiplin (`Mr_hukuman_disiplin`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat hukuman disiplin dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_hukuman_disiplin`

URL:
- List: `/manajemen-data-kepegawaian/mr-hukuman-disiplin/`
- Detail: `/manajemen-data-kepegawaian/mr-hukuman-disiplin/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_hukuman_disiplin/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_hukuman_disiplin.view`
- `kepegawaian.Mr_hukuman_disiplin.create`
- `kepegawaian.Mr_hukuman_disiplin.edit`
- `kepegawaian.Mr_hukuman_disiplin.delete`

## 7o) Data Pegawai: Kepegawaian → Riwayat → SKP (`Mr_skp`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat SKP dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_skp`

URL:
- List: `/manajemen-data-kepegawaian/mr-skp/`
- Detail: `/manajemen-data-kepegawaian/mr-skp/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_skp/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_skp.view`
- `kepegawaian.Mr_skp.create`
- `kepegawaian.Mr_skp.edit`
- `kepegawaian.Mr_skp.delete`

## 7p) Data Pegawai: Kepegawaian → Riwayat → Tugas Ke Luar Negeri (`Mr_tugas_ln`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat tugas luar negeri dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_tugas_ln`

URL:
- List: `/manajemen-data-kepegawaian/mr-tugas-ln/`
- Detail: `/manajemen-data-kepegawaian/mr-tugas-ln/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_tugas_ln/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_tugas_ln.view`
- `kepegawaian.Mr_tugas_ln.create`
- `kepegawaian.Mr_tugas_ln.edit`
- `kepegawaian.Mr_tugas_ln.delete`

## 7q) Data Pegawai: Kepegawaian → Riwayat → Tanda Jasa (`Mr_tandajasa`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat tanda jasa dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_tandajasa`

URL:
- List: `/manajemen-data-kepegawaian/mr-tandajasa/`
- Detail: `/manajemen-data-kepegawaian/mr-tandajasa/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_tandajasa/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_tandajasa.view`
- `kepegawaian.Mr_tandajasa.create`
- `kepegawaian.Mr_tandajasa.edit`
- `kepegawaian.Mr_tandajasa.delete`

## 7r) Data Pegawai: Kepegawaian → Riwayat → Gaji Berkala (`Mr_gaji_berkala`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat gaji berkala dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_gaji_berkala`

URL:
- List: `/manajemen-data-kepegawaian/mr-gaji-berkala/`
- Detail: `/manajemen-data-kepegawaian/mr-gaji-berkala/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_gaji_berkala/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_gaji_berkala.view`
- `kepegawaian.Mr_gaji_berkala.create`
- `kepegawaian.Mr_gaji_berkala.edit`
- `kepegawaian.Mr_gaji_berkala.delete`

## 7s) Data Pegawai: Kepegawaian → Riwayat → Kinerja (`Mr_kinerja`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data riwayat kinerja dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_kinerja`

URL:
- List: `/manajemen-data-kepegawaian/mr-kinerja/`
- Detail: `/manajemen-data-kepegawaian/mr-kinerja/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_kinerja/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_kinerja.view`
- `kepegawaian.Mr_kinerja.create`
- `kepegawaian.Mr_kinerja.edit`
- `kepegawaian.Mr_kinerja.delete`

## 7t) Data Pegawai: Kepegawaian → Riwayat → Assessment Pegawai (`Mr_assessment`)
Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_kepegawaian_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- (Opsional) `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

Import data assessment dari DB Laravel `esim_pegawai`:
- `docker exec esimpeg_python_app python manage.py import_mr_assessment`

URL:
- List: `/manajemen-data-kepegawaian/mr-assessment/`
- Detail: `/manajemen-data-kepegawaian/mr-assessment/<id>/`

Folder template:
- `apps/manajemen/templates/manajemen_data_kepegawaian/access/ma_da_ke_Mr_assessment/`
  - `list.html`
  - `form.html`
  - `partials/_table.html`
  - `partials/_form.html`

Permission keys:
- `kepegawaian.Mr_assessment.view`
- `kepegawaian.Mr_assessment.create`
- `kepegawaian.Mr_assessment.edit`
- `kepegawaian.Mr_assessment.delete`

## 6e) CRUD Manajemen Data: Kedudukan Pegawai
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_kedudukan_pegawai`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/kedudukan-pegawai/`
- Create: `/manajemen-data/kedudukan-pegawai/create/`
- Edit: `/manajemen-data/kedudukan-pegawai/<id>/edit/`
- Delete: `/manajemen-data/kedudukan-pegawai/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_kedudukan_pegawai/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_kedudukan_pegawai.view`
- `manajemen_data.md_kedudukan_pegawai.create`
- `manajemen_data.md_kedudukan_pegawai.edit`
- `manajemen_data.md_kedudukan_pegawai.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Kedudukan Pegawai

## 6f) CRUD Manajemen Data: Jenis Jabatan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_jenis_jabatan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/jenis-jabatan/`
- Create: `/manajemen-data/jenis-jabatan/create/`
- Edit: `/manajemen-data/jenis-jabatan/<id>/edit/`
- Delete: `/manajemen-data/jenis-jabatan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_jenis_jabatan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_jenis_jabatan.view`
- `manajemen_data.md_jenis_jabatan.create`
- `manajemen_data.md_jenis_jabatan.edit`
- `manajemen_data.md_jenis_jabatan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Jenis Jabatan

## 6g) CRUD Manajemen Data: Kategori Jabatan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_kategori_jabatan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/kategori-jabatan/`
- Create: `/manajemen-data/kategori-jabatan/create/`
- Edit: `/manajemen-data/kategori-jabatan/<id>/edit/`
- Delete: `/manajemen-data/kategori-jabatan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_kategori_jabatan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_kategori_jabatan.view`
- `manajemen_data.md_kategori_jabatan.create`
- `manajemen_data.md_kategori_jabatan.edit`
- `manajemen_data.md_kategori_jabatan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Kategori Jabatan

## 6h) CRUD Manajemen Data: Pangkat
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_pangkat`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/pangkat/`
- Create: `/manajemen-data/pangkat/create/`
- Edit: `/manajemen-data/pangkat/<id>/edit/`
- Delete: `/manajemen-data/pangkat/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_pangkat/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_pangkat.view`
- `manajemen_data.md_pangkat.create`
- `manajemen_data.md_pangkat.edit`
- `manajemen_data.md_pangkat.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Pangkat

## 6i) CRUD Manajemen Data: Jenjang Jabatan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_jenjang_jabatan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/jenjang-jabatan/`
- Create: `/manajemen-data/jenjang-jabatan/create/`
- Edit: `/manajemen-data/jenjang-jabatan/<id>/edit/`
- Delete: `/manajemen-data/jenjang-jabatan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_jenjang_jabatan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_jenjang_jabatan.view`
- `manajemen_data.md_jenjang_jabatan.create`
- `manajemen_data.md_jenjang_jabatan.edit`
- `manajemen_data.md_jenjang_jabatan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Jenjang Jabatan

## 6j) CRUD Manajemen Data: Eselon
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_eselon`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/eselon/`
- Create: `/manajemen-data/eselon/create/`
- Edit: `/manajemen-data/eselon/<id>/edit/`
- Delete: `/manajemen-data/eselon/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_eselon/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_eselon.view`
- `manajemen_data.md_eselon.create`
- `manajemen_data.md_eselon.edit`
- `manajemen_data.md_eselon.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Eselon

## 6k) CRUD Manajemen Data: Diklat Struktural
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_diklat_struktural`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/diklat-struktural/`
- Create: `/manajemen-data/diklat-struktural/create/`
- Edit: `/manajemen-data/diklat-struktural/<id>/edit/`
- Delete: `/manajemen-data/diklat-struktural/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_diklat_struktural/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_diklat_struktural.view`
- `manajemen_data.md_diklat_struktural.create`
- `manajemen_data.md_diklat_struktural.edit`
- `manajemen_data.md_diklat_struktural.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Diklat Struktural

## 6l) CRUD Manajemen Data: Jenis Surat
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_jenis_surat`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/jenis-surat/`
- Create: `/manajemen-data/jenis-surat/create/`
- Edit: `/manajemen-data/jenis-surat/<id>/edit/`
- Delete: `/manajemen-data/jenis-surat/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_jenis_surat/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_jenis_surat.view`
- `manajemen_data.md_jenis_surat.create`
- `manajemen_data.md_jenis_surat.edit`
- `manajemen_data.md_jenis_surat.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Jenis Surat

## 6m) CRUD Manajemen Data: Pejabat Menetapkan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_pejabat_menetapkan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/pejabat-menetapkan/`
- Create: `/manajemen-data/pejabat-menetapkan/create/`
- Edit: `/manajemen-data/pejabat-menetapkan/<id>/edit/`
- Delete: `/manajemen-data/pejabat-menetapkan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_pejabat_menetapkan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_pejabat_menetapkan.view`
- `manajemen_data.md_pejabat_menetapkan.create`
- `manajemen_data.md_pejabat_menetapkan.edit`
- `manajemen_data.md_pejabat_menetapkan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Pejabat Menetapkan

## 6n) CRUD Manajemen Data: Jenis Organisasi
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_jenis_organisasi`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/jenis-organisasi/`
- Create: `/manajemen-data/jenis-organisasi/create/`
- Edit: `/manajemen-data/jenis-organisasi/<id>/edit/`
- Delete: `/manajemen-data/jenis-organisasi/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_jenis_organisasi/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_jenis_organisasi.view`
- `manajemen_data.md_jenis_organisasi.create`
- `manajemen_data.md_jenis_organisasi.edit`
- `manajemen_data.md_jenis_organisasi.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Jenis Organisasi

## 6o) CRUD Manajemen Data: Kategori Pemberitahuan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_kategori_pemberitahuan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/kategori-pemberitahuan/`
- Create: `/manajemen-data/kategori-pemberitahuan/create/`
- Edit: `/manajemen-data/kategori-pemberitahuan/<id>/edit/`
- Delete: `/manajemen-data/kategori-pemberitahuan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_kategori_pemberitahuan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_kategori_pemberitahuan.view`
- `manajemen_data.md_kategori_pemberitahuan.create`
- `manajemen_data.md_kategori_pemberitahuan.edit`
- `manajemen_data.md_kategori_pemberitahuan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Kategori Pemberitahuan

## 6p) CRUD Manajemen Data: Kategori Peraturan
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_md_kategori_peraturan`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/kategori-peraturan/`
- Create: `/manajemen-data/kategori-peraturan/create/`
- Edit: `/manajemen-data/kategori-peraturan/<id>/edit/`
- Delete: `/manajemen-data/kategori-peraturan/<id>/delete/`

Folder template (Manajemen Data):
- `apps/manajemen/templates/manajemen_data/access/ma_da_kategori_peraturan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_kategori_peraturan.view`
- `manajemen_data.md_kategori_peraturan.create`
- `manajemen_data.md_kategori_peraturan.edit`
- `manajemen_data.md_kategori_peraturan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Kategori Peraturan

## 6p1) CRUD Relasi Organisasi: Unit Organisasi (Tabel)
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_ms_unit_organisasi`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_relasi_organisasi_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-relasi-organisasi/unit-organisasi-tabel/`
- Create: `/manajemen-relasi-organisasi/unit-organisasi-tabel/create/`
- Edit: `/manajemen-relasi-organisasi/unit-organisasi-tabel/<id>/edit/`
- Delete: `/manajemen-relasi-organisasi/unit-organisasi-tabel/<id>/delete/`

Folder template (Relasi Organisasi):
- `apps/manajemen/templates/manajemen_relasi_organisasi/access/ma_re_or_unit_organisasi_tabel/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.create`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.edit`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.delete`

Sidebar:
- SUPER ADMIN → Relasi Organisasi → Unit Organisasi Tabel

## 6p2) CRUD Relasi Organisasi: Unit Organisasi (Struktural)
Prerequisite data:
- Import dari DB Laravel (jika diperlukan):
  - `docker exec esimpeg_python_app python manage.py import_ms_unit_organisasi`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_relasi_organisasi_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-relasi-organisasi/unit-organisasi-struktural/`
- Create: `/manajemen-relasi-organisasi/unit-organisasi-struktural/create/`
- Edit: `/manajemen-relasi-organisasi/unit-organisasi-struktural/<id>/edit/`
- Delete: `/manajemen-relasi-organisasi/unit-organisasi-struktural/<id>/delete/`
- Move Parent: `/manajemen-relasi-organisasi/unit-organisasi-struktural/<id>/move-parent/`

Folder template (Relasi Organisasi):
- `apps/manajemen/templates/manajemen_relasi_organisasi/access/ma_re_or_unit_organisasi_struktural/`
  - `list.html`
  - `form.html`
  - `add_child_modal.html`
  - `edit_unit_modal.html`
  - `move_parent_modal.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.view`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.create`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.edit`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.move`
- `manajemen_relasi_organisasi.ma_re_or_unit_organisasi.delete`

Sidebar:
- SUPER ADMIN → Relasi Organisasi → Unit Organisasi Struktural

## 6q) CRUD Manajemen Analisis Jabatan: Satuan Kerja (Anjab)
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_satuan_kerja`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/satuan-kerja/`
- Create: `/manajemen-analisis-jabatan/satuan-kerja/create/`
- Edit: `/manajemen-analisis-jabatan/satuan-kerja/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/satuan-kerja/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_satuan_kerja/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_satuan_kerja.view`
- `manajemen_analisis_jabatan.ma_an_satuan_kerja.create`
- `manajemen_analisis_jabatan.ma_an_satuan_kerja.edit`
- `manajemen_analisis_jabatan.ma_an_satuan_kerja.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Satuan Kerja (Anjab)

## 6r) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Bakat
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_bakat`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/bakat/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/bakat/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/bakat/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/bakat/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_bakat/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_bakat.view`
- `manajemen_analisis_jabatan.ma_an_sj_bakat.create`
- `manajemen_analisis_jabatan.ma_an_sj_bakat.edit`
- `manajemen_analisis_jabatan.ma_an_sj_bakat.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Bakat

## 6s) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Temperamen Kerja
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_temperamen_kerja`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/temperamen-kerja/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/temperamen-kerja/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/temperamen-kerja/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/temperamen-kerja/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_temperamen_kerja/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.view`
- `manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.create`
- `manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.edit`
- `manajemen_analisis_jabatan.ma_an_sj_temperamen_kerja.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Temperamen Kerja

## 6t) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Minat Kerja
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_minat_kerja`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/minat-kerja/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/minat-kerja/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/minat-kerja/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/minat-kerja/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_minat_kerja/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_minat_kerja.view`
- `manajemen_analisis_jabatan.ma_an_sj_minat_kerja.create`
- `manajemen_analisis_jabatan.ma_an_sj_minat_kerja.edit`
- `manajemen_analisis_jabatan.ma_an_sj_minat_kerja.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Minat Kerja

## 6u) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Jabatan Data
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_jabatan_data`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-data/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-data/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-data/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-data/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_jabatan_data/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_data.view`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_data.create`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_data.edit`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_data.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Jabatan Data

## 6v) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Jabatan Orang
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_jabatan_orang`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-orang/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-orang/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-orang/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-orang/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_jabatan_orang/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.view`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.create`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.edit`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_orang.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Jabatan Orang

## 6w) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Jabatan Benda
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_jabatan_benda`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-benda/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-benda/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-benda/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/jabatan-benda/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_jabatan_benda/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.view`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.create`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.edit`
- `manajemen_analisis_jabatan.ma_an_sj_jabatan_benda.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Jabatan Benda

## 6x) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Upaya Fisik
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_upaya_fisik`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/upaya-fisik/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/upaya-fisik/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/upaya-fisik/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/upaya-fisik/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_upaya_fisik/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.view`
- `manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.create`
- `manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.edit`
- `manajemen_analisis_jabatan.ma_an_sj_upaya_fisik.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Upaya Fisik

## 6y) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Pengetahuan Kerja
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_pengetahuan_kerja`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/pengetahuan-kerja/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/pengetahuan-kerja/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/pengetahuan-kerja/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/pengetahuan-kerja/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_pengetahuan_kerja/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.view`
- `manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.create`
- `manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.edit`
- `manajemen_analisis_jabatan.ma_an_sj_pengetahuan_kerja.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Pengetahuan Kerja

## 6z) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Keterampilan Kerja
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_keterampilan_kerja`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/keterampilan-kerja/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/keterampilan-kerja/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/keterampilan-kerja/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/keterampilan-kerja/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_keterampilan_kerja/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.view`
- `manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.create`
- `manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.edit`
- `manajemen_analisis_jabatan.ma_an_sj_keterampilan_kerja.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Keterampilan Kerja

## 6aa) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Pelatihan Fungsional
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_pelatihan_fungsional`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-fungsional/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-fungsional/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-fungsional/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-fungsional/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_pelatihan_fungsional/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.view`
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.create`
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.edit`
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_fungsional.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Pelatihan Fungsional

## 6ab) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Jenis Kelamin
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_jenis_kelamin`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/jenis-kelamin/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/jenis-kelamin/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/jenis-kelamin/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/jenis-kelamin/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_jenis_kelamin/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.view`
- `manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.create`
- `manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.edit`
- `manajemen_analisis_jabatan.ma_an_sj_jenis_kelamin.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Jenis Kelamin

## 6ac) CRUD Manajemen Analisis Jabatan: Syarat Jabatan - Pelatihan Teknis
Seeder data awal:
- `docker exec esimpeg_python_app python manage.py seed_ma_an_sj_pelatihan_teknis`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_analisis_jabatan_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-teknis/`
- Create: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-teknis/create/`
- Edit: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-teknis/<id>/edit/`
- Delete: `/manajemen-analisis-jabatan/syarat-jabatan/pelatihan-teknis/<id>/delete/`

Folder template (Manajemen Analisis Jabatan):
- `apps/manajemen/templates/manajemen_analisis_jabatan/access/ma_an_sj_pelatihan_teknis/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.view`
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.create`
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.edit`
- `manajemen_analisis_jabatan.ma_an_sj_pelatihan_teknis.delete`

Sidebar:
- SUPER ADMIN → Manajemen Analisis Jabatan → Syarat Jabatan - Pelatihan Teknis

## 7) Catatan penting
- Semua seeder dirancang **idempotent** (aman dipanggil berkali-kali).
- Permission check **default** mengandalkan `RoleRule` (explicit assignment). Untuk mode bypass, ada flag `PERMISSIONS_SUPERADMIN_OVERRIDE`, tapi rekomendasi: gunakan assignment eksplisit via `seed_superadmin_full_access`.
- Sidebar diambil dari tabel `menu_items` (DB-driven).

## 9) Manajemen Referensi Data BKN

### 9a) CRUD Manajemen Referensi Data BKN: BKN Lokasi Kerja
Catatan skema:
- Implementasi Django mengikuti skema tabel real di DB `esim_pegawai` (kolom sampai `deleted_at`).
- Migration Laravel yang lebih baru menambah kolom (`kanreg_nama`, `satuan_kerja_*`, `unor_*`, `instansi_*`), namun kolom tersebut tidak dipakai karena tidak ada di DB `esim_pegawai`. Jika suatu saat DB sudah mengikuti skema baru, barulah bisa ditambahkan kembali dengan migration baru.

Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_lokasi_kerja`
  - Catatan: di sebagian dump/DB lama, `deleted_at` bisa berisi `0000-00-00 00:00:00` (bukan NULL). Import/export akan memperlakukan nilai tersebut sebagai **aktif**. Jika ingin benar-benar include deleted, gunakan `--include-deleted`.

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_lokasi_kerja_json --out /app/tmp/bkn_lokasi_kerja.json`

Seeder offline dari dump SQL (alternatif jika tidak bisa konek DB Laravel):
- `docker exec esimpeg_python_app python manage.py seed_bkn_lokasi_kerja --sql /home/prakom/project-docker/all-projects-darireal/projects/ESIMPEG/database/esim_pegawai.sql`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_lokasi_kerja --json /app/tmp/bkn_lokasi_kerja.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_lokasi_kerja.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_lokasi_kerja`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- Export dari DB sumber (hanya di environment yang bisa akses DB `esim_pegawai`):
  - `docker exec esimpeg_python_app python manage.py export_bkn_lokasi_kerja_json --out /app/tmp/bkn_lokasi_kerja.json`
- Copy hasil export ke lokasi bundled di repo (di dalam container path-nya `/app/...`):
  - `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_lokasi_kerja.json /app/apps/master_data/seeders/offline/bkn_lokasi_kerja.json"`
- Commit file `apps/master_data/seeders/offline/bkn_lokasi_kerja.json` ke repo.

Urutan saat deploy (tanpa koneksi DB sumber):
- `docker exec esimpeg_python_app python manage.py migrate`
- `docker exec esimpeg_python_app python manage.py seed_bkn_lokasi_kerja`
- `docker exec esimpeg_python_app python manage.py seed_manajemen_referensi_data_bkn_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`

Seeder akses (permission + sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_referensi_data_bkn_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-referensi-data-bkn/bkn-lokasi-kerja/`
- Create: `/manajemen-referensi-data-bkn/bkn-lokasi-kerja/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-lokasi-kerja/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-lokasi-kerja/<id>/delete/`

### 9b) CRUD Manajemen Referensi Data BKN: BKN Alasan Hukuman
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_alasan_hukuman`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_alasan_hukuman_json --out /app/tmp/bkn_alasan_hukuman.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_alasan_hukuman --json /app/tmp/bkn_alasan_hukuman.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_alasan_hukuman.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_alasan_hukuman`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_alasan_hukuman_json --out /app/tmp/bkn_alasan_hukuman.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_alasan_hukuman.json /app/apps/master_data/seeders/offline/bkn_alasan_hukuman.json"`
- Commit file `apps/master_data/seeders/offline/bkn_alasan_hukuman.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-alasan-hukuman/`
- Create: `/manajemen-referensi-data-bkn/bkn-alasan-hukuman/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-alasan-hukuman/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-alasan-hukuman/<id>/delete/`

### 9c) CRUD Manajemen Referensi Data BKN: BKN Jenis Hukuman
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jenis_hukuman`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_hukuman_json --out /app/tmp/bkn_jenis_hukuman.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_hukuman --json /app/tmp/bkn_jenis_hukuman.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jenis_hukuman.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_hukuman`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_hukuman_json --out /app/tmp/bkn_jenis_hukuman.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jenis_hukuman.json /app/apps/master_data/seeders/offline/bkn_jenis_hukuman.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jenis_hukuman.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jenis-hukuman/`
- Create: `/manajemen-referensi-data-bkn/bkn-jenis-hukuman/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jenis-hukuman/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jenis-hukuman/<id>/delete/`

### 9d) CRUD Manajemen Referensi Data BKN: BKN Tingkat Hukuman Disiplin
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_tingkat_hukdis`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_tingkat_hukdis_json --out /app/tmp/bkn_tingkat_hukdis.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_tingkat_hukdis --json /app/tmp/bkn_tingkat_hukdis.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_tingkat_hukdis.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_tingkat_hukdis`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_tingkat_hukdis_json --out /app/tmp/bkn_tingkat_hukdis.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_tingkat_hukdis.json /app/apps/master_data/seeders/offline/bkn_tingkat_hukdis.json"`
- Commit file `apps/master_data/seeders/offline/bkn_tingkat_hukdis.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-tingkat-hukdis/`
- Create: `/manajemen-referensi-data-bkn/bkn-tingkat-hukdis/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-tingkat-hukdis/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-tingkat-hukdis/<id>/delete/`

### 9e) CRUD Manajemen Referensi Data BKN: BKN Nomor PP Hukdis
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_nomorpp_hukdis`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_nomorpp_hukdis_json --out /app/tmp/bkn_nomorpp_hukdis.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_nomorpp_hukdis --json /app/tmp/bkn_nomorpp_hukdis.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_nomorpp_hukdis.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_nomorpp_hukdis`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_nomorpp_hukdis_json --out /app/tmp/bkn_nomorpp_hukdis.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_nomorpp_hukdis.json /app/apps/master_data/seeders/offline/bkn_nomorpp_hukdis.json"`
- Commit file `apps/master_data/seeders/offline/bkn_nomorpp_hukdis.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-nomorpp-hukdis/`
- Create: `/manajemen-referensi-data-bkn/bkn-nomorpp-hukdis/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-nomorpp-hukdis/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-nomorpp-hukdis/<id>/delete/`

### 9f) CRUD Manajemen Referensi Data BKN: BKN Jabatan Fungsional
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jabatan_fungsional`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jabatan_fungsional_json --out /app/tmp/bkn_jabatan_fungsional.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jabatan_fungsional --json /app/tmp/bkn_jabatan_fungsional.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jabatan_fungsional.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jabatan_fungsional`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jabatan_fungsional_json --out /app/tmp/bkn_jabatan_fungsional.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jabatan_fungsional.json /app/apps/master_data/seeders/offline/bkn_jabatan_fungsional.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jabatan_fungsional.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jabatan-fungsional/`
- Create: `/manajemen-referensi-data-bkn/bkn-jabatan-fungsional/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jabatan-fungsional/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jabatan-fungsional/<id>/delete/`

### 9g) CRUD Manajemen Referensi Data BKN: BKN Jenis Kenaikan Pangkat
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jenis_kenaikan_pangkat`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_kenaikan_pangkat_json --out /app/tmp/bkn_jenis_kenaikan_pangkat.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_kenaikan_pangkat --json /app/tmp/bkn_jenis_kenaikan_pangkat.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jenis_kenaikan_pangkat.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_kenaikan_pangkat`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_kenaikan_pangkat_json --out /app/tmp/bkn_jenis_kenaikan_pangkat.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jenis_kenaikan_pangkat.json /app/apps/master_data/seeders/offline/bkn_jenis_kenaikan_pangkat.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jenis_kenaikan_pangkat.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jenis-kenaikan-pangkat/`
- Create: `/manajemen-referensi-data-bkn/bkn-jenis-kenaikan-pangkat/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jenis-kenaikan-pangkat/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jenis-kenaikan-pangkat/<id>/delete/`

### 9h) CRUD Manajemen Referensi Data BKN: BKN Jenis Diklat
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jenis_diklat`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_diklat_json --out /app/tmp/bkn_jenis_diklat.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_diklat --json /app/tmp/bkn_jenis_diklat.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jenis_diklat.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_diklat`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_diklat_json --out /app/tmp/bkn_jenis_diklat.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jenis_diklat.json /app/apps/master_data/seeders/offline/bkn_jenis_diklat.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jenis_diklat.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jenis-diklat/`
- Create: `/manajemen-referensi-data-bkn/bkn-jenis-diklat/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jenis-diklat/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jenis-diklat/<id>/delete/`

### 9i) CRUD Manajemen Referensi Data BKN: BKN Daftar KPPN
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_daftar_kppn`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_daftar_kppn_json --out /app/tmp/bkn_daftar_kppn.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_daftar_kppn --json /app/tmp/bkn_daftar_kppn.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_daftar_kppn.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_daftar_kppn`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_daftar_kppn_json --out /app/tmp/bkn_daftar_kppn.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_daftar_kppn.json /app/apps/master_data/seeders/offline/bkn_daftar_kppn.json"`
- Commit file `apps/master_data/seeders/offline/bkn_daftar_kppn.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-daftar-kppn/`
- Create: `/manajemen-referensi-data-bkn/bkn-daftar-kppn/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-daftar-kppn/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-daftar-kppn/<id>/delete/`

### 9j) CRUD Manajemen Referensi Data BKN: BKN Jenis Penghargaan
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jenis_penghargaan`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_penghargaan_json --out /app/tmp/bkn_jenis_penghargaan.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_penghargaan --json /app/tmp/bkn_jenis_penghargaan.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jenis_penghargaan.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_penghargaan`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_penghargaan_json --out /app/tmp/bkn_jenis_penghargaan.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jenis_penghargaan.json /app/apps/master_data/seeders/offline/bkn_jenis_penghargaan.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jenis_penghargaan.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jenis-penghargaan/`
- Create: `/manajemen-referensi-data-bkn/bkn-jenis-penghargaan/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jenis-penghargaan/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jenis-penghargaan/<id>/delete/`

### 9k) CRUD Manajemen Referensi Data BKN: BKN Jenis Mutasi
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jenis_mutasi`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_mutasi_json --out /app/tmp/bkn_jenis_mutasi.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_mutasi --json /app/tmp/bkn_jenis_mutasi.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jenis_mutasi.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_mutasi`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_mutasi_json --out /app/tmp/bkn_jenis_mutasi.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jenis_mutasi.json /app/apps/master_data/seeders/offline/bkn_jenis_mutasi.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jenis_mutasi.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jenis-mutasi/`
- Create: `/manajemen-referensi-data-bkn/bkn-jenis-mutasi/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jenis-mutasi/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jenis-mutasi/<id>/delete/`

### 9l) CRUD Manajemen Referensi Data BKN: BKN Jenis Penugasan
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_jenis_penugasan`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_penugasan_json --out /app/tmp/bkn_jenis_penugasan.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_penugasan --json /app/tmp/bkn_jenis_penugasan.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_jenis_penugasan.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_jenis_penugasan`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_jenis_penugasan_json --out /app/tmp/bkn_jenis_penugasan.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_jenis_penugasan.json /app/apps/master_data/seeders/offline/bkn_jenis_penugasan.json"`
- Commit file `apps/master_data/seeders/offline/bkn_jenis_penugasan.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-jenis-penugasan/`
- Create: `/manajemen-referensi-data-bkn/bkn-jenis-penugasan/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-jenis-penugasan/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-jenis-penugasan/<id>/delete/`

### 9m) CRUD Manajemen Referensi Data BKN: BKN Sub Jabatan
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Seed permissions + menu (agar tidak 403 & muncul di sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_referensi_data_bkn_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`
- Jika group Super Admin kamu namanya `SUPER ADMIN` (bukan `Super Admin`), jalankan:
  - `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access --group "SUPER ADMIN"`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_bkn_sub_jabatan`

Export dari DB (untuk dijadikan seed offline JSON):
- `docker exec esimpeg_python_app python manage.py export_bkn_sub_jabatan_json --out /app/tmp/bkn_sub_jabatan.json`

Seeder offline dari JSON (hasil export):
- `docker exec esimpeg_python_app python manage.py seed_bkn_sub_jabatan --json /app/tmp/bkn_sub_jabatan.json`

Seeder offline TANPA koneksi DB (standalone/bundled):
- Simpan file JSON ke: `apps/master_data/seeders/offline/bkn_sub_jabatan.json`
- Lalu jalankan (tanpa parameter):
  - `docker exec esimpeg_python_app python manage.py seed_bkn_sub_jabatan`

Workflow membuat bundled JSON (sekali saja, untuk kemudian dipakai saat deploy tanpa koneksi DB):
- `docker exec esimpeg_python_app python manage.py export_bkn_sub_jabatan_json --out /app/tmp/bkn_sub_jabatan.json`
- `docker exec esimpeg_python_app sh -lc "cp /app/tmp/bkn_sub_jabatan.json /app/apps/master_data/seeders/offline/bkn_sub_jabatan.json"`
- Commit file `apps/master_data/seeders/offline/bkn_sub_jabatan.json` ke repo.

URL:
- List: `/manajemen-referensi-data-bkn/bkn-sub-jabatan/`
- Create: `/manajemen-referensi-data-bkn/bkn-sub-jabatan/create/`
- Edit: `/manajemen-referensi-data-bkn/bkn-sub-jabatan/<id>/edit/`
- Delete: `/manajemen-referensi-data-bkn/bkn-sub-jabatan/<id>/delete/`

### 10) Relasi Organisasi: Jabatan Struktural Tabel
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Seed permissions + menu (agar tidak 403 & muncul di sidebar):
- `docker exec esimpeg_python_app python manage.py seed_manajemen_relasi_organisasi_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`
- Jika group Super Admin kamu namanya `SUPER ADMIN` (bukan `Super Admin`), jalankan:
  - `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access --group "SUPER ADMIN"`

Import/sync dari DB Laravel (recommended):
- `docker exec esimpeg_python_app python manage.py import_ms_jabatan_struktural`

URL:
- List: `/manajemen-relasi-organisasi/jabatan-struktural-tabel/`

Folder template:
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_lokasi_kerja/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_alasan_hukuman/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jenis_hukuman/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_tingkat_hukdis/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_nomorpp_hukdis/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jabatan_fungsional/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jenis_kenaikan_pangkat/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jenis_diklat/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_daftar_kppn/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jenis_penghargaan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jenis_mutasi/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_jenis_penugasan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`
- `apps/manajemen/templates/manajemen_referensi_data_bkn/access/Ma_re_Bkn_sub_jabatan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_referensi_data_bkn.bkn_lokasi_kerja.view`
- `manajemen_referensi_data_bkn.bkn_lokasi_kerja.create`
- `manajemen_referensi_data_bkn.bkn_lokasi_kerja.edit`
- `manajemen_referensi_data_bkn.bkn_lokasi_kerja.delete`
- `manajemen_referensi_data_bkn.bkn_alasan_hukuman.view`
- `manajemen_referensi_data_bkn.bkn_alasan_hukuman.create`
- `manajemen_referensi_data_bkn.bkn_alasan_hukuman.edit`
- `manajemen_referensi_data_bkn.bkn_alasan_hukuman.delete`
- `manajemen_referensi_data_bkn.bkn_jenis_hukuman.view`
- `manajemen_referensi_data_bkn.bkn_jenis_hukuman.create`
- `manajemen_referensi_data_bkn.bkn_jenis_hukuman.edit`
- `manajemen_referensi_data_bkn.bkn_jenis_hukuman.delete`
- `manajemen_referensi_data_bkn.bkn_tingkat_hukdis.view`
- `manajemen_referensi_data_bkn.bkn_tingkat_hukdis.create`
- `manajemen_referensi_data_bkn.bkn_tingkat_hukdis.edit`
- `manajemen_referensi_data_bkn.bkn_tingkat_hukdis.delete`
- `manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.view`
- `manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.create`
- `manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.edit`
- `manajemen_referensi_data_bkn.bkn_nomorpp_hukdis.delete`
- `manajemen_referensi_data_bkn.bkn_jabatan_fungsional.view`
- `manajemen_referensi_data_bkn.bkn_jabatan_fungsional.create`
- `manajemen_referensi_data_bkn.bkn_jabatan_fungsional.edit`
- `manajemen_referensi_data_bkn.bkn_jabatan_fungsional.delete`
- `manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.view`
- `manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.create`
- `manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.edit`
- `manajemen_referensi_data_bkn.bkn_jenis_kenaikan_pangkat.delete`
- `manajemen_referensi_data_bkn.bkn_jenis_diklat.view`
- `manajemen_referensi_data_bkn.bkn_jenis_diklat.create`
- `manajemen_referensi_data_bkn.bkn_jenis_diklat.edit`
- `manajemen_referensi_data_bkn.bkn_jenis_diklat.delete`
- `manajemen_referensi_data_bkn.bkn_daftar_kppn.view`
- `manajemen_referensi_data_bkn.bkn_daftar_kppn.create`
- `manajemen_referensi_data_bkn.bkn_daftar_kppn.edit`
- `manajemen_referensi_data_bkn.bkn_daftar_kppn.delete`
- `manajemen_referensi_data_bkn.bkn_jenis_penghargaan.view`
- `manajemen_referensi_data_bkn.bkn_jenis_penghargaan.create`
- `manajemen_referensi_data_bkn.bkn_jenis_penghargaan.edit`
- `manajemen_referensi_data_bkn.bkn_jenis_penghargaan.delete`
- `manajemen_referensi_data_bkn.bkn_jenis_mutasi.view`
- `manajemen_referensi_data_bkn.bkn_jenis_mutasi.create`
- `manajemen_referensi_data_bkn.bkn_jenis_mutasi.edit`
- `manajemen_referensi_data_bkn.bkn_jenis_mutasi.delete`
- `manajemen_referensi_data_bkn.bkn_jenis_penugasan.view`
- `manajemen_referensi_data_bkn.bkn_jenis_penugasan.create`
- `manajemen_referensi_data_bkn.bkn_jenis_penugasan.edit`
- `manajemen_referensi_data_bkn.bkn_jenis_penugasan.delete`
- `manajemen_referensi_data_bkn.bkn_sub_jabatan.view`
- `manajemen_referensi_data_bkn.bkn_sub_jabatan.create`
- `manajemen_referensi_data_bkn.bkn_sub_jabatan.edit`
- `manajemen_referensi_data_bkn.bkn_sub_jabatan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Referensi Data BKN → Lokasi Kerja
- SUPER ADMIN → Manajemen Referensi Data BKN → Alasan Hukuman
- SUPER ADMIN → Manajemen Referensi Data BKN → Jenis Hukuman
- SUPER ADMIN → Manajemen Referensi Data BKN → Tingkat Hukuman Disiplin
- SUPER ADMIN → Manajemen Referensi Data BKN → Nomor PP Hukdis
- SUPER ADMIN → Manajemen Referensi Data BKN → Jabatan Fungsional
- SUPER ADMIN → Manajemen Referensi Data BKN → Jenis Kenaikan Pangkat
- SUPER ADMIN → Manajemen Referensi Data BKN → Jenis Diklat
- SUPER ADMIN → Manajemen Referensi Data BKN → Daftar KPPN
- SUPER ADMIN → Manajemen Referensi Data BKN → Jenis Penghargaan
- SUPER ADMIN → Manajemen Referensi Data BKN → Jenis Mutasi
- SUPER ADMIN → Manajemen Referensi Data BKN → Jenis Penugasan
- SUPER ADMIN → Manajemen Referensi Data BKN → Sub Jabatan

## 8) Seed data master (tanpa koneksi DB Laravel)
Jika kamu tidak ingin / tidak bisa konek ke DB Laravel, kamu bisa mengisi master data tertentu dengan **seed data statis**.

Commands:
- `docker exec esimpeg_python_app python manage.py seed_md_agama`
- `docker exec esimpeg_python_app python manage.py seed_md_status_perkawinan`
- `docker exec esimpeg_python_app python manage.py seed_md_jenjang_pendidikan`
- `docker exec esimpeg_python_app python manage.py seed_md_kategori_pegawai`
- `docker exec esimpeg_python_app python manage.py seed_md_kedudukan_pegawai`
 - `docker exec esimpeg_python_app python manage.py seed_md_jenis_jabatan`
 - `docker exec esimpeg_python_app python manage.py seed_md_kategori_jabatan`
 - `docker exec esimpeg_python_app python manage.py seed_md_pangkat`
 - `docker exec esimpeg_python_app python manage.py seed_md_jenjang_jabatan`
 - `docker exec esimpeg_python_app python manage.py seed_md_eselon`
 - `docker exec esimpeg_python_app python manage.py seed_md_diklat_struktural`
 - `docker exec esimpeg_python_app python manage.py seed_md_jenis_surat`
 - `docker exec esimpeg_python_app python manage.py seed_md_pejabat_menetapkan`
 - `docker exec esimpeg_python_app python manage.py seed_md_jenis_organisasi`
 - `docker exec esimpeg_python_app python manage.py seed_md_kategori_pemberitahuan`

## 9) CRUD Manajemen Data: Md_peraturan dan Md_tentang

### Catatan penting (prasyarat agar CRUD/Form muncul & bisa diakses)
Jika kamu menambah CRUD baru (list/form/delete) dan merasa menu/tombol tidak muncul atau dapat 403, cek urutan/prasyarat berikut:

1) **Tabel sudah ada (migrations)**
   - Pastikan model + migration sudah dibuat dan dijalankan (`migrate`).

2) **Permission/function/rule sudah ada (seed permissions)**
   - Halaman list/form biasanya memakai pengecekan permission berbasis `module + function`.
   - Jalankan seeder permissions yang relevan (contoh untuk Manajemen Data: `seed_master_data_permissions`).

3) **Menu sidebar sudah ada (seed menus)**
   - Sidebar hanya menampilkan menu yang ter-seed + memenuhi permission.
   - Jalankan `seed_menus` setelah permissions ada.

4) **Role assignment sudah ada (seed superadmin / assign role manual)**
   - Untuk role SUPER ADMIN agar otomatis punya akses: jalankan `seed_superadmin_full_access`.
   - Untuk role lain: assign rule/permission sesuai kebutuhan lewat UI manajemen role/rules.

Checklist cepat: `migrate` -> `seed_*_permissions` -> `seed_menus` -> `seed_superadmin_full_access`.

### 9x) CRUD Manajemen Data: Peraturan (Md_peraturan)
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Seed permissions + menu (agar muncul di sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/peraturan/`
- Create: `/manajemen-data/peraturan/create/`
- Edit: `/manajemen-data/peraturan/<id>/edit/`
- Delete: `/manajemen-data/peraturan/<id>/delete/`

Folder template:
- `apps/manajemen/templates/manajemen_data/access/ma_da_peraturan/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_peraturan.view`
- `manajemen_data.md_peraturan.create`
- `manajemen_data.md_peraturan.edit`
- `manajemen_data.md_peraturan.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Peraturan

### 9y) CRUD Manajemen Data: Tentang (Md_tentang)
Migrate:
- `docker exec esimpeg_python_app python manage.py migrate`

Seed permissions + menu (agar muncul di sidebar):
- `docker exec esimpeg_python_app python manage.py seed_master_data_permissions`
- `docker exec esimpeg_python_app python manage.py seed_menus`
- `docker exec esimpeg_python_app python manage.py seed_superadmin_full_access`

URL:
- List: `/manajemen-data/tentang/`
- Create: `/manajemen-data/tentang/create/`
- Edit: `/manajemen-data/tentang/<id>/edit/`
- Delete: `/manajemen-data/tentang/<id>/delete/`

Folder template:
- `apps/manajemen/templates/manajemen_data/access/ma_da_tentang/`
  - `list.html`
  - `form.html`
  - `delete.html`
  - `partials/_table.html`

Permission keys:
- `manajemen_data.md_tentang.view`
- `manajemen_data.md_tentang.create`
- `manajemen_data.md_tentang.edit`
- `manajemen_data.md_tentang.delete`

Sidebar:
- SUPER ADMIN → Manajemen Data → Tentang

Opsi:
- `--force` untuk mengisi `created_at`/`updated_at` saat seed (berguna untuk konsistensi timestamp).
