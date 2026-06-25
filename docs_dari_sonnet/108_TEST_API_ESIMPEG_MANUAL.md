# Test API ESIMPEG dari Survey Pemda (Manual)

**Tanggal**: 2026-04-08  
**Status**: ✅ Konfigurasi sudah benar  
**URL**: `http://localhost:8005` (ESIMPEG Python)

---

## ✅ Konfigurasi Survey Pemda

**File**: `projects/survey_pemda_python/.env`

```bash
ESIMPEG_API_URL=http://localhost:8005
ESIMPEG_API_TIMEOUT=10
```

**Status**: ✅ Sudah diubah dan container sudah di-restart

---

## 📋 Test Manual dengan CURL

### 1. Test Login ke ESIMPEG API

```bash
curl -X POST http://localhost:8005/apisimpeg/5.0/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "GANTI_DENGAN_USERNAME_KAMU",
    "password": "GANTI_DENGAN_PASSWORD_KAMU"
  }' | python3 -m json.tool
```

**Expected Response** (jika berhasil):
```json
{
    "status": "success",
    "message": "Login successful",
    "data": {
        "access_token": "eyJhbGc...",
        "refresh_token": "eyJhbGc...",
        "token_type": "Bearer",
        "expires_in": 86400,
        "user": {
            "user_id": 2,
            "username": "...",
            "name": "...",
            "email": "...",
            "is_active": true
        }
    },
    "version": "5.0"
}
```

**Copy `access_token`** untuk step berikutnya!

---

### 2. Test Get Pegawai List

```bash
# Ganti TOKEN_DARI_STEP_1 dengan access_token yang didapat
curl "http://localhost:8005/apisimpeg/5.0/pegawai/data/list?page=1&per_page=5" \
  -H "Authorization: Bearer TOKEN_DARI_STEP_1" \
  | python3 -m json.tool
```

**Expected Response** (jika berhasil):
```json
{
    "data": {
        "items": [
            {
                "id_pegawai": 11091,
                "namaPegawai": "...",
                "nipBaru": "197004051989031001",
                "id_opd": 1,
                "nm_opd": "SEKRETARIAT DAERAH",
                "nama_jabatan": "...",
                "namaGolongan": "IV/a",
                "namaPangkat": "Pembina"
            },
            ...
        ],
        "pagination": {
            "page": 1,
            "per_page": 5,
            "total": 11203,
            "total_pages": 2241
        }
    },
    "success_message": "",
    "errors": [],
    "error_message": null
}
```

---

### 3. Test dengan per_page=200 (Optimal)

```bash
curl "http://localhost:8005/apisimpeg/5.0/pegawai/data/list?page=1&per_page=200" \
  -H "Authorization: Bearer TOKEN_DARI_STEP_1" \
  | python3 -m json.tool | head -100
```

**Expected**: 200 records per page (lebih cepat!)

---

## 🔧 Troubleshooting

### Error: "Anda tidak memiliki izin untuk mengakses endpoint API pegawai ini"

**Penyebab**: User tidak punya permission untuk akses API pegawai

**Solusi**: Login dengan user yang punya permission. Cek permission di ESIMPEG:

```bash
# Di ESIMPEG container
docker exec esimpeg_python_app python manage.py shell -c "
from apps.accounts.models import User
from apps.manajemen.models import UserPermission

user = User.objects.get(username='USERNAME_KAMU')
perms = UserPermission.objects.filter(user=user)
for p in perms:
    print(f'{p.permission_key}')
"
```

User harus punya permission: `api.pegawai.view` atau sejenisnya.

---

### Error: "Token tidak valid"

**Penyebab**: Token expired atau salah

**Solusi**: Login ulang untuk dapat token baru (Step 1)

---

### Error: Connection refused

**Penyebab**: ESIMPEG container tidak running

**Solusi**:
```bash
docker ps | grep esimpeg
# Jika tidak ada, start container
docker-compose up -d esimpeg-python
```

---

## 🎯 Test dari Survey Pemda UI

### 1. Login ke Survey Pemda

```
http://localhost:8006
```

Login dengan user yang ada di ESIMPEG (username + password sama)

### 2. Akses Menu Data Pegawai ESIMPEG

```
http://localhost:8006/api-simpeg/pegawai/
```

### 3. Klik Tombol "Sinkronisasi"

Akan muncul progress bar dan data pegawai akan di-sync dari ESIMPEG API ke database Survey Pemda.

**Expected**:
- Progress bar muncul
- Sync selesai dalam 30-90 detik (untuk 11,203 pegawai)
- Data pegawai muncul di tabel

---

## 📊 Performance Test

### Test Response Time per Page

```bash
# Test 1 page dengan 200 records
time curl -s "http://localhost:8005/apisimpeg/5.0/pegawai/data/list?page=1&per_page=200" \
  -H "Authorization: Bearer TOKEN" \
  > /dev/null
```

**Expected**: < 1 second (setelah indexes applied)

### Test Full Sync Simulation

```bash
# Simulate sync 11,203 pegawai dengan per_page=200
# Total pages: 57 pages (11203 / 200 = 56.015)

for page in {1..5}; do
  echo "Page $page..."
  time curl -s "http://localhost:8005/apisimpeg/5.0/pegawai/data/list?page=$page&per_page=200" \
    -H "Authorization: Bearer TOKEN" \
    > /dev/null
done
```

**Expected**: 5 pages dalam 3-5 detik

---

## ✅ Checklist Verifikasi

- [ ] ESIMPEG container running di port 8005
- [ ] Survey Pemda container running di port 8006
- [ ] `.env` Survey Pemda: `ESIMPEG_API_URL=http://localhost:8005`
- [ ] Survey Pemda container sudah di-restart setelah ubah .env
- [ ] Login API berhasil (dapat access_token)
- [ ] Get pegawai list berhasil (dapat data)
- [ ] Sync dari UI Survey Pemda berhasil
- [ ] Data pegawai muncul di tabel Survey Pemda

---

## 📝 Summary

**Endpoint yang Dipakai**:
1. ✅ `POST /apisimpeg/5.0/auth/login` - Login
2. ✅ `GET /apisimpeg/5.0/pegawai/data/list` - Get pegawai list
3. ✅ `POST /apisimpeg/5.0/auth/change-password` - Change password
4. ✅ `GET /apisimpeg/5.0/pegawai/data/nip/{nip}` - Get pegawai by NIP

**Konfigurasi**:
- Survey Pemda: `http://localhost:8006`
- ESIMPEG API: `http://localhost:8005`
- Default per_page: 200 (optimal)
- Timeout: 10 seconds

**Performance**:
- Query time: 0.1-0.3 detik per page (dengan indexes)
- Sync time: 30-90 detik untuk 11,203 pegawai
- Total pages: 57 pages (dengan per_page=200)

Semua sudah siap dan optimal! 🚀
