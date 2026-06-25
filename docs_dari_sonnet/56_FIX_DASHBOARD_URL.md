# Fix: Dashboard URL di Template Pegawai List

## Error

```
NoReverseMatch at /api-simpeg/pegawai/
Reverse for 'dashboard' not found. 'dashboard' is not a valid view function or pattern name.
```

## Penyebab

Template `pegawai_list.html` menggunakan:
```django
<li class="breadcrumb-item"><a href="{% url 'dashboard' %}">Dashboard</a></li>
```

Tapi URL name yang benar adalah `manajemen_aplikasi:dashboard` (dengan namespace).

## Solusi

Update template dari:
```django
{% url 'dashboard' %}
```

Menjadi:
```django
{% url 'manajemen_aplikasi:dashboard' %}
```

## File yang Diubah

- `projects/survey_pemda_python/apps/api_simpeg/templates/api_simpeg/pegawai_list.html`
  - Line 10: Update URL name dari `'dashboard'` ke `'manajemen_aplikasi:dashboard'`

## Testing

```bash
# 1. Restart container (optional)
docker restart survey_pemda_python_app

# 2. Akses halaman pegawai
# URL: http://localhost:8006/api-simpeg/pegawai/
# Seharusnya tidak ada error lagi
```

## Kesimpulan

✅ Error NoReverseMatch fixed
✅ Breadcrumb link ke dashboard sekarang bekerja
✅ User bisa akses halaman pegawai list

---

**Fixed**: 2026-03-31
