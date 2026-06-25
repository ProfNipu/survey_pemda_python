# Konfigurasi Combo Box — Logic Filtering (Jenis Jabatan & Jabatan)

Dokumen ini menjelaskan ekspektasi perilaku dan mapping field untuk filter pada halaman **Konfigurasi Combo Box**.

## Tujuan

- Filter pegawai berdasarkan:
  - Unit Kerja / Sub Unit Kerja
  - Jenis Jabatan
  - Jabatan (single/multi)
- Dropdown **Jabatan** bersifat **dependent** terhadap pilihan **Jenis Jabatan**.
- Dukungan HTMX:
  - Update tabel tanpa reload penuh
  - Querystring tetap terbawa saat pagination/jump page
  - URL mencerminkan filter untuk bookmarking

## Parameter Querystring

- `id_opd`
- `id_sub_opd`
- `caripegawai` (atau `search`, kompatibel)
- `id_jenis_jabatan`
- `id_jabatan` (bisa multi: query param berulang)
- `id_sub_jabatan` (khusus jenis=3; bisa multi: query param berulang)

Kompatibilitas lama:
- `id_jabatan_struktural` masih diterima sebagai fallback untuk `id_jabatan`.

Contoh multi-value:

- `...?id_jenis_jabatan=2&id_jabatan=10&id_jabatan=12`

## Rule Umum Queryset `MsPegawai`

Baseline:

- `MsPegawai.deleted_at is null`
- Exclude tertentu:
  - `exclude(A_01=99)`
  - `exclude(B_11__status_hitung=2)`

Filter organisasi:

- Jika `id_opd` terisi: `filter(id_opd_id=id_opd)`
- Jika `id_sub_opd` terisi: `filter(id_sub_opd_id=id_sub_opd)`
- Edge-case: jika `id_opd == id_sub_opd`, maka `id_sub_opd` dianggap kosong (agar tidak over-restrict).

Filter jenis jabatan:

- Jika `id_jenis_jabatan` terisi: `filter(id_jenis_jabatan_id=id_jenis_jabatan)`

Filter pencarian:

- Jika `caripegawai` terisi, match salah satu:
  - `B_02B` (NIP baru)
  - `B_02` (NIP lama)
  - `B_03` (nama)

## Dependent Dropdown: Sumber Data Jabatan

Dropdown `Jabatan` (`id_jabatan`) menggunakan endpoint remote-search yang berbeda berdasarkan `id_jenis_jabatan`.

### Jenis Jabatan = 1 (Struktural)

- **Sumber dropdown**: `MsJabatanStruktural`
- **Endpoint**: `ajax_jabatan_struktural_list`
- **Syarat input**:
  - Wajib `id_opd`
  - Opsional `id_sub_opd`
- **Filter endpoint**:
  - Filter by `id_sub_opd` jika diisi, kalau tidak by `id_opd`

**Filter pegawai** (multi-value):

- `MsPegawai.id_jabatan_id IN (id_jabatan...)`

### Jenis Jabatan = 2 (Non-Struktural/Pelaksana)

- **Sumber dropdown**: `MsJabatanNonStruktural`
- **Endpoint**: `ajax_jabatan_non_struktural_list`
- **Syarat input**:
  - Wajib `id_jenis_jabatan`
- **Filter endpoint**:
  - `deleted_at is null`
  - `id_status = 1`
  - `id_jenis_jabatan = <jenis>`

**Filter pegawai** (multi-value):

- `MsPegawai.id_jfu_jft_id IN (id_jabatan...)`

### Jenis Jabatan = 3 (Fungsional Tertentu) — Opsi A

- **Sumber dropdown**: `BknJabatanFungsional`
- **Endpoint**: `ajax_bkn_jabatan_fungsional_list`

**Catatan**: untuk jenis=3, pilihan di dropdown adalah record `BknJabatanFungsional` (id integer). Namun filtering pegawai mengikuti mapping dari Laravel addForm.

#### Mapping Filter

Jika user memilih satu/lebih item `BknJabatanFungsional`:

