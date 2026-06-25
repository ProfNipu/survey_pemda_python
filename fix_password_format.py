#!/usr/bin/env python
"""
Fix password format: Add Django hasher prefix to Laravel bcrypt passwords
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("Fixing password format for all users...")
print("=" * 60)

users = User.objects.all()
updated = 0
skipped = 0

for user in users:
    # Check if password is raw Laravel format (starts with $2y$ or $2b$)
    if user.password.startswith(('$2y$', '$2b$', '$2a$')):
        # Add laravel_bcrypt prefix
        old_password = user.password
        user.password = f"laravel_bcrypt${user.password}"
        user.save(update_fields=['password'])
        
        print(f"✅ Updated: {user.username}")
        print(f"   Old: {old_password[:30]}...")
        print(f"   New: {user.password[:45]}...")
        print()
        updated += 1
    else:
        print(f"⏭️  Skipped: {user.username} (already has prefix)")
        skipped += 1

print("=" * 60)
print(f"✅ Updated: {updated} users")
print(f"⏭️  Skipped: {skipped} users")
print(f"Total: {users.count()} users")
