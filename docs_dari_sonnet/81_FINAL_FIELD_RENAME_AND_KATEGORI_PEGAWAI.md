# Final Field Rename & Kategori Pegawai

**Tanggal**: 2 April 2026  
**Status**: ✅ COMPLETE

---

## 🎯 CHANGES MADE

### 1. Rename Field: `no_urut` → `id_opd_urut`

**Reason**: Lebih jelas bahwa ini adalah urutan OPD (A_12 dari ms_unit_organisasi)

**Before**:
```python
no_urut = models.IntegerField(null=True, blank=True, verbose_name='No Urut OPD (A_12)')
```

**After**:
```python
id_opd_urut = models.IntegerField(null=True, blank=True, verbose_name='Urutan OPD (A_12)')
```

---

### 2. Add Field: `kategori_pegawai`

**Purpose**: Untuk status priority dalam ordering (PNS, CPNS, P3K)

**Implementation**:
```python
kategori_pegawai = models.IntegerField(
    null=True, 
    blank=True, 
    verbose_name='Kategori Pegawai (1=CPNS, 2=PNS, 3=P3K)', 
    db_index=True
)
```

**Mapping from API**:
- `kategoriPegawai: "1"` → CPNS
- `kategoriPegawai: "2"` → PNS
- `kategoriPegawai: "3"` → P3K (atau yang punya `akhirKerjaP3K`)

---

## 🔧 UPDATED ORDERING

### Complete Ordering Logic

```python
pegawai_qs = pegawai_qs.annotate(
    _eselon_group_priority=Case(
        When(kode_eselon__in=[11, 12], then=Value(1)),      # Eselon II.a, II.b
        When(kode_eselon__in=[21, 22], then=Value(2)),      # Eselon III.a, III.b
        When(kode_eselon__isnull=True, then=Value(99)),     # Non-Eselon
        default=Value(3),                                    # Eselon lainnya
        output_field=IntegerField(),
    ),
    _status_priority=Case(
        When(kategori_pegawai=2, then=Value(1)),            # PNS (priority 1)
        When(kategori_pegawai=1, then=Value(2)),            # CPNS (priority 2)
        When(akhir_kerja_p3k__isnull=False, then=Value(3)), # P3K (priority 3)
        default=Value(4),                                    # Others
        output_field=IntegerField(),
    )
).order_by(
    '_eselon_group_priority',   # 1. Eselon group priority
    'id_opd_urut',              # 2. OPD by id_opd_urut (A_12 - URUTAN RESMI!)
    'kode_eselon',              # 3. Eselon ID
    '_status_priority',         # 4. Status priority (PNS → CPNS → P3K)
    'id_golongan',              # 5. Golongan (ascending)
    'id_pegawai',               # 6. ID Pegawai (tie-breaker)
)
```

---

## 📊 ORDERING COMPARISON

### Final Comparison with ESIMPEG

| Level | ESIMPEG | Survey Pemda (Before) | Survey Pemda (After) | Status |
|-------|---------|----------------------|---------------------|--------|
| 1 | `_eselon_group_priority` | `_eselon_group_priority` | `_eselon_group_priority` | ✅ Same |
| 2 | `id_opd__no_urut` | `no_urut` | `id_opd_urut` | ✅ Renamed |
| 3 | `I_06_id` | `kode_eselon` | `kode_eselon` | ✅ Same |
| 4 | `_status_priority` | `_status_priority` (placeholder) | `_status_priority` (real) | ✅ Implemented |
| 5 | `F_03` (asc) | `id_golongan` (asc) | `id_golongan` (asc) | ✅ Same |
| 6 | `id_pegawai` | `id_pegawai` | `id_pegawai` | ✅ Same |

---

## 🔄 SYNC MAPPING

### Updated Sync Logic

**File**: `apps/api_simpeg/views.py`

