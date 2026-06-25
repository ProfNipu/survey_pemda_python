# 🚀 Panduan Penggunaan Route SIASN untuk Fetch Data Pegawai

## 📋 ROUTES YANG TERSEDIA

### 1. **FETCH PEGAWAI DATA** (Main Route)
**Equivalent Laravel:** `Ms_pegawai_profilController::prefetchSiasnData()`

#### A. Fetch Full Data (Integrasi)
```bash
GET /integrations/pegawai/fetch/{nip}/
```

**Example dengan NIP: 199411192019031001**
```bash
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/
```

**Response:**
```json
{
  "success": true,
  "message": "Data successfully fetched for NIP: 199411192019031001",
  "nip": "199411192019031001",
  "fetch_type": "integrasi",
  "statistics": {
    "total_endpoints": 10,
    "success_count": 9,
    "failed_count": 1,
    "duration_seconds": 12.5,
    "success_rate": "90.0%"
  },
  "data_summary": {
    "endpoints_fetched": [
      "data_utama",
      "data_riwayat_jabatan",
      "data_riwayat_golongan",
      "data_riwayat_pendidikan",
      ...
    ],
    "total_properties": 10
  },
  "data": {
    "data_utama": {...},
    "data_riwayat_jabatan": [...],
    "data_riwayat_golongan": [...],
    ...
  }
}
```

#### B. Fetch Essential Data Only (Sync)
```bash
GET /integrations/pegawai/fetch/{nip}/sync/
```

**Example dengan NIP: 199411192019031001**
```bash
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/sync/
```

**Perbedaan:**
- **integrasi**: 10+ endpoints (data lengkap)
- **sync**: 3 endpoints (data utama, jabatan, golongan)

---

### 2. **CHECK PROGRESS** (Real-time)
**Track progress saat fetching data**

```bash
GET /integrations/pegawai/progress/{nip}/
GET /integrations/pegawai/progress/{nip}/{fetch_type}/
```

**Example:**
```bash
curl http://localhost:8005/integrations/pegawai/progress/199411192019031001/
```

**Response:**
```json
{
  "success": true,
  "nip": "199411192019031001",
  "fetch_type": "integrasi",
  "progress": {
    "total_endpoints": 10,
    "current_endpoint": 7,
    "percentage": 70,
    "status_message": "Menarik data: Riwayat Diklat",
    "endpoint_name": "Riwayat Diklat",
    "completed": false,
    "success": null,
    "error_message": null,
    "started_at": "2025-10-22T11:20:00",
    "updated_at": "2025-10-22T11:20:15"
  }
}
```

---

### 3. **GET CACHED DATA**
**Ambil data dari cache (jika ada)**

```bash
GET /integrations/pegawai/cache/{nip}/
```

**Example:**
```bash
curl http://localhost:8005/integrations/pegawai/cache/199411192019031001/
```

**Response (If Cached):**
```json
{
  "success": true,
  "message": "Cached data found",
  "nip": "199411192019031001",
  "cached": true,
  "cache_info": {
    "age_minutes": 120,
    "success_rate": 90.0,
    "updated_at": "2025-10-22T09:20:00"
  },
  "data": {
    "data_utama": {...},
    "data_riwayat_jabatan": [...],
    ...
  }
}
```

**Response (If Not Cached):**
```json
{
  "success": false,
  "message": "No cached data found or cache expired",
  "nip": "199411192019031001"
}
```

---

## 🔄 FLOW PENGGUNAAN

### Scenario 1: Fetch Data Baru (First Time)

```bash
# 1. Fetch data pegawai
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/

# Response akan langsung fetch dari SIASN API
# Proses bisa memakan waktu 10-30 detik tergantung jumlah endpoints
```

### Scenario 2: Check Progress (While Fetching)

```bash
# Saat fetching sedang berjalan, check progress dari terminal lain
curl http://localhost:8005/integrations/pegawai/progress/199411192019031001/

# Response akan menunjukkan progress real-time:
# - Endpoint mana yang sedang diproses
# - Berapa persen sudah selesai
# - Status message
```

### Scenario 3: Fetch Data yang Sudah Cached

```bash
# Fetch data yang sudah pernah diambil (dalam 24 jam terakhir)
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/

# Response:
{
  "success": true,
  "message": "Data already cached",
  "cached": true,
  "cache_info": {
    "age_minutes": 45,
    "success_rate": 90.0
  },
  "data": {...}
}

# Data langsung diambil dari cache, TIDAK fetch ulang dari SIASN
```

### Scenario 4: Force Refresh (Bypass Cache)

