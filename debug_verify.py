#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth import get_user_model
import bcrypt

User = get_user_model()
user = User.objects.get(username='199411192019031001')
password = 'Pegawai@Pessel'

print("=" * 60)
print(f"User: {user.name}")
print(f"Password hash: {user.password}")
print()

# Test 1: Identify hasher
hasher = identify_hasher(user.password)
print(f"Hasher identified: {hasher.algorithm}")
print(f"Hasher class: {hasher.__class__.__name__}")
print()

# Test 2: Extract encoded part (after algorithm prefix)
encoded = user.password
if '$' in encoded:
    parts = encoded.split('$', 1)
    algorithm = parts[0]
    encoded_part = parts[1] if len(parts) > 1 else encoded
    
    print(f"Algorithm: {algorithm}")
    print(f"Encoded part: {encoded_part[:50]}...")
    print()

# Test 3: Manual bcrypt verify
print("Manual bcrypt verify:")
hash_2b = encoded_part.replace('$2y$', '$2b$')
try:
    result = bcrypt.checkpw(password.encode('utf-8'), hash_2b.encode('utf-8'))
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 4: Hasher verify
print("Hasher verify:")
try:
    result = hasher.verify(password, user.password)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
