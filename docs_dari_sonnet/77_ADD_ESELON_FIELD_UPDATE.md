# Add Eselon Field & Update Pegawai Model

**Tanggal**: 2 April 2026  
**Status**: ✅ IMPLEMENTED

---

## 🎯 REQUIREMENT

User request:
> "bearti di database harus nambah kd_eselon tersbut agar bisa di filterkan ini dmn json rawnya seperti ini "kodeEselon": 99, utk id_golongan dari "kodeGolongan": 34, tpi id pangkat di hapus, tpi nama pangkat tetap ada ditambah untuk "akhirKerjaP3K": null, column baru juga"

### Changes Required

1. **Add kode_eselon** field (dari `kodeEselon` di raw JSON)
2. **Update id_golongan** mapping (dari `kodeGolongan` bukan dari field lain)
3. **Remove id_pangkat** field (tapi tetap simpan `nama_pangkat`)
4. **Add akhir_kerja_p3k** field (dari `akhirKerjaP3K` di raw JSON)
5. **Update default ordering** untuk include eselon (seperti ESIMPEG)

---

## 🔧 IMPLEMENTATION

### 1. Update Model

**File**: `apps/api_simpeg/models.py`

#### Changes

**Added Fields**:
```python
# Eselon
kode_eselon = models.BigIntegerField(
    null=True, 
    blank=True, 
    verbose_name='Kode Eselon', 
    db_index=True
)

# Akhir Kerja P3K
akhir_kerja_p3k = models.CharField(
    max_length=50, 
    null=True, 
    blank=True, 
    verbose_name='Akhir Kerja P3K'
)
```

**Updated Field**:
```python
# id_golongan sekarang dari kodeGolongan (bukan dari field lain)
id_golongan = models.BigIntegerField(
    null=True, 
    blank=True, 
    verbose_name='ID Golongan (dari kodeGolongan)', 
    db_index=True
)
```

**Removed Field**:
```python
# id_pangkat DIHAPUS (tapi nama_pangkat tetap ada)
# id_pangkat = models.BigIntegerField(...)  # ← REMOVED
```

**Updated Indexes**:
```python
indexes = [
    models.Index(fields=['nip_baru']),
    models.Index(fields=['id_pegawai']),
    models.Index(fields=['id_opd']),
    models.Index(fields=['nama_pegawai']),
    models.Index(fields=['synced_at']),
    models.Index(fields=['kode_eselon']),      # ← NEW
    models.Index(fields=['id_golongan']),      # ← NEW
]
```

---

### 2. Update View Mapping

**File**: `apps/api_simpeg/views.py`

#### Before
```python
pegawai_data = {
    # ...
    'id_golongan': item.get('id_golongan'),  # ← Wrong field
    'nama_golongan': item.get('namaGolongan'),
    'id_pangkat': item.get('id_pangkat'),    # ← Will be removed
    'nama_pangkat': item.get('namaPangkat'),
    # ...
}
```

#### After
```python
pegawai_data = {
    # ...
    'kode_eselon': item.get('kodeEselon'),           # ← NEW
    'id_golongan': item.get('kodeGolongan'),         # ← FROM kodeGolongan
    'nama_golongan': item.get('namaGolongan'),
    'nama_pangkat': item.get('namaPangkat'),         # ← id_pangkat removed
    'akhir_kerja_p3k': item.get('akhirKerjaP3K'),   # ← NEW
    # ...
}
```

---

### 3. Update Default Ordering

**File**: `apps/api_simpeg/views.py`

#### Before
```python
pegawai_qs = pegawai_qs.order_by(
    'id_opd',           # OPD
    '-id_golongan',     # Golongan (desc)
    'nama_pegawai',     # Nama (asc)
)
```

#### After
```python
pegawai_qs = pegawai_qs.order_by(
    'id_opd',           # OPD
    'kode_eselon',      # Eselon (asc) ← NEW
    '-id_golongan',     # Golongan (desc)
    'nama_pegawai',     # Nama (asc)
)
```

**Now matches ESIMPEG ordering**:
```python
# ESIMPEG ordering
.order_by(
    'id_opd__no_urut',      # OPD order
    'I_06_id',              # Eselon ← Same concept
    '_status_priority',     # Status priority
    'F_03',                 # Golongan
    'id_pegawai',           # ID Pegawai
)
```

---

### 4. Add Eselon Filter

**File**: `apps/api_simpeg/views.py`

```python
# Get parameters
search = request.GET.get('search', '').strip()
id_opd = request.GET.get('id_opd', '')
kode_eselon = request.GET.get('kode_eselon', '')  # ← NEW

# Apply filters
if kode_eselon:
    try:
        pegawai_qs = pegawai_qs.filter(kode_eselon=int(kode_eselon))
    except (ValueError, TypeError):
        pass

# Pass to context
context = {
    'table': table,
    'total': total,
    'search_query': search,
    'id_opd': id_opd,
    'kode_eselon': kode_eselon,  # ← NEW
    'last_sync': last_sync,
}
```

