"""
Seed extended MenuItem data to mirror common static sidebar items.
Run: python manage.py seed_menus_extend
"""
from django.core.management.base import BaseCommand
from apps.manajemen.models import MenuItem


class Command(BaseCommand):
    help = 'Seed extended MenuItem records (SUPER ADMIN + Akun Saya)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Extended Menu Items'))
        self.stdout.write('=' * 70)

        created_count = 0

        def _dedupe_root_by_name(name: str):
            qs = MenuItem.objects.filter(name=name, parent__isnull=True).order_by('id')
            obj = qs.first()
            if not obj:
                return None
            dups = qs.exclude(id=obj.id)
            if dups.exists():
                dups.update(is_active=False)
            return obj

        # SUPER ADMIN group (category 1)
        existing_group = MenuItem.objects.filter(name='Manajemen Aplikasi', parent__isnull=True).first()
        if existing_group:
            existing_group.name = 'Pengaturan Aplikasi'
            existing_group.save(update_fields=['name'])

        super_admin_group = _dedupe_root_by_name('Pengaturan Aplikasi')
        if super_admin_group:
            created = False
        else:
            super_admin_group = MenuItem.objects.create(
                name='Pengaturan Aplikasi',
                type='menuItem',
                icon='fas fa-cogs',
                order=1,
                category=1,
                is_active=True,
            )
            created = True
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Pengaturan Aplikasi (group)')

        # Children under SUPER ADMIN
        items_super_admin = [
            {
                'name': 'Manajemen Akses Granular',
                'permission_key': 'pengaturan.manajemen_permission.view',
                'url_name': 'manajemen_aplikasi:dashboard',
                'icon': 'fas fa-shield-alt',
                'order': 1,
            },
            {
                'name': 'Manajemen Menu',
                'permission_key': 'pengaturan.manajemen_menu.view',
                'url_name': 'manajemen_aplikasi:menu_list',
                'icon': 'fas fa-sitemap',
                'order': 2,
            },
            {
                'name': 'Dokumentasi API',
                'permission_key': 'pengaturan.api_documentation.view',
                'url_name': 'manajemen_aplikasi:api_documentation_list',
                'icon': 'fas fa-book',
                'order': 3,
            },
            {
                'name': 'Dokumentasi AJAX',
                'permission_key': 'pengaturan.api_documentation.view',
                'url_name': 'manajemen_aplikasi:ajax_documentation_list',
                'icon': 'fas fa-bolt',
                'order': 4,
            },
            {
                'name': 'Manajemen Fungsi',
                'permission_key': 'pengaturan.permission_function.view',
                'url_name': 'manajemen_aplikasi:function_list',
                'icon': 'fas fa-bolt',
                'order': 5,
            },
            {
                'name': 'Manajemen Kontrol',
                'permission_key': 'pengaturan.permission_control.view',
                'url_name': 'manajemen_aplikasi:control_list',
                'icon': 'fas fa-database',
                'order': 6,
            },
            {
                'name': 'Manajemen Module',
                'permission_key': 'pengaturan.permission_module.view',
                'url_name': 'manajemen_aplikasi:module_list',
                'icon': 'fas fa-th-large',
                'order': 7,
            },
            {
                'name': 'Manajemen Rules',
                'permission_key': 'pengaturan.permission_rule.view',
                'url_name': 'manajemen_aplikasi:rule_list',
                'icon': 'fas fa-gavel',
                'order': 8,
            },
            {
                'name': 'Manajemen Role',
                'permission_key': 'pengaturan.permission_role.view',
                'url_name': 'manajemen_aplikasi:roles_list',
                'icon': 'fas fa-user-tag',
                'order': 9,
            },
            {
                'name': 'Manajemen User',
                'permission_key': 'pengaturan.permission_user.view',
                'url_name': 'manajemen_aplikasi:users_list',
                'icon': 'fas fa-users-cog',
                'order': 10,
            },
        ]

        for data in items_super_admin:
            obj, created = MenuItem.objects.get_or_create(
                name=data['name'],
                parent=super_admin_group,
                defaults={
                    'permission_key': data['permission_key'],
                    'url_name': data['url_name'],
                    'icon': data['icon'],
                    'type': 'module',
                    'order': data['order'],
                    'category': 1,
                    'is_active': True,
                }
            )
            created_count += int(created)
            if created:
                self.stdout.write(f"  ✓ Created: {data['name']}")
            else:
                changed = False
                if obj.permission_key != data['permission_key']:
                    obj.permission_key = data['permission_key']
                    changed = True
                if obj.url_name != data['url_name']:
                    obj.url_name = data['url_name']
                    changed = True
                if obj.icon != data['icon']:
                    obj.icon = data['icon']
                    changed = True
                if obj.type != 'module':
                    obj.type = 'module'
                    changed = True
                if (obj.order or 0) != data['order']:
                    obj.order = data['order']
                    changed = True
                if (obj.category or 0) != 1:
                    obj.category = 1
                    changed = True
                if obj.parent_id != super_admin_group.id:
                    obj.parent = super_admin_group
                    changed = True
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save()
                    self.stdout.write(f"  ✓ Updated: {data['name']}")

        # AKUN SAYA (we place under category 0: Menu Lainnya)
        akun_group = _dedupe_root_by_name('Akun Saya')
        if akun_group:
            created = False
        else:
            akun_group = MenuItem.objects.create(
                name='Akun Saya',
                type='menuItem',
                icon='fas fa-user-circle',
                order=99,
                category=0,
                is_active=True,
            )
            created = True
        created_count += int(created)
        if created:
            self.stdout.write('  ✓ Created: Akun Saya (group)')

        items_akun = [
            {
                'name': 'Pengaturan Akun',
                'url_name': 'accounts:profile',
                'icon': 'fas fa-user-circle',
                'order': 1,
            },
            {
                'name': 'Ganti Password',
                'url_name': 'accounts:change_password',
                'icon': 'fas fa-key',
                'order': 2,
            },
        ]

        for data in items_akun:
            obj, created = MenuItem.objects.get_or_create(
                name=data['name'],
                parent=akun_group,
                defaults={
                    'permission_key': None,  # always visible for logged-in users
                    'url_name': data['url_name'],
                    'icon': data['icon'],
                    'type': 'module',
                    'order': data['order'],
                    'category': 0,
                    'is_active': True,
                }
            )
            created_count += int(created)
            if created:
                self.stdout.write(f"  ✓ Created: {data['name']}")
            else:
                # Ensure existing item matches desired config (especially url_name)
                changed = False
                if obj.url_name != data['url_name']:
                    obj.url_name = data['url_name']
                    changed = True
                if obj.icon != data['icon']:
                    obj.icon = data['icon']
                    changed = True
                if obj.order != data['order']:
                    obj.order = data['order']
                    changed = True
                if obj.category != 0:
                    obj.category = 0
                    changed = True
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save()
                    self.stdout.write(f"  ✓ Updated: {data['name']}")

        # Ensure only ONE canonical Logout item exists (dedupe & standardize)
        try:
            logout_qs = MenuItem.objects.filter(name='Logout')
            if not logout_qs.exists():
                top_logout = MenuItem.objects.create(
                    name='Logout',
                    parent=None,
                    permission_key=None,
                    url_name='accounts:logout',
                    icon='fas fa-sign-out-alt',
                    type='module',
                    order=100,
                    category=0,
                    is_active=True,
                )
                created_count += 1
                self.stdout.write('  ✓ Created: Logout (root)')
            else:
                # Prefer a root item as canonical, else first
                top_logout = logout_qs.filter(parent=None).first() or logout_qs.first()
                updated = False
                if top_logout.parent_id:
                    top_logout.parent = None
                    updated = True
                if top_logout.url_name != 'accounts:logout':
                    top_logout.url_name = 'accounts:logout'
                    updated = True
                if top_logout.icon != 'fas fa-sign-out-alt':
                    top_logout.icon = 'fas fa-sign-out-alt'
                    updated = True
                if (top_logout.order or 0) != 100:
                    top_logout.order = 100
                    updated = True
                if (top_logout.category or 0) != 0:
                    top_logout.category = 0
                    updated = True
                if not top_logout.is_active:
                    top_logout.is_active = True
                    updated = True
                if updated:
                    top_logout.save()
                    self.stdout.write('  ✓ Updated: Logout (canonical)')

                # Deactivate duplicates
                duplicates = logout_qs.exclude(pk=top_logout.pk)
                deactivated = 0
                for dup in duplicates:
                    if dup.is_active or dup.parent_id is not None:
                        dup.is_active = False
                        dup.parent = None  # normalize location
                        dup.save(update_fields=['is_active', 'parent'])
                        deactivated += 1
                if deactivated:
                    self.stdout.write(f'  ✓ Deactivated duplicates: {deactivated}')
        except Exception:
            pass

        # Deactivate legacy 'Profile' menu item if present
        try:
            deactivated = MenuItem.objects.filter(name='Profile', url_name='accounts:profile').update(is_active=False)
            if deactivated:
                self.stdout.write('  ✓ Deactivated legacy Profile menu')
        except Exception:
            pass

        # Rename legacy 'Profile Saya' to 'Pengaturan Akun' if present
        try:
            legacy = MenuItem.objects.filter(name='Profile Saya', parent=akun_group).first()
            if legacy:
                legacy.name = 'Pengaturan Akun'
                legacy.url_name = 'accounts:profile'
                legacy.is_active = True
                legacy.save()
                self.stdout.write('  ✓ Renamed "Profile Saya" to "Pengaturan Akun"')
        except Exception:
            pass

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Extended menu seeding completed! Created: {created_count}'))
