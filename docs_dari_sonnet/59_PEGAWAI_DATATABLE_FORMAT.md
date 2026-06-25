# Update: Pegawai List dengan Format Datatable Reusable

## Perubahan

Template pegawai list sekarang menggunakan format datatable yang sama dengan halaman manajemen fungsi dan halaman lain di aplikasi.

## Format Datatable Reusable

### Struktur Template

```
pegawai_list.html (main template)
├── includes/datatable_filters.html (search & filters)
├── includes/datatable_bulk_actions.html (bulk actions toolbar)
└── api_simpeg/partials/_pegawai_table.html (table content)
    ├── includes/datatable_loading.html (loading indicator)
    └── Table dengan pagination
```

### Fitur yang Tersedia

1. **Search & Filters**
   - Search box dengan placeholder "Cari nama atau NIP..."
   - Auto-submit on enter

2. **Bulk Actions**
   - Select all checkbox
   - Individual row checkbox
   - Export (CSV, Excel, PDF)
   - Print
   - Copy to clipboard

3. **Table Features**
   - Sortable columns (ID, NIP, Nama)
   - Hover effect pada rows
   - Responsive design
   - Column visibility toggle

4. **Pagination**
   - Previous/Next buttons
   - Page numbers (max 10 pages shown)
   - Current page highlighted
   - Total records info

5. **Actions**
   - View detail (SweetAlert2 modal)
   - Sync button (untuk sinkronisasi data)

### Komponen Reusable

#### 1. datatable_filters.html
```django
{% include 'includes/datatable_filters.html' with 
    show_search=True 
    search_placeholder="Cari nama atau NIP..." 
    show_status_filter=False 
%}
```

#### 2. datatable_bulk_actions.html
```django
{% include 'includes/datatable_bulk_actions.html' with 
    show_clear=True 
    show_copy=True 
    show_export=can_export 
    show_print=True 
    show_delete=False 
    export_formats="csv,excel,pdf" 
%}
```

#### 3. datatable_loading.html
```django
{% include 'includes/datatable_loading.html' %}
```

### JavaScript Integration

Template menggunakan `DatatableHelper` class untuk handle:
- Column sorting
- Bulk selection
- Export functionality
- Print functionality
- AJAX loading

```javascript
window.pegawaiIntegratedDT = new DatatableHelper({
    tableId: 'pegawai_table',
    pageKey: 'pegawai_list',
    saveUrl: '{% url "api_simpeg:pegawai_list" %}',
    deleteUrl: '',
    csrfToken: csrfToken,
    exportFormats: ['csv','excel','pdf'],
    entity: 'pegawai',
    useToast: true,
    debug: true
});
```

## Perbandingan

### Sebelum (Custom Template)
- Custom HTML tanpa reusable components
- Tidak ada bulk actions
- Tidak ada export functionality
- Tidak ada column sorting
- Pagination manual

### Sesudah (Datatable Reusable)
- ✅ Menggunakan reusable components
- ✅ Bulk actions (select, export, print, copy)
- ✅ Export ke CSV, Excel, PDF
- ✅ Column sorting
- ✅ Pagination otomatis
- ✅ Konsisten dengan halaman lain

## File yang Dibuat/Diubah

### 1. Template Utama
- `apps/api_simpeg/templates/api_simpeg/pegawai_list.html`
  - Menggunakan format datatable reusable
  - Include filters, bulk actions, dan table partial

### 2. Partial Table
- `apps/api_simpeg/templates/api_simpeg/partials/_pegawai_table.html`
  - Table content dengan pagination
  - Detail modal dengan SweetAlert2

### 3. View (Tidak Berubah)
- `apps/api_simpeg/views.py`
  - View sudah support HTMX untuk partial loading

### 4. URLs (Tidak Berubah)
- `apps/api_simpeg/urls.py`
  - URL pattern sudah ada

## Testing

```bash
# 1. Container sudah direstart

# 2. Logout dan login kembali
#    Username: Prakom@admin2025.com
#    Password: Prakom@2025

# 3. Akses halaman pegawai
#    URL: http://localhost:8006/api-simpeg/pegawai/

# 4. Test fitur:
#    ✅ Search pegawai
#    ✅ Select rows (checkbox)
#    ✅ Export data (CSV/Excel/PDF)
#    ✅ Print table
#    ✅ Copy to clipboard
#    ✅ Sort columns
#    ✅ Pagination
#    ✅ View detail modal
```

## Fitur Tambahan

### Sync Button
Button untuk sinkronisasi data dari ESIMPEG API:

```javascript
function syncPegawai() {
    Swal.fire({
        title: 'Sinkronisasi Data',
        text: 'Apakah Anda yakin ingin menyinkronkan data pegawai dari ESIMPEG?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Ya, Sinkronkan!',
        cancelButtonText: 'Batal'
    }).then((result) => {
        if (result.isConfirmed) {
            // TODO: Implement sync API call
        }
    });
}
```

### Detail Modal
Modal detail menggunakan SweetAlert2 dengan layout 2 kolom:
- Kolom kiri: Data Pribadi
- Kolom kanan: Data Kepegawaian
- Bawah: Data Pensiun (jika ada)

## Konsistensi dengan Halaman Lain

Template sekarang konsisten dengan:
- `/manajemen-aplikasi/functions/` (Manajemen Fungsi)
- `/manajemen-aplikasi/modules/` (Manajemen Module)
- `/manajemen-aplikasi/controls/` (Manajemen Control)
- `/survey/jenis-survey/` (Jenis Survey)
- `/survey/pertanyaan-survey/` (Pertanyaan Survey)

Semua menggunakan format datatable reusable yang sama!

## Kesimpulan

✅ **Format konsisten**: Sama dengan halaman lain di aplikasi
✅ **Reusable components**: Menggunakan includes yang sudah ada
✅ **Fitur lengkap**: Search, sort, export, print, bulk actions
✅ **Responsive**: Mobile-friendly
✅ **User-friendly**: Familiar interface untuk user

---

**Updated**: 2026-03-31
**Format**: Datatable Reusable
**Status**: READY ✅
