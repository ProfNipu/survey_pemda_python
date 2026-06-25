# Test Scripts Collection - Survey Pemda Python

Kumpulan test scripts untuk testing berbagai functionality di Survey Pemda Python.

---

## 1. Test Password Change

**Deskripsi**: Test untuk verify password change functionality via ESIMPEG API

**File Original**: `test_password_change.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Test script untuk verify password change functionality
Tests:
1. Login via ESIMPEG API
2. Change password via ESIMPEG API
3. Verify old password no longer works
4. Login with new password
"""

import requests
import json

# Configuration
ESIMPEG_API_URL = "http://172.18.0.6:8000"
TEST_USERNAME = "199107202025212002"
OLD_PASSWORD = "Pegawai@Pessel"
NEW_PASSWORD = "NewPassword123!"

def test_login(username, password):
    """Test login and return token"""
    print(f"\n{'='*60}")
    print(f"Testing login: {username}")
    print(f"{'='*60}")
    
    url = f"{ESIMPEG_API_URL}/apisimpeg/5.0/auth/login"
    
    response = requests.post(
        url,
        json={
            'username': username,
            'password': password
        },
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            token = data['data']['access_token']
            print(f"\n✅ Login successful!")
            print(f"Token: {token[:50]}...")
            return token
    
    print(f"\n❌ Login failed!")
    return None


def test_change_password(token, old_password, new_password):
    """Test change password via API"""
    print(f"\n{'='*60}")
    print(f"Testing change password")
    print(f"{'='*60}")
    
    url = f"{ESIMPEG_API_URL}/apisimpeg/5.0/auth/change-password"
    
    response = requests.post(
        url,
        json={
            'old_password': old_password,
            'new_password': new_password,
            'confirm_password': new_password
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            print(f"\n✅ Password change successful!")
            return True
    
    print(f"\n❌ Password change failed!")
    return False


def main():
    print("\n" + "="*60)
    print("PASSWORD CHANGE TEST SCRIPT")
    print("="*60)
    print(f"ESIMPEG API: {ESIMPEG_API_URL}")
    print(f"Test User: {TEST_USERNAME}")
    print(f"Old Password: {OLD_PASSWORD}")
    print(f"New Password: {NEW_PASSWORD}")
    
    # Step 1: Login with old password
    print("\n\n[STEP 1] Login with OLD password")
    token = test_login(TEST_USERNAME, OLD_PASSWORD)
    
    if not token:
        print("\n❌ FAILED: Cannot login with old password")
        print("Please reset password to 'Pegawai@Pessel' first")
        return
    
    # Step 2: Change password
    print("\n\n[STEP 2] Change password via API")
    success = test_change_password(token, OLD_PASSWORD, NEW_PASSWORD)
    
    if not success:
        print("\n❌ FAILED: Cannot change password")
        return
    
    # Step 3: Try login with old password (should fail)
    print("\n\n[STEP 3] Try login with OLD password (should fail)")
    token_old = test_login(TEST_USERNAME, OLD_PASSWORD)
    
    if token_old:
        print("\n❌ FAILED: Old password still works!")
        return
    else:
        print("\n✅ PASSED: Old password no longer works")
    
    # Step 4: Login with new password (should succeed)
    print("\n\n[STEP 4] Login with NEW password (should succeed)")
    token_new = test_login(TEST_USERNAME, NEW_PASSWORD)
    
    if not token_new:
        print("\n❌ FAILED: Cannot login with new password")
        return
    else:
        print("\n✅ PASSED: New password works!")
    
    # Step 5: Change password back to default (need new token first)
    print("\n\n[STEP 5] Change password back to default")
    token_fresh = test_login(TEST_USERNAME, NEW_PASSWORD)
    if token_fresh:
        success = test_change_password(token_fresh, NEW_PASSWORD, OLD_PASSWORD)
        
        if success:
            print("\n✅ PASSED: Password reset to default")
        else:
            print("\n⚠️  WARNING: Could not reset password to default")
    else:
        print("\n⚠️  WARNING: Could not get fresh token to reset password")
    
    # Final summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ All tests passed!")
    print("Password change functionality is working correctly.")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
```

