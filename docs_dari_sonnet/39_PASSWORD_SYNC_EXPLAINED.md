# Password Sync - Penjelasan Lengkap & Mudah Dipahami

**Date**: 2026-03-31  
**Status**: 📚 DOKUMENTASI LENGKAP

---

## 🎯 Tujuan

Agar password user **SELALU SAMA** di semua aplikasi:
- ESIMPEG Python
- Survey Pemda Python
- Aplikasi lain (future)

**Contoh:**
- User `prakom@admin.com` ganti password di Survey Pemda → password di ESIMPEG juga berubah
- User `prakom@admin.com` ganti password di ESIMPEG → password di Survey Pemda juga berubah

---

## 📊 Status Implementasi Saat Ini

### ✅ Yang Sudah Jalan (REALTIME)

**Skenario: Ganti Password di Survey Pemda**

```
┌─────────────────────────────────────────────────────────────┐
│                   Survey Pemda Python                       │
│                                                             │
│  User klik "Ganti Password"                                 │
│      ↓                                                       │
│  Input: old_password, new_password                          │
│      ↓                                                       │
│  Submit form                                                │
│      ↓                                                       │
│  Backend cek: User login via API?                           │
│      ↓ (Ya, ada token di session)                           │
│  Panggil API ESIMPEG:                                       │
│  POST /apisimpeg/5.0/auth/change-password                   │
│      ↓                                                       │
│  ⚡ LANGSUNG (dalam 1-2 detik)                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
                          ↓ HTTP Request
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                        ESIMPEG                              │
│                                                             │
│  Terima request change-password                             │
│      ↓                                                       │
│  Validasi old_password                                      │
│      ↓                                                       │
│  Update password di database                                │
│      ↓                                                       │
│  ✅ Return success                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
                          ↓ Response
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Survey Pemda Python                       │
│                                                             │
│  Terima response success                                    │
│      ↓                                                       │
│  Update password di database lokal                          │
│      ↓                                                       │
│  ✅ Tampilkan pesan sukses                                  │
└─────────────────────────────────────────────────────────────┘

✅ HASIL: Password berubah di KEDUA aplikasi dalam 1-2 detik!
```

**Kode yang sudah dibuat:**
- ✅ `apps/accounts/views.py` → `change_password_view()` 
- ✅ `apps/accounts/views.py` → `force_change_password_view()`
- ✅ `apps/accounts/services.py` → `EsimpegAPIService.change_password()`

**Status:** ✅ **SUDAH JALAN** - Tidak perlu aktivasi apapun!

---

### ⏳ Yang Belum Jalan (Perlu Setup)

**Skenario: Ganti Password di ESIMPEG**

```
┌─────────────────────────────────────────────────────────────┐
│                        ESIMPEG                              │
│                                                             │
│  User klik "Ganti Password"                                 │
│      ↓                                                       │
│  Input: old_password, new_password                          │
│      ↓                                                       │
│  Submit form                                                │
│      ↓                                                       │
│  Update password di database                                │
│      ↓                                                       │
│  ✅ Password di ESIMPEG berubah                             │
│      ↓                                                       │
│  ❓ Bagaimana Survey Pemda tahu?                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
                          ↓ ⏰ TUNGGU...
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Survey Pemda Python                       │
│                                                             │
│  ❌ Password masih yang lama                                │
│  ❌ User tidak bisa login dengan password baru              │
└─────────────────────────────────────────────────────────────┘

❌ MASALAH: Survey Pemda tidak tahu password sudah berubah!
```

**Solusi: Webhook System**

```
┌─────────────────────────────────────────────────────────────┐
│                        ESIMPEG                              │
│                                                             │
│  User ganti password                                        │
│      ↓                                                       │
│  Update password di database                                │
│      ↓                                                       │
│  Create PasswordChangeEvent                                 │
│      ↓                                                       │
│  ⏰ Cron Job (every 5 minutes)                              │
│      ↓                                                       │
│  Kirim webhook ke Survey Pemda                              │
│  POST /accounts/webhooks/password-changed/                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
                          ↓ HTTP Request (webhook)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Survey Pemda Python                       │
│                                                             │
│  Terima webhook                                             │
│      ↓                                                       │
│  Validasi signature (security)                              │
│      ↓                                                       │
│  Update password di database                                │
│      ↓                                                       │
│  ✅ Password sync selesai                                   │
└─────────────────────────────────────────────────────────────┘

✅ HASIL: Password sync dalam max 5 menit
```

