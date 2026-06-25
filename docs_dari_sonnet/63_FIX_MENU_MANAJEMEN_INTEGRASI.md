# Fix Menu Manajemen Integrasi

**Tanggal**: 1 April 2026  
**Status**: ✅ FIXED

## Masalah

Menu "Manajemen Integrasi" tidak bisa dibuka / tidak muncul di sidebar.

## Root Cause

1. Menu ESIMPEG ada di category "Data Pegawai" (ID: 4) bukan "Manajemen Integrasi" (ID: 6)
2. Child menu "Pegawai" tidak punya URL (url_name = None)

## Solusi

### 1. Update Category Menu ESIMPEG

```python
# Get correct category
cat_integrasi = MenuCategory.objects.get(code=4)  # Manajemen Integrasi

# Update menu ESIMPEG
esimpeg = MenuItem.objects.get(name='ESIMPEG')
esimpeg.category = cat_integrasi.id
esimpeg.save()
```

### 2. Update URL Child Menu Pegawai

```python
# Update child menu Pegawai
pegawai = MenuItem.objects.get(name='Pegawai', parent=esimpeg.id)
pegawai.url_name = 'api_simpeg:pegawai_list'
pegawai.save()
```

### 3. Restart Container

```bash
docker restart survey_pemda_python_app
```

## Hasil

✅ Menu "Manajemen Integrasi" sekarang muncul di sidebar  
✅ Submenu "ESIMPEG" → "Pegawai" bisa diklik  
✅ URL mengarah ke: `/api-simpeg/pegawai/`

## Testing

1. Login ke Survey Pemda: http://localhost:8006/
2. Cek sidebar, seharusnya ada menu "Manajemen Integrasi"
3. Klik "ESIMPEG" → "Pegawai"
4. Seharusnya redirect ke halaman pegawai list

## Catatan

Masalah ini terjadi karena seeder `seed_api_simpeg_menu` mendeteksi menu sudah ada (di category lain) dan tidak mengupdate category-nya.