```python
# Extract values from API response
kode_golongan = item.get('kodeGolongan')
kode_eselon = item.get('kodeEselon')
kategori_pegawai_raw = item.get('kategoriPegawai')  # NEW!

pegawai_data = {
    # ... other fields ...
    'id_opd_urut': item.get('no_urut') or None,  # RENAMED!
    'kategori_pegawai': int(kategori_pegawai_raw) if kategori_pegawai_raw and str(kategori_pegawai_raw).strip() else None,  # NEW!
    # ... other fields ...
}
```

---

## 📈 STATUS PRIORITY LOGIC

### Priority Mapping

```
Priority 1: PNS (kategori_pegawai=2)
  ↓
Priority 2: CPNS (kategori_pegawai=1)
  ↓
Priority 3: P3K (akhir_kerja_p3k IS NOT NULL)
  ↓
Priority 4: Others (default)
```

### Example

```
Eselon II.a → Sekretariat Daerah → Eselon 11 → PNS → Golongan IV/e → ID 123
Eselon II.a → Sekretariat Daerah → Eselon 11 → CPNS → Golongan IV/d → ID 456
Eselon II.a → Sekretariat Daerah → Eselon 11 → P3K → Golongan III/c → ID 789
```

---

## 🗄️ DATABASE CHANGES

### Migration 0006

**File**: `apps/api_simpeg/migrations/0006_add_kategori_pegawai_and_rename_no_urut.py`

**Operations**:
1. Remove index on `no_urut`
2. Remove field `no_urut`
3. Add field `id_opd_urut` (IntegerField, nullable, indexed)
4. Add field `kategori_pegawai` (IntegerField, nullable, indexed)
5. Create index on `id_opd_urut`
6. Create index on `kategori_pegawai`

**Status**: ✅ Applied successfully

---

## ✅ VERIFICATION

### Database Columns

```
id_opd_urut: int ✅
kategori_pegawai: int ✅
no_urut: (removed) ✅
```

### Model Fields

```python
id_opd_urut: IntegerField ✅
kategori_pegawai: IntegerField ✅
```

### Container Status

```
survey_pemda_python_app: Up (healthy) ✅
```

---

## 🎯 NEXT STEPS

### 1. Re-Sync Data

**CRITICAL**: Data must be re-synced to populate new fields!

```
Current status:
- id_opd_urut: NULL for all records
- kategori_pegawai: NULL for all records

After sync:
- id_opd_urut: Populated from API (no_urut)
- kategori_pegawai: Populated from API (kategoriPegawai)
```

**How to sync**:
1. Go to http://localhost:8005/api-simpeg/pegawai/
2. Click "Sinkronisasi Data"
3. Wait for completion

---

### 2. Verify Ordering

After sync, verify ordering is correct:

```python
from apps.api_simpeg.models import Pegawai
from django.db.models import Case, When, Value, IntegerField

pegawai_qs = Pegawai.objects.annotate(
    _eselon_group_priority=Case(
        When(kode_eselon__in=[11, 12], then=Value(1)),
        When(kode_eselon__in=[21, 22], then=Value(2)),
        When(kode_eselon__isnull=True, then=Value(99)),
        default=Value(3),
        output_field=IntegerField(),
    ),
    _status_priority=Case(
        When(kategori_pegawai=2, then=Value(1)),
        When(kategori_pegawai=1, then=Value(2)),
        When(akhir_kerja_p3k__isnull=False, then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
).order_by(
    '_eselon_group_priority',
    'id_opd_urut',
    'kode_eselon',
    '_status_priority',
    'id_golongan',
    'id_pegawai'
)

# Print first 20
for p in pegawai_qs[:20]:
    status_map = {1: 'CPNS', 2: 'PNS', 3: 'P3K', None: 'Unknown'}
    status = status_map.get(p.kategori_pegawai, 'Unknown')
    print(f'Priority: {p._eselon_group_priority}, OPD Urut: {p.id_opd_urut}, Eselon: {p.kode_eselon}, Status: {status} ({p._status_priority}), Golongan: {p.id_golongan}, ID: {p.id_pegawai}')
```

