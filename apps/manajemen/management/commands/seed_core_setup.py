"""Seed core data for permissions + sidebar.

This command is intended to be repeatable (idempotent) and used for new deployments
where the dataset/instansi may differ but the seeding method is the same.

It composes existing seeders in the correct order:
- seed_permissions
- seed_permission_management_core
- seed_permission_manajemen_menu
- seed_menu_categories
- seed_menus
- seed_menus_extend
- seed_admin_access

Usage:
  python manage.py seed_core_setup
  python manage.py seed_core_setup --force

Notes:
- It does not delete data by default.
- With --force it will re-run seeders but still uses get_or_create patterns.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed core permissions + sidebar menus (composed seeding)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-run (still idempotent, does not purge by default).',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Core Setup (Permissions + Sidebar)'))
        self.stdout.write('=' * 70)

        # Core permissions
        call_command('seed_permissions')

        # Granular permission management pages under module "pengaturan"
        call_command('seed_permission_management_core')

        # Manajemen Menu & Kategori under module "pengaturan"
        call_command('seed_permission_manajemen_menu')

        # API Documentation (read-only) under module "pengaturan"
        call_command('seed_permission_api_documentation')

        # Sidebar categories (optional feature)
        call_command('seed_menu_categories')

        # Sidebar items
        call_command('seed_menus')
        call_command('seed_menus_extend')

        # Admin access rules and admin sidebar link
        call_command('seed_admin_access')

        self.stdout.write(self.style.SUCCESS('✅ seed_core_setup completed'))
