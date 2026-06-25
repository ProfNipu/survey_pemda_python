# Deploy Password Popup Feature ke VPS

**Tanggal**: 2026-04-08  
**Fitur**: Password popup untuk sync pegawai tanpa logout/login  
**Status**: ✅ Ready to deploy

---

## 📋 Files yang Diubah

### 1. Backend (Python)
- `apps/api_simpeg/views.py` - Function `pegawai_sync()` (line 120-180)

### 2. Frontend (JavaScript)
- `apps/api_simpeg/templates/api_simpeg/pegawai_list.html` - Function `syncPegawai()` dan `showPasswordPopup()`

---

## 🚀 Cara Deploy ke VPS

### Step 1: Backup Files di VPS

```bash
# SSH ke VPS
ssh root@103.143.152.139

# Backup files yang akan diubah
cd /root/projects/survey_pemda_python
cp apps/api_simpeg/views.py apps/api_simpeg/views.py.backup.$(date +%Y%m%d_%H%M%S)
cp apps/api_simpeg/templates/api_simpeg/pegawai_list.html apps/api_simpeg/templates/api_simpeg/pegawai_list.html.backup.$(date +%Y%m%d_%H%M%S)
```

### Step 2: Copy Files dari Laptop ke VPS

```bash
# Di laptop
cd ~/project-docker/all-projects-darireal/projects/survey_pemda_python

# Copy views.py
scp apps/api_simpeg/views.py root@103.143.152.139:/root/projects/survey_pemda_python/apps/api_simpeg/

# Copy pegawai_list.html
scp apps/api_simpeg/templates/api_simpeg/pegawai_list.html root@103.143.152.139:/root/projects/survey_pemda_python/apps/api_simpeg/templates/api_simpeg/
```

### Step 3: Update .env di VPS (Jika Belum)

```bash
# Di VPS
cd /root/projects/survey_pemda_python

# Check current ESIMPEG_API_URL
grep ESIMPEG_API_URL .env

# Jika masih pakai IP lama, update ke gateway
# Untuk VPS, pakai IP Docker gateway atau hostname container
nano .env
```

**Update**:
```bash
# Opsi 1: Pakai Docker gateway (recommended)
ESIMPEG_API_URL=http://172.17.0.1:8005

# Opsi 2: Pakai IP container ESIMPEG langsung
# ESIMPEG_API_URL=http://172.21.0.2:8000
```

### Step 4: Restart Container Survey Pemda

```bash
# Di VPS
cd /root/projects/survey_pemda_python

# Restart container
docker-compose restart survey-pemda-python

# Atau jika nama container berbeda
docker restart survey_pemda_python_app

# Check logs
docker logs -f survey_pemda_python_app --tail 50
```

### Step 5: Test di VPS

```bash
# Akses Survey Pemda VPS
http://103.143.152.139:8006

# Login dengan user biasa (bukan via ESIMPEG)
# Akses menu "Data Pegawai ESIMPEG"
# Klik "Sinkronisasi"
# Popup password muncul
# Masukkan password ESIMPEG
# Sync berjalan
```

---

## 🧪 Testing Checklist

### Test 1: User Tanpa Token
- [ ] Login dengan user database lokal
- [ ] Akses menu "Data Pegawai ESIMPEG"
- [ ] Klik tombol "Sinkronisasi"
- [ ] Popup konfirmasi muncul
- [ ] Klik "Ya, Sinkronkan!"
- [ ] Popup password muncul dengan pesan "Token ESIMPEG tidak ditemukan"
- [ ] Masukkan password ESIMPEG yang benar
- [ ] Klik "Login & Sinkronkan"
- [ ] Progress bar muncul
- [ ] Sync berjalan dan selesai
- [ ] Data pegawai muncul di tabel

### Test 2: Password Salah
- [ ] Ulangi Test 1
- [ ] Masukkan password yang salah
- [ ] Error muncul: "Login ke ESIMPEG gagal. Password salah..."
- [ ] Klik OK
- [ ] Bisa coba lagi

### Test 3: User Dengan Token (Sudah Login via ESIMPEG)
- [ ] Logout
- [ ] Login dengan kredensial ESIMPEG (`Prakom@admin2025.com` / `Prakom@2025`)
- [ ] Akses menu "Data Pegawai ESIMPEG"
- [ ] Klik tombol "Sinkronisasi"
- [ ] Popup konfirmasi muncul
- [ ] Klik "Ya, Sinkronkan!"
- [ ] Langsung mulai sync (tidak ada popup password)
- [ ] Progress bar muncul
- [ ] Sync selesai

