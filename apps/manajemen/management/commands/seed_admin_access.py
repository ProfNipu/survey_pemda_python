"""
Seed admin access rules and menu link for Django Admin.
- Creates PermissionRule(s) for keys in settings.ADMIN_ACCESS_PERMISSION_KEYS
- Assigns those rules to Group 'Super Admin' via RoleRule
- Adds SUPER ADMIN menu item 'Manajemen Menu' linking to /admin/manajemen_aplikasi/menuitem/

Usage:
    python manage.py seed_admin_access
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group

from apps.manajemen.models import (
    PermissionModule,
    PermissionControl,
    PermissionFunction,
    PermissionRule,
    RoleRule,
    MenuItem,
)


class Command(BaseCommand):
    help = 'Seed admin access rules and sidebar menu link for Django Admin'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Admin Access Rules & Menu Link'))
        self.stdout.write('=' * 70)

        keys = getattr(settings, 'ADMIN_ACCESS_PERMISSION_KEYS', [
            'pengaturan.manajemen_user.view',
            'pengaturan.manajemen_permission.view',
        ])

        # Ensure group exists
        group, _ = Group.objects.get_or_create(name='Super Admin')

        created_rules = 0
        created_assignments = 0

        for key in keys:
            parts = [p.strip() for p in key.split('.') if p.strip()]
            if len(parts) < 2:
                self.stdout.write(self.style.WARNING(f'- Skip invalid key: {key}'))
                continue
            module_name = parts[0]
            control_name = parts[1]
            function_name = parts[2] if len(parts) >= 3 else 'view'

            # Ensure module, control, function
            module, _ = PermissionModule.objects.get_or_create(
                nama_module=module_name,
                defaults={
                    'label_module': module_name.title(),
                    'deskripsi_module': f'Module {module_name}',
                    'icon': 'fas fa-cogs',
                    'order': 99,
                }
            )

            control, _ = PermissionControl.objects.get_or_create(
                nama_kontrol=control_name,
                defaults={
                    'label_kontrol': control_name.replace('_', ' ').title(),
                    'deskripsi_kontrol': f'Kontrol {control_name}',
                }
            )

            func, _ = PermissionFunction.objects.get_or_create(
                nama_fungsi=function_name,
                defaults={
                    'label_fungsi': function_name.title(),
                    'deskripsi_fungsi': f'Aksi {function_name}',
                }
            )

            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control,
                function=func,
            )
            created_rules += int(created)

            rr, assigned = RoleRule.objects.get_or_create(
                role=group,
                rule=rule,
            )
            created_assignments += int(assigned)

        self.stdout.write(f'  ✓ Rules created: {created_rules}')
        self.stdout.write(f'  ✓ Assignments created: {created_assignments}')

        def _dedupe_root_by_name(name: str):
            qs = MenuItem.objects.filter(name=name, parent__isnull=True).order_by('id')
            obj = qs.first()
            if not obj:
                return None
            dups = qs.exclude(id=obj.id)
            if dups.exists():
                dups.update(is_active=False)
            return obj

        # Canonical root group is "Pengaturan Aplikasi".
        # Older seeders used "Manajemen Aplikasi"; rename it if present to avoid duplicates.
        legacy_root = MenuItem.objects.filter(name='Manajemen Aplikasi', parent__isnull=True).order_by('id').first()
        if legacy_root:
            legacy_root.name = 'Pengaturan Aplikasi'
            legacy_root.save(update_fields=['name'])

        parent = _dedupe_root_by_name('Pengaturan Aplikasi')
        if not parent:
            parent = MenuItem.objects.create(
                name='Pengaturan Aplikasi',
                parent=None,
                permission_key=None,
                url_name=None,
                external_url=None,
                icon='fas fa-cogs',
                type='menuItem',
                order=1,
                category=1,
                is_active=True,
            )

        # Use the first admin access key for visibility of this link
        perm_key = keys[0] if keys else 'pengaturan.manajemen_permission.view'

        child, created = MenuItem.objects.get_or_create(
            name='Manajemen Menu',
            parent=parent,
            defaults={
                'permission_key': perm_key,
                'url_name': 'manajemen_aplikasi:menu_list',
                'external_url': None,
                'icon': 'fas fa-sitemap',
                'type': 'module',
                'order': 4,
                'category': 1,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write('  ✓ Created sidebar item: Manajemen Menu')
        else:
            # Ensure external_url and perm are updated if exists without them
            updated = False
            # Migrate to custom UI url_name
            if child.url_name != 'manajemen_aplikasi:menu_list':
                child.url_name = 'manajemen_aplikasi:menu_list'
                updated = True
            if child.external_url:
                child.external_url = None
                updated = True
            if child.permission_key != perm_key:
                child.permission_key = perm_key
                updated = True
            if updated:
                child.save()
                self.stdout.write('  ✓ Updated sidebar item: Manajemen Menu')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Admin access seeding completed!'))
