from django.core.management.base import BaseCommand
from apps.manajemen.models import PermissionModule, PermissionControl, PermissionFunction, PermissionRule


class Command(BaseCommand):
    help = 'Seed permissions untuk Survey JPT'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🌱 Seeding Permissions: Survey')
        self.stdout.write('=' * 70)

        # Module: survey
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

        # Control: jenis_survey
        control_jenis, created = PermissionControl.objects.get_or_create(
            nama_kontrol='jenis_survey',
            defaults={
                'label_kontrol': 'Jenis Survey',
                'deskripsi_kontrol': 'Kelola master jenis survey',
            }
        )
        if created:
            self.stdout.write('  ✓ Created control: Jenis Survey')

        # Control: pertanyaan_survey
        control_pertanyaan, created = PermissionControl.objects.get_or_create(
            nama_kontrol='pertanyaan_survey',
            defaults={
                'label_kontrol': 'Pertanyaan Survey',
                'deskripsi_kontrol': 'Kelola pertanyaan survey',
            }
        )
        if created:
            self.stdout.write('  ✓ Created control: Pertanyaan Survey')

        # Functions (reusable)
        functions_data = [
            {'nama': 'view', 'label': 'Lihat'},
            {'nama': 'create', 'label': 'Tambah'},
            {'nama': 'edit', 'label': 'Edit'},
            {'nama': 'delete', 'label': 'Hapus'},
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

        # Create Rules for jenis_survey
        for func_data in functions_data:
            func = PermissionFunction.objects.get(nama_fungsi=func_data['nama'])
            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control_jenis,
                function=func,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'    ✓ Created rule: survey.jenis_survey.{func_data["nama"]}')

        # Create Rules for pertanyaan_survey
        for func_data in functions_data:
            func = PermissionFunction.objects.get(nama_fungsi=func_data['nama'])
            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control_pertanyaan,
                function=func,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'    ✓ Created rule: survey.pertanyaan_survey.{func_data["nama"]}')

        self.stdout.write('')
        self.stdout.write('✅ Permission seeding completed!')
