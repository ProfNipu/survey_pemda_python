# Periode Survey Integration

## Overview
Mengintegrasikan sistem periode survey dengan form penilaian JPT. Sekarang penilaian hanya bisa dilakukan pada periode yang aktif dan data tersimpan dengan link ke periode.

## Features Implemented

### 1. Periode Check
- Form penilaian hanya bisa diakses jika ada periode aktif
- Menampilkan pesan jika periode belum/sudah selesai
- Menampilkan info periode yang akan datang

### 2. Data Storage
- RespondenSurvey sekarang punya field `jenis_survey` dan `periode`
- Setiap penilaian terhubung dengan periode yang sedang aktif
- Mencegah duplikasi penilaian di periode yang sama

### 3. Validation
- Cek apakah user sudah pernah menilai pegawai yang sama di periode ini
- Validasi periode aktif sebelum menyimpan data

## Changes Made

### 1. Migration (`0006_add_periode_to_responden.py`)

Added fields to RespondenSurvey:
```python
jenis_survey = ForeignKey(JenisSurvey)
periode = ForeignKey(PeriodeSurvey)
```

### 2. Model Update (`models.py`)

```python
class RespondenSurvey(models.Model):
    jenis_survey = models.ForeignKey(JenisSurvey, ...)
    periode = models.ForeignKey(PeriodeSurvey, ...)
    # ... other fields
```

### 3. View Update (`views.py` - `buat_penilaian`)

**Periode Check:**
```python
periode_aktif = jenis_survey.periode.filter(
    is_active=True,
    tanggal_mulai__lte=timezone.now(),
    tanggal_selesai__gte=timezone.now()
).first()

if not periode_aktif:
    messages.error(request, 'Periode survey belum aktif')
    return redirect('survey:penilaian_list')
```

**Duplicate Check:**
```python
existing = RespondenSurvey.objects.filter(
    jenis_survey=jenis_survey,
    periode=periode_aktif,
    nip_pegawaiPenilai=nip_penilai,
    nip_pegawaiDinilai=nip_dinilai
).first()

if existing:
    messages.warning(request, 'Sudah pernah menilai di periode ini')
    return redirect('survey:penilaian_list')
```

**Save with Periode:**
```python
responden = RespondenSurvey.objects.create(
    jenis_survey=jenis_survey,
    periode=periode_aktif,
    nip_pegawaiPenilai=nip_penilai,
    nip_pegawaiDinilai=nip_dinilai,
    # ...
)
```

### 4. Template Update (`buat_penilaian_form_dynamic.html`)

Display periode info:
```django
<div class="year-badge">
    <i class="fas fa-calendar-alt"></i>
    Periode: {{ jenis_survey.periode_aktif.nama_periode }}
</div>
<p class="text-sm text-gray-600 mt-2">
    {{ jenis_survey.periode_aktif.tanggal_mulai|date:"d M Y H:i" }} - 
    {{ jenis_survey.periode_aktif.tanggal_selesai|date:"d M Y H:i" }}
</p>
```

### 5. Seeder (`seed_periode_jpt.py`)

Command untuk create periode aktif:
```bash
python manage.py seed_periode_jpt
```

Creates periode 3 bulan dari sekarang.

## User Flow

### Scenario 1: Periode Aktif
1. User akses form penilaian
2. System cek periode aktif
3. Form ditampilkan dengan info periode
4. User isi dan submit
5. System cek duplikasi
6. Data disimpan dengan link ke periode

### Scenario 2: Periode Belum Aktif
1. User akses form penilaian
2. System cek periode aktif → tidak ada
3. System cek periode mendatang
4. Tampilkan pesan: "Survey akan dibuka pada [tanggal]"
5. Redirect ke list

### Scenario 3: Periode Sudah Selesai
1. User akses form penilaian
2. System cek periode aktif → tidak ada
3. Tampilkan pesan: "Periode survey sudah ditutup"
4. Redirect ke list

### Scenario 4: Duplikasi
1. User submit penilaian
2. System cek existing penilaian
3. Found: User sudah menilai pegawai ini di periode ini
4. Tampilkan pesan: "Sudah pernah menilai, silakan edit"
5. Redirect ke list

## Database Structure

### Before:
```
RespondenSurvey:
- nip_pegawaiPenilai
- nip_pegawaiDinilai
- peranPenilai
- statusData
```

### After:
```
RespondenSurvey:
- jenis_survey (FK) → JenisSurvey
- periode (FK) → PeriodeSurvey
- nip_pegawaiPenilai
- nip_pegawaiDinilai
- peranPenilai
- statusData
```

## Benefits

1. **Controlled Access**: Penilaian hanya bisa dilakukan pada periode yang ditentukan
2. **Data Integrity**: Setiap penilaian terhubung dengan periode spesifik
3. **No Duplicates**: Mencegah user menilai pegawai yang sama berkali-kali di periode yang sama
4. **Better Reporting**: Bisa filter laporan berdasarkan periode
5. **Audit Trail**: Tahu kapan penilaian dilakukan (periode mana)

## Deployment Steps

1. **Run migration**:
   ```bash
   docker exec -it survey_pemda_python_app python manage.py migrate
   ```

2. **Create periode aktif**:
   ```bash
   docker exec -it survey_pemda_python_app python manage.py seed_periode_jpt
   ```

3. **Verify**:
   - Akses form penilaian
   - Lihat info periode di header
   - Coba submit penilaian
   - Cek data di tabel survey_responden

## Admin Tasks

### Create New Periode
1. Masuk ke menu "Master Survey > Periode Survey"
2. Klik "Tambah Periode"
3. Pilih Jenis Survey: "Penilaian JPT"
4. Isi nama periode, tanggal mulai, tanggal selesai
5. Centang "Aktif"
6. Simpan

### Close Current Periode
1. Masuk ke menu "Master Survey > Periode Survey"
2. Edit periode yang aktif
3. Ubah tanggal selesai atau uncheck "Aktif"
4. Simpan

### View Responses by Periode
1. Masuk ke menu "Master Survey > Responden Survey"
2. Filter by periode
3. Export data jika perlu

## Files Modified

- `apps/survey/models.py` - Added jenis_survey and periode fields
- `apps/survey/views.py` - Added periode check and validation
- `apps/survey/templates/survey_jpt/buat_penilaian_form_dynamic.html` - Display periode info

## Files Created

- `apps/survey/migrations/0006_add_periode_to_responden.py` - Migration file
- `apps/survey/management/commands/seed_periode_jpt.py` - Periode seeder
- `docs_dari_sonnet/29_PERIODE_SURVEY_INTEGRATION.md` - This documentation
