# Survey System - Overview & Architecture

## 🎯 Sistem Survey Dinamis

Project ini menggunakan sistem survey yang **100% dinamis** - artinya Anda bisa menambah jenis survey baru dan pertanyaan tanpa perlu mengubah kode.

## 📊 Database Schema

### 1. survey_jenis (Master Jenis Survey)
```python
- id (PK)
- kode (unique) - Kode survey (misal: JPT, SURVEY_360)
- nama - Nama lengkap survey
- deskripsi - Deskripsi survey (optional)
- is_active - Status aktif/nonaktif
- created_at, updated_at
```

### 2. survey_pertanyaan (Pertanyaan per Survey)
```python
- id (PK)
- jenis_survey_id (FK → survey_jenis)
- kode_pertanyaan - Kode pertanyaan (misal: survey01)
- pertanyaan - Teks pertanyaan
- urutan - Nomor urut untuk sorting
- bobot - Bobot untuk perhitungan (default: 1.0)
- is_active - Status aktif/nonaktif
- created_at, updated_at
- UNIQUE: (jenis_survey_id, kode_pertanyaan)
```

### 3. survey_responden (Data Responden)
```python
- id (PK)
- id_pegawaiPenilai - ID pegawai yang menilai
- nip_pegawaiPenilai - NIP penilai
- id_pegawaiDinilai - ID pegawai yang dinilai
- nip_pegawaiDinilai - NIP yang dinilai
- peranPenilai - Peran penilai (atasan, rekan, bawahan, dll)
- statusData - Status (draft, submitted, approved)
- created_at, updated_at
```

### 4. survey_jawaban (Jawaban Survey)
```python
- id (PK)
- responden_id (FK → survey_responden)
- pertanyaan_id (FK → survey_pertanyaan)
- nilai - Nilai 1-5
- created_at, updated_at
- UNIQUE: (responden_id, pertanyaan_id)
```

## 🔄 Flow Sistem

### 1. Setup Master Data
```
Admin → Master Survey → Jenis Survey
  ↓
Tambah: JPT, SURVEY_360, dll
  ↓
Admin → Master Survey → Pertanyaan Survey
  ↓
Tambah pertanyaan untuk setiap jenis survey
```

### 2. Input Penilaian
```
User → Penilaian JPT → Tambah Penilaian
  ↓
Pilih pegawai yang dinilai
  ↓
Isi form pertanyaan (nilai 1-5)
  ↓
Submit → Data masuk ke survey_responden & survey_jawaban
```

### 3. Perhitungan Otomatis
```python
# Untuk setiap jawaban
nilai_terbobot = nilai × bobot_pertanyaan

# Total nilai responden
total_nilai = sum(nilai_terbobot untuk semua jawaban)

# Rata-rata
rata_rata = total_nilai / sum(bobot_pertanyaan)
```

### 4. Laporan
```
Admin → Penilaian JPT → Laporan Hasil
  ↓
Filter: pegawai, periode, jenis survey
  ↓
Tampilkan: grafik, tabel, statistik
```

## 🎨 Menu Structure

```
📊 Survey
├── ⭐ Penilaian JPT
│   ├── 📋 Daftar Penilaian (TODO: implement view)
│   ├── ➕ Tambah Penilaian (TODO: implement form)
│   └── 📊 Laporan Hasil (TODO: implement report)
│
└── ⚙️ Master Survey
    ├── 🏷️ Jenis Survey (Django Admin - READY ✓)
    └── ❓ Pertanyaan Survey (Django Admin - READY ✓)
```

## ✅ Status Implementasi

### DONE ✓
- [x] Database models (4 tabel)
- [x] Django Admin interface
- [x] Menu sidebar structure
- [x] Seeder untuk data awal (JPT + 7 pertanyaan)
- [x] Dokumentasi lengkap

### TODO 📝
- [ ] Form input penilaian (Tambah Penilaian)
- [ ] List view penilaian (Daftar Penilaian)
- [ ] Report/analytics (Laporan Hasil)
- [ ] API endpoints (optional)
- [ ] Export to Excel/PDF (optional)

## 🚀 Quick Start

### 1. Akses Master Data
```
URL: http://localhost:8006/admin/survey_jpt/jenissurvey/
Login dengan superadmin
```

### 2. Tambah Jenis Survey Baru
```python
Kode: SURVEY_360
Nama: Survey 360 Derajat
Deskripsi: Penilaian dari berbagai sudut pandang
Is Active: ✓
```

### 3. Tambah Pertanyaan
```python
Jenis Survey: SURVEY_360
Kode Pertanyaan: q01
Pertanyaan: Bagaimana kemampuan komunikasi?
Urutan: 1
Bobot: 1.5  # Bisa berbeda per pertanyaan
Is Active: ✓
```

## 💡 Keunggulan Sistem Dinamis

### 1. Fleksibilitas
- Tambah survey baru tanpa coding
- Pertanyaan bisa berbeda per jenis survey
- Bobot bisa dikustomisasi per pertanyaan

