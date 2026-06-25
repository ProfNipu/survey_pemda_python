# Analisis Flow Pengambilan Data SIASN
## Perbandingan Laravel ESIMPEG vs Python

### 🔄 FLOW LARAVEL ESIMPEG

#### 1. Controller Entry Point
**File:** `Ms_pegawai_profilController.php`
**Method:** `prefetchSiasnData($id, $B_02B, $type)`

```php
// Entry point untuk fetch SIASN data
public function prefetchSiasnData($id, $B_02B, $type = 'integrasi')
```

**Flow:**
1. **Check Cache** (skip untuk type='sync')
   - Cek `Bkn_result_api` table
   - Timeout: 24 jam (1440 menit)
   - Return cached jika masih valid

2. **Get Endpoints** berdasarkan type
   - `type='integrasi'`: 30+ endpoints (lengkap)
   - `type='sync'`: Essential endpoints only
   
3. **Progress Tracking via Session**
   ```php
   session(['prefetch_progress' => [
       'nip' => $B_02B,
       'total' => $totalEndpoints,
       'current' => $currentIndex,
       'percentage' => $percentage,
       'status' => "Menarik data: {$description}"
   ]]);
   ```

4. **Loop Through Endpoints**
   - For each endpoint:
     a. Update progress session
     b. Build URL: `linkIntegrasiSIASN($path) . $B_02B`
     c. Call API: `$siasnService->getApiResult($url, "getData")`
     d. Parse JSON response
     e. **Incremental Save** ke database
     f. Track success/failure

5. **Save to Database**
   ```php
   RepositoryPegawai::saveSiasnDataToDatabase(
       $B_02B, $id, $tempResult, $incremental, $endpoints
   );
   ```

#### 2. Endpoints Definition

**Integrasi Endpoints (30+):**
```php
'/pns/data-utama/' => 'dataUtama'
'/pns/rw-jabatan/' => 'dataRiwayatJabatan'
'/pns/rw-golongan/' => 'dataRiwayatGolongan'
'/pns/rw-pendidikan/' => 'dataRiwayatPendidikan'
'/pns/rw-diklat/' => 'dataRiwayatDiklat'
'/pns/rw-kursus/' => 'dataRiwayatKursus'
'/pns/rw-skp/' => 'dataRiwayatSKP'
'/pns/rw-cltn/' => 'dataRiwayatCLTN'
'/pns/rw-anak/' => 'dataRiwayatAnak'
// ... dan 20+ lainnya
```

**Sync Endpoints (Essential):**
```php
'/pns/data-utama/'
'/pns/rw-jabatan/'
'/pns/rw-golongan/'
```

#### 3. API Call Flow

**Service Class:** `Ws_siasn`
**Method:** `getApiResult($url, $apiData, $data = null, $status_post = false)`

```php
// 1. Get tokens from database
$tokens = self::select('production', 'access_token', 'statis')
    ->whereIn('production', ['sso_token', 'apikey_token'])
    ->get()
    ->keyBy('production');

// 2. Make HTTP request with headers
Http::withHeaders([
    'Content-Type' => 'multipart/form-data',
    'Auth' => 'bearer ' . $ssoToken->statis,  // SSO static token
    'Authorization' => 'Bearer ' . $apikeyToken->access_token  // API key
])
```

#### 4. Response Handling

```php
if (isset($apiResult['curl_exec_result'])) {
    $decodedResult = json_decode($apiResult['curl_exec_result']);
    if ($decodedResult && isset($decodedResult->data)) {
        $result->{$property} = $decodedResult->data;
        // Save incrementally
        RepositoryPegawai::saveSiasnDataToDatabase(...);
    }
}
```

#### 5. Database Save

**Table:** `bkn_result_api`
**Fields:**
- `B_02B` (NIP)
- `result_api` (JSON data)
- `updated_at` (timestamp)

**Repository Method:**
```php
public static function saveSiasnDataToDatabase(
    $B_02B, 
    $id, 
    $siasnData, 
    $incremental = true, 
    $endpointHistory = []
)
```

---

### 🐍 IMPLEMENTASI PYTHON (CURRENT STATUS)

#### ✅ Yang Sudah Ada:

