# Password Migration Guide - Laravel Hash ke Universal Hash

## Overview

Aplikasi ESIMPEG-Python telah **diupgrade** dari Laravel-specific password hash ke **universal password hashing** menggunakan **Argon2** (recommended by OWASP).

## Apa yang Berubah?

### SEBELUM (Laravel-dependent)
```
Password Hash: laravel_bcrypt$$2b$12$xxx...
Format: Laravel bcrypt format ($2y$)
Dependency: Bergantung dengan Laravel hashing system
```

### SESUDAH (Universal, Independent)
```
Password Hash: argon2$argon2id$v=19$m=102400,t=2,p=8$xxx...
Format: Argon2 (OWASP recommended)
Dependency: TIDAK bergantung dengan Laravel lagi!
```

## Password Hashing Priority

Urutan hasher di `settings.py`:

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',       # ⭐ NEW PASSWORDS
    'django.contrib.auth.hashers.BCryptPasswordHasher',       # Standard bcrypt
    'apps.accounts.hashers.LaravelBcryptPasswordHasher',      # Laravel compatibility (old)
    'apps.accounts.hashers.LaravelCompatibleBcryptHasher',    # Bcrypt fallback
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher', # Django bcrypt
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',       # Django default
]
```

### Cara Kerja:
1. **Password BARU** → Menggunakan `Argon2PasswordHasher` (hasher pertama)
2. **Password LAMA** → Masih bisa verify dengan hasher lainnya (backward compatibility)
3. **Auto-upgrade** → Saat user login, hash akan otomatis upgrade ke Argon2

## Backward Compatibility

✅ **User dengan password lama (Laravel hash) masih bisa login!**

System akan:
1. Verify password dengan Laravel hasher (backward compatibility)
2. Saat user berhasil login, Django akan otomatis upgrade hash ke Argon2
3. Saat user ganti password, langsung pakai Argon2

## Migration Strategy

### Automatic Migration (Recommended)
Password akan otomatis migrate saat:
- User login (auto-upgrade hash)
- User ganti password
- Admin reset password

### Manual Migration (Optional)
Jika ingin migrate semua user sekaligus:

```python
python manage.py shell

from accounts.models import User

# Get all users dengan Laravel hash
users = User.objects.filter(password__startswith='laravel_bcrypt')

for user in users:
    # Force rehash dengan password yang sama (kalau tahu passwordnya)
    # Atau tunggu user login untuk auto-upgrade
    pass
```

**CATATAN:** Manual migration tidak praktis karena password original tidak bisa di-recover dari hash. **Biarkan auto-migrate saat user login.**

## Password Hash Formats

### 1. Argon2 (⭐ RECOMMENDED - NEW DEFAULT)
```
Format: argon2$argon2id$v=19$m=102400,t=2,p=8$[salt]$[hash]
```
**Features:**
- ✅ Winner Password Hashing Competition 2015
- ✅ Most secure (resistant to GPU/ASIC attacks)
- ✅ Recommended by OWASP
- ✅ Modern standard
- ✅ Memory-hard function
- ✅ Configurable time/memory/parallelism cost

**Parameters:**
- `v=19`: Argon2 version
- `m=102400`: Memory cost (100 MB)
- `t=2`: Time cost (iterations)
- `p=8`: Parallelism (threads)

### 2. Bcrypt (Standard)
```
Format: bcrypt$$2b$12$[salt+hash]
```
**Features:**
- ✅ Industry standard
- ✅ Widely supported
- ✅ Cross-platform compatible
- ✅ Proven secure
- ⚠️  Slower than Argon2

### 3. Laravel Bcrypt (OLD - Backward Compatibility Only)
```
Format: laravel_bcrypt$$2b$12$[salt+hash]
```
**Features:**
- ⚠️  Laravel-specific format
- ⚠️  Only used for old passwords
- ⚠️  Will be auto-upgraded when user login
- ❌ Tidak recommended untuk password baru

## Testing Password Hashing

### Test 1: Create User Baru
```python
from accounts.models import User

# Create user dengan password baru
user = User.objects.create_user(
    username='testuser',
    name='Test User',
    password='SecurePassword123!'
)

# Check hash format
print(user.password)
# Output: argon2$argon2id$v=19$m=102400,t=2,p=8$xxx...
```

### Test 2: Verify Backward Compatibility
```python
from accounts.models import User

# User dengan Laravel hash lama
user = User.objects.get(username='old_user')
print(user.password)
# Output: laravel_bcrypt$$2b$12$xxx...

# Password masih bisa verify
result = user.check_password('old_password')
print(result)  # True - backward compatibility OK!
```

### Test 3: Change Password (Auto-upgrade)
```python
from accounts.models import User

user = User.objects.get(username='old_user')
print(user.password[:20])
# Output: laravel_bcrypt$$2b$...

# Ganti password
user.set_password('NewPassword123!')
user.save()

