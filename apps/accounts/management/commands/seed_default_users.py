from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Seed two default users: Super Admin and Regular Pegawai (idempotent)'

    def handle(self, *args, **options):
        U = get_user_model()

        def ensure_user(username, password, name, email=None):
            obj, created = U.objects.get_or_create(username=username, defaults={'name': name, 'email': email})
            updated = False
            if not created:
                if obj.name != name:
                    obj.name = name
                    updated = True
                if email and obj.email != email:
                    obj.email = email
                    updated = True
            obj.set_password(password)
            obj.save()
            state = 'created' if created else ('updated' if updated else 'exists')
            self.stdout.write(f"  ✓ {username} -> {state}")
            return obj

        # Super Admin
        admin_user = ensure_user(
            username='Prakom@admin2025.com',
            password='Prakom@2025',
            name='Prakom Admin',
            email='Prakom@admin2025.com',
        )
        group, _ = Group.objects.get_or_create(name='Super Admin')
        admin_user.groups.add(group)
        self.stdout.write("  ✓ Added Super Admin group to Prakom@admin2025.com")

        # Regular Pegawai
        ensure_user(
            username='199411192019031001',
            password='Pegawai@Pessel',
            name='Pegawai Biasa',
            email=None,
        )

        self.stdout.write(self.style.SUCCESS('✅ Default users seeding completed.'))