**Expected Output**:
```
Priority: 1, OPD Urut: 1, Eselon: 11, Status: PNS (1), Golongan: 18, ID: 123
Priority: 1, OPD Urut: 1, Eselon: 11, Status: CPNS (2), Golongan: 17, ID: 456
Priority: 1, OPD Urut: 1, Eselon: 12, Status: PNS (1), Golongan: 18, ID: 789
...
```

---

### 3. Check Data Population

```python
from apps.api_simpeg.models import Pegawai

total = Pegawai.objects.count()
with_id_opd_urut = Pegawai.objects.filter(id_opd_urut__isnull=False).count()
with_kategori_pegawai = Pegawai.objects.filter(kategori_pegawai__isnull=False).count()

pns_count = Pegawai.objects.filter(kategori_pegawai=2).count()
cpns_count = Pegawai.objects.filter(kategori_pegawai=1).count()
p3k_count = Pegawai.objects.filter(akhir_kerja_p3k__isnull=False).count()

print(f'Total pegawai: {total}')
print(f'With id_opd_urut: {with_id_opd_urut}')
print(f'With kategori_pegawai: {with_kategori_pegawai}')
print(f'  - PNS: {pns_count}')
print(f'  - CPNS: {cpns_count}')
print(f'  - P3K: {p3k_count}')
```

**Expected Result**:
```
Total pegawai: 4867
With id_opd_urut: 4867
With kategori_pegawai: 4867
  - PNS: ~4500
  - CPNS: ~300
  - P3K: ~67
```

---

## 📁 FILES MODIFIED

### 1. Model
- ✅ `apps/api_simpeg/models.py`
  - Renamed `no_urut` → `id_opd_urut`
  - Added `kategori_pegawai` field
  - Updated indexes

### 2. Views
- ✅ `apps/api_simpeg/views.py`
  - Updated ordering to use `id_opd_urut`
  - Updated `_status_priority` to use `kategori_pegawai`
  - Updated sync mapping for both fields

### 3. Migration
- ✅ `apps/api_simpeg/migrations/0006_add_kategori_pegawai_and_rename_no_urut.py`
  - Created and applied successfully

---

## 🎉 SUCCESS CRITERIA

### Code Changes
- [x] Rename `no_urut` to `id_opd_urut`
- [x] Add `kategori_pegawai` field
- [x] Update ordering logic
- [x] Update sync mapping
- [x] Create migration
- [x] Apply migration
- [x] Restart container
- [x] Container healthy

### Data Status (After Re-Sync)
- [ ] Re-sync data from ESIMPEG API
- [ ] Verify `id_opd_urut` is populated
- [ ] Verify `kategori_pegawai` is populated
- [ ] Test ordering with real data
- [ ] Verify PNS appears before CPNS
- [ ] Verify CPNS appears before P3K

---

## ⚠️ IMPORTANT NOTES

### Field Name Change

**Old**: `no_urut`  
**New**: `id_opd_urut`

**Reason**: Lebih jelas dan konsisten dengan naming convention (id_opd, id_sub_opd, id_opd_urut)

### Status Priority

**Implementation**:
```python
When(kategori_pegawai=2, then=Value(1)),            # PNS first
When(kategori_pegawai=1, then=Value(2)),            # CPNS second
When(akhir_kerja_p3k__isnull=False, then=Value(3)), # P3K third
```

**Note**: P3K detection uses `akhir_kerja_p3k` field as fallback if `kategori_pegawai` is not set.

### Re-Sync Required

**CRITICAL**: Data must be re-synced for changes to take effect!

Without re-sync:
- `id_opd_urut` will be NULL
- `kategori_pegawai` will be NULL
- Ordering will not work correctly
- Status priority will default to 4 (Others)

---

**STATUS**: ✅ **COMPLETE - RE-SYNC REQUIRED**

Code is ready and migration applied. Now re-sync data! 🔄