- Map `kel_jabatan_id` (BKN) ke `MsJabatanNonStruktural.id_bkn` via relasi pegawai:
  - `MsPegawai.id_jfu_jft__id_bkn = BknJabatanFungsional.kel_jabatan_id`
- Map `jenjang` (BKN) ke `MdJenjangJabatan.id_bkn`, lalu ke pegawai:
  - `MdJenjangJabatan.id_bkn = BknJabatanFungsional.jenjang`
  - `MsPegawai.I_07_id = MdJenjangJabatan.id`

#### Cara Apply untuk Multi-Select

Untuk multi-select, rule dibangun sebagai OR per item yang dipilih:

- `(kel_1 AND jenjang_1) OR (kel_2 AND jenjang_2) OR ...`

Jika salah satu komponen mapping tidak ditemukan:

- Jika `kel_jabatan_id` kosong, maka komponen filter kel di-skip.
- Jika `jenjang` kosong atau tidak ada mapping `MdJenjangJabatan`, maka komponen filter jenjang di-skip.
- Jika keduanya kosong untuk sebuah item, item tersebut tidak menyumbang filter.

## Sub Jabatan (khusus Jenis Jabatan = 3)

### Sumber dropdown

- **Sumber dropdown**: `BknSubJabatan`
- **Endpoint**: `ajax_bkn_sub_jabatan_list`
- **Parameter endpoint**:
  - `id_jabatan` (repeatable) berisi id `BknJabatanFungsional` yang sedang dipilih

### Rule tampilkan opsi

Dropdown `Sub Jabatan` hanya akan mengembalikan opsi jika pilihan `Jabatan` (BKN Jabatan Fungsional) memenuhi:

- Memiliki `kel_jabatan_id` yang valid, dan
- Seluruh pilihan `Jabatan` yang dipilih resolve ke **tepat 1 nilai** `kel_jabatan_id`.

Jika user memilih beberapa `Jabatan` dan `kel_jabatan_id`-nya berbeda-beda, endpoint akan mengembalikan hasil kosong.

### Filter pegawai

Jika `id_sub_jabatan` diisi:

- `MsPegawai.id_sub_jabatan_id IN (id_sub_jabatan...)`

## UI / UX Rules

### Multi-select Jabatan

- `id_jabatan` adalah `<select multiple>`.
- Komponen searchable-select menampilkan pilihan terpilih sebagai **chips/tags**.

### Tombol Clear (×)

Setiap combobox enhanced memiliki tombol clear di sisi kanan:

- **Single select**: mengosongkan nilai
- **Multi select**: menghapus semua chip

### Reset

Tombol Reset form:

- Clear semua filter (termasuk Unit/Sub Unit, Jenis Jabatan, Jabatan)
- Jabatan akan kembali disabled sampai Jenis Jabatan dipilih (dan jika jenis=1, wajib pilih Unit Kerja)

## Pagination / Jump to Page

- Pagination HTMX harus meng-include seluruh parameter filter.
- Untuk multi-select `id_jabatan`, querystring dibangun dengan param berulang:
  - `&id_jabatan=10&id_jabatan=12`
- Untuk multi-select `id_sub_jabatan` (jenis=3), querystring dibangun dengan param berulang:
  - `&id_sub_jabatan=7&id_sub_jabatan=9`

## Catatan Risiko & Saran Perbaikan

- Jenis=3 (fungsional) saat multi-select dapat melakukan lookup `MdJenjangJabatan` per item; jika item banyak, bisa dioptimasi dengan bulk fetch (`id_bkn__in`).
- Jika ada data BKN yang tidak lengkap (kel/jenjang kosong), hasil filter bisa membingungkan. Opsi lanjut: tampilkan warning UI bila mapping tidak lengkap.

## Catatan untuk Form Insert/Edit (bukan filter)

- Untuk kebutuhan **insert/edit data jabatan aktif/riwayat**, umumnya field `Jabatan`/`Sub Jabatan` adalah **single-select**, bukan multi.
- Multi-select tetap cocok untuk **filter/listing**, karena user bisa mencari pegawai yang match salah satu dari banyak jabatan.
