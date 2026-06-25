# Fix: ESIMPEG Access Token di Session

## Masalah

User yang dibuat via seeder (contoh: `Prakom@admin2025.com`) tidak bisa mengakses halaman `/api-simpeg/pegawai/` karena:

1. User dibuat via seeder di database Survey Pemda
2. User login dengan password yang sudah ada di database
3. Tapi TIDAK ada `esimpeg_access_token` di session
4. Halaman pegawai list membutuhkan token untuk fetch data dari ESIMPEG API
5. Error: "Anda harus login via ESIMPEG API terlebih dahulu"

## Penyebab

Kode sebelumnya hanya menyimpan token ESIMPEG ke session jika:
- User TIDAK ada di database lokal
- User dibuat baru dari ESIMPEG API

Tapi TIDAK menyimpan token jika:
- User sudah ada di database lokal (via seeder atau registrasi manual)
- User login dengan password yang sudah tersimpan

## Solusi

### 1. Simpan Token Saat User Baru Dibuat dari ESIMPEG API

```python
# Setelah user dibuat dari ESIMPEG API
user = authenticate(request, username=username, password=password)

# Store ESIMPEG API tokens in session for future API calls
request.session['esimpeg_access_token'] = api_response.get('access_token')
request.session['esimpeg_refresh_token'] = api_response.get('refresh_token')
logger.info(f"Stored ESIMPEG tokens in session for user {username}")
```

### 2. Simpan Token Saat User Existing Login

```python
# User exists in local database, authenticate normally
user = authenticate(request, username=username, password=password)

# If authentication successful, try to get ESIMPEG token
if user is not None:
    logger.info(f"User {username} exists locally, attempting ESIMPEG API login for token...")
    
    from apps.accounts.services import EsimpegAPIService
    esimpeg_api = EsimpegAPIService()
    
    try:
        api_response = esimpeg_api.login(username, password)
        
        if api_response:
            # Store ESIMPEG API tokens in session
            request.session['esimpeg_access_token'] = api_response.get('access_token')
            request.session['esimpeg_refresh_token'] = api_response.get('refresh_token')
            logger.info(f"Stored ESIMPEG tokens in session for existing user {username}")
        else:
            logger.warning(f"Could not get ESIMPEG token for user {username}")
            
    except Exception as api_err:
        logger.warning(f"ESIMPEG API error for existing user {username}: {api_err}")
        # Continue with local login even if ESIMPEG API fails
```

## Cara Kerja Sekarang

### Skenario 1: User Baru (Tidak Ada di Database Lokal)
1. User login dengan username/password
2. Survey Pemda cek database lokal → TIDAK ADA
3. Survey Pemda call ESIMPEG API `/apisimpeg/5.0/auth/login`
4. ESIMPEG API return: `access_token`, `refresh_token`, `user data`
5. Survey Pemda create user baru di database lokal
6. **SIMPAN token ke session**: `esimpeg_access_token`, `esimpeg_refresh_token`
7. User bisa akses `/api-simpeg/pegawai/` dengan token

### Skenario 2: User Existing (Ada di Database Lokal)
1. User login dengan username/password
2. Survey Pemda cek database lokal → ADA
3. Survey Pemda authenticate dengan password lokal → SUKSES
4. **Survey Pemda call ESIMPEG API `/apisimpeg/5.0/auth/login`** (untuk dapat token)
5. ESIMPEG API return: `access_token`, `refresh_token`
6. **SIMPAN token ke session**: `esimpeg_access_token`, `esimpeg_refresh_token`
7. User bisa akses `/api-simpeg/pegawai/` dengan token

### Skenario 3: User Existing Tapi Tidak Ada di ESIMPEG
1. User login dengan username/password
2. Survey Pemda cek database lokal → ADA
3. Survey Pemda authenticate dengan password lokal → SUKSES
4. Survey Pemda call ESIMPEG API → GAGAL (user tidak ada di ESIMPEG)
5. **TIDAK simpan token** (karena tidak ada)
6. User tetap bisa login ke Survey Pemda
7. Tapi TIDAK bisa akses `/api-simpeg/pegawai/` (butuh token)

## Catatan Penting

### User dari Seeder

Jika user dibuat via seeder (contoh: `Prakom@admin2025.com`):

1. **Pastikan user juga ada di ESIMPEG** dengan username dan password yang sama
2. Jika user TIDAK ada di ESIMPEG:
   - User bisa login ke Survey Pemda
   - Tapi TIDAK bisa akses fitur API SIMPEG (pegawai list, dll)
   - Solusi: Buat user di ESIMPEG atau gunakan user yang sudah ada di ESIMPEG

### Sinkronisasi User

Untuk user yang dibuat via seeder di kedua sistem:

```bash
# Survey Pemda
docker exec survey_pemda_python_app python manage.py seed_users

# ESIMPEG
docker exec esimpeg_python_app python manage.py seed_users
```

Pastikan username dan password SAMA di kedua sistem!

### Testing

1. **Logout** dari Survey Pemda
2. **Login** kembali dengan user yang sama
3. Token akan otomatis disimpan di session
4. Akses `/api-simpeg/pegawai/` → Seharusnya berhasil

## File yang Diubah

- `projects/survey_pemda_python/core/views.py`
  - Function: `landing_page()`
  - Tambah: Simpan token saat user baru dibuat dari API
  - Tambah: Simpan token saat user existing login

## Testing Commands

```bash
# 1. Restart container
docker restart survey_pemda_python_app

# 2. Check logs
docker logs -f survey_pemda_python_app

# 3. Login dan cek session
# - Logout dari Survey Pemda
# - Login kembali
# - Akses: http://localhost:8006/api-simpeg/pegawai/
# - Seharusnya berhasil tampil data pegawai
```

## Troubleshooting

### Error: "Anda harus login via ESIMPEG API terlebih dahulu"

**Penyebab**: Token tidak ada di session

**Solusi**:
1. Logout dari Survey Pemda
2. Login kembali (token akan disimpan otomatis)
3. Akses halaman pegawai lagi

### Error: "Gagal mengambil data pegawai dari ESIMPEG API"

**Penyebab**: Token invalid atau expired

**Solusi**:
1. Logout dari Survey Pemda
2. Login kembali (dapat token baru)
3. Akses halaman pegawai lagi

### User Tidak Ada di ESIMPEG

**Penyebab**: User hanya ada di Survey Pemda, tidak ada di ESIMPEG

**Solusi**:
1. Buat user di ESIMPEG dengan username/password yang sama
2. Atau gunakan user yang sudah ada di ESIMPEG (contoh: `prakom@admin.com`)

## Kesimpulan

✅ Token ESIMPEG sekarang otomatis disimpan di session saat login
✅ User baru dan user existing sama-sama dapat token
✅ User bisa akses fitur API SIMPEG (pegawai list, dll)
✅ Jika ESIMPEG API down, user tetap bisa login (tapi tidak dapat token)