```bash
# Gunakan type 'sync' untuk force refresh
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/sync/

# Akan fetch ulang dari SIASN meskipun ada cache
```

### Scenario 5: Check Cache Sebelum Fetch

```bash
# 1. Check apakah ada cache
curl http://localhost:8005/integrations/pegawai/cache/199411192019031001/

# 2. Jika tidak ada atau expired, baru fetch
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/
```

---

## 📊 CACHE BEHAVIOR

### Cache Timeout: 24 Jam

| Umur Cache | Behavior |
|------------|----------|
| 0-24 jam | Cache valid, data diambil dari cache |
| > 24 jam | Cache expired, fetch ulang dari SIASN |

### Force Refresh

Gunakan type `sync` untuk bypass cache:
```bash
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/sync/
```

---

## 🔧 TESTING DENGAN NIP: 199411192019031001

### Test 1: Fetch Full Data
```bash
curl -X GET http://localhost:8005/integrations/pegawai/fetch/199411192019031001/ | jq '.'
```

### Test 2: Fetch Minimal Data
```bash
curl -X GET http://localhost:8005/integrations/pegawai/fetch/199411192019031001/sync/ | jq '.'
```

### Test 3: Check Progress
```bash
curl -X GET http://localhost:8005/integrations/pegawai/progress/199411192019031001/ | jq '.progress'
```

### Test 4: Get Cached Data
```bash
curl -X GET http://localhost:8005/integrations/pegawai/cache/199411192019031001/ | jq '.cache_info'
```

### Test 5: Get Statistics Only
```bash
curl -X GET http://localhost:8005/integrations/pegawai/fetch/199411192019031001/ | jq '.statistics'
```

---

## 📋 COMPARISON WITH LARAVEL

### Laravel Route:
```php
POST /pegawai/{id}/prefetch/{nip}/{type?}
```

### Python Routes:
```python
GET /integrations/pegawai/fetch/{nip}/              # integrasi (default)
GET /integrations/pegawai/fetch/{nip}/sync/         # sync
GET /integrations/pegawai/progress/{nip}/           # progress
GET /integrations/pegawai/cache/{nip}/              # cache
```

### Key Differences:
- Python menggunakan GET (lebih RESTful untuk data retrieval)
- Laravel menggunakan POST (untuk session management)
- Python memiliki separate endpoints untuk progress dan cache
- Python tidak memerlukan pegawai ID, cukup NIP

---

## 🎯 RECOMMENDED WORKFLOW

### Frontend Integration:

```javascript
// 1. Check cache first
const cacheResponse = await fetch(
  'http://localhost:8005/integrations/pegawai/cache/199411192019031001/'
);

if (cacheResponse.ok) {
  const cached = await cacheResponse.json();
  if (cached.success) {
    // Use cached data
    console.log('Using cached data:', cached.data);
    return;
  }
}

// 2. No cache, start fetching
const fetchResponse = await fetch(
  'http://localhost:8005/integrations/pegawai/fetch/199411192019031001/'
);

// 3. Poll for progress
const checkProgress = setInterval(async () => {
  const progress = await fetch(
    'http://localhost:8005/integrations/pegawai/progress/199411192019031001/'
  );
  const progressData = await progress.json();
  
  console.log(`Progress: ${progressData.progress.percentage}%`);
  console.log(`Status: ${progressData.progress.status_message}`);
  
  if (progressData.progress.completed) {
    clearInterval(checkProgress);
    // Fetch completed, get final data
  }
}, 2000); // Check every 2 seconds
```

---

## 🚀 QUICK START

**Satu pegawai dengan NIP 199411192019031001:**

```bash
# Fetch data lengkap
curl http://localhost:8005/integrations/pegawai/fetch/199411192019031001/
```

**Done!** 🎉

Data akan:
1. ✅ Diambil dari SIASN API (10 endpoints)
2. ✅ Disimpan ke cache (24 jam)
3. ✅ Progress tracked real-time
4. ✅ Return JSON response lengkap

---

## 📞 API ENDPOINTS SUMMARY

| Endpoint | Method | Purpose | Cache Check |
|----------|--------|---------|-------------|
| `/pegawai/fetch/{nip}/` | GET | Fetch full data | ✅ Yes |
| `/pegawai/fetch/{nip}/sync/` | GET | Fetch essential | ❌ No (force) |
| `/pegawai/progress/{nip}/` | GET | Get progress | N/A |
| `/pegawai/cache/{nip}/` | GET | Get cached data | N/A |

---

## 🎊 READY TO USE!

Route sudah siap digunakan untuk fetch data pegawai dari SIASN BKN dengan NIP **199411192019031001** atau NIP lainnya!
