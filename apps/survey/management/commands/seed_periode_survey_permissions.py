from django.core.management.base import BaseCommand
from apps.manajemen.models import PermissionModule, PermissionControl, PermissionFunction, PermissionRule, Group


class Command(BaseCommand):
    help = 'Seed permissions for Periode Survey'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🌱 Seeding Permissions: Periode Survey')
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

        # Control: periode_survey
        control_periode, created = PermissionControl.objects.get_or_create(
            nama_kontrol='periode_survey',
            defaults={
                'label_kontrol': 'Periode Survey',
                'deskripsi_kontrol': 'Kelola periode survey (waktu buka/tutup)',
            }
        )
        if created:
            self.stdout.write('  ✓ Created control: Periode Survey')

        # Functions (reusable)
        functions_data = [
            {'nama': 'view', 'label': 'Lihat'},
            {'nama': 'create', 'label': 'Tambah'},
            {'nama': 'edit', 'label': 'Edit'},
            {'nama': 'delete', 'label': 'Hapus'},
            {'nama': 'export', 'label': 'Export'},
            {'nama': 'bulk_delete', 'label': 'Bulk Delete'},
        ]

        for func_data in functions_data:
            func, created = PermissionFunction.objects.get_or_create(
                nama_fungsi=func_data['nama'],
                defaults={
                    'label_fungsi': func_data['label'],
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created function: {func_data["label"]}')

        # Create Rules for periode_survey
        created_rules = 0
        for func_data in functions_data:
            func = PermissionFunction.objects.get(nama_fungsi=func_data['nama'])
            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control_periode,
                function=func,
                defaults={'is_active': True}
            )
            if created:
                created_rules += 1
                self.stdout.write(f'    ✓ Created rule: survey.periode_survey.{func_data["nama"]}')

        self.stdout.write(f'\nCreated {created_rules} new permission rules')
        
        # Grant all permissions to Super Admin group
        try:
            from django.contrib.auth.models import Group as AuthGroup
            from apps.manajemen.models import RoleRule
            
            super_admin_group = AuthGroup.objects.get(name='Super Admin')
            periode_rules = PermissionRule.objects.filter(
                module=module,
                control=control_periode
            )
            
            granted_count = 0
            for rule in periode_rules:
                role_rule, created = RoleRule.objects.get_or_create(
                    role=super_admin_group,
                    rule=rule
                )
                if created:
                    granted_count += 1
                    perm_key = f"{rule.module.nama_module}.{rule.control.nama_kontrol}.{rule.function.nama_fungsi}"
                    self.stdout.write(f'    ✓ Granted: {perm_key}')
            
            self.stdout.write(f'\nGranted {granted_count} new permissions to Super Admin group')
            
        except AuthGroup.DoesNotExist:
            self.stdout.write(self.style.WARNING('\nSuper Admin group not found, skipping permission grant'))
        
        self.stdout.write('')
        self.stdout.write('✅ Permission seeding completed!')