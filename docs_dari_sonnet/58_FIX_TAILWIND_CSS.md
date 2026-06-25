# Fix: Tampilan Kacau - Bootstrap ke Tailwind CSS

## Masalah

Tampilan halaman `/api-simpeg/pegawai/` kacau karena menggunakan Bootstrap classes tapi base template menggunakan Tailwind CSS.

## Penyebab

Template `pegawai_list.html` menggunakan Bootstrap classes:
- `container-fluid`
- `card`, `card-header`, `card-body`
- `table`, `table-striped`, `table-hover`
- `btn`, `btn-primary`, `btn-sm`
- `modal`, `modal-dialog`, `modal-content`

Tapi `base_dashboard.html` menggunakan Tailwind CSS, bukan Bootstrap!

## Solusi

Rewrite template dari Bootstrap ke Tailwind CSS:

### Bootstrap → Tailwind Mapping

| Bootstrap | Tailwind |
|-----------|----------|
| `container-fluid` | `(removed, use full width)` |
| `card` | `bg-white rounded-xl shadow-lg` |
| `card-header` | `(removed, use heading)` |
| `card-body` | `p-6` |
| `table` | `min-w-full divide-y divide-gray-200` |
| `table-striped` | `divide-y divide-gray-200` + `hover:bg-gray-50` |
| `btn btn-primary` | `bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg` |
| `btn-sm` | `px-3 py-1 text-sm` |
| `badge bg-primary` | `px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800` |
| `modal` | `Swal.fire()` (SweetAlert2) |

### Perubahan Utama

1. **Layout**: Dari Bootstrap grid ke Tailwind flexbox
2. **Card**: Dari Bootstrap card ke Tailwind rounded-xl + shadow
3. **Table**: Dari Bootstrap table ke Tailwind table dengan divide
4. **Buttons**: Dari Bootstrap btn ke Tailwind custom buttons
5. **Badges**: Dari Bootstrap badge ke Tailwind badge
6. **Modal**: Dari Bootstrap modal ke SweetAlert2

### Detail Modal

Bootstrap modal diganti dengan SweetAlert2:

```javascript
function showDetail123() {
    Swal.fire({
        title: '<strong>Detail Pegawai</strong>',
        html: `...`,
        width: '800px',
        showCloseButton: true,
        showConfirmButton: false
    });
}
```

## File yang Diubah

- `projects/survey_pemda_python/apps/api_simpeg/templates/api_simpeg/pegawai_list.html`
  - Rewrite lengkap dari Bootstrap ke Tailwind CSS
  - Modal diganti dengan SweetAlert2
  - Responsive design dengan Tailwind

## Testing

```bash
# 1. Container sudah direstart

# 2. Akses halaman pegawai
# URL: http://localhost:8006/api-simpeg/pegawai/
# Seharusnya:
# ✅ Tampilan rapi dengan Tailwind CSS
# ✅ Table responsive
# ✅ Search dan pagination bekerja
# ✅ Detail modal dengan SweetAlert2
```

## Hasil

✅ **Tampilan rapi**: Menggunakan Tailwind CSS yang konsisten dengan base template
✅ **Responsive**: Mobile-friendly dengan Tailwind responsive classes
✅ **Modal cantik**: SweetAlert2 untuk detail pegawai
✅ **Konsisten**: Sama dengan halaman lain di aplikasi

## Catatan

Survey Pemda menggunakan Tailwind CSS, bukan Bootstrap. Semua template harus menggunakan Tailwind CSS classes.

Referensi template lain yang sudah benar:
- `apps/survey/templates/master_survey/jenis_survey/list.html`
- `apps/survey/templates/master_survey/pertanyaan_survey/list.html`
- `templates/dashboard/index.html`

---

**Fixed**: 2026-03-31
