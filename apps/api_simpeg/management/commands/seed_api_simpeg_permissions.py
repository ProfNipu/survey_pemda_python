"""
Management command untuk seed permissions API SIMPEG
"""
from django.core.management.base import BaseCommand
from apps.manajemen.models import PermissionModule, PermissionControl, PermissionFunction, PermissionRule


class Command(BaseCommand):
    help = 'Seed permissions untuk API SIMPEG (Pegawai)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('Seeding API SIMPEG Permissions')
        self.stdout.write('=' * 70)

        # 1. Create module "api_simpeg"
        module, created = PermissionModule.objects.get_or_create(
            nama_module='api_simpeg',
            defaults={
                'label_module': 'API SIMPEG',
                'deskripsi_module': 'Integrasi dengan API ESIMPEG untuk data pegawai',
                'icon': 'fa-solid fa-plug',
                'order': 4,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created module: {module.label_module}'))
        else:
            self.stdout.write(f'  Module already exists: {module.label_module}')

        # 2. Create control "pegawai"
        control, created = PermissionControl.objects.get_or_create(
            nama_kontrol='pegawai',
            defaults={
                'label_kontrol': 'Pegawai',
                'deskripsi_kontrol': 'Manajemen data pegawai dari ESIMPEG',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created control: {control.label_kontrol}'))
        else:
            self.stdout.write(f'  Control already exists: {control.label_kontrol}')

        # 3. Create functions
        functions_data = [
            {'nama': 'view', 'label': 'View', 'deskripsi': 'Lihat daftar pegawai'},
            {'nama': 'sync', 'label': 'Sync', 'deskripsi': 'Sinkronisasi data pegawai dari ESIMPEG'},
            {'nama': 'export', 'label': 'Export', 'deskripsi': 'Export data pegawai'},
        ]

        functions = []
        for func_data in functions_data:
            func, created = PermissionFunction.objects.get_or_create(
                nama_fungsi=func_data['nama'],
                defaults={
                    'label_fungsi': func_data['label'],
                    'deskripsi_fungsi': func_data['deskripsi'],
                }
            )
            functions.append(func)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created function: {func.label_fungsi}'))
            else:
                self.stdout.write(f'  Function already exists: {func.label_fungsi}')

        # 4. Create permission rules
        rules_created = 0
        rules_existing = 0

        for func in functions:
            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control,
                function=func,
                defaults={
                    'is_active': True
                }
            )
            
            if created:
                rules_created += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created rule: {module.nama_module}.{control.nama_kontrol}.{func.nama_fungsi}'))
            else:
                rules_existing += 1
                self.stdout.write(f'  Rule already exists: {module.nama_module}.{control.nama_kontrol}.{func.nama_fungsi}')

        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('✓ API SIMPEG Permissions Seeding Complete'))
        self.stdout.write('=' * 70)
        self.stdout.write('')
        self.stdout.write('Summary:')
        self.stdout.write(f'  Module: {module.label_module} ({module.nama_module})')
        self.stdout.write(f'  Control: {control.label_kontrol} ({control.nama_kontrol})')
        self.stdout.write(f'  Functions: {len(functions)} (view, sync, export)')
        self.stdout.write(f'  Rules created: {rules_created}')
        self.stdout.write(f'  Rules existing: {rules_existing}')
        self.stdout.write('')
        self.stdout.write('Permission rules:')
        for func in functions:
            rule_code = f'{module.nama_module}.{control.nama_kontrol}.{func.nama_fungsi}'
            self.stdout.write(f'  - {rule_code}')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Run: docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access')
        self.stdout.write('  2. Restart: docker restart survey_pemda_python_app')
        self.stdout.write('  3. Access: http://localhost:8006/api-simpeg/pegawai/')
        self.stdout.write('')