### Test 4: Token Tersimpan di Session
- [ ] Setelah Test 1 berhasil (masukkan password)
- [ ] Jangan logout
- [ ] Klik "Sinkronisasi" lagi
- [ ] Tidak ada popup password (token sudah tersimpan)
- [ ] Langsung mulai sync

---

## 🔧 Troubleshooting

### Issue 1: Popup Password Tidak Muncul

**Cek**:
```bash
# Di VPS, check logs
docker logs survey_pemda_python_app --tail 100 | grep -i "password\|token"
```

**Solusi**:
- Pastikan file `pegawai_list.html` sudah ter-update
- Clear browser cache (Ctrl+Shift+R)
- Check console browser untuk JavaScript errors

### Issue 2: Login Gagal Terus

**Cek**:
```bash
# Test login manual dari VPS
docker exec survey_pemda_python_app python manage.py shell -c "
from apps.accounts.services import EsimpegAPIService
api = EsimpegAPIService()
result = api.login('Prakom@admin2025.com', 'Prakom@2025')
print('Success!' if result else 'Failed!')
"
```

**Solusi**:
- Cek `ESIMPEG_API_URL` di `.env`
- Cek ESIMPEG container running: `docker ps | grep esimpeg`
- Cek network connectivity

### Issue 3: Sync Timeout

**Cek**:
```bash
# Check ESIMPEG API performance
time curl -s "http://172.17.0.1:8005/apisimpeg/5.0/pegawai/data/list?page=1&per_page=200" \
  -H "Authorization: Bearer TOKEN" > /dev/null
```

**Solusi**:
- Apply database indexes (jika belum)
- Check `per_page` default = 200
- Increase timeout di `.env`: `ESIMPEG_API_TIMEOUT=30`

---

## 📊 Perbandingan

### Sebelum (Cara Lama)
```
User tanpa token → Error "Autentikasi Diperlukan"
                 → Harus logout
                 → Login ulang dengan ESIMPEG
                 → Baru bisa sync
                 
Langkah: 4 steps
User experience: ❌ Ribet
```

### Sesudah (Cara Baru)
```
User tanpa token → Popup password muncul
                 → Masukkan password
                 → Langsung sync
                 → Token tersimpan untuk next time
                 
Langkah: 2 steps
User experience: ✅ Mudah
```

---

## 🎯 Konfigurasi VPS

### Survey Pemda `.env`
```bash
# Docker gateway (recommended)
ESIMPEG_API_URL=http://172.17.0.1:8005
ESIMPEG_API_TIMEOUT=10
```

### ESIMPEG API
```python
# Default per_page = 200 (optimal)
per_page = _int_or_none(request.GET.get('per_page')) or 200
```

### Database Indexes
```bash
# Apply indexes untuk performance
docker exec mysql-main mysql -u root -p'!23#' esim_pegawai \
  < /root/ESIMPEG-Python/sql_optimizations/add_indexes_simple.sql
```

---

## ✅ Deployment Checklist

- [ ] Backup files di VPS
- [ ] Copy `views.py` ke VPS
- [ ] Copy `pegawai_list.html` ke VPS
- [ ] Update `.env` (ESIMPEG_API_URL)
- [ ] Restart container Survey Pemda
- [ ] Test login dengan user lokal
- [ ] Test popup password muncul
- [ ] Test sync dengan password
- [ ] Test sync kedua (token tersimpan)
- [ ] Verify data pegawai muncul

---

## 📝 Notes

**Keamanan**:
- Password tidak disimpan di database
- Password hanya dikirim sekali ke ESIMPEG API
- Token tersimpan di session (encrypted)
- Session expired setelah 30 menit inactivity

**Performance**:
- Sync 9,002 pegawai: 30-90 detik
- Query time: 0.1-0.3 detik per page
- Default per_page: 200 (optimal)

**User Experience**:
- Tidak perlu logout/login
- Cukup masukkan password sekali
- Token tersimpan untuk sync berikutnya
- Progress bar real-time

---

## 🚀 Quick Deploy Command

```bash
# One-liner deploy (di laptop)
cd ~/project-docker/all-projects-darireal/projects/survey_pemda_python && \
scp apps/api_simpeg/views.py root@103.143.152.139:/root/projects/survey_pemda_python/apps/api_simpeg/ && \
scp apps/api_simpeg/templates/api_simpeg/pegawai_list.html root@103.143.152.139:/root/projects/survey_pemda_python/apps/api_simpeg/templates/api_simpeg/ && \
ssh root@103.143.152.139 "cd /root/projects/survey_pemda_python && docker-compose restart survey-pemda-python"
```

Selesai! 🎉
