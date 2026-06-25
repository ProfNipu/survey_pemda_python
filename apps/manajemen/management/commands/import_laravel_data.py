from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Import/sync data from Laravel DB into Django DB (unit organisasi, ms_pegawai, riwayat pangkat/jabatan/pendidikan)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-deleted',
            action='store_true',
            help='Include soft-deleted rows (deleted_at not null) when supported by import commands',
        )
        parser.add_argument(
            '--skip-unit',
            action='store_true',
            help='Skip import_ms_unit_organisasi',
        )
        parser.add_argument(
            '--skip-pegawai',
            action='store_true',
            help='Skip import_ms_pegawai',
        )
        parser.add_argument(
            '--skip-riwayat',
            action='store_true',
            help='Skip riwayat imports (mr_pangkat, mr_jabatan, mr_pendidikan)',
        )

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))
        skip_unit = bool(options.get('skip_unit'))
        skip_pegawai = bool(options.get('skip_pegawai'))
        skip_riwayat = bool(options.get('skip_riwayat'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  IMPORT DATA (Laravel → Django)'))
        self.stdout.write('=' * 70)

        cmd_opts = {'include_deleted': include_deleted}

        if not skip_unit:
            self.stdout.write(self.style.WARNING('• Importing unit organisasi (ms_opd → Ms_unit_organisasi)'))
            call_command('import_ms_unit_organisasi', **cmd_opts)

        if not skip_pegawai:
            self.stdout.write(self.style.WARNING('• Importing ms_pegawai'))
            call_command('import_ms_pegawai', **cmd_opts)

        if not skip_riwayat:
            self.stdout.write(self.style.WARNING('• Importing riwayat pangkat (Mr_pangkat)'))
            call_command('import_mr_pangkat', **cmd_opts)

            self.stdout.write(self.style.WARNING('• Importing riwayat jabatan (Mr_jabatan)'))
            call_command('import_mr_jabatan', **cmd_opts)

            self.stdout.write(self.style.WARNING('• Importing riwayat pendidikan (ms_riwayat_pendidikan → Mr_pendidikan)'))
            call_command('import_mr_pendidikan', **cmd_opts)

        self.stdout.write(self.style.SUCCESS('✅ Import completed'))