**Kode yang sudah dibuat:**
- ✅ `apps/accounts/webhooks.py` → `handle_password_changed()` (receiver)
- ✅ `register_webhook.py` → Script untuk register webhook

**Status:** ⏳ **BELUM AKTIF** - Perlu setup di ESIMPEG!

---

## 🔧 Cara Aktivasi Webhook (Step by Step)

### Langkah 1: Cek Apakah ESIMPEG Sudah Support Webhook

```bash
# Cek apakah endpoint webhook ada
curl http://localhost:8005/apisimpeg/5.0/webhooks/list

# Jika dapat response (bukan 404), berarti sudah support
# Jika 404, berarti ESIMPEG belum implement webhook system
```

**Hasil yang diharapkan:**
```json
{
  "status": "success",
  "data": {
    "webhooks": []
  }
}
```

### Langkah 2: Register Webhook (Jika ESIMPEG Sudah Support)

```bash
# Cara 1: Pakai script otomatis
cd projects/survey_pemda_python
docker exec -it survey_pemda_python_app python register_webhook.py

# Ikuti instruksi:
# 1. Masukkan webhook URL: http://localhost:8006/accounts/webhooks/password-changed/
# 2. Masukkan ESIMPEG admin username: prakom@admin.com
# 3. Masukkan ESIMPEG admin password: ********

# Output:
# ✅ Webhook registered successfully!
# ESIMPEG_WEBHOOK_SECRET=abc123xyz789...
```

### Langkah 3: Update .env

```bash
# Edit file .env
nano projects/survey_pemda_python/.env

# Tambahkan secret key dari step 2:
ESIMPEG_WEBHOOK_SECRET=abc123xyz789...

# Save (Ctrl+O, Enter, Ctrl+X)
```

### Langkah 4: Restart Container

```bash
docker restart survey_pemda_python_app
```

### Langkah 5: Setup Cron Job di ESIMPEG

```bash
# Login ke server ESIMPEG
# Edit crontab
crontab -e

# Tambahkan baris ini (sync every 5 minutes):
*/5 * * * * docker exec -i esimpeg_python_app python manage.py sync_password_to_apps >> /var/log/esimpeg_password_sync.log 2>&1

# Save
```

### Langkah 6: Test

```bash
# Test 1: Ganti password di ESIMPEG
# (via web browser atau API)

# Test 2: Trigger sync manual (jangan tunggu 5 menit)
docker exec -it esimpeg_python_app python manage.py sync_password_to_apps

# Expected output:
# ✓ survey_pemda: 200 (45ms)

# Test 3: Cek password di Survey Pemda
docker exec -it survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='prakom@admin.com')
print(f'Password: {u.password[:50]}...')
"
```

---

## 📋 Checklist Status

### Survey Pemda → ESIMPEG (REALTIME)

- [x] ✅ Code implemented
- [x] ✅ API integration working
- [x] ✅ Change password view updated
- [x] ✅ Force change password view updated
- [x] ✅ Tested and working
- [ ] ⏳ Documentation complete

**Status:** ✅ **SUDAH JALAN 100%**

### ESIMPEG → Survey Pemda (WEBHOOK)

- [x] ✅ Webhook receiver implemented (Survey Pemda)
- [x] ✅ Signature validation implemented
- [x] ✅ Registration script created
- [ ] ⏳ ESIMPEG webhook sender implemented
- [ ] ⏳ Webhook registered
- [ ] ⏳ Secret key configured
- [ ] ⏳ Cron job setup
- [ ] ⏳ Tested end-to-end

**Status:** ⏳ **SIAP DIAKTIFKAN** (tunggu ESIMPEG implement webhook sender)

---

## 🎬 Demo Scenario

### Scenario 1: User Login via API, Ganti Password di Survey Pemda