---

## 📊 DATABASE CHANGES

### Migration Created

**File**: `0004_remove_pegawai_id_pangkat_pegawai_akhir_kerja_p3k_and_more.py`

**Operations**:
1. ✅ Remove field `id_pangkat` from pegawai
2. ✅ Add field `akhir_kerja_p3k` to pegawai
3. ✅ Add field `kode_eselon` to pegawai
4. ✅ Alter field `id_golongan` on pegawai (update verbose_name)
5. ✅ Create index on `kode_eselon`
6. ✅ Create index on `id_golongan`

### Table Structure (After Migration)

```sql
CREATE TABLE api_simpeg_pegawai (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_pegawai BIGINT UNIQUE NOT NULL,
    nip_baru VARCHAR(50),
    nip_lama VARCHAR(50),
    nama_pegawai VARCHAR(255) NOT NULL,
    tempat_lahir VARCHAR(100),
    tanggal_lahir VARCHAR(50),
    jenis_kelamin INT,
    alamat_rumah TEXT,
    no_hp VARCHAR(50),
    id_jabatan BIGINT,
    nama_jabatan VARCHAR(255),
    masa_kerja_jabatan VARCHAR(100),
    kode_eselon BIGINT,                    -- ← NEW
    id_opd BIGINT,
    nm_opd VARCHAR(255),
    id_sub_opd BIGINT,
    nm_sub_opd VARCHAR(255),
    id_golongan BIGINT,                    -- ← FROM kodeGolongan
    nama_golongan VARCHAR(100),
    -- id_pangkat BIGINT,                  -- ← REMOVED
    nama_pangkat VARCHAR(100),
    tmt_cpns VARCHAR(50),
    masa_kerja_tahun INT,
    masa_kerja_bulan INT,
    akhir_kerja_p3k VARCHAR(50),           -- ← NEW
    raw_data JSON NOT NULL,
    synced_at DATETIME NOT NULL,
    synced_by_id INT,
    created_at DATETIME NOT NULL,
    
    INDEX idx_nip_baru (nip_baru),
    INDEX idx_id_pegawai (id_pegawai),
    INDEX idx_id_opd (id_opd),
    INDEX idx_nama_pegawai (nama_pegawai),
    INDEX idx_synced_at (synced_at),
    INDEX idx_kode_eselon (kode_eselon),   -- ← NEW
    INDEX idx_id_golongan (id_golongan)    -- ← NEW
);
```

---

## 🔄 DATA MAPPING

### Raw JSON from API

```json
{
  "id_pegawai": 1,
  "nipBaru": "199001012020121001",
  "namaPegawai": "ADRIANI, S.ST",
  "kodeEselon": 99,                    // ← Map to kode_eselon
  "kodeGolongan": 34,                  // ← Map to id_golongan
  "namaGolongan": "IV/d",
  "namaPangkat": "Pembina Utama Muda",
  "akhirKerjaP3K": null,               // ← Map to akhir_kerja_p3k
  ...
}
```

### Database Mapping

| Raw JSON Field | Database Field | Type | Notes |
|----------------|----------------|------|-------|
| `kodeEselon` | `kode_eselon` | BigInt | NEW field |
| `kodeGolongan` | `id_golongan` | BigInt | Changed mapping |
| `namaGolongan` | `nama_golongan` | Varchar | No change |
| `namaPangkat` | `nama_pangkat` | Varchar | No change |
| `akhirKerjaP3K` | `akhir_kerja_p3k` | Varchar | NEW field |
| ~~`id_pangkat`~~ | ~~`id_pangkat`~~ | ~~BigInt~~ | REMOVED |

---

## 🎯 ORDERING COMPARISON

### Before Update

```python
.order_by(
    'id_opd',           # OPD
    '-id_golongan',     # Golongan (desc)
    'nama_pegawai',     # Nama (asc)
)
```

**Result**:
```
OPD: BKD (id_opd=1)
  ├─ Golongan IV/d (id_golongan=17) - Ahmad
  ├─ Golongan IV/d (id_golongan=17) - Budi
  ├─ Golongan IV/c (id_golongan=16) - Citra
  └─ Golongan III/d (id_golongan=13) - Dewi
```

### After Update

```python
.order_by(
    'id_opd',           # OPD
    'kode_eselon',      # Eselon (asc) ← NEW
    '-id_golongan',     # Golongan (desc)
    'nama_pegawai',     # Nama (asc)
)
```

**Result**:
```
OPD: BKD (id_opd=1)
  Eselon: II.a (kode_eselon=1)
    ├─ Golongan IV/d (id_golongan=17) - Ahmad
    └─ Golongan IV/c (id_golongan=16) - Budi
  Eselon: III.a (kode_eselon=2)
    ├─ Golongan IV/d (id_golongan=17) - Citra
    └─ Golongan III/d (id_golongan=13) - Dewi
  Eselon: Non-Eselon (kode_eselon=99)
    └─ Golongan III/a (id_golongan=11) - Eko
```

---

## 🧪 TESTING

### Test Migration

```bash
# Check migration status
docker exec survey_pemda_python_app python manage.py showmigrations api_simpeg

# Expected output:
# [X] 0001_initial
# [X] 0002_synclog
# [X] 0003_syncprogress
# [X] 0004_remove_pegawai_id_pangkat_pegawai_akhir_kerja_p3k_and_more
```

### Test Database Structure

```bash
docker exec survey_pemda_python_app python manage.py dbshell
```

```sql
-- Check columns
DESCRIBE api_simpeg_pegawai;

-- Expected new columns:
-- kode_eselon (bigint)
-- akhir_kerja_p3k (varchar)

-- Expected removed column:
-- id_pangkat (should NOT exist)

-- Check indexes
SHOW INDEX FROM api_simpeg_pegawai;

-- Expected new indexes:
-- idx_kode_eselon
-- idx_id_golongan
```

### Test Data Sync

1. Navigate to http://localhost:8006/api-simpeg/pegawai/
2. Click "Sinkronisasi"
3. Wait for completion
4. Check database:

```python
from apps.api_simpeg.models import Pegawai

# Check kode_eselon populated
pegawai = Pegawai.objects.first()
print(f"Kode Eselon: {pegawai.kode_eselon}")  # Should show value (e.g., 99)

# Check id_golongan from kodeGolongan
print(f"ID Golongan: {pegawai.id_golongan}")  # Should show value (e.g., 34)

# Check akhir_kerja_p3k
print(f"Akhir Kerja P3K: {pegawai.akhir_kerja_p3k}")  # Should show value or None

# Check id_pangkat removed
# print(f"ID Pangkat: {pegawai.id_pangkat}")  # Should raise AttributeError

# Check nama_pangkat still exists
print(f"Nama Pangkat: {pegawai.nama_pangkat}")  # Should show value
```

### Test Ordering

```python
from apps.api_simpeg.models import Pegawai

# Test default ordering
pegawai_list = Pegawai.objects.all()[:10]

for p in pegawai_list:
    print(f"OPD: {p.id_opd}, Eselon: {p.kode_eselon}, Golongan: {p.id_golongan}, Nama: {p.nama_pegawai}")

# Expected: Grouped by OPD, then Eselon, then Golongan (desc), then Nama (asc)
```

### Test Filter

```bash
# Test filter by eselon
curl "http://localhost:8006/api-simpeg/pegawai/?kode_eselon=99"

# Expected: Only pegawai with kode_eselon=99
```

---

## ✅ VERIFICATION

### Database Changes
- [x] Migration created (0004_...)
- [x] Migration applied successfully
- [x] Field `kode_eselon` added
- [x] Field `akhir_kerja_p3k` added
- [x] Field `id_pangkat` removed
- [x] Field `id_golongan` updated (verbose_name)
- [x] Index on `kode_eselon` created
- [x] Index on `id_golongan` created

### Code Changes
- [x] Model updated
- [x] View mapping updated (both places)
- [x] Default ordering updated
- [x] Eselon filter added
- [x] Context updated

### Container
- [x] Container restarted
- [x] Container healthy
- [x] No errors in logs

---

## 📁 FILES MODIFIED

1. ✅ `apps/api_simpeg/models.py`
   - Added `kode_eselon` field
   - Added `akhir_kerja_p3k` field
   - Removed `id_pangkat` field
   - Updated `id_golongan` verbose_name
   - Added indexes

2. ✅ `apps/api_simpeg/views.py`
   - Updated mapping in `pegawai_sync()` (first page)
   - Updated mapping in `_run_sync_in_background()` (all pages)
   - Updated default ordering
   - Added `kode_eselon` filter
   - Updated context

3. ✅ `apps/api_simpeg/migrations/0004_remove_pegawai_id_pangkat_pegawai_akhir_kerja_p3k_and_more.py`
   - Migration file created

---

## 🎉 SUCCESS CRITERIA

All changes implemented:
- ✅ `kode_eselon` field added (from `kodeEselon`)
- ✅ `id_golongan` now from `kodeGolongan`
- ✅ `id_pangkat` field removed
- ✅ `nama_pangkat` field kept
- ✅ `akhir_kerja_p3k` field added (from `akhirKerjaP3K`)
- ✅ Default ordering updated (OPD → Eselon → Golongan → Nama)
- ✅ Eselon filter added
- ✅ Indexes created for performance
- ✅ Migration applied successfully
- ✅ Container healthy

---

## 📚 NEXT STEPS

Optional enhancements:
1. Add eselon filter dropdown in UI
2. Add eselon column in table (optional)
3. Add eselon badge/label in detail view
4. Add statistics by eselon
5. Export with eselon grouping

---

**STATUS**: ✅ **IMPLEMENTED**

Database sekarang punya field `kode_eselon` dan `akhir_kerja_p3k`, `id_golongan` dari `kodeGolongan`, dan `id_pangkat` sudah dihapus! 🎉

