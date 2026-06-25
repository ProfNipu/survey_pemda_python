# Cara Kerja API Token Flow - ESIMPEG & Survey Pemda

**Tanggal**: 31 Maret 2026  
**Status**: ✅ WORKING

---

## 📋 Ringkasan

Dokumentasi lengkap tentang bagaimana token ESIMPEG API bekerja untuk mengambil data pegawai dari Survey Pemda.

---

## 🔐 Flow Authentication & Token

### 1. User Login ke Survey Pemda

```
User → Survey Pemda Login Form
  ↓
Survey Pemda cek database lokal
  ↓
Jika user ADA:
  → Authenticate dengan password lokal
  → Call ESIMPEG API untuk dapat token ✅
  → Simpan token di session
  
Jika user TIDAK ADA:
  → Call ESIMPEG API login
  → Create user baru di database lokal
  → Simpan token di session ✅
```

### 2. Token Disimpan di Session

**File**: `projects/survey_pemda_python/core/views.py`  
**Function**: `landing_page()`

```python
# Simpan token ke session
request.session['esimpeg_access_token'] = api_response.get('access_token')
request.session['esimpeg_refresh_token'] = api_response.get('refresh_token')
```

**Token Properties**:
- `esimpeg_access_token`: Token untuk akses API (valid 24 jam)
- `esimpeg_refresh_token`: Token untuk refresh (valid 7 hari)

---

## 📡 Flow Get Data Pegawai

### 1. User Akses Halaman Pegawai

```
User → http://localhost:8006/api-simpeg/pegawai/
  ↓
Survey Pemda: pegawai_list view
  ↓
Ambil token dari session
  ↓
Call ESIMPEG API dengan token
  ↓
Tampilkan data pegawai
```

### 2. Kode di pegawai_list View

**File**: `projects/survey_pemda_python/apps/api_simpeg/views.py`

```python
@permission_required_403('api_simpeg', 'pegawai', 'view')
def pegawai_list(request):
    # 1. Ambil token dari session
    esimpeg_token = request.session.get('esimpeg_access_token')
    
    if not esimpeg_token:
        messages.error(request, 'Anda harus login via ESIMPEG API terlebih dahulu')
        return redirect('landing_page')
    
    # 2. Call ESIMPEG API dengan token
    api_service = EsimpegAPIService()
    data = api_service.get_pegawai_list(
        token=esimpeg_token,
        page=page,
        per_page=per_page,
        search=search
    )
    
    # 3. Render data
    return render(request, 'api_simpeg/pegawai_list.html', context)
```

### 3. API Service Call

**File**: `projects/survey_pemda_python/apps/accounts/services.py`

```python
def get_pegawai_list(self, token, page=1, per_page=50, search=None):
    url = f"{self.base_url}/apisimpeg/5.0/pegawai/data/list"
    
    response = requests.get(
        url,
        params={'page': page, 'per_page': per_page, 'search': search},
        headers={
            'Authorization': f'Bearer {token}',  # ← Token di header
            'Content-Type': 'application/json'
        },
        timeout=self.timeout
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data')
    
    return None
```

---

## 🔧 Konfigurasi

### Survey Pemda `.env`

```env
# ESIMPEG API Configuration
ESIMPEG_API_URL=http://172.21.0.2:8000
ESIMPEG_API_TIMEOUT=10
```

**Catatan**: Gunakan IP address (172.21.0.2) bukan container name untuk menghindari Django host validation error.

---

## 🧪 Testing Flow

### Test 1: Login dan Dapat Token

```bash
# 1. Logout dari Survey Pemda
# 2. Login dengan user yang ada di ESIMPEG
#    Username: Prakom@admin2025.com
#    Password: Prakom@2025

# 3. Cek logs
docker logs survey_pemda_python_app 2>&1 | grep "Stored ESIMPEG tokens"
```

**Expected Output**:
```
INFO Stored ESIMPEG tokens in session for existing user Prakom@admin2025.com
```

### Test 2: Akses Halaman Pegawai

