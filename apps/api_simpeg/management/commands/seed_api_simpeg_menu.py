"""
Management command untuk seed menu API SIMPEG
"""
from django.core.management.base import BaseCommand
from apps.manajemen.models import MenuCategory, MenuItem


class Command(BaseCommand):
    help = 'Seed menu untuk API SIMPEG (Pegawai)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('Seeding API SIMPEG Menu')
        self.stdout.write('=' * 70)

        # 1. Get or create category "Manajemen Integrasi"
        category, created = MenuCategory.objects.get_or_create(
            code=4,
            defaults={
                'name': 'Manajemen Integrasi',
                'icon': 'fa-solid fa-plug',
                'order': 4,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))
        else:
            self.stdout.write(f'  Category already exists: {category.name}')

        # 2. Create parent menu "ESIMPEG"
        parent_menu, created = MenuItem.objects.get_or_create(
            category=category.code,
            name='ESIMPEG',
            parent=None,
            defaults={
                'external_url': '#',
                'icon': 'fa-solid fa-users',
                'order': 1,
                'is_active': True,
                'type': 'module'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created parent menu: {parent_menu.name}'))
        else:
            self.stdout.write(f'  Parent menu already exists: {parent_menu.name}')

        # 3. Create child menu "Pegawai"
        child_menu, created = MenuItem.objects.get_or_create(
            category=category.code,
            name='Pegawai',
            parent=parent_menu,
            defaults={
                'external_url': '/api-simpeg/pegawai/',
                'icon': 'fa-solid fa-user-tie',
                'order': 1,
                'is_active': True,
                'type': 'menu'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created child menu: {child_menu.name}'))
        else:
            self.stdout.write(f'  Child menu already exists: {child_menu.name}')

        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('✓ API SIMPEG Menu Seeding Complete'))
        self.stdout.write('=' * 70)
        self.stdout.write('')
        self.stdout.write('Menu structure:')
        self.stdout.write(f'  Category: {category.name} (code {category.code})')
        self.stdout.write(f'  └─ Parent: {parent_menu.name}')
        self.stdout.write(f'     └─ Child: {child_menu.name} → {child_menu.external_url}')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Run: docker exec survey_pemda_python_app python manage.py seed_api_simpeg_permissions')
        self.stdout.write('  2. Run: docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access')
        self.stdout.write('  3. Restart: docker restart survey_pemda_python_app')
        self.stdout.write('  4. Access: http://localhost:8006/api-simpeg/pegawai/')
        self.stdout.write('')
