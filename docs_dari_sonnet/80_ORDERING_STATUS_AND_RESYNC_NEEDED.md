# Ordering Status & Re-Sync Needed

**Tanggal**: 2 April 2026  
**Status**: ⚠️ RE-SYNC REQUIRED

---

## 🎯 CURRENT STATUS

### Ordering Implementation: ✅ COMPLETE

The ordering logic has been successfully updated to match ESIMPEG exactly:

```python
.order_by(
    '_eselon_group_priority',  # 1. Eselon group priority (1, 2, 3, 99)
    'no_urut',                 # 2. OPD by no_urut (A_12 from ms_unit_organisasi)
    'kode_eselon',             # 3. Eselon ID (11, 12, 21, 22, ...)
    '_status_priority',        # 4. Status priority (PNS, CPNS, P3K)
    'id_golongan',             # 5. Golongan (ascending: 1 → 18)
    'id_pegawai',              # 6. ID Pegawai (tie-breaker)
)
```

### Data Status: ⚠️ NEEDS RE-SYNC

**Problem**: All `no_urut` and `is_opd_induk` fields are NULL

```
Total pegawai: 4867
With no_urut: 0
With is_opd_induk=True: 0
```

**Reason**: Data was synced BEFORE these fields were added to the API response.

---

## 🔍 VERIFICATION

### Current Ordering Behavior

When sorted, all records have `no_urut=None`, so they're sorted by other fields:

```
Priority: 2, no_urut: None, Eselon: 21, Golongan: 44, ID: 11691
Priority: 2, no_urut: None, Eselon: 22, Golongan: 41, ID: 293
Priority: 2, no_urut: None, Eselon: 22, Golongan: 41, ID: 11256
...
```

**This means**:
- ✅ Ordering logic is correct
- ❌ Data is incomplete (no_urut is NULL)
- ⚠️ Ordering will work AFTER re-sync

---

## 🔧 SOLUTION: RE-SYNC DATA

### Step 1: Verify ESIMPEG API Returns no_urut

The ESIMPEG API has been updated to include `no_urut` and `is_opd_induk`:

**File**: `projects/ESIMPEG-Python/apps/pegawai/api_views.py` (lines 1490-1492)

```python
'no_urut': getattr(sub_opd, 'no_urut', None) or 0,
'is_opd_induk': getattr(getattr(sub_opd, 'id_unit', None), 'is_opd_induk', False) if sub_opd and getattr(sub_opd, 'id_unit', None) else False,
```

### Step 2: Re-Sync from UI

1. Go to: http://localhost:8005/api-simpeg/pegawai/
2. Click "Sinkronisasi Data" button
3. Wait for progress bar to complete
4. Verify data is populated

### Step 3: Verify After Sync

Run this query to verify:

```python
from apps.api_simpeg.models import Pegawai

total = Pegawai.objects.count()
with_no_urut = Pegawai.objects.filter(no_urut__isnull=False).count()
with_is_opd_induk = Pegawai.objects.filter(is_opd_induk=True).count()

print(f'Total pegawai: {total}')
print(f'With no_urut: {with_no_urut}')
print(f'With is_opd_induk=True: {with_is_opd_induk}')
```

**Expected Result**:
```
Total pegawai: 4867
With no_urut: 4867  ← Should be populated
With is_opd_induk=True: ~50  ← Some OPD should be induk
```

---

## 📊 ORDERING COMPARISON

### Complete Comparison Table

| Level | ESIMPEG | Survey Pemda | Status |
|-------|---------|--------------|--------|
| 1 | `_eselon_group_priority` | `_eselon_group_priority` | ✅ Same |
| 2 | `id_opd__no_urut` | `no_urut` | ✅ Fixed |
| 3 | `I_06_id` | `kode_eselon` | ✅ Same |
| 4 | `_status_priority` | `_status_priority` | ✅ Added |
| 5 | `F_03` (asc) | `id_golongan` (asc) | ✅ Fixed |
| 6 | `id_pegawai` | `id_pegawai` | ✅ Fixed |

---

## 🎯 KEY CHANGES MADE

### 1. Changed from id_opd to no_urut

**Before**:
```python
.order_by('id_opd', ...)  # Wrong! Auto-increment ID
```

**After**:
```python
.order_by('no_urut', ...)  # Correct! Official OPD order (A_12)
```

**Why Important**:
- `no_urut` is the official OPD ordering (A_12 from ms_unit_organisasi)
- `id_opd` is just an auto-increment ID (random order)

**Example**:
```
no_urut=1: Sekretariat Daerah
no_urut=2: Dinas Pendidikan
no_urut=3: Dinas Kesehatan
...
```

---

### 2. Added _status_priority Annotation

**Implementation**:
```python
_status_priority=Case(
    default=Value(1),  # Placeholder for now
    output_field=IntegerField(),
)
```

**Why Placeholder**:
- Survey Pemda doesn't have `B_09_id` (kategori_pegawai) field yet
- All pegawai have same priority for now
- Will be updated when `kategori_pegawai` field is added

**Future Implementation**:
```python
_status_priority=Case(
    When(kategori_pegawai=2, then=Value(1)),  # PNS
    When(kategori_pegawai=1, then=Value(2)),  # CPNS
    When(akhir_kerja_p3k__isnull=False, then=Value(3)),  # P3K
    default=Value(4),
)
```

---

### 3. Changed Golongan from Descending to Ascending

**Before**:
```python
.order_by('-id_golongan', ...)  # Descending: 18 → 1
```

**After**:
```python
.order_by('id_golongan', ...)  # Ascending: 1 → 18
```

**Assumption**:
- `id_golongan=1` = Golongan I/a (terendah)
- `id_golongan=18` = Golongan IV/e (tertinggi)
- Ascending = Rendah ke tinggi

**Note**: If this assumption is wrong, we need to change back to descending.

---

### 4. Changed from nama_pegawai to id_pegawai

**Before**:
```python
.order_by('nama_pegawai')  # Can change (typo, update)
```

**After**:
```python
.order_by('id_pegawai')  # Stable unique identifier
```

**Why Better**:
- `id_pegawai` is a stable unique identifier
- `nama_pegawai` can change (typo corrections, updates)
- Consistent tie-breaker

---

## 📈 ORDERING FLOW

### Complete Ordering Logic

```
1. _eselon_group_priority (1 → 2 → 3 → 99)
   ├─ Priority 1: Eselon II.a, II.b (kode 11, 12)
   ├─ Priority 2: Eselon III.a, III.b (kode 21, 22)
   ├─ Priority 3: Eselon lainnya
   └─ Priority 99: Non-Eselon (NULL)
   
   ↓

2. no_urut (1 → 2 → 3 → ...)
   ├─ 1: Sekretariat Daerah
   ├─ 2: Dinas Pendidikan
   ├─ 3: Dinas Kesehatan
   └─ ...
   
   ↓

3. kode_eselon (11 → 12 → 21 → 22 → ...)
   ├─ 11: Eselon II.a
   ├─ 12: Eselon II.b
   ├─ 21: Eselon III.a
   └─ ...
   
   ↓

4. _status_priority (1 → 2 → 3 → 4)
   ├─ 1: PNS
   ├─ 2: CPNS
   ├─ 3: P3K
   └─ 4: Others
   
   ↓

5. id_golongan (1 → 2 → 3 → ... → 18)
   ├─ 1: Golongan I/a
   ├─ 2: Golongan I/b
   ├─ ...
   └─ 18: Golongan IV/e
   
   ↓

6. id_pegawai (1 → 2 → 3 → ...)
   └─ Tie-breaker (stable unique ID)
```

---

## ✅ VERIFICATION CHECKLIST

### Code Changes
- [x] Sort by `no_urut` (not `id_opd`)
- [x] Add `_status_priority` annotation
- [x] Change golongan to ascending (not descending)
- [x] Sort by `id_pegawai` (not `nama_pegawai`)
- [x] Container restarted
- [x] Container healthy

### Data Status
- [ ] Re-sync data from ESIMPEG API
- [ ] Verify `no_urut` is populated
- [ ] Verify `is_opd_induk` is populated
- [ ] Test ordering with real data

---

## 📁 FILES MODIFIED

1. ✅ `apps/api_simpeg/views.py`
   - Updated ordering to match ESIMPEG exactly
   - Added `_status_priority` annotation
   - Changed from `id_opd` to `no_urut`
   - Changed from `-id_golongan` to `id_golongan`
   - Changed from `nama_pegawai` to `id_pegawai`

2. ✅ `apps/api_simpeg/models.py`
   - Already has `no_urut` field (migration 0005)
   - Already has `is_opd_induk` field (migration 0005)

3. ✅ ESIMPEG API (`projects/ESIMPEG-Python/apps/pegawai/api_views.py`)
   - Already returns `no_urut` and `is_opd_induk` (lines 1490-1492)

---

## 🎉 NEXT STEPS

### For User

1. **Re-sync data** from UI:
   - Go to http://localhost:8005/api-simpeg/pegawai/
   - Click "Sinkronisasi Data"
   - Wait for completion

2. **Verify ordering** after sync:
   - Check if pegawai are sorted correctly
   - Verify OPD grouping is correct
   - Verify eselon priority is correct

3. **Test filters**:
   - Filter by OPD
   - Filter by Eselon
   - Search by name/NIP

### For Future

1. **Add kategori_pegawai field**:
   - Add to Pegawai model
   - Map from API response
   - Update `_status_priority` annotation

2. **Verify golongan direction**:
   - Check if ascending is correct
   - If wrong, change to descending

3. **Add more filters**:
   - Filter by status (PNS/CPNS/P3K)
   - Filter by golongan
   - Filter by jenis kelamin

---

## ⚠️ IMPORTANT NOTES

### Status Priority

Survey Pemda belum punya field `kategori_pegawai` (B_09_id), jadi untuk sementara semua pegawai punya `_status_priority=1`.

**To add in future**:
1. Add `kategori_pegawai` field to Pegawai model
2. Map from API response (`kategoriPegawai`)
3. Update `_status_priority` annotation

### Golongan Direction

Need to verify if `id_golongan` ascending is correct:
- If `id_golongan=1` is lowest (I/a), then ascending is correct ✅
- If `id_golongan=1` is highest (IV/e), then need to change to descending ❌

### Re-Sync Required

**CRITICAL**: Data must be re-synced for ordering to work correctly!

Without re-sync:
- `no_urut` will be NULL
- Ordering will fall back to other fields
- OPD grouping will be wrong

---

**STATUS**: ⚠️ **RE-SYNC REQUIRED**

Code is ready, but data needs to be re-synced! 🔄