```bash
# 1. Buka browser: http://localhost:8006/api-simpeg/pegawai/
# 2. Seharusnya tampil data pegawai
# 3. Cek logs
docker logs survey_pemda_python_app 2>&1 | grep "pegawai" | tail -5
```

**Expected Output**:
```
172.21.0.1 - - [31/Mar/2026:16:07:56 +0700] "GET /api-simpeg/pegawai/ HTTP/1.1" 200 113086
172.21.0.1 - - [31/Mar/2026:16:07:56 +0700] "POST /api-simpeg/pegawai/ HTTP/1.1" 200 113086
```

### Test 3: Verify Token di Session

```python
# Di Django shell
docker exec -it survey_pemda_python_app python manage.py shell

from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='Prakom@admin2025.com')

# Get user's session
from django.contrib.sessions.backends.db import SessionStore
# (Session key ada di database atau cookies)
```

---

## 🐛 Troubleshooting

### Problem 1: "Anda harus login via ESIMPEG API terlebih dahulu"

**Penyebab**: Token tidak ada di session

**Solusi**:
1. Logout dari Survey Pemda
2. Login kembali (token akan disimpan otomatis)
3. Akses halaman pegawai lagi

### Problem 2: Data Pegawai Tidak Muncul

**Penyebab**: Token invalid atau expired

**Cek**:
```bash
# Cek logs untuk error
docker logs survey_pemda_python_app 2>&1 | grep -i "error\|exception" | tail -20
```

**Solusi**:
1. Logout dan login kembali (dapat token baru)
2. Pastikan ESIMPEG API running
3. Pastikan user ada di ESIMPEG

### Problem 3: Connection Error ke ESIMPEG API

**Penyebab**: ESIMPEG API tidak running atau network issue

**Cek**:
```bash
# Test connection dari Survey Pemda container
docker exec survey_pemda_python_app curl -s http://172.21.0.2:8000/health/
```

**Solusi**:
```bash
# Restart ESIMPEG
docker restart esimpeg_python_app

# Verify running
docker ps | grep esimpeg_python_app
```

---

## 📊 API Endpoints yang Digunakan

### 1. Login API (Dapat Token)

**Endpoint**: `POST /apisimpeg/5.0/auth/login`  
**URL**: `http://172.21.0.2:8000/apisimpeg/5.0/auth/login`

**Request**:
```json
{
  "username": "Prakom@admin2025.com",
  "password": "Prakom@2025"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "user": {...}
  }
}
```

### 2. Get Pegawai List (Gunakan Token)

**Endpoint**: `GET /apisimpeg/5.0/pegawai/data/list`  
**URL**: `http://172.21.0.2:8000/apisimpeg/5.0/pegawai/data/list`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Query Params**:
```
page=1
per_page=50
search=nama_pegawai (optional)
id_opd=123 (optional)
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 1234,
      "total_pages": 25
    }
  }
}
```

---

## ✅ Status Saat Ini

**Login Flow**: ✅ WORKING
- User bisa login ke Survey Pemda
- Token otomatis disimpan di session
- Token valid 24 jam

**Get Data Flow**: ✅ WORKING  
- Halaman pegawai bisa diakses
- Data berhasil di-fetch dari ESIMPEG API
- Response 200 dengan data 113KB

**Logs Terakhir** (16:07-16:08):
```
INFO Stored ESIMPEG tokens in session for existing user Prakom@admin2025.com
GET /api-simpeg/pegawai/ HTTP/1.1" 200 113086
POST /api-simpeg/pegawai/ HTTP/1.1" 200 113086
```

---

## 📝 Kesimpulan

✅ Token flow sudah bekerja dengan baik
✅ User bisa login dan dapat token otomatis
✅ Data pegawai berhasil di-fetch dari ESIMPEG API
✅ Tidak ada error di logs terbaru

**Jika masih ada masalah**, kemungkinan:
1. User belum logout/login ulang (masih pakai session lama)
2. Browser cache (clear cache dan refresh)
3. ESIMPEG API down (restart container)



---