print(user.password[:20])
# Output: argon2$argon2id$...
# ✅ Auto-upgraded to Argon2!
```

## Security Benefits

### Argon2 vs Bcrypt

| Feature | Argon2 | Bcrypt |
|---------|--------|--------|
| **Algorithm** | Memory-hard | CPU-intensive |
| **GPU Resistance** | ✅ Excellent | ⚠️  Moderate |
| **ASIC Resistance** | ✅ Excellent | ⚠️  Moderate |
| **Memory Cost** | Configurable | Fixed |
| **Time Cost** | Configurable | Fixed (rounds) |
| **Parallelism** | Configurable | None |
| **OWASP Recommendation** | ✅ Yes | ✅ Yes |
| **Modern Standard** | ✅ 2015+ | ⚠️  1999 |

### Why Argon2?

1. **Resistant to GPU attacks**
   - Requires large memory (can't parallelize efficiently on GPU)
   - More expensive to crack than bcrypt

2. **Resistant to ASIC attacks**
   - Memory-hard algorithm
   - Custom hardware less effective

3. **Tunable parameters**
   - Memory cost: More memory = harder to crack
   - Time cost: More iterations = slower hashing
   - Parallelism: Use multiple threads

4. **Future-proof**
   - Winner of Password Hashing Competition
   - Actively maintained
   - Industry standard for new applications

## Dependencies

### Required Package
```txt
argon2-cffi==23.1.0
```

Installation:
```bash
pip install argon2-cffi==23.1.0
```

Docker:
```bash
docker exec esimpeg_python_app pip install argon2-cffi==23.1.0
```

## Configuration

### settings.py
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',       # Priority 1
    'django.contrib.auth.hashers.BCryptPasswordHasher',       # Fallback
    'apps.accounts.hashers.LaravelBcryptPasswordHasher',      # Old passwords
]
```

### Custom Argon2 Parameters (Optional)
```python
# In settings.py
ARGON2_TIME_COST = 2        # Iterations (default: 2)
ARGON2_MEMORY_COST = 102400 # Memory in KB (default: 102400 = 100MB)
ARGON2_PARALLELISM = 8      # Threads (default: 8)
```

## Migration Timeline

### Phase 1: Setup (DONE ✅)
- ✅ Install argon2-cffi
- ✅ Update PASSWORD_HASHERS priority
- ✅ Test backward compatibility
- ✅ Test auto-upgrade

### Phase 2: Gradual Migration (ONGOING)
- 🔄 User login → auto-upgrade
- 🔄 User ganti password → auto-upgrade
- 🔄 Admin reset password → auto-upgrade

### Phase 3: Complete Migration (Future)
- Monitoring: Check berapa % user sudah migrate
- Report: Generate migration progress report
- Optional: Force re-login untuk upgrade hash

## Statistics

Check migration progress:
```python
from accounts.models import User

total = User.objects.count()
argon2 = User.objects.filter(password__startswith='argon2').count()
bcrypt = User.objects.filter(password__startswith='bcrypt').count()
laravel = User.objects.filter(password__startswith='laravel_bcrypt').count()

print(f'Total users: {total}')
print(f'Argon2: {argon2} ({argon2/total*100:.1f}%)')
print(f'Bcrypt: {bcrypt} ({bcrypt/total*100:.1f}%)')
print(f'Laravel: {laravel} ({laravel/total*100:.1f}%)')
```

## FAQ

### Q: Apakah user lama masih bisa login?
**A:** ✅ Ya! Backward compatibility dijaga. Laravel hash masih bisa verify.

### Q: Kapan password akan upgrade ke Argon2?
**A:** Otomatis saat user:
- Login (dengan middleware auto-upgrade)
- Ganti password
- Reset password

### Q: Apakah perlu migrate manual?
**A:** ❌ Tidak perlu! Auto-migration lebih aman dan praktis.

### Q: Apakah bisa rollback ke Laravel hash?
**A:** ⚠️  Bisa, tapi tidak recommended. Argon2 lebih secure.

### Q: Bagaimana performance impact?
**A:** Minimal. Argon2 sedikit lebih lambat (milliseconds), tapi jauh lebih secure.

### Q: Apakah compatible dengan Laravel aplikasi lain?
**A:** ⚠️  Password baru (Argon2) TIDAK compatible dengan Laravel (Laravel tidak support Argon2 default). Tapi aplikasi Python ini tidak bergantung Laravel lagi!

### Q: Bagaimana jika mau share user database dengan Laravel?
**A:** Gunakan JWT token untuk komunikasi antar aplikasi. Password hash tidak perlu di-share.

## Conclusion

✅ **Migrasi berhasil!**
- Password baru menggunakan Argon2 (OWASP recommended)
- Backward compatibility terjaga
- Tidak bergantung dengan Laravel lagi
- Auto-upgrade saat user login/change password
- More secure & future-proof

---

**Date:** November 3, 2025  
**Status:** ✅ Active  
**Version:** 1.0