**Cara Pakai**:
```bash
# Reset password dulu
docker exec -i esimpeg_python_app python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='199107202025212002')
user.set_password('Pegawai@Pessel')
user.save()
print("Password reset to default")
EOF

# Jalankan test
cd projects/survey_pemda_python
python3 -c "$(cat docs_dari_sonnet/TEST_SCRIPTS_COLLECTION.md | sed -n '/^```python/,/^```/p' | sed '1d;$d')"
```

---

## 2. Test ESIMPEG API Login

**Deskripsi**: Test login via ESIMPEG API v5.0

**File Original**: `test_esimpeg_api_login.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Test ESIMPEG API Login v5.0
"""
import requests
import json

ESIMPEG_API_URL = "http://172.18.0.6:8000"

def test_login(username, password):
    """Test login via ESIMPEG API"""
    print(f"\n{'='*60}")
    print(f"Testing ESIMPEG API Login")
    print(f"{'='*60}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
    url = f"{ESIMPEG_API_URL}/apisimpeg/5.0/auth/login"
    
    try:
        response = requests.post(
            url,
            json={
                'username': username,
                'password': password
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("\n✅ Login successful!")
                return data['data']
        
        print("\n❌ Login failed!")
        return None
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

if __name__ == '__main__':
    # Test dengan user yang ada
    result = test_login('199107202025212002', 'Pegawai@Pessel')
    
    if result:
        print("\n" + "="*60)
        print("LOGIN SUCCESS")
        print("="*60)
        print(f"User ID: {result['user']['user_id']}")
        print(f"Username: {result['user']['username']}")
        print(f"Name: {result['user']['name']}")
        print(f"Token: {result['access_token'][:50]}...")
```

---

## 3. Test Web Login

**Deskripsi**: Test login via web form (Survey Pemda)

**File Original**: `test_web_login.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Test Web Login - Survey Pemda Python
"""
import requests

SURVEY_URL = "http://localhost:8001"

def test_web_login(username, password):
    """Test login via web form"""
    print(f"\n{'='*60}")
    print(f"Testing Web Login")
    print(f"{'='*60}")
    print(f"Username: {username}")
    
    session = requests.Session()
    
    # Get CSRF token
    response = session.get(f"{SURVEY_URL}/")
    
    # Login
    response = session.post(
        f"{SURVEY_URL}/",
        data={
            'username': username,
            'password': password,
        },
        allow_redirects=False
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 302:
        print("✅ Login successful! (Redirected)")
        return True
    else:
        print("❌ Login failed!")
        return False

if __name__ == '__main__':
    test_web_login('199107202025212002', 'Pegawai@Pessel')
```

---

## 4. Test API Connection

**Deskripsi**: Test koneksi ke ESIMPEG API

**File Original**: `test_api_connection.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Test ESIMPEG API Connection
"""
import requests

ESIMPEG_API_URL = "http://172.18.0.6:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{ESIMPEG_API_URL}/health/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test login endpoint"""
    print("\nTesting login endpoint...")
    try:
        response = requests.post(
            f"{ESIMPEG_API_URL}/apisimpeg/5.0/auth/login",
            json={'username': 'test', 'password': 'test'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("ESIMPEG API CONNECTION TEST")
    print("="*60)
    
    health_ok = test_health()
    login_ok = test_login()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Health: {'✅' if health_ok else '❌'}")
    print(f"Login: {'✅' if login_ok else '❌'}")
```

---

## 5. Test ESIMPEG Connection

**Deskripsi**: Test koneksi dari Survey Pemda ke ESIMPEG

**File Original**: `test_esimpeg_connection.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Test ESIMPEG Connection from Survey Pemda
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.services import EsimpegAPIService

def test_connection():
    """Test connection to ESIMPEG API"""
    print("="*60)
    print("ESIMPEG CONNECTION TEST")
    print("="*60)
    
    api_service = EsimpegAPIService()
    
    print(f"\nESIMPEG API URL: {api_service.base_url}")
    print(f"Timeout: {api_service.timeout}s")
    
    # Test login
    print("\n[TEST 1] Login Test")
    result = api_service.login('199107202025212002', 'Pegawai@Pessel')
    
    if result:
        print("✅ Login successful!")
        print(f"Token: {result['access_token'][:50]}...")
        
        # Test get pegawai list
        print("\n[TEST 2] Get Pegawai List")
        pegawai = api_service.get_pegawai_list(result['access_token'], page=1, per_page=10)
        
        if pegawai:
            print(f"✅ Got {len(pegawai.get('items', []))} pegawai")
        else:
            print("❌ Failed to get pegawai list")
    else:
        print("❌ Login failed!")

if __name__ == '__main__':
    test_connection()
```

---

## 6. Check Password Sync Status

**Deskripsi**: Check status password sync antara Survey Pemda dan ESIMPEG

**File Original**: `check_password_sync_status.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Check Password Sync Status
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.services import EsimpegAPIService

User = get_user_model()

def check_sync_status():
    """Check password sync status"""
    print("="*60)
    print("PASSWORD SYNC STATUS CHECK")
    print("="*60)
    
    # Get sample users
    users = User.objects.all()[:5]
    
    api_service = EsimpegAPIService()
    
    for user in users:
        print(f"\n[User: {user.username}]")
        print(f"Name: {user.name}")
        
        # Try login with default password
        result = api_service.login(user.username, 'Pegawai@Pessel')
        
        if result:
            print("✅ Can login with default password")
        else:
            print("❌ Cannot login with default password")

if __name__ == '__main__':
    check_sync_status()
```

---

## 7. Register Webhook

**Deskripsi**: Register webhook untuk password sync

**File Original**: `register_webhook.py`

**Script**:
```python
#!/usr/bin/env python3
"""
Register Webhook for Password Sync
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.services import EsimpegAPIService
from django.conf import settings

def register_webhook():
    """Register webhook to ESIMPEG"""
    print("="*60)
    print("REGISTER WEBHOOK")
    print("="*60)
    
    api_service = EsimpegAPIService()
    
    # Login as admin
    print("\n[STEP 1] Login as admin...")
    result = api_service.login('prakom@admin.com', 'admin123')
    
    if not result:
        print("❌ Login failed!")
        return
    
    token = result['access_token']
    print("✅ Login successful!")
    
    # Register webhook
    print("\n[STEP 2] Register webhook...")
    webhook_url = f"{settings.BASE_URL}/webhooks/password-sync/"
    
    print(f"Webhook URL: {webhook_url}")
    print(f"Event: user.password_changed")
    
    # TODO: Implement webhook registration API call
    print("⚠️  Webhook registration not implemented yet")

if __name__ == '__main__':
    register_webhook()
```

---

## Catatan Penggunaan

Semua script di atas sudah didokumentasikan di sini. File .py original sudah dihapus untuk menjaga kebersihan project.

Jika ingin menjalankan script, copy code dari dokumentasi ini dan jalankan dengan:
```bash
python3 -c "$(cat script_code_here)"
```

Atau buat file temporary:
```bash
# Contoh untuk test password change
cat > /tmp/test.py << 'EOF'
# paste script code here
EOF

python3 /tmp/test.py
rm /tmp/test.py
```

## Related Documentation

- [88_FIX_PASSWORD_CHANGE_COMPLETE.md](./88_FIX_PASSWORD_CHANGE_COMPLETE.md) - Password change fix
- [86_LOGIN_VIA_ESIMPEG_API_SUCCESS.md](./86_LOGIN_VIA_ESIMPEG_API_SUCCESS.md) - Login via API
- [85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md](./85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md) - Authentication backend
