# User ID OPD - README

**Tanggal**: 31 Maret 2026

---

## ✅ Selesai

### 1. ESIMPEG API - Tambah user_id_opd ke Response

**Endpoint:** `POST /apisimpeg/5.0/auth/login`

**Response sekarang include:**
```json
{
  "user": {
    "user_id": 1,
    "username": "prakom@admin.com",
    "id_pegawai": 123,
    "user_id_opd": 456  ← NEW!
  }
}
```

### 2. Survey Pemda - Simpan user_id_opd ke Database

**Saat login via ESIMPEG API:**
- User dibuat di database lokal Survey Pemda
- Field `user_id_opd` disimpan dari response ESIMPEG
- Tercatat di log `ms_log_data`

---

## 🧪 Cara Test

```bash
# 1. Login di Survey Pemda dengan user yang belum ada
# URL: http://localhost:8006/
# Username: test@example.com (dari ESIMPEG)
# Password: password_dari_esimpeg

# 2. Cek database
docker exec -it survey_pemda_python_app python manage.py shell

>>> from apps.accounts.models import User
>>> user = User.objects.get(username='test@example.com')
>>> user.user_id_opd
456  # ✅ Tersimpan!
```

---

## 📝 File yang Diubah

| File | Perubahan |
|------|-----------|
| `projects/ESIMPEG-Python/esimpeg_core/views.py` | ✅ Tambah `user_id_opd` ke response |
| `projects/survey_pemda_python/core/views.py` | ✅ Simpan `user_id_opd` saat create user |
| `projects/survey_pemda_python/apps/accounts/services.py` | ✅ Update docstring |

---

## 🗑️ File yang Dihapus

- ✅ `projects/ESIMPEG-Python/test_login_user_id_opd.sh` (dihapus sesuai permintaan)

---

## 📚 Dokumentasi Lengkap

- `49_USER_ID_OPD_SYNC.md` - Dokumentasi lengkap dengan flow dan testing
- `48_LOGIN_API_USER_ID_OPD.md` - Dokumentasi perubahan di ESIMPEG API

---

**Status**: ✅ SELESAI & SIAP DIPAKAI
