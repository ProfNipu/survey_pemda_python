from django.core.management.base import BaseCommand
from apps.manajemen.models import PermissionModule, PermissionControl, PermissionFunction, PermissionRule, RoleRule
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Seed permissions untuk Penilaian JPT'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🌱 Seeding Permissions: Penilaian JPT')
        self.stdout.write('=' * 70)

        # Get or create module: survey
        module, created = PermissionModule.objects.get_or_create(
            nama_module='survey',
            defaults={
                'label_module': 'Survey',
                'deskripsi_module': 'Modul Survey (JPT, 360, dll)',
                'icon': 'fas fa-poll-h',
                'order': 7,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('  ✓ Created module: Survey')

        # Control: survey_jpt
        control_penilaian, created = PermissionControl.objects.get_or_create(
            nama_kontrol='survey_jpt',
            defaults={
                'label_kontrol': 'Survey JPT',
                'deskripsi_kontrol': 'Kelola penilaian JPT (Jabatan Pimpinan Tinggi)',
            }
        )
        if created:
            self.stdout.write('  ✓ Created control: Penilaian JPT')

        # Functions
        functions_data = [
            {'nama': 'view', 'label': 'Lihat'},
            {'nama': 'create', 'label': 'Tambah'},
            {'nama': 'edit', 'label': 'Edit'},
            {'nama': 'delete', 'label': 'Hapus'},
            {'nama': 'export', 'label': 'Export'},
            {'nama': 'bulk_delete', 'label': 'Hapus Massal'},
            {'nama': 'report', 'label': 'Laporan'},
        ]

        created_functions = 0
        for func_data in functions_data:
            func, created = PermissionFunction.objects.get_or_create(
                nama_fungsi=func_data['nama'],
                defaults={
                    'label_fungsi': func_data['label'],
                }
            )
            if created:
                created_functions += 1
                self.stdout.write(f'  ✓ Created function: {func_data["label"]}')

        # Create Rules for survey_jpt
        created_rules = 0
        for func_data in functions_data:
            func = PermissionFunction.objects.get(nama_fungsi=func_data['nama'])
            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control_penilaian,
                function=func,
                defaults={'is_active': True}
            )
            if created:
                created_rules += 1
                self.stdout.write(f'    ✓ Created rule: survey.survey_jpt.{func_data["nama"]}')

        # Grant permissions to Super Admin group
        try:
            super_admin_group = Group.objects.get(name='Super Admin')
            all_rules = PermissionRule.objects.filter(
                module=module,
                control=control_penilaian
            )
            
            granted_count = 0
            for rule in all_rules:
                role_rule, created = RoleRule.objects.get_or_create(
                    role=super_admin_group,
                    rule=rule
                )
                if created:
                    granted_count += 1
            
            if granted_count > 0:
                self.stdout.write(f'  ✓ Granted {granted_count} permissions to Super Admin group')
            else:
                self.stdout.write('  ℹ Super Admin already has all permissions')
                
        except Group.DoesNotExist:
            self.stdout.write('  ⚠ Super Admin group not found')

        self.stdout.write('')
        self.stdout.write(f'✅ Created {created_functions} new functions and {created_rules} new rules')
        self.stdout.write('✅ Permission seeding completed!')