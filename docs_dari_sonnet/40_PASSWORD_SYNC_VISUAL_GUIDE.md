# Password Sync - Visual Guide

**Date**: 2026-03-31  
**Status**: 📊 DIAGRAM & VISUAL

---

## 🎯 Ringkasan Singkat

| Arah | Status | Kecepatan | Perlu Setup? |
|------|--------|-----------|--------------|
| Survey Pemda → ESIMPEG | ✅ JALAN | REALTIME (1-2 detik) | ❌ Tidak |
| ESIMPEG → Survey Pemda | ⏳ SIAP | Max 5 menit | ✅ Ya |

---

## 📊 Diagram Alur

### Alur 1: Survey Pemda → ESIMPEG (✅ SUDAH JALAN)

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  👤 USER DI SURVEY PEMDA                                         │
│                                                                  │
│  1. Login via API                                                │
│     http://localhost:8006/                                       │
│     Username: prakom@admin.com                                   │
│     Password: password123                                        │
│                                                                  │
│  2. Klik "Ganti Password"                                        │
│     http://localhost:8006/accounts/change-password/              │
│                                                                  │
│  3. Input:                                                       │
│     Old Password: password123                                    │
│     New Password: newpassword456                                 │
│     Confirm: newpassword456                                      │
│                                                                  │
│  4. Submit ✅                                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ (Backend Process)
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  SURVEY PEMDA BACKEND                                            │
│                                                                  │
│  ✓ Cek session: ada esimpeg_access_token?                       │
│  ✓ Ya! User login via API                                       │
│  ✓ Panggil API ESIMPEG                                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ HTTP POST
                            ↓ /apisimpeg/5.0/auth/change-password
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  ESIMPEG API                                                     │
│                                                                  │
│  ✓ Validasi old_password                                        │
│  ✓ Update password di database                                  │
│  ✓ Return success                                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ Response
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  SURVEY PEMDA BACKEND                                            │
│                                                                  │
│  ✓ Terima response success                                      │
│  ✓ Update password di database lokal                            │
│  ✓ Tampilkan pesan sukses                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  ✅ SELESAI!                                                     │
│                                                                  │
│  Password berubah di:                                            │
│  ✓ ESIMPEG database                                             │
│  ✓ Survey Pemda database                                        │
│                                                                  │
│  Waktu: 1-2 detik                                               │
└──────────────────────────────────────────────────────────────────┘
```


### Alur 2: ESIMPEG → Survey Pemda (⏳ PERLU SETUP)

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  👤 USER DI ESIMPEG                                              │
│                                                                  │
│  1. Login                                                        │
│     http://localhost:8005/                                       │
│     Username: prakom@admin.com                                   │
│     Password: password123                                        │
│                                                                  │
│  2. Klik "Ganti Password"                                        │
│     http://localhost:8005/accounts/change-password/              │
│                                                                  │
│  3. Input:                                                       │
│     Old Password: password123                                    │
│     New Password: newpassword789                                 │
│     Confirm: newpassword789                                      │
│                                                                  │
│  4. Submit ✅                                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  ESIMPEG BACKEND                                                 │
│                                                                  │
│  ✓ Update password di database                                  │
│  ✓ Create PasswordChangeEvent (cache)                           │
│  ✓ Tampilkan pesan sukses                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ ⏰ TUNGGU CRON JOB
                            ↓ (Max 5 menit)
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  ESIMPEG CRON JOB                                                │
│                                                                  │
│  */5 * * * * sync_password_to_apps                              │
│                                                                  │
│  ✓ Cek PasswordChangeEvent yang belum sync                      │
│  ✓ Kirim webhook ke registered apps                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓ HTTP POST
                            ↓ /accounts/webhooks/password-changed/
                            ↓ Header: X-Webhook-Signature
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  SURVEY PEMDA WEBHOOK ENDPOINT                                   │
│                                                                  │
│  ✓ Validasi HMAC signature                                      │
│  ✓ Find user by username                                        │
│  ✓ Update password (already hashed)                             │
│  ✓ Log to ms_log_data                                           │
│  ✓ Return success                                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│  ✅ SELESAI!                                                     │
│                                                                  │
│  Password berubah di:                                            │
│  ✓ ESIMPEG database (langsung)                                  │
│  ✓ Survey Pemda database (max 5 menit)                          │
│                                                                  │
│  Waktu: Max 5 menit (via cron)                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Perbedaan Utama

| Aspek | Survey Pemda → ESIMPEG | ESIMPEG → Survey Pemda |
|-------|------------------------|------------------------|
| **Metode** | API Call (HTTP POST) | Webhook (HTTP POST) |
| **Trigger** | Langsung saat submit form | Cron job (every 5 min) |
| **Kecepatan** | REALTIME (1-2 detik) | Delayed (max 5 menit) |
| **Perlu Token?** | Ya (dari login API) | Tidak (pakai signature) |
| **Setup** | ❌ Tidak perlu | ✅ Perlu register webhook |
| **Status** | ✅ Sudah jalan | ⏳ Siap, perlu aktivasi |

---

## 📝 Checklist Aktivasi Webhook

### Persiapan (Survey Pemda)
- [x] ✅ Webhook endpoint created
- [x] ✅ Signature validation implemented
- [x] ✅ Registration script ready
- [ ] ⏳ .env configured with secret key

### Setup (ESIMPEG)
- [ ] ⏳ Webhook system implemented
- [ ] ⏳ Cron job configured
- [ ] ⏳ Webhook registered

### Testing
- [ ] ⏳ Manual webhook test
- [ ] ⏳ End-to-end test
- [ ] ⏳ Production deployment

---

**Last Updated**: 2026-03-31  
**Status**: 📊 Visual Guide Complete
