# Fix DisallowedHost Error - ESIMPEG API Connection

**Tanggal**: 1 April 2026  
**Status**: ✅ RESOLVED

---

## 🔴 Masalah

Survey Pemda tidak bisa connect ke ESIMPEG API dengan error:
```
DisallowedHost: Invalid HTTP_HOST header: '172.21.0.2:8000'. 
You may need to add '172.21.0.2' to ALLOWED_HOSTS.
```

Error ini muncul meskipun sudah set `ALLOWED_HOSTS = ['*']` di settings.py.

---

## 🔍 Root Cause

Django memvalidasi HTTP_HOST header dengan 2 tahap:

1. **Cek apakah host ada di ALLOWED_HOSTS**
   - `ALLOWED_HOSTS = ['*']` seharusnya allow semua host
   
2. **Validasi format hostname (RFC 1034/1035)**
   - Django tetap validasi format meskipun `ALLOWED_HOSTS = ['*']`
   - Format `172.21.0.2:8000` (IP dengan port) dianggap invalid
   - Port `:8000` tidak boleh ada di HTTP_HOST header

**Kenapa ini terjadi?**

Ketika `requests.post()` dari Survey Pemda ke ESIMPEG:
```python
response = requests.post(
    "http://172.21.0.2:8000/apisimpeg/5.0/auth/login",
    ...
)
```

Requests library mengirim HTTP header:
```
Host: 172.21.0.2:8000
```

Django menerima header ini dan validasi:
1. ✅ `172.21.0.2:8000` ada di `ALLOWED_HOSTS = ['*']`? → YES
2. ❌ Format `172.21.0.2:8000` valid menurut RFC 1034/1035? → NO (port tidak boleh)

Maka Django raise `DisallowedHost` error.

---

## ✅ Solusi

### Solusi 1: Tambahkan IP Explicitly ke ALLOWED_HOSTS (RECOMMENDED)

Meskipun `ALLOWED_HOSTS = ['*']`, kita harus tambahkan IP address explicitly untuk bypass validasi format.

**File**: `projects/ESIMPEG-Python/esimpeg_core/settings.py`

```python
# Allow all hosts in development (for container networking)
# In DEBUG mode, allow all hosts including IP addresses with ports
if DEBUG:
    ALLOWED_HOSTS = ['*']
    # Also explicitly allow IP addresses (Django validates format even with '*')
    ALLOWED_HOSTS.extend(['172.21.0.2', '172.21.0.3', '172.18.0.5', '172.18.0.6', 'localhost', '127.0.0.1', '0.0.0.0'])
else:
    ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')]
```

**Catatan**: 
- Tambahkan semua IP yang mungkin digunakan container
- IP container bisa berubah setiap restart
- Gunakan `docker inspect` untuk cek IP terbaru

---

## 🔧 Implementasi

### Step 1: Update ESIMPEG Settings

```bash
# Edit settings.py
nano projects/ESIMPEG-Python/esimpeg_core/settings.py
```

Tambahkan IP addresses ke ALLOWED_HOSTS (lihat kode di atas).

### Step 2: Cek IP Container ESIMPEG

```bash
docker inspect esimpeg_python_app --format='{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'
# Output: 172.21.0.3 172.18.0.6
```

### Step 3: Update Survey Pemda .env

```bash
# Edit .env
nano projects/survey_pemda_python/.env
```

Update ESIMPEG_API_URL dengan IP yang benar:
```env
# From container: http://172.21.0.3:8000 (using IP to avoid Django host validation issues)
ESIMPEG_API_URL=http://172.21.0.3:8000
ESIMPEG_API_TIMEOUT=10
```

### Step 4: Restart Containers

```bash
docker restart esimpeg_python_app survey_pemda_python_app
```

### Step 5: Test Connection

```bash
# Wait for containers to start
sleep 8

# Test API login
docker exec survey_pemda_python_app curl -s -X POST \
  http://172.21.0.3:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}' \
  | python3 -m json.tool
```

**Expected Response**:
```json
{
    "status": "success",
    "message": "Login successful",
    "data": {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "user": {
            "user_id": 1,
            "username": "Prakom@admin2025.com",
            "name": "Prakom Admin"
        }
    }
}
```

---

## 🧪 Testing

### Test 1: Login ke Survey Pemda

1. Buka browser: http://localhost:8006/
2. Login dengan:
   - Username: `Prakom@admin2025.com`
   - Password: `Prakom@2025`
3. Seharusnya berhasil login dan redirect ke dashboard

### Test 2: Cek Token di Session

