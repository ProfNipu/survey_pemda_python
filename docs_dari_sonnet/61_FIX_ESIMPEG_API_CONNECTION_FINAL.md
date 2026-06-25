# Fix ESIMPEG API Connection - DisallowedHost Error

**Tanggal**: 31 Maret 2026  
**Status**: ✅ RESOLVED

## Masalah

Survey Pemda tidak bisa connect ke ESIMPEG API dengan error:
```
DisallowedHost: Invalid HTTP_HOST header: 'esimpeg_python_app:8000'. 
The domain name provided is not valid according to RFC 1034/1035.
```

## Root Cause

Django memvalidasi HTTP_HOST header berdasarkan RFC 1034/1035:
- Container name dengan underscore (`esimpeg_python_app`) tidak valid
- Port dalam hostname (`:8000`) tidak valid
- Meskipun `ALLOWED_HOSTS = ['*']`, Django tetap validasi format hostname

## Solusi

Gunakan IP address container instead of container name:

### 1. Update Survey Pemda `.env`

```bash
# OLD (tidak work)
ESIMPEG_API_URL=http://esimpeg_python_app:8000

# NEW (work!)
ESIMPEG_API_URL=http://172.21.0.2:8000
```

### 2. Restart Survey Pemda Container

```bash
docker restart survey_pemda_python_app
```

## Cara Mendapatkan IP Container

```bash
docker inspect esimpeg_python_app --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
# Output: 172.21.0.2172.18.0.5 (pilih yang pertama)
```

## Testing

```bash
# Test dari Survey Pemda container
docker exec survey_pemda_python_app curl -X POST \
  http://172.21.0.2:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}'
```

Response sukses:
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

## Files Modified

1. `projects/survey_pemda_python/.env` - Updated ESIMPEG_API_URL
2. `projects/ESIMPEG-Python/esimpeg_core/settings.py` - Added host validation bypass (for future)

## Next Steps

User sekarang bisa:
1. Login ke Survey Pemda via ESIMPEG API
2. Access pegawai list page: http://localhost:8006/api-simpeg/pegawai/
3. Data pegawai akan di-fetch dari ESIMPEG API