```
1. User buka: http://localhost:8006/
2. Login dengan: prakom@admin.com / password123
   → Backend panggil API ESIMPEG login
   → Dapat token, simpan di session
   
3. User buka: http://localhost:8006/accounts/change-password/
4. Input:
   - Old password: password123
   - New password: newpassword456
   - Confirm: newpassword456
   
5. Submit
   → Backend cek: ada token? Ya!
   → Panggil API ESIMPEG change-password
   → ESIMPEG update password ✅
   → Survey Pemda update password lokal ✅
   
6. User logout
7. User login lagi dengan password baru: newpassword456
   → ✅ Berhasil login!
   
8. User buka ESIMPEG: http://localhost:8005/
9. Login dengan: prakom@admin.com / newpassword456
   → ✅ Berhasil login! (password sudah sync)
```

**Hasil:** ✅ Password sync REALTIME (1-2 detik)

### Scenario 2: User Ganti Password di ESIMPEG (Jika Webhook Aktif)

```
1. User buka: http://localhost:8005/
2. Login dengan: prakom@admin.com / password123
3. User buka: http://localhost:8005/accounts/change-password/
4. Input:
   - Old password: password123
   - New password: newpassword789
   - Confirm: newpassword789
   
5. Submit
   → ESIMPEG update password ✅
   → Create PasswordChangeEvent
   
6. ⏰ Tunggu max 5 menit (cron job)
   → Cron job trigger
   → ESIMPEG kirim webhook ke Survey Pemda
   → Survey Pemda update password ✅
   
7. User buka Survey Pemda: http://localhost:8006/
8. Login dengan: prakom@admin.com / newpassword789
   → ✅ Berhasil login! (password sudah sync)
```

**Hasil:** ✅ Password sync dalam max 5 menit

---

## ❓ FAQ

### Q1: Apakah password sync otomatis?

**A:** Tergantung arah:
- **Survey Pemda → ESIMPEG:** ✅ Otomatis REALTIME (sudah jalan)
- **ESIMPEG → Survey Pemda:** ⏳ Otomatis tapi ada delay max 5 menit (perlu setup webhook)

### Q2: Kenapa ada delay 5 menit?

**A:** Karena menggunakan cron job untuk efisiensi. Bisa dipercepat dengan:
- Ubah cron jadi setiap 1 menit: `*/1 * * * *`
- Atau trigger manual: `docker exec -it esimpeg_python_app python manage.py sync_password_to_apps`

### Q3: Apakah harus login via API dulu?

**A:** Untuk sync REALTIME (Survey Pemda → ESIMPEG), ya harus login via API dulu agar ada token di session.

Jika login langsung ke database (bukan via API), password hanya berubah di Survey Pemda saja, tidak sync ke ESIMPEG.

### Q4: Bagaimana jika webhook belum aktif?

**A:** Saat ini:
- ✅ Ganti password di Survey Pemda → sync ke ESIMPEG (REALTIME)
- ❌ Ganti password di ESIMPEG → TIDAK sync ke Survey Pemda

Solusi sementara: Selalu ganti password di Survey Pemda, bukan di ESIMPEG.

### Q5: Apakah aman?

**A:** ✅ Sangat aman!
- Password di-hash dengan PBKDF2 SHA256
- Webhook menggunakan HMAC signature validation
- Secret key disimpan di .env (tidak di-commit ke git)
- HTTPS di production

---

## 🚀 Kesimpulan

### Yang Sudah Bisa Digunakan Sekarang

✅ **Ganti password di Survey Pemda** → otomatis sync ke ESIMPEG (REALTIME)

**Cara pakai:**
1. Login via API (bukan langsung ke database)
2. Ganti password di Survey Pemda
3. ✅ Password otomatis berubah di ESIMPEG juga!

### Yang Perlu Setup Dulu

⏳ **Ganti password di ESIMPEG** → otomatis sync ke Survey Pemda (max 5 menit)

**Perlu:**
1. ESIMPEG implement webhook sender
2. Register webhook
3. Setup cron job
4. Test end-to-end

---

## 📞 Bantuan

Jika ada pertanyaan atau masalah:

1. Cek log: `docker logs -f survey_pemda_python_app`
2. Cek dokumentasi: `docs_dari_sonnet/38_PASSWORD_SYNC_SETUP.md`
3. Test manual: `docker exec -it survey_pemda_python_app python manage.py shell`

---

**Last Updated**: 2026-03-31  
**Version**: 1.0  
**Status**: ✅ Survey Pemda → ESIMPEG (JALAN) | ⏳ ESIMPEG → Survey Pemda (PERLU SETUP)
