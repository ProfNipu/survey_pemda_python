# Pegawai Riwayat Data - Snapshot System

## Overview

Sistem snapshot data pegawai untuk survey. Ketika survey dibuka (periode survey aktif), sistem otomatis mengambil snapshot data pegawai dari ESIMPEG API dan menyimpannya di tabel `pegawai_riwayat_data`.

## Tujuan

Data pegawai di ESIMPEG bisa berubah sewaktu-waktu (promosi, mutasi, dll). Untuk menjaga konsistensi laporan survey, kita perlu "freeze" data pegawai pada saat survey dibuka.

## Use Case Example

### Scenario:
1. **Januari 2026** - Survey dibuka
   - Pegawai A: Golongan III/a, Eselon IV, Jabatan: Kepala Seksi
   - Data disimpan ke `pegawai_riwayat_data` untuk periode Januari 2026

2. **Februari 2026** - Pegawai A dipromosikan
   - Data di ESIMPEG berubah: Golongan III/b, Eselon III, Jabatan: Kepala Bidang
   - Data di `pegawai_riwayat_data` untuk periode Januari 2026 TETAP: III/a, Eselon IV

3. **Maret 2026** - Laporan survey Januari 2026 dibuat
   - Laporan menggunakan data dari `pegawai_riwayat_data` (snapshot Januari)
   - Menampilkan: Golongan III/a, Eselon IV (data saat survey dibuka)
   - BUKAN data terbaru dari ESIMPEG

## Database Schema

### Table: `pegawai_riwayat_data`

```sql
CREATE TABLE pegawai_riwayat_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Relasi Survey
    periode_survey_id BIGINT NOT NULL,
    jenis_survey_id BIGINT NOT NULL,
    
    -- Data Pegawai (Snapshot)
    id_pegawai BIGINT NOT NULL,
    nip_baru VARCHAR(50),
    nip_lama VARCHAR(50),
    nama_pegawai VARCHAR(255) NOT NULL,
    
    -- Data Personal
    tempat_lahir VARCHAR(100),
    tanggal_lahir VARCHAR(50),
    jenis_kelamin INT,
    alamat_rumah TEXT,
    no_hp VARCHAR(50),
    
    -- Data Jabatan (saat snapshot)
    id_jabatan BIGINT,
    nama_jabatan VARCHAR(255),
    masa_kerja_jabatan VARCHAR(100),
    kode_eselon BIGINT,
    nama_eselon VARCHAR(100),
    
    -- Data OPD (saat snapshot)
    id_opd BIGINT,
    nm_opd VARCHAR(255),
    id_opd_urut INT,
    is_opd_induk BOOLEAN DEFAULT FALSE,
    id_sub_opd BIGINT,
    nm_sub_opd VARCHAR(255),
    
    -- Data Kepegawaian (saat snapshot)
    id_golongan BIGINT,
    nama_golongan VARCHAR(100),
    nama_pangkat VARCHAR(100),
    kategori_pegawai INT,
    nama_kategori_pegawai VARCHAR(100),
    tmt_cpns VARCHAR(50),
    masa_kerja_tahun INT,
    masa_kerja_bulan INT,
    akhir_kerja_p3k VARCHAR(50),
    
    -- Raw Data & Metadata
    raw_data JSON NOT NULL,
    snapshot_at DATETIME NOT NULL,
    snapshot_by_id BIGINT,
    
    -- Indexes
    INDEX idx_periode_nip (periode_survey_id, nip_baru),
    INDEX idx_jenis_pegawai (jenis_survey_id, id_pegawai),
    INDEX idx_periode_opd (periode_survey_id, id_opd),
    INDEX idx_periode_eselon (periode_survey_id, kode_eselon),
    INDEX idx_snapshot_at (snapshot_at),
    
    -- Unique Constraint
    UNIQUE KEY unique_periode_pegawai (periode_survey_id, id_pegawai),
    
    FOREIGN KEY (periode_survey_id) REFERENCES survey_periode(id) ON DELETE CASCADE,
    FOREIGN KEY (jenis_survey_id) REFERENCES survey_jenis(id) ON DELETE CASCADE
);
```

## Automatic Snapshot Creation

### Signal-based (Otomatis)

Snapshot dibuat otomatis saat:
1. Periode survey baru dibuat dengan `is_active=True` dan `status='aktif'`
2. Periode survey existing diubah dari `is_active=False` ke `is_active=True`
3. Periode survey status berubah menjadi `'aktif'`

File: `apps/survey/signals.py`

```python
@receiver(post_save, sender=PeriodeSurvey)
def create_snapshot_on_periode_activation(sender, instance, created, **kwargs):
    # Otomatis membuat snapshot saat periode diaktifkan
    pass
```

### Manual Command

Jika perlu membuat snapshot manual atau re-create:

```bash
# Masuk ke container
docker exec -it survey_pemda_python_app bash

# Buat snapshot untuk periode tertentu
python manage.py create_pegawai_snapshot --periode-id=1

# Force re-create (hapus yang lama, buat baru)
python manage.py create_pegawai_snapshot --periode-id=1 --force
```

## How to Use in Reports

### Query Snapshot Data

```python
from apps.survey.models import PegawaiRiwayatData, PeriodeSurvey

# Get snapshot untuk periode tertentu
periode = PeriodeSurvey.objects.get(id=1)
pegawai_snapshots = PegawaiRiwayatData.objects.filter(periode_survey=periode)

# Filter by OPD
pegawai_opd = pegawai_snapshots.filter(id_opd=123)

# Filter by Eselon
pegawai_eselon = pegawai_snapshots.filter(kode_eselon=4)

# Get specific pegawai
pegawai = pegawai_snapshots.get(id_pegawai=456)
print(f"{pegawai.nama_pegawai} - {pegawai.nama_jabatan}")
```

### View Example

```python
def survey_report_view(request, periode_id):
    periode = get_object_or_404(PeriodeSurvey, id=periode_id)
    
    # GUNAKAN SNAPSHOT, BUKAN DATA LIVE
    pegawai_list = PegawaiRiwayatData.objects.filter(
        periode_survey=periode
    ).select_related('periode_survey', 'jenis_survey')
    
    # JANGAN gunakan:
    # pegawai_list = Pegawai.objects.all()  # ❌ Data live, bisa berubah
    
    context = {
        'periode': periode,
        'pegawai_list': pegawai_list,
    }
    return render(request, 'survey/report.html', context)
```

## Admin Interface

Akses di Django Admin:
- URL: `/admin/survey/pegawairiwayatdata/`
- Filter by: Periode Survey, Jenis Survey, Kategori Pegawai, Eselon
- Search: NIP, Nama Pegawai, Nama OPD

## Migration

File: `apps/survey/migrations/0003_add_pegawai_riwayat_data.py`

Run migration:
```bash
docker exec -it survey_pemda_python_app bash
python manage.py migrate survey
```

## Data Flow

```
┌─────────────────────┐
│  ESIMPEG API        │
│  (Data Live)        │
└──────────┬──────────┘
           │
           │ API Call: get_pegawai_list()
           │
           ▼
┌─────────────────────┐
│  Periode Survey     │
│  Status: Aktif      │
└──────────┬──────────┘
           │
           │ Signal: post_save
           │ Trigger: create_snapshot
           │
           ▼
┌─────────────────────┐
│ pegawai_riwayat_    │
│ data (Snapshot)     │
│ - FROZEN DATA       │
│ - Tidak berubah     │
└──────────┬──────────┘
           │
           │ Query untuk laporan
           │
           ▼
┌─────────────────────┐
│  Survey Report      │
│  (Konsisten)        │
└─────────────────────┘
```

## Important Notes

1. **Data Frozen**: Data di `pegawai_riwayat_data` TIDAK akan berubah meskipun data di ESIMPEG berubah
2. **One Snapshot Per Periode**: Satu pegawai hanya punya satu snapshot per periode (unique constraint)
3. **Automatic Creation**: Snapshot dibuat otomatis saat periode diaktifkan (via signal)
4. **Manual Override**: Bisa re-create snapshot dengan command `--force`
5. **Raw Data Stored**: Full JSON response dari API disimpan di field `raw_data` untuk referensi

## Troubleshooting

### Snapshot tidak terbuat otomatis?

1. Cek signal terdaftar:
```python
# apps/survey/apps.py
def ready(self):
    import apps.survey.signals  # Pastikan ada
```

2. Cek log:
```bash
docker logs survey_pemda_python_app | grep snapshot
```

3. Buat manual:
```bash
python manage.py create_pegawai_snapshot --periode-id=1
```

### Data snapshot salah?

Re-create dengan force:
```bash
python manage.py create_pegawai_snapshot --periode-id=1 --force
```

### API ESIMPEG error?

Cek koneksi:
```bash
# Test API connection
docker exec -it survey_pemda_python_app bash
python manage.py shell

from apps.accounts.services import EsimpegAPIService
api = EsimpegAPIService()
pegawai = api.get_pegawai_list()
print(len(pegawai))
```

## Related Files

- Model: `apps/survey/models_pegawai_riwayat.py`
- Signal: `apps/survey/signals.py`
- Command: `apps/survey/management/commands/create_pegawai_snapshot.py`
- Migration: `apps/survey/migrations/0003_add_pegawai_riwayat_data.py`
- Admin: `apps/survey/admin.py`

## Next Steps

1. Run migration: `python manage.py migrate survey`
2. Test dengan membuat periode survey baru
3. Cek apakah snapshot terbuat otomatis
4. Update views/reports untuk menggunakan `PegawaiRiwayatData` instead of live data