```bash
# Cek logs untuk konfirmasi token disimpan
docker logs survey_pemda_python_app 2>&1 | grep "Stored ESIMPEG tokens" | tail -3
```

**Expected Output**:
```
INFO Stored ESIMPEG tokens in session for existing user Prakom@admin2025.com
```

### Test 3: Akses Halaman Pegawai

1. Buka browser: http://localhost:8006/api-simpeg/pegawai/
2. Seharusnya tampil data pegawai dari ESIMPEG API
3. Tidak ada error di console browser

### Test 4: Cek Logs untuk Error

```bash
# Cek error logs
docker logs survey_pemda_python_app 2>&1 | grep -i "disallowed\|error" | tail -10
```

**Expected**: Tidak ada error DisallowedHost lagi.

---

## 📝 Files Modified

### 1. ESIMPEG Settings

**File**: `projects/ESIMPEG-Python/esimpeg_core/settings.py`

**Changes**:
- Added explicit IP addresses to ALLOWED_HOSTS
- Includes both current and potential future IPs

### 2. Survey Pemda Environment

**File**: `projects/survey_pemda_python/.env`

**Changes**:
- Updated ESIMPEG_API_URL from `172.21.0.2` to `172.21.0.3`
- Added comment explaining IP usage

---

## 🚨 Important Notes

### IP Address Changes

Container IP addresses dapat berubah setiap kali:
- Container restart
- Docker network recreate
- System reboot

**Jika API connection gagal lagi**, cek IP terbaru:
```bash
docker inspect esimpeg_python_app --format='{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'
```

Update `.env` dan restart containers.

### Alternative: Use Container Name (NOT RECOMMENDED)

Bisa juga gunakan container name:
```env
ESIMPEG_API_URL=http://esimpeg_python_app:8000
```

Tapi ini akan trigger error yang sama karena underscore di container name tidak valid menurut RFC 1034/1035.

### Alternative: Custom Middleware (OVERKILL)

Bisa buat custom middleware untuk bypass host validation, tapi ini overkill untuk development environment. Lebih simple tambahkan IP ke ALLOWED_HOSTS.

---

## ✅ Status Saat Ini

**API Connection**: ✅ WORKING
- Survey Pemda bisa connect ke ESIMPEG API
- Login berhasil dan dapat token
- Token disimpan di session
- Data pegawai bisa di-fetch

**Logs Terakhir** (08:07):
```
INFO ESIMPEG API login successful for user: Prakom@admin2025.com
INFO Stored ESIMPEG tokens in session for existing user Prakom@admin2025.com
GET /api-simpeg/pegawai/ HTTP/1.1" 200
```

**No More Errors**: ✅
- Tidak ada DisallowedHost error
- Tidak ada connection error
- API response 200 OK

---

## 🎯 Kesimpulan

Masalah DisallowedHost sudah resolved dengan:
1. ✅ Tambahkan IP addresses explicitly ke ALLOWED_HOSTS
2. ✅ Update ESIMPEG_API_URL dengan IP yang benar
3. ✅ Restart containers
4. ✅ Test connection berhasil

User sekarang bisa:
- ✅ Login ke Survey Pemda via ESIMPEG API
- ✅ Token otomatis disimpan di session
- ✅ Akses halaman pegawai dan lihat data dari ESIMPEG
- ✅ Tidak ada error lagi

---

## 📞 Troubleshooting

### Problem: API Connection Failed Setelah Restart

**Penyebab**: IP container berubah

**Solusi**:
```bash
# 1. Cek IP baru
docker inspect esimpeg_python_app --format='{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'

# 2. Update .env
nano projects/survey_pemda_python/.env
# Update ESIMPEG_API_URL dengan IP baru

# 3. Restart Survey Pemda
docker restart survey_pemda_python_app
```

### Problem: Masih Ada DisallowedHost Error

**Penyebab**: IP belum ditambahkan ke ALLOWED_HOSTS

**Solusi**:
```bash
# 1. Cek IP yang digunakan
docker logs survey_pemda_python_app 2>&1 | grep "DisallowedHost" | tail -1
# Lihat IP di error message

# 2. Tambahkan IP ke settings.py
nano projects/ESIMPEG-Python/esimpeg_core/settings.py
# Tambahkan IP ke ALLOWED_HOSTS.extend([...])

# 3. Restart ESIMPEG
docker restart esimpeg_python_app
```

### Problem: User Tidak Dapat Token

**Penyebab**: User belum logout/login ulang

**Solusi**:
1. Logout dari Survey Pemda
2. Clear browser cache (Ctrl+Shift+Del)
3. Login kembali
4. Token akan disimpan otomatis

---

**END OF DOCUMENTATION**
