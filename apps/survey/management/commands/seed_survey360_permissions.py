from django.core.management.base import BaseCommand
from apps.manajemen.models import PermissionModule, PermissionControl, PermissionFunction, PermissionRule


class Command(BaseCommand):
    help = 'Seed permissions untuk Survey 360'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('Seeding Permissions: Survey 360')
        self.stdout.write('=' * 70)

        module, created = PermissionModule.objects.get_or_create(
            nama_module='survey360',
            defaults={
                'label_module': 'Survey 360',
                'deskripsi_module': 'Modul Survey 360 Derajat',
                'icon': 'fas fa-sync-alt',
                'order': 8,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('  Created module: Survey 360')

        control_fill, created = PermissionControl.objects.get_or_create(
            nama_kontrol='survey360_fill',
            defaults={
                'label_kontrol': 'Isi Survey 360',
                'deskripsi_kontrol': 'Mengisi survey 360 derajat',
            }
        )
        if created:
            self.stdout.write('  Created control: Isi Survey 360')

        control_report, created = PermissionControl.objects.get_or_create(
            nama_kontrol='survey360_report',
            defaults={
                'label_kontrol': 'Laporan Survey 360',
                'deskripsi_kontrol': 'Lihat laporan dan export survey 360',
            }
        )
        if created:
            self.stdout.write('  Created control: Laporan Survey 360')

        functions_map = {}
        for nama, label in [('view', 'Lihat'), ('create', 'Tambah'), ('submit', 'Submit'),
                          ('export', 'Export'), ('reset', 'Reset')]:
            fn, fn_created = PermissionFunction.objects.get_or_create(
                nama_fungsi=nama,
                defaults={'label_fungsi': label}
            )
            if fn_created:
                self.stdout.write(f'  Created function: {label}')
            functions_map[nama] = fn

        for fn_name in ['view', 'create', 'submit']:
            fn = functions_map[fn_name]
            rule, r_created = PermissionRule.objects.get_or_create(
                module=module,
                control=control_fill,
                function=fn,
                defaults={'is_active': True}
            )
            if r_created:
                self.stdout.write(f'    Created rule: survey360.survey360_fill.{fn_name}')

        for fn_name in ['view', 'export', 'reset']:
            fn = functions_map[fn_name]
            rule, r_created = PermissionRule.objects.get_or_create(
                module=module,
                control=control_report,
                function=fn,
                defaults={'is_active': True}
            )
            if r_created:
                self.stdout.write(f'    Created rule: survey360.survey360_report.{fn_name}')

        self.stdout.write('')
        self.stdout.write('Permission seeding completed!')