### 2. Skalabilitas
- Support unlimited jenis survey
- Support unlimited pertanyaan per survey
- Support unlimited responden

### 3. Maintainability
- Semua konfigurasi di database
- Mudah di-backup/restore
- Mudah di-migrate antar environment

### 4. Perhitungan Otomatis
- Nilai terbobot otomatis
- Total & rata-rata otomatis
- Bisa custom formula di model

## 📝 Contoh Use Case

### Use Case 1: Survey JPT (Sudah Ada)
```
Jenis: JPT
Pertanyaan: 7 pertanyaan (survey01-survey07)
Bobot: Semua 1.0
Target: Pejabat JPT
Penilai: Atasan, rekan, bawahan
```

### Use Case 2: Survey 360 (Bisa Ditambah)
```
Jenis: SURVEY_360
Pertanyaan: 20 pertanyaan (berbeda dari JPT)
Bobot: Bervariasi (1.0 - 2.0)
Target: Semua pegawai
Penilai: 360 derajat (atasan, rekan, bawahan, diri sendiri)
```

### Use Case 3: Survey Kepuasan (Bisa Ditambah)
```
Jenis: KEPUASAN_LAYANAN
Pertanyaan: 10 pertanyaan tentang layanan
Bobot: Semua 1.0
Target: Masyarakat/stakeholder
Penilai: Pengguna layanan
```

## 🔧 Development Guide

### Menambah Custom View
```python
# apps/survey_jpt/views.py
from django.views.generic import ListView, CreateView
from .models import RespondenSurvey, JenisSurvey

class PenilaianListView(ListView):
    model = RespondenSurvey
    template_name = 'survey_jpt/penilaian_list.html'
    context_object_name = 'penilaian_list'
    
class PenilaianCreateView(CreateView):
    model = RespondenSurvey
    template_name = 'survey_jpt/penilaian_form.html'
    fields = ['id_pegawaiDinilai', 'nip_pegawaiDinilai', 'peranPenilai']
```

### Menambah URL
```python
# apps/survey_jpt/urls.py
from django.urls import path
from . import views

app_name = 'survey_jpt'

urlpatterns = [
    path('penilaian/', views.PenilaianListView.as_view(), name='penilaian_list'),
    path('penilaian/create/', views.PenilaianCreateView.as_view(), name='penilaian_create'),
    path('penilaian/<int:pk>/', views.PenilaianDetailView.as_view(), name='penilaian_detail'),
    path('laporan/', views.LaporanView.as_view(), name='penilaian_report'),
]
```

### Menambah Template
```html
<!-- apps/survey_jpt/templates/survey_jpt/penilaian_form.html -->
{% extends 'base_dashboard.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">Tambah Penilaian</h1>
    
    <form method="post" class="space-y-4">
        {% csrf_token %}
        
        <!-- Form fields here -->
        
        <button type="submit" class="btn btn-primary">
            Simpan Penilaian
        </button>
    </form>
</div>
{% endblock %}
```

## 📊 Query Examples

### Get all pertanyaan for a survey type
```python
from apps.survey_jpt.models import JenisSurvey

jpt = JenisSurvey.objects.get(kode='JPT')
pertanyaan_list = jpt.pertanyaan.filter(is_active=True).order_by('urutan')
```

### Calculate total score for a responden
```python
from apps.survey_jpt.models import RespondenSurvey

responden = RespondenSurvey.objects.get(id=1)
total_nilai = sum(j.nilai_terbobot for j in responden.jawaban.all())
total_bobot = sum(j.pertanyaan.bobot for j in responden.jawaban.all())
rata_rata = total_nilai / total_bobot if total_bobot > 0 else 0
```

### Get all penilaian for a pegawai
```python
from apps.survey_jpt.models import RespondenSurvey

penilaian_list = RespondenSurvey.objects.filter(
    nip_pegawaiDinilai='196801011990031001'
).select_related('jawaban__pertanyaan__jenis_survey')
```

## 🔐 Security Considerations

1. **Permission Check**: Pastikan user hanya bisa menilai pegawai yang sesuai role
2. **Data Validation**: Nilai harus 1-5, tidak boleh kosong
3. **Duplicate Prevention**: UNIQUE constraint pada (responden, pertanyaan)
4. **Audit Trail**: created_at & updated_at untuk tracking

## 📈 Performance Tips

1. **Use select_related**: Untuk menghindari N+1 queries
2. **Use prefetch_related**: Untuk relasi many-to-many
3. **Add indexes**: Pada field yang sering di-query (NIP, status)
4. **Cache results**: Untuk laporan yang sering diakses

## 🎓 Next Steps

1. **Implement Form Input**: Buat form untuk input penilaian
2. **Implement List View**: Tampilkan daftar penilaian
3. **Implement Report**: Buat laporan dengan grafik
4. **Add Validation**: Validasi business logic
5. **Add Tests**: Unit test & integration test

---

**Status**: System architecture READY ✓ | Views implementation TODO 📝
