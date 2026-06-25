# Dynamic Assessment Implementation

## Overview
Mengubah sistem penilaian JPT dari hardcoded aspects menjadi dynamic dari database menggunakan JenisSurvey dan PertanyaanSurvey.

## Changes Made

### 1. View Update (`apps/survey/views.py`)

#### Function: `buat_penilaian`
- **Before**: Menggunakan PenilaianJPT model dengan 6 aspek hardcoded (kepemimpinan, kerjasama, komunikasi, inovasi, integritas, orientasi_hasil)
- **After**: Menggunakan RespondenSurvey dan JawabanSurvey untuk menyimpan penilaian dinamis

#### Key Changes:
1. **GET Request**:
   - Fetch pertanyaan dari database: `PertanyaanSurvey.objects.filter(jenis_survey=jenis_survey, is_active=True)`
   - Pass `pertanyaan_list` ke template
   - Render template `buat_penilaian_form_dynamic.html` instead of `buat_penilaian_form.html`

2. **POST Request**:
   - Create `RespondenSurvey` object dengan data penilai dan yang dinilai
   - Loop through `pertanyaan_list` dan save jawaban ke `JawabanSurvey`
   - Field name format: `pertanyaan_{pertanyaan.id}` dengan nilai 1-5

### 2. Template Update (`apps/survey/templates/survey_jpt/buat_penilaian_form_dynamic.html`)

#### Changes:
1. **Form Fields**:
   - Replace Django form fields dengan plain HTML inputs
   - Hidden fields untuk data penilai (nip_penilai, nama_penilai, jabatan_penilai, unit_kerja_penilai)
   - Text inputs untuk data yang dinilai (nip_dinilai, nama_dinilai, jabatan_dinilai, unit_kerja_dinilai)

2. **Dynamic Questions**:
   ```django
   {% for pertanyaan in pertanyaan_list %}
   <div class="question-section">
       <div class="question-title">{{ forloop.counter }}. {{ pertanyaan.pertanyaan }}</div>
       <input type="range" name="pertanyaan_{{ pertanyaan.id }}" min="1" max="5" value="3">
   </div>
   {% endfor %}
   ```

3. **Slider Implementation**:
   - Range input (1-5) untuk setiap pertanyaan
   - JavaScript untuk update display value
   - Visual feedback dengan color gradient

## Database Models Used

### JenisSurvey
- Stores survey types (e.g., "Penilaian JPT")
- Fields: kode, nama, deskripsi, is_active

### PertanyaanSurvey
- Stores questions for each survey type
- Fields: jenis_survey (FK), kode_pertanyaan, pertanyaan, urutan, bobot, is_active

### RespondenSurvey
- Stores responder information
- Fields: nip_pegawaiPenilai, nip_pegawaiDinilai, peranPenilai, statusData

### JawabanSurvey
- Stores answers for each question
- Fields: responden (FK), pertanyaan (FK), nilai (1-5)

## Benefits

1. **Flexibility**: Admin dapat menambah/edit pertanyaan tanpa ubah kode
2. **Scalability**: Bisa digunakan untuk berbagai jenis survey
3. **Maintainability**: Tidak perlu migration setiap kali ada perubahan aspek penilaian
4. **Reusability**: Model RespondenSurvey dan JawabanSurvey bisa digunakan untuk survey lain

## Testing

1. Pastikan ada data di tabel `survey_jenis` dan `survey_pertanyaan`
2. Akses URL: `/survey/buat-penilaian/`
3. Isi form dan submit
4. Check data di tabel `survey_responden` dan `survey_jawaban`

## Migration Path

### Old System (PenilaianJPT):
```python
PenilaianJPT(
    nip_dinilai='...',
    kepemimpinan=4,
    kerjasama=5,
    komunikasi=4,
    ...
)
```

### New System (RespondenSurvey + JawabanSurvey):
```python
responden = RespondenSurvey(
    nip_pegawaiPenilai='...',
    nip_pegawaiDinilai='...'
)

JawabanSurvey(responden=responden, pertanyaan=pertanyaan1, nilai=4)
JawabanSurvey(responden=responden, pertanyaan=pertanyaan2, nilai=5)
```

## Next Steps

1. Update `penilaian_list` view to show data from RespondenSurvey
2. Update `penilaian_detail` view to display answers from JawabanSurvey
3. Create report/export functionality for dynamic survey results
4. Consider deprecating PenilaianJPT model if no longer needed

## Files Modified

- `apps/survey/views.py` - buat_penilaian function
- `apps/survey/templates/survey_jpt/buat_penilaian_form_dynamic.html` - new dynamic template

## Files Created

- `docs_dari_sonnet/27_DYNAMIC_ASSESSMENT_IMPLEMENTATION.md` - this documentation
