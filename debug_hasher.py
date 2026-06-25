#!/usr/bin/env python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='199411192019031001')

print(f"Password hash: {user.password}")
print()

try:
    hasher = identify_hasher(user.password)
    print(f"Identified hasher: {hasher.algorithm}")
    print(f"Hasher class: {hasher.__class__.__name__}")
except Exception as e:
    print(f"ERROR identifying hasher: {e}")
    print()
    print("This means password format is not recognized by Django!")
    print("Password needs to be in format: algorithm$data")
    print(f"Current format: {user.password[:30]}...")
