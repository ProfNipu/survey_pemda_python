# 📍 DJANGO ROUTING GUIDE - ESIMPEG PYTHON

## File Lokasi Routes

### 1. Main Routes (Level 1)
**File:** `esimpeg_core/urls.py`
```python
urlpatterns = [
    path('integrations/', include('apps.integrations.urls')),  # ← Forward ke app
]
```

### 2. Integration Routes (Level 2)  
**File:** `apps/integrations/urls.py`
```python
urlpatterns = [
    path('pegawai/foto/<str:nip>/', views.download_foto_pegawai),  # ← Define endpoint
]
```

### 3. View Functions (Level 3)
**File:** `apps/integrations/views.py`
```python
def download_foto_pegawai(request, nip):
    # Handle request
    return JsonResponse({'success': True})
```

---

## Semua Routes SIASN

**Base URL:** `http://localhost:8005/integrations/`

### SIASN Management
- `POST siasn/refresh-token/` - Refresh SSO & API Key Token
- `GET siasn/` - SIASN Dashboard
- `GET siasn/logs/` - API Call Logs

### Fetch Data
- `GET pegawai/fetch/{nip}/` - Fetch all endpoints (default: 25 endpoints)
- `GET pegawai/fetch/{nip}/integrasi/` - Fetch 25 endpoints (tanpa foto)
- `GET pegawai/fetch/{nip}/minimal/` - Fetch 5 endpoints (data utama, pangkat, pendidikan, jabatan, nilai ipasn)
- `GET pegawai/fetch/{nip}/sync/` - Sync mode (sama dengan minimal: 5 endpoints)
- **Note:** Foto TIDAK di-fetch otomatis, gunakan endpoint download terpisah

### Progress Tracking
- `GET pegawai/progress/{nip}/` - Get fetch progress
- `GET pegawai/progress/{nip}/{type}/` - Get progress by type
- `GET prefetch-progress/?nip={nip}&type={type}` - Polling progress

### Cache Access
- `GET pegawai/cache/{nip}/` - Get cached SIASN data

### Download Files (Terpisah dari Fetch)
**Foto dan dokumen TIDAK di-fetch otomatis, gunakan endpoint khusus:**
- `GET pegawai/foto/{nip}/` - Download foto pegawai (base64, JPEG/PNG)
  - Format filename: `PICASN_{nip}_SIMPEG{id_pegawai}.jpg`
  - Butuh: ID dari data_utama
- `GET siasn/download-dokumen/?uri={path}` - Download dokumen (base64, PDF/DOC)
  - Format filename: Extracted from URI
  - Butuh: URI path dokumen

---

## Contoh Penggunaan

### 1. Download Foto
```bash
GET http://localhost:8005/integrations/pegawai/foto/199411192019031001/

Response:
{
  "success": true,
  "nip": "199411192019031001",
  "id_bkn": "7E2C0FACC094B6DDE050640A3C0313D4",
  "id_pegawai": 1876,
  "filename": "PICASN_199411192019031001_SIMPEG1876.jpg",
  "content": "iVBORw0KGgo...",  // Base64
  "content_size": 200364
}
```

### 2. Fetch Data SIASN
```bash
GET http://localhost:8005/integrations/pegawai/fetch/199411192019031001/integrasi/

Response:
{
  "success": true,
  "nip": "199411192019031001",
  "statistics": {
    "total_endpoints": 26,
    "success_count": 25,
    "failed_count": 1,
    "success_rate": "96.2%"
  }
}
```

### 3. Check Progress
```bash
GET http://localhost:8005/integrations/pegawai/progress/199411192019031001/

Response:
{
  "nip": "199411192019031001",
  "total": 26,
  "current": 15,
  "percentage": 57,
  "status": "Menarik data: Riwayat Jabatan",
  "completed": false
}
```

### 4. Get Cache
```bash
GET http://localhost:8005/integrations/pegawai/cache/199411192019031001/

Response:
{
  "success": true,
  "cached": true,
  "cache_info": {
    "age_minutes": 45,
    "success_rate": "96.2%"
  },
  "data": {
    "data_utama": {...},
    "data_riwayat_pangkat": [...],
    ...
  }
}
```

---

## URL Parameters

### Path Parameters (dalam URL)
```python
path('pegawai/foto/<str:nip>/', ...)
                    ↑
                Parameter: <type:name>

Contoh: /pegawai/foto/199411192019031001/
        nip = '199411192019031001'
```

**Types:**
- `<str:name>` - String
- `<int:id>` - Integer
- `<slug:slug>` - Slug (alphanumeric + hyphen)
- `<uuid:uuid>` - UUID

### Query Parameters (setelah ?)
```python
path('download-dokumen/', ...)

Contoh: /download-dokumen/?uri=/path/file.pdf&format=pdf
        request.GET.get('uri') = '/path/file.pdf'
        request.GET.get('format') = 'pdf'
```

