# Fix: Koneksi ke ESIMPEG API

## Masalah

Data pegawai tidak bisa diambil dari ESIMPEG API dengan error "Gagal mengambil data pegawai dari ESIMPEG API".

## Penyebab

`ESIMPEG_API_URL` di `.env` menggunakan IP container (`http://172.21.0.2:8000`) yang tidak bisa diakses dari Survey Pemda container.

## Solusi

Update `.env` untuk menggunakan nama container:

```env
# Sebelum
ESIMPEG_API_URL=http://172.21.0.2:8000

# Sesudah
ESIMPEG_API_URL=http://esimpeg_python_app:8000
```

## Testing Koneksi

### 1. Test dari Host
```bash
curl http://localhost:8005/health
```

### 2. Test dari Survey Pemda Container
```bash
docker exec survey_pemda_python_app curl -s http://esimpeg_python_app:8000/health
```

### 3. Test Login API
```bash
docker exec survey_pemda_python_app curl -s -X POST \
  http://esimpeg_python_app:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}'
```

### 4. Test Pegawai List API (dengan token)
```bash
# Get token first
TOKEN=$(docker exec survey_pemda_python_app curl -s -X POST \
  http://esimpeg_python_app:8000/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Test pegawai list
docker exec survey_pemda_python_app curl -s \
  "http://esimpeg_python_app:8000/apisimpeg/5.0/pegawai/data/list?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

## Cara Kerja

### Network Architecture

```
Host Machine (localhost)
├── Port 8005 → esimpeg_python_app:8000 (ESIMPEG)
└── Port 8006 → survey_pemda_python_app:8000 (Survey Pemda)

Docker Network (esimpeg-python_default)
├── esimpeg_python_app (container name)
│   └── Internal: 8000
└── survey_pemda_python_app (container name)
    └── Internal: 8000
```

### Akses dari Host
```
http://localhost:8005 → esimpeg_python_app:8000
http://localhost:8006 → survey_pemda_python_app:8000
```

### Akses antar Container
```
survey_pemda_python_app → http://esimpeg_python_app:8000
```

## File yang Diubah

- `projects/survey_pemda_python/.env`
  - Update `ESIMPEG_API_URL` dari IP ke container name

## Testing Setelah Fix

```bash
# 1. Restart container (sudah dilakukan)
docker restart survey_pemda_python_app

# 2. Logout dan login kembali
#    Username: Prakom@admin2025.com
#    Password: Prakom@2025

# 3. Akses halaman pegawai
#    URL: http://localhost:8006/api-simpeg/pegawai/

# 4. Seharusnya tampil data pegawai dari ESIMPEG API ✅
```

## Troubleshooting

### Error: "Connection refused"
**Penyebab**: ESIMPEG container tidak running

**Solusi**:
```bash
docker start esimpeg_python_app
docker ps | grep esimpeg
```

### Error: "Name or service not known"
**Penyebab**: Container tidak dalam network yang sama

**Solusi**:
```bash
# Check network
docker network inspect esimpeg-python_default

# Reconnect if needed
docker network connect esimpeg-python_default survey_pemda_python_app
```

### Error: "Token invalid"
**Penyebab**: Token expired atau tidak valid

**Solusi**:
1. Logout dari Survey Pemda
2. Login kembali (token baru akan dibuat)
3. Akses halaman pegawai lagi

## Kesimpulan

✅ **Koneksi fixed**: Menggunakan container name instead of IP
✅ **Network**: Kedua container dalam network yang sama
✅ **API accessible**: ESIMPEG API bisa diakses dari Survey Pemda
✅ **Ready to use**: Data pegawai bisa diambil dari ESIMPEG API

---

**Fixed**: 2026-03-31
**Issue**: Container networking
**Solution**: Use container name instead of IP address
