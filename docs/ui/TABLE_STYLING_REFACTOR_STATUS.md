# Status Refactor Table Styling (Django Tables2)

## Ringkasan Tujuan
Standarisasi tampilan semua tabel list page agar konsisten (border/gridline, padding, header uppercase, dan default `whitespace-nowrap`) dengan referensi gaya tabel **Kategori Pegawai**.

## Perubahan yang Sudah Dilakukan (Tercatat)

### 1) Standardisasi `attrs` kolom secara manual (sebelum Opsi B)
- File: `apps/manajemen/tables_analisis_jabatan.py`
  - Semua kolom pada tabel Analisis Jabatan (Anjab) disamakan `attrs`-nya agar konsisten: header uppercase + padding + border + `whitespace-nowrap`.

- File: `apps/manajemen/tables_kepegawaian.py`
  - Penyesuaian beberapa kolom agar konsisten terutama `td` menambahkan `whitespace-nowrap`.

- File: `apps/manajemen/tables_relasi_organisasi.py`
  - Penyesuaian beberapa kolom agar konsisten terutama `td` menambahkan `whitespace-nowrap`.

### 2) Seeder permission: tambah fungsi bulk
- File: `apps/manajemen/management/commands/seed_master_data_permissions.py`
  - Tambah fungsi: `bulk_delete`, `export`
- File: `apps/manajemen/management/commands/seed_manajemen_referensi_data_bkn_permissions.py`
  - Tambah fungsi: `bulk_delete`, `export`
- File: `apps/manajemen/management/commands/seed_manajemen_analisis_jabatan_permissions.py`
  - Tambah fungsi: `bulk_delete`, `export`
- File: `apps/manajemen/management/commands/seed_manajemen_relasi_organisasi_permissions.py`
  - Tambah fungsi: `bulk_delete`, `export` (tetap mempertahankan `move`)
- File: `apps/manajemen/management/commands/seed_assessment_permissions.py`
  - Tambah fungsi: `bulk_delete`, `export`
- File: `apps/pegawai/management/commands/seed_kepegawaian_permissions.py`
  - Tambah fungsi: `bulk_delete`, `export`

### 3) Fix error seeder menu
- File: `apps/manajemen/management/commands/seed_menus.py`
  - Fix `NameError`: import `Q` dari `django.db.models`.

## Implementasi Opsi B (Helper dt_col_*)
Tujuan Opsi B: tetap manual/eksplisit memilih align/width/nowrap per kolom, tapi menghilangkan copy-paste class `attrs`.

### 4) Helper baru untuk `attrs` kolom
- File baru: `apps/common/table_attrs.py`
  - Menyediakan helper:
    - `dt_th()`, `dt_td()`, `dt_col_attrs()`
    - `dt_checkbox_attrs()`, `dt_row_number_attrs()`, `dt_actions_attrs()`

### 5) Refactor table ke helper Opsi B
- File: `apps/master_data/tables.py`
  - `KategoriPegawaiTable` direfactor:
    - `selection` -> `dt_checkbox_attrs()`
    - `row_number` -> `dt_row_number_attrs()`
    - kolom umum -> `dt_col_attrs()`
    - `actions` -> `dt_actions_attrs()`

- File: `apps/manajemen/tables_master_data.py`
  - Pondasi table direfactor:
    - `_BaseMasterDataTable.selection` -> `dt_checkbox_attrs()`
    - `_BaseMasterDataTable.row_number` -> `dt_row_number_attrs()`
    - `_actions_col()` -> `dt_actions_attrs()`
  - Kolom tabel yang sudah direfactor ke `dt_col_attrs()`:
    - `KategoriPegawaiTable`
    - `AgamaTable`
    - `StatusPerkawinanTable`
    - `JenjangPendidikanTable`
    - `DaftarPendidikanTable`
    - `KedudukanPegawaiTable`
  - Catatan penting:
    - Pernah ada mismatch nama kolom `StatusPerkawinanTable` vs `Meta.fields`; sudah diperbaiki agar nama kolom `status_perkawinan` sesuai `Meta.fields`.

## Pekerjaan yang Masih Pending
- Refactor sisa kolom di `apps/manajemen/tables_master_data.py` agar semua pakai `dt_col_attrs()`.
- Refactor modul lain agar konsisten pakai helper:
  - `apps/manajemen/tables_analisis_jabatan.py`
  - `apps/manajemen/tables_kepegawaian.py`
  - `apps/manajemen/tables_relasi_organisasi.py`
  - `apps/manajemen/tables.py` (permission management)
- Tambah guardrails agar tidak kejadian lagi:
  - Dokumentasi: aturan pembuatan tabel baru harus pakai helper
  - (Opsional) cek sederhana/grep di CI/pre-commit untuk mendeteksi `attrs={...}` manual di file tables.