1. **Helper Functions** ✅
   - `link_integrasi_siasn()` - URL builder
   - `get_default_endpoints()` - Endpoint mappings
   - `get_minimal_endpoints()` - Essential endpoints

2. **SIASN Service** ✅
   - Token management
   - Token refresh
   - Basic API calling

3. **Models** ✅
   - `WsSiasnToken` - Token storage
   - `SiasnApiLog` - API call logging
   - `PegawaiSiasn` - Employee data

#### ❌ Yang Belum Ada:

1. **fetchMultipleEndpoints Method** ❌
   - Belum ada method untuk fetch multiple endpoints sekaligus
   - Belum ada progress tracking
   - Belum ada incremental save

2. **Cache Mechanism** ❌
   - Belum ada cache checking
   - Belum ada timeout validation

3. **Progress Tracking** ❌
   - Belum ada real-time progress updates
   - Belum ada session/WebSocket mechanism

4. **Database Save Method** ❌
   - Belum ada save ke `bkn_result_api` equivalent
   - Belum ada incremental save logic

---

### 🎯 YANG PERLU DIBUAT DI PYTHON:

#### 1. Service Method: `fetch_multiple_endpoints()`

```python
def fetch_multiple_endpoints(
    self, 
    nip: str, 
    endpoints: dict,
    progress_callback=None,
    incremental_save=True
):
    """
    Fetch data from multiple SIASN endpoints
    Equivalent to Laravel prefetchSiasnData
    """
```

#### 2. Cache Model

```python
class BknResultApi(models.Model):
    """Cache for SIASN API results"""
    nip = models.CharField(max_length=18)
    result_api = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
```

#### 3. Progress Tracking

```python
class FetchProgress:
    """Track fetch progress for real-time updates"""
    def __init__(self, nip, total_endpoints):
        self.nip = nip
        self.total = total_endpoints
        self.current = 0
        
    def update(self, current, status, endpoint_name):
        # Update progress (session/cache/WebSocket)
        pass
```

#### 4. Views untuk Fetch

```python
@csrf_exempt
def fetch_pegawai_siasn(request, nip):
    """
    Fetch employee data from SIASN
    Equivalent to Laravel prefetchSiasnData
    """
```

---

### 📋 COMPARISON TABLE

| Feature | Laravel ESIMPEG | Python (Current) | Python (Needed) |
|---------|-----------------|------------------|-----------------|
| **URL Builder** | `linkIntegrasiSIASN()` | ✅ `link_integrasi_siasn()` | - |
| **Endpoints Mapping** | `getIntegrasiEndpoints()` | ✅ `get_default_endpoints()` | - |
| **Token Management** | ✅ `ws_siasn_token` table | ✅ `WsSiasnToken` model | - |
| **Multiple Fetch** | ✅ `prefetchSiasnData()` | ❌ Not implemented | ⚠️ Need to create |
| **Progress Tracking** | ✅ Session-based | ❌ Not implemented | ⚠️ Need to create |
| **Cache System** | ✅ `Bkn_result_api` | ❌ Not implemented | ⚠️ Need to create |
| **Incremental Save** | ✅ Per-endpoint save | ❌ Not implemented | ⚠️ Need to create |
| **API Logging** | ✅ Log facade | ✅ `SiasnApiLog` model | - |
| **Error Handling** | ✅ Try-catch per endpoint | ✅ Basic error handling | ⚠️ Enhance |

---

### 🚀 NEXT STEPS:

1. ✅ Create `BknResultApi` model (cache table)
2. ✅ Implement `fetch_multiple_endpoints()` method
3. ✅ Add progress tracking mechanism
4. ✅ Create views for fetching pegawai data
5. ✅ Add incremental save functionality
6. ✅ Implement cache checking with timeout
7. ✅ Add comprehensive error handling
8. ✅ Create API endpoints similar to Laravel routes

---

### 💡 INTEGRATION POINTS:

**Laravel Route:**
```php
Route::post('/pegawai/{id}/prefetch/{nip}/{type?}', [
    Ms_pegawai_profilController::class, 'prefetchSiasnData'
]);
```

**Python Route (To Create):**
```python
path('pegawai/<int:id>/fetch/<str:nip>/<str:type>/', 
     views.fetch_pegawai_siasn, 
     name='fetch_pegawai_siasn'),
```
