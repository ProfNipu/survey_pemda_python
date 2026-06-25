# Password Sync Setup - Survey Pemda Python

**Date**: 2026-03-31  
**Status**: ✅ IMPLEMENTED

---

## Overview

Survey Pemda Python sekarang support **automatic password sync** dari ESIMPEG menggunakan webhook system.

**Cara Kerja:**
1. User ganti password di ESIMPEG (atau aplikasi lain yang terintegrasi)
2. ESIMPEG kirim webhook ke Survey Pemda
3. Survey Pemda update password otomatis
4. ✅ Password sync dalam hitungan detik!

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ESIMPEG                              │
│                                                             │
│  User ganti password                                        │
│      ↓                                                       │
│  Django Signal: post_save                                   │
│      ↓                                                       │
│  PasswordChangeEvent (cache)                                │
│      ↓                                                       │
│  Cron Job (every 5 min)                                     │
│      ↓                                                       │
│  sync_password_to_apps                                      │
│      ↓                                                       │
│  Send Webhook (HMAC signature)                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
                          ↓ POST /accounts/webhooks/password-changed/
                          ↓ Headers: X-Webhook-Signature
                          ↓ Body: {username, password_hash, changed_at}
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Survey Pemda Python                       │
│                                                             │
│  Webhook Endpoint                                           │
│      ↓                                                       │
│  Validate HMAC Signature                                    │
│      ↓                                                       │
│  Find User by username                                      │
│      ↓                                                       │
│  Update password (already hashed)                           │
│      ↓                                                       │
│  Log to ms_log_data                                         │
│      ↓                                                       │
│  ✅ Return success                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup Steps

### 1. Register Webhook ke ESIMPEG

Ada 2 cara:

#### Cara 1: Menggunakan Script (Recommended)

```bash
cd projects/survey_pemda_python
docker exec -it survey_pemda_python_app python register_webhook.py
```

Script akan meminta:
- Survey Pemda webhook URL (e.g., `http://localhost:8006/accounts/webhooks/password-changed/`)
- ESIMPEG admin username
- ESIMPEG admin password

Output:
```
✅ Webhook registered successfully!

⚠️  IMPORTANT: Save this secret key to .env file:

ESIMPEG_WEBHOOK_SECRET=abc123xyz789...

📝 Add this to projects/survey_pemda_python/.env
```

#### Cara 2: Manual via API

```bash
# 1. Login ke ESIMPEG
curl -X POST "http://localhost:8005/apisimpeg/5.0/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "prakom@admin.com",
    "password": "your_password"
  }'

# Response: {"data": {"access_token": "eyJhbGc..."}}

# 2. Register webhook
curl -X POST "http://localhost:8005/apisimpeg/5.0/webhooks/register" \
  -H "Authorization: Bearer <token_from_step_1>" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "survey_pemda",
    "webhook_url": "http://localhost:8006/accounts/webhooks/password-changed/"
  }'

# Response: {"data": {"secret_key": "abc123xyz..."}}
```

### 2. Update .env File

Edit `projects/survey_pemda_python/.env`:

```bash
# ESIMPEG API Configuration
ESIMPEG_API_URL=http://172.21.0.2:8000
ESIMPEG_API_TIMEOUT=10
ESIMPEG_WEBHOOK_SECRET=abc123xyz789...  # ← Paste secret key dari step 1
```

### 3. Restart Container

```bash
docker restart survey_pemda_python_app
```

---

## Testing

### Test 1: Manual Webhook Call

```bash
# 1. Generate signature
SECRET="abc123xyz789..."
PAYLOAD='{"username":"prakom@admin.com","password_hash":"pbkdf2_sha256$...","changed_at":"2026-03-31T10:00:00Z"}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

# 2. Send webhook
curl -X POST "http://localhost:8006/accounts/webhooks/password-changed/" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIGNATURE" \
  -d "$PAYLOAD"

# Expected response:
# {"status": "success", "message": "Password synced successfully", ...}
```

### Test 2: End-to-End Test

```bash
# 1. Change password di ESIMPEG
curl -X POST "http://localhost:8005/apisimpeg/5.0/auth/change-password" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "old_password",
    "new_password": "new_password123",
    "confirm_password": "new_password123"
  }'

# 2. Trigger sync manually (don't wait cron)
docker exec -it esimpeg_python_app python manage.py sync_password_to_apps

# Expected output:
# ✓ survey_pemda: 200 (45ms)

# 3. Verify di Survey Pemda
docker exec -it survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='prakom@admin.com')
print(f'Password hash: {u.password[:50]}...')
"
```

---

