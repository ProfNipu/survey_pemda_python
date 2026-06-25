# Menu Survey - Panduan Akses

## Lokasi Menu "Jenis Survey"

Menu **Jenis Survey** dapat diakses melalui sidebar dengan struktur berikut:

```
📊 Survey (Kategori)
├── ⭐ Penilaian JPT (Parent Menu)
│   ├── 📋 Daftar Penilaian (TODO)
│   ├── ➕ Tambah Penilaian (TODO)
│   └── 📊 Laporan Hasil (TODO)
│
└── ⚙️ Master Survey (Parent Menu)  ← KLIK INI
    ├── 🏷️ Jenis Survey           ← MENU YANG DICARI (CRUD ✓)
    └── ❓ Pertanyaan Survey        ← (CRUD ✓)
```

## Cara Akses

### Via Sidebar
1. Login ke aplikasi: http://localhost:8006
2. Lihat sidebar sebelah kiri
3. Cari kategori **"Survey"** (icon: 📊)
4. Klik **"Master Survey"** untuk expand
5. Klik **"Jenis Survey"**

### Via URL Langsung
Akses langsung ke halaman CRUD:
```
http://localhost:8006/survey/jenis-survey/
http://localhost:8006/survey/pertanyaan-survey/
```

**Catatan**: Tidak lagi menggunakan Django Admin, sekarang menggunakan custom views dengan Tailwind CSS.

## Fungsi Menu

### 1. Jenis Survey
**URL**: `/survey/jenis-survey/`

**Fungsi**:
- Mengelola master jenis survey (JPT, 360, dll)
- Menambah jenis survey baru
- Edit/hapus jenis survey existing
- Aktifkan/nonaktifkan jenis survey

**Interface**:
- ✅ Custom views dengan Tailwind CSS
- ✅ Search functionality
- ✅ Pagination (10/25/50/100 per page)
- ✅ HTMX support untuk smooth form submission
- ✅ SweetAlert2 untuk notifikasi
- ✅ Dependency check saat delete

**Kolom**:
- Kode Survey (unique)
- Nama Survey
- Deskripsi
- Jumlah Pertanyaan (badge)
- Status (Aktif/Nonaktif badge)
- Aksi (Edit/Delete icons)

### 2. Pertanyaan Survey
**URL**: `/survey/pertanyaan-survey/`

**Fungsi**:
- Mengelola pertanyaan per jenis survey
- Menambah pertanyaan baru
- Set bobot pertanyaan
- Atur urutan pertanyaan
- Aktifkan/nonaktifkan pertanyaan

**Interface**:
- ✅ Custom views dengan Tailwind CSS
- ✅ Search functionality
- ✅ Filter by jenis survey (dropdown)
- ✅ Pagination (10/25/50/100 per page)
- ✅ HTMX support
- ✅ SweetAlert2 untuk notifikasi

**Kolom**:
- Jenis Survey (nama)
- Kode Pertanyaan
- Pertanyaan (truncated jika panjang)
- Urutan (sorting)
- Bobot (monospace font)
- Status (Aktif/Nonaktif badge)
- Aksi (Edit/Delete icons)

## Contoh Penggunaan

### Menambah Jenis Survey Baru

1. Akses menu **Survey → Master Survey → Jenis Survey**
2. Klik tombol **"Add Jenis Survey"** (kanan atas)
3. Isi form:
   ```
   Kode Survey: SURVEY_360
   Nama Survey: Survey 360 Derajat
   Deskripsi: Penilaian dari berbagai sudut pandang
   Is Active: ✓
   ```
4. Klik **"Save"**

### Menambah Pertanyaan untuk Survey

1. Akses menu **Survey → Master Survey → Pertanyaan Survey**
2. Klik tombol **"Add Pertanyaan Survey"** (kanan atas)
3. Isi form:
   ```
   Jenis Survey: [Pilih dari dropdown]
   Kode Pertanyaan: survey01
   Pertanyaan: Bagaimana kemampuan kepemimpinan?
   Urutan: 1
   Bobot: 1.0
   Is Active: ✓
   ```
4. Klik **"Save"**

## Data Awal (Seeded)

Saat ini sudah ada data awal:

### Jenis Survey
- **Kode**: `JPT`
- **Nama**: Penilaian JPT (Jabatan Pimpinan Tinggi)
- **Status**: Active

### Pertanyaan (7 pertanyaan)
1. survey01 - bobot 1.0
2. survey02 - bobot 1.0
3. survey03 - bobot 1.0
4. survey04 - bobot 1.0
5. survey05 - bobot 1.0
6. survey06 - bobot 1.0
7. survey07 - bobot 1.0

## Sistem Dinamis

Keunggulan sistem ini:
- ✅ Tambah jenis survey baru tanpa coding
- ✅ Pertanyaan bisa berbeda per jenis survey
- ✅ Bobot pertanyaan bisa dikustomisasi
- ✅ Perhitungan nilai otomatis
- ✅ Mudah dikelola via Django Admin

## Troubleshooting

### Menu tidak muncul
```bash
docker exec survey_pemda_python_app python manage.py seed_survey_menu
docker restart survey_pemda_python_app
```

### Permission denied
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### Ingin akses langsung tanpa login
Pastikan user sudah login dan punya permission superadmin.

## Next Steps

Setelah mengelola master data, langkah selanjutnya:
1. Buat form input penilaian (via menu **Penilaian JPT → Tambah Penilaian**)
2. Lihat daftar penilaian (via menu **Penilaian JPT → Daftar Penilaian**)
3. Generate laporan (via menu **Penilaian JPT → Laporan Hasil**)

---

**Catatan**: Menu ini menggunakan Django Admin sebagai interface sementara. Untuk custom UI yang lebih user-friendly, bisa dikembangkan views/templates khusus di masa depan.