---

## Alur Request

```
REQUEST: GET /integrations/pegawai/foto/199411192019031001/
   │
   ├─► 1. esimpeg_core/urls.py
   │      path('integrations/', include('apps.integrations.urls'))
   │      ✓ Match! Forward to integrations app
   │
   ├─► 2. apps/integrations/urls.py
   │      path('pegawai/foto/<str:nip>/', views.download_foto_pegawai)
   │      ✓ Match! Extract: nip='199411192019031001'
   │      ✓ Call view function
   │
   ├─► 3. apps/integrations/views.py
   │      def download_foto_pegawai(request, nip):
   │          pegawai = SiasnPegawai.objects.get(nip=nip)
   │          ...
   │          return JsonResponse({...})
   │
   └─► 4. RESPONSE (JSON)
```

---

## Cara Tambah Route Baru

### Step 1: Edit `apps/integrations/urls.py`
```python
from django.urls import path
from . import views

urlpatterns = [
    # Existing routes...
    
    # New route
    path('pegawai/detail/<str:nip>/', views.get_pegawai_detail, name='pegawai_detail'),
]
```

### Step 2: Edit `apps/integrations/views.py`
```python
from django.http import JsonResponse

def get_pegawai_detail(request, nip):
    try:
        from .siasn.models_cache import SiasnPegawai
        
        pegawai = SiasnPegawai.objects.get(nip=nip)
        
        return JsonResponse({
            'success': True,
            'nip': nip,
            'data': pegawai.data_utama
        })
        
    except SiasnPegawai.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Data tidak ditemukan'
        }, status=404)
```

### Step 3: Test
```bash
GET http://localhost:8005/integrations/pegawai/detail/199411192019031001/
```

---

## Django vs Laravel

| Laravel | Django | Keterangan |
|---------|--------|------------|
| `routes/web.php` | `urls.py` | File routing |
| `Route::get()` | `path()` | Define route |
| `{nip}` | `<str:nip>` | URL parameter |
| `Controller@method` | `views.function` | Handler |
| `route('name')` | `reverse('name')` | Generate URL |

**Contoh:**

```php
// Laravel
Route::get('/foto/{nip}', [FotoController::class, 'download'])
     ->name('foto.download');
```

```python
# Django
path('foto/<str:nip>/', views.download_foto, name='foto_download')
```

---

## Tips & Best Practices

### 1. Naming Convention
```python
# Good
path('pegawai/foto/<str:nip>/', views.download_foto_pegawai, name='download_foto_pegawai')

# Bad
path('foto/<str:n>/', views.dfp, name='f')
```

### 2. URL Pattern Order
```python
urlpatterns = [
    # Specific patterns first
    path('pegawai/all/', views.get_all_pegawai),
    
    # Generic patterns last
    path('pegawai/<str:nip>/', views.get_pegawai_detail),
]
```

### 3. Use name parameter
```python
# Define
path('pegawai/foto/<str:nip>/', views.download_foto, name='download_foto')

# Use in code
from django.urls import reverse
url = reverse('integrations:download_foto', args=['199411192019031001'])
# Result: /integrations/pegawai/foto/199411192019031001/
```

---

## Debugging Routes

### 1. List all routes
```bash
docker exec esimpeg_python_app python manage.py show_urls
```

### 2. Check specific app
```bash
docker exec esimpeg_python_app python manage.py shell
>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> for pattern in resolver.url_patterns:
...     print(pattern)
```

### 3. Test route
```bash
curl http://localhost:8005/integrations/pegawai/foto/199411192019031001/
```

---

## File Structure

```
ESIMPEG-Python/
├── esimpeg_core/
│   └── urls.py              ← MAIN (include apps)
│
├── apps/
│   ├── integrations/
│   │   ├── urls.py          ← APP ROUTES ⭐
│   │   ├── views.py         ← VIEW FUNCTIONS ⭐
│   │   └── siasn/
│   │       └── services.py  ← BUSINESS LOGIC
│   │
│   └── dashboard/
│       ├── urls.py
│       └── views.py
```

---

## Quick Reference

| Action | URL | Method |
|--------|-----|--------|
| Refresh Token | `/integrations/siasn/refresh-token/` | POST |
| Fetch Data | `/integrations/pegawai/fetch/{nip}/integrasi/` | GET |
| Download Foto | `/integrations/pegawai/foto/{nip}/` | GET |
| Get Progress | `/integrations/pegawai/progress/{nip}/` | GET |
| Get Cache | `/integrations/pegawai/cache/{nip}/` | GET |
| Download Doc | `/integrations/siasn/download-dokumen/?uri=...` | GET |
| Health Check | `/health/` | GET |

---

**🎯 Semua routes sudah berfungsi dengan baik!**