## 🔍 Debugging Guide - Jika Masih Gagal

### Step 1: Cek User Sudah Login dengan Benar

```bash
# Cek user terakhir yang login
docker logs survey_pemda_python_app 2>&1 | grep "Stored ESIMPEG tokens" | tail -3
```

**Expected**:
```
INFO Stored ESIMPEG tokens in session for existing user Prakom@admin2025.com
```

Jika TIDAK ADA output → User belum login ulang setelah fix!

### Step 2: Cek Token Ada di Session

```python
# Test di browser console (F12)
// Cek cookies
document.cookie

// Atau test dengan fetch
fetch('/api-simpeg/pegawai/')
  .then(r => r.text())
  .then(html => console.log(html.length))
```

### Step 3: Test API Langsung dari Container

```bash
# Login dan dapat token
TOKEN=$(docker exec survey_pemda_python_app curl -s -X POST \
  http://172.21.0.2:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

echo "Token: $TOKEN"

# Test get pegawai dengan token
docker exec survey_pemda_python_app curl -s \
  "http://172.21.0.2:8000/apisimpeg/5.0/pegawai/data/list?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool | head -50
```

**Expected**: Data pegawai dalam format JSON

### Step 4: Cek Response di Browser

1. Buka: http://localhost:8006/api-simpeg/pegawai/
2. Buka Developer Tools (F12)
3. Tab Network
4. Refresh halaman
5. Cek request ke `/api-simpeg/pegawai/`
6. Lihat Response

**Jika Response 200 tapi halaman kosong**:
- Kemungkinan masalah di JavaScript/rendering
- Cek Console untuk error JavaScript

**Jika Response 302 (redirect)**:
- User belum login atau session expired
- Logout dan login ulang

**Jika Response 500**:
- Ada error di server
- Cek logs: `docker logs survey_pemda_python_app 2>&1 | tail -50`

### Step 5: Force Logout dan Login Ulang

```bash
# 1. Buka browser
# 2. Logout dari Survey Pemda
# 3. Clear browser cache (Ctrl+Shift+Del)
# 4. Close browser
# 5. Open browser baru
# 6. Login ke: http://localhost:8006/
#    Username: Prakom@admin2025.com
#    Password: Prakom@2025
# 7. Akses: http://localhost:8006/api-simpeg/pegawai/
```

### Step 6: Cek Logs Real-time

```bash
# Terminal 1: Watch logs
docker logs -f survey_pemda_python_app

# Terminal 2: Akses halaman pegawai di browser
# Lihat logs di Terminal 1
```

**Expected logs**:
```
INFO User Prakom@admin2025.com exists locally, attempting ESIMPEG API login for token...
INFO ESIMPEG API login successful for user: Prakom@admin2025.com
INFO Stored ESIMPEG tokens in session for existing user Prakom@admin2025.com
GET /api-simpeg/pegawai/ HTTP/1.1" 200 113086
```

---

## 🎯 Checklist Troubleshooting

- [ ] User sudah logout dan login ulang setelah fix?
- [ ] Logs menunjukkan "Stored ESIMPEG tokens in session"?
- [ ] ESIMPEG container running? (`docker ps | grep esimpeg`)
- [ ] Network connection OK? (test dengan curl)
- [ ] Browser cache sudah di-clear?
- [ ] User menggunakan credentials yang benar?
- [ ] User ada di ESIMPEG database?
- [ ] Response 200 di Network tab browser?

---

## 📞 Jika Masih Gagal

Kirim informasi berikut:

1. **Logs login**:
```bash
docker logs survey_pemda_python_app 2>&1 | grep "Prakom@admin2025.com" | tail -10
```

2. **Logs pegawai access**:
```bash
docker logs survey_pemda_python_app 2>&1 | grep "pegawai" | tail -10
```

3. **Error logs**:
```bash
docker logs survey_pemda_python_app 2>&1 | grep -i "error\|exception" | tail -20
```

4. **Screenshot** dari:
   - Browser showing halaman pegawai
   - Developer Tools Network tab
   - Developer Tools Console tab