## Webhook Endpoint Details

### URL
```
POST /accounts/webhooks/password-changed/
```

### Headers
```
Content-Type: application/json
X-Webhook-Signature: <hmac_sha256_signature>
```

### Request Body
```json
{
  "username": "prakom@admin.com",
  "password_hash": "pbkdf2_sha256$600000$...",
  "changed_at": "2026-03-31T10:00:00Z",
  "changed_by": 123
}
```

### Response (Success)
```json
{
  "status": "success",
  "message": "Password synced successfully",
  "username": "prakom@admin.com",
  "synced_at": "2026-03-31T10:00:05.123456Z"
}
```

### Response (Error)
```json
{
  "status": "error",
  "message": "Invalid signature"
}
```

### Status Codes
- `200` - Success
- `400` - Bad request (invalid JSON, missing fields)
- `403` - Forbidden (invalid signature)
- `404` - User not found
- `500` - Internal server error

---

## Security

### HMAC Signature Validation

Webhook menggunakan HMAC SHA256 untuk validasi:

```python
import hmac
import hashlib

# Calculate signature
signature = hmac.new(
    secret_key.encode('utf-8'),
    payload,
    hashlib.sha256
).hexdigest()

# Compare (constant time)
if not hmac.compare_digest(received_signature, expected_signature):
    return 403
```

### Best Practices

1. ✅ **Secret key harus random** - Minimal 32 karakter
2. ✅ **Simpan di .env** - Jangan commit ke git
3. ✅ **HTTPS di production** - Webhook URL harus HTTPS
4. ✅ **Validate signature** - Selalu cek signature sebelum process
5. ✅ **Log semua request** - Untuk audit trail

---

## Monitoring

### Check Webhook Logs

```bash
# Survey Pemda logs
docker logs -f survey_pemda_python_app | grep webhook

# ESIMPEG logs
docker logs -f esimpeg_python_app | grep webhook
```

### Check Sync Status

```bash
# Check last sync di ms_log_data
docker exec -it survey_pemda_python_app python manage.py shell -c "
from core.models import MsLogData
logs = MsLogData.objects.filter(action='password_sync').order_by('-created_at')[:5]
for log in logs:
    print(f'{log.created_at} - {log.new_data}')
"
```

---

## Troubleshooting

### Problem: Webhook signature invalid

**Cause**: Secret key tidak match

**Solution**:
```bash
# 1. Check secret di Survey Pemda
cat projects/survey_pemda_python/.env | grep ESIMPEG_WEBHOOK_SECRET

# 2. Check secret di ESIMPEG
docker exec -it esimpeg_python_app python manage.py shell -c "
from apps.integrations.webhooks.models import WebhookRegistration
w = WebhookRegistration.objects.get(app_name='survey_pemda')
print(f'Secret: {w.secret_key}')
"

# 3. Update .env jika berbeda
# 4. Restart container
docker restart survey_pemda_python_app
```

### Problem: User not found

**Cause**: Username tidak ada di Survey Pemda database

**Solution**:
```bash
# Check user exists
docker exec -it survey_pemda_python_app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(username='prakom@admin.com').exists())
"

# If False, create user or sync from ESIMPEG
```

### Problem: Webhook tidak terkirim

**Cause**: Cron job belum setup di ESIMPEG

**Solution**:
```bash
# Setup cron di ESIMPEG (lihat doc 29_PASSWORD_SYNC_QUICKSTART.md)
# Atau trigger manual:
docker exec -it esimpeg_python_app python manage.py sync_password_to_apps
```

---

## Files Changed

### New Files
1. `apps/accounts/webhooks.py` - Webhook handler
2. `register_webhook.py` - Registration script
3. `docs_dari_sonnet/38_PASSWORD_SYNC_SETUP.md` - This doc

### Modified Files
1. `apps/accounts/urls.py` - Added webhook URL
2. `.env` - Added ESIMPEG_WEBHOOK_SECRET

---

## Next Steps

1. ✅ Webhook endpoint implemented
2. ⏳ Register webhook ke ESIMPEG
3. ⏳ Update .env dengan secret key
4. ⏳ Test end-to-end
5. ⏳ Setup monitoring

---

## Related Docs

- `projects/ESIMPEG-Python/docs_dari_sonnet/29_PASSWORD_SYNC_QUICKSTART.md` - ESIMPEG side setup
- `projects/survey_pemda_python/docs_dari_sonnet/37_SESSION_SUMMARY_ESIMPEG_INTEGRATION.md` - Integration overview

---

**Last Updated**: 2026-03-31  
**Status**: ✅ Implemented, ready for testing
