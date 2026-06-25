"""
Auto-seed core data when database is empty.
- Seeds permission modules, controls, functions, and rules
- Seeds menu items (base + extend)
- Seeds admin access rules and sidebar link
- Seeds default users (Super Admin + Pegawai biasa)

Run: python manage.py auto_seed
Idempotent: safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.manajemen.models import MenuItem, PermissionModule


class Command(BaseCommand):
    help = 'Auto seed core data when empty (permissions, menus, admin access)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Run idempotent seeders to sync core data even if DB is not empty.',
        )
        parser.add_argument(
            '--permissions-only',
            action='store_true',
            help='Only run permission-related seeders (skip menus/users/import). Useful for deploy updates.',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🧩 AUTO SEED CHECK'))
        self.stdout.write('=' * 70)

        sync = bool(options.get('sync'))
        permissions_only = bool(options.get('permissions_only'))

        menu_empty = MenuItem.objects.count() == 0
        module_empty = PermissionModule.objects.count() == 0

        if permissions_only and not sync:
            raise CommandError('--permissions-only requires --sync')

        if not sync and not (menu_empty or module_empty):
            self.stdout.write('Database already has core data. Skipping auto-seed.')
            return

        if sync:
            self.stdout.write('Sync mode enabled. Running idempotent seeders...')
        else:
            self.stdout.write('Database looks empty. Running seeders...')

        # ---- PERMISSIONS (idempotent) ----
        # Base permissions (modules/controls/functions/rules)
        call_command('seed_permissions')
        # Core permission management pages
        call_command('seed_permission_management_core')
        # Menu management + API/AJAX documentation permissions (minimal instance needs these)
        call_command('seed_permission_manajemen_menu')
        call_command('seed_permission_api_documentation')

        if permissions_only:
            self.stdout.write(self.style.SUCCESS('✅ Permission sync completed'))
            return

        # ---- MENUS / USERS (only meaningful for initial setup, but safe to re-run if written idempotently) ----
        call_command('seed_menu_categories')
        call_command('seed_menus')
        call_command('seed_menus_extend')
        call_command('seed_admin_access')
        call_command('seed_default_users')

        self.stdout.write(self.style.SUCCESS('✅ Auto-seed completed'))
