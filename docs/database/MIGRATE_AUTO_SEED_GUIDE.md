# ESIMPEG-Python — Tahap Migrate + Auto-Seed (Copy-Paste Friendly)

Dokumen ini fokus ke tahap database bootstrap yang benar dan aman untuk:
- setup aplikasi baru (database masih kosong)
- deploy update (database sudah ada, hanya ingin sync seeder/permissions)

## Prinsip (wajib diingat)

- `migrate` selalu pertama. Jangan jalankan import data sebelum `migrate` selesai.
- Setelah `migrate`, project ini punya mekanisme auto-seed:
  - `apps.manajemen.signals` menjalankan `python manage.py auto_seed` pada event `post_migrate`.
  - `auto_seed` hanya seed jika database terlihat kosong (kecuali mode `--sync`).
- Import dari Laravel itu manual dan opsional:
  - Butuh koneksi `DATABASES['laravel']` valid
  - Prosesnya lama
  - Tidak wajib untuk aplikasi baru kalau memang tidak perlu data legacy

---

## A. Setup baru (database kosong)

Jalankan urutan ini:

```bash
python manage.py migrate
```

Jika database masih kosong, setelah migrate, `auto_seed` akan jalan otomatis dan membuat core data (permissions, menus, default users).

Kredensial hasil seeder user (`seed_default_users`) saat setup baru:
- superadmin:
  - username: `Prakom@admin2025.com`
  - password: `Prakom@2025`
 - superadmin (alternate):
   - username: `admin`
   - password: `admin123`

Kalau kamu ingin jalankan manual (misalnya untuk memastikan output terlihat):

```bash
python manage.py auto_seed
```

Alternatif yang lebih eksplisit (tanpa auto detection):

```bash
python manage.py seed_core_setup
python manage.py seed_superadmin_full_access
```

Catatan:
- `seed_core_setup` itu komposisi seeder core (permissions + menu)
- `seed_superadmin_full_access` menyiapkan akses superadmin

---

## B. Deploy update (database sudah ada)

Kasus: kamu deploy code baru dan ada perubahan seeder permissions (tambah function/controls/rules), tapi database sudah berisi data.

Rekomendasi:

```bash
python manage.py migrate
python manage.py auto_seed --sync --permissions-only
```

Jika kamu juga ingin sync menu dan default users (lebih agresif):

```bash
python manage.py auto_seed --sync
```

---

## C. Import data dari Laravel (opsional)

Jika kamu butuh data legacy (unit organisasi, pegawai, riwayat, dll), jalankan setelah migrate selesai:

```bash
python manage.py import_laravel_all_ordered --include-deleted
```

Catatan:
- Import ini tidak membuat user login aplikasi.
- User login dibuat oleh `auto_seed` (memanggil `seed_default_users`).

Command ini:
- menolak jalan jika masih ada migrations yang belum diterapkan
- menjalankan import berurutan (master → unit organisasi → jabatan → pendidikan → pegawai → riwayat)
- menjalankan `post_import_seed_flags` di akhir untuk menjaga flag internal seperti `is_opd_induk`

---

## D. One-liner untuk VPS (opsional)

Kalau kamu ingin sekali jalan (migrate + seed) dan opsional import:

```bash
chmod +x vps-migrate-seed.sh
RUN_IMPORT_LARAVEL_ALL_ORDERED=1 ./vps-migrate-seed.sh
```

---

## E. Validasi cepat setelah migrate/seed

Verifikasi permission seed masuk:

```bash
python manage.py shell -c "from apps.manajemen.models import PermissionFunction; print('permission_functions=', PermissionFunction.objects.count())"
```

Verifikasi flag `is_opd_induk`:

```bash
python manage.py shell -c "from apps.master_data.models import MdJenisOrganisasi; print('jenis_org_total=', MdJenisOrganisasi.objects.count()); print('is_opd_induk_true=', MdJenisOrganisasi.objects.filter(is_opd_induk=True).count())"
```
