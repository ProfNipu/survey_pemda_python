# Add Judul Field to PertanyaanSurvey

## Overview
Menambahkan field `judul` untuk judul singkat aspek penilaian, dan mengubah field `pertanyaan` menjadi pertanyaan lengkap (opsional).

## Problem
Sebelumnya field `pertanyaan` digunakan untuk menyimpan judul singkat seperti "Berorientasi Pelayanan (1-5)". Ini tidak fleksibel karena:
- Tidak ada tempat untuk pertanyaan lengkap/deskripsi
- Judul dan pertanyaan tercampur dalam satu field

## Solution
Memisahkan menjadi 2 field:
- **judul**: Judul singkat aspek (contoh: "Berorientasi Pelayanan")
- **pertanyaan**: Pertanyaan lengkap/deskripsi (contoh: "Sejauh mana pegawai mampu memberikan pelayanan yang baik...")

## Changes Made

### 1. Migration (`0005_add_judul_field_to_pertanyaan.py`)

```python
# Step 1: Add 'judul' field (nullable)
# Step 2: Copy data from 'pertanyaan' to 'judul'
# Step 3: Make 'judul' non-nullable
# Step 4: Change 'pertanyaan' to TextField (nullable)
# Step 5: Clear old data from 'pertanyaan'
```

### 2. Model Update (`models.py`)

```python
class PertanyaanSurvey(models.Model):
    judul = models.CharField(max_length=200, verbose_name='Judul Aspek')
    pertanyaan = models.TextField(null=True, blank=True, verbose_name='Pertanyaan Lengkap')
    # ... other fields
```

### 3. Form Update (`forms.py`)

Added `judul` field to PertanyaanSurveyForm with proper widgets and help texts.

### 4. Table Update (`tables.py`)

Changed column to display `judul` instead of `pertanyaan`:
```python
pertanyaan = tables.Column(
    verbose_name='Judul Aspek',
    accessor='judul',
    # ...
)
```

### 5. Template Update (`buat_penilaian_form_dynamic.html`)

```django
<div class="question-title">{{ forloop.counter }}. {{ pertanyaan.judul }}</div>
{% if pertanyaan.pertanyaan %}
<div class="question-text">{{ pertanyaan.pertanyaan }}</div>
{% endif %}
```

### 6. Data Seeder (`update_pertanyaan_judul.py`)

Command untuk update data existing dengan judul dan pertanyaan lengkap:
```bash
python manage.py update_pertanyaan_judul
```

## Data Structure

### Before:
```
kode_pertanyaan: survey01
pertanyaan: "Berorientasi Pelayanan (1-5)"
```

### After:
```
kode_pertanyaan: survey01
judul: "Berorientasi Pelayanan"
pertanyaan: "Sejauh mana pegawai mampu memberikan pelayanan yang baik, responsif, dan berkualitas kepada masyarakat atau stakeholder?"
```

## Example Data

| Kode | Judul | Pertanyaan Lengkap |
|------|-------|-------------------|
| survey01 | Berorientasi Pelayanan | Sejauh mana pegawai mampu memberikan pelayanan yang baik, responsif, dan berkualitas kepada masyarakat atau stakeholder? |
| survey02 | Akuntabel | Sejauh mana pegawai bertanggung jawab atas tugas dan keputusan yang diambil, serta dapat mempertanggungjawabkan hasilnya? |
| survey03 | Kompeten | Sejauh mana pegawai memiliki pengetahuan, keterampilan, dan kemampuan yang diperlukan untuk melaksanakan tugasnya dengan baik? |
| survey04 | Harmonis | Sejauh mana pegawai mampu menciptakan dan memelihara hubungan kerja yang baik dengan rekan kerja dan atasan? |
| survey05 | Loyal | Sejauh mana pegawai menunjukkan kesetiaan dan dedikasi terhadap organisasi serta komitmen dalam melaksanakan tugas? |
| survey06 | Adaptif | Sejauh mana pegawai mampu menyesuaikan diri dengan perubahan, belajar hal baru, dan berinovasi dalam bekerja? |
| survey07 | Kolaboratif | Sejauh mana pegawai mampu bekerja sama dengan tim, berbagi pengetahuan, dan berkontribusi dalam pencapaian tujuan bersama? |

## Deployment Steps

1. **Run migration**:
   ```bash
   python manage.py migrate
   ```

2. **Update existing data**:
   ```bash
   python manage.py update_pertanyaan_judul
   ```

3. **Verify in admin/UI**:
   - Check Pertanyaan Survey list
   - Check form penilaian displays correctly

## Benefits

1. **Clearer structure**: Judul dan pertanyaan terpisah
2. **More flexible**: Bisa tambah pertanyaan lengkap atau tidak
3. **Better UX**: User bisa baca pertanyaan lengkap di form
4. **Easier maintenance**: Admin bisa edit judul dan pertanyaan terpisah

## Files Modified

- `apps/survey/models.py` - Added judul field
- `apps/survey/forms.py` - Updated form fields
- `apps/survey/tables.py` - Changed column to display judul
- `apps/survey/templates/survey_jpt/buat_penilaian_form_dynamic.html` - Display judul and pertanyaan

## Files Created

- `apps/survey/migrations/0005_add_judul_field_to_pertanyaan.py` - Migration file
- `apps/survey/management/commands/update_pertanyaan_judul.py` - Data seeder
- `docs_dari_sonnet/28_ADD_JUDUL_FIELD_TO_PERTANYAAN.md` - This documentation
