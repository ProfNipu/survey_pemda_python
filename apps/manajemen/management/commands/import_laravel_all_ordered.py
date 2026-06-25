from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management import call_command
from django.core.management import get_commands
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

class Command(BaseCommand):
    help = (
        "Import data from Laravel DB into Django DB in a safe dependency order "
        "(master refs → unit organisasi → jabatan → pendidikan → pegawai → riwayat)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-deleted',
            action='store_true',
            help='Include soft-deleted rows (deleted_at not null) when supported by import commands',
        )
        parser.add_argument(
            '--skip-master',
            action='store_true',
            help='Skip importing master/reference tables (md_*, bkn_*)',
        )
        parser.add_argument(
            '--skip-unit',
            action='store_true',
            help='Skip import_ms_unit_organisasi',
        )
        parser.add_argument(
            '--skip-jabatan',
            action='store_true',
            help='Skip importing jabatan struktural/non-struktural',
        )
        parser.add_argument(
            '--skip-pendidikan',
            action='store_true',
            help='Skip importing pendidikan references (md_jenjang_pendidikan + ms_daftar_pendidikan)',
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
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bypass migration checks (DANGEROUS). Only use if you know schema is up-to-date.',
        )

    def check_pending_migrations(self) -> bool:
        """Return True if there are unapplied migrations on the default DB."""
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)
        return len(plan) > 0

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))
        force = bool(options.get('force'))
        cmd_opts = {'include_deleted': include_deleted}

        def call_maybe_include_deleted(command_name: str):
            """Call a command with include_deleted when supported.

            Some legacy import commands don't declare --include-deleted; Django raises TypeError.
            """
            if not include_deleted:
                call_command(command_name)
                return
            try:
                call_command(command_name, **cmd_opts)
            except TypeError as e:
                msg = str(e)
                if 'Unknown option' in msg and 'include_deleted' in msg:
                    call_command(command_name)
                    return
                raise

        skip_master = bool(options.get('skip_master'))
        skip_unit = bool(options.get('skip_unit'))
        skip_jabatan = bool(options.get('skip_jabatan'))
        skip_pendidikan = bool(options.get('skip_pendidikan'))
        skip_pegawai = bool(options.get('skip_pegawai'))
        skip_riwayat = bool(options.get('skip_riwayat'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  IMPORT LARAVEL (ORDERED)'))
        self.stdout.write('=' * 70)

        # ====== PRE-FLIGHT CHECK ======
        self.stdout.write('Checking database schema status...')
        if not force and self.check_pending_migrations():
            raise CommandError(
                "CRITICAL: There are unapplied Django migrations!\n"
                "Running import now can cause database column errors.\n"
                "Please run 'python manage.py migrate' first, then re-run this import."
            )
        self.stdout.write(self.style.SUCCESS('✓ Schema is fully migrated.'))
        self.stdout.write('-' * 70)

        # 1) Master/reference tables (needed by pegawai/jabatan/riwayat)
        if not skip_master:
            self.stdout.write(self.style.WARNING('\n• Importing master/reference tables (md_*, bkn_*)'))
            # Minimal set that is commonly referenced by MsPegawai / Jabatan / Riwayat
            core_master_commands = [
                'import_md_jenis_organisasi',
                'import_md_agama',
                'import_md_status_perkawinan',
                'import_md_kedudukan_pegawai',
                'import_md_kategori_jabatan',
                'import_md_jenis_jabatan',
                'import_md_eselon',
                'import_md_jenjang_jabatan',
                'import_md_pangkat',
                'import_bkn_lokasi_kerja',
                'import_bkn_sub_jabatan',
            ]
            for cmd in core_master_commands:
                call_maybe_include_deleted(cmd)

            # Then import any additional available MD/BKN master commands.
            # Keep Md_jenjang_pendidikan in the pendidikan stage.
            all_commands = set(get_commands().keys())
            excluded = set(core_master_commands) | {
                'import_md_jenjang_pendidikan',
            }
            extra_master_commands = sorted(
                c
                for c in all_commands
                if (c.startswith('import_md_') or c.startswith('import_bkn_')) and c not in excluded
            )
            for cmd in extra_master_commands:
                call_maybe_include_deleted(cmd)

        # 2) Unit organisasi (relasi unit kerja)
        if not skip_unit:
            self.stdout.write(self.style.WARNING('\n• Importing unit organisasi (ms_opd → Ms_unit_organisasi)'))
            call_maybe_include_deleted('import_ms_unit_organisasi')

        # 3) Jabatan (struktural/non)
        if not skip_jabatan:
            self.stdout.write(self.style.WARNING('\n• Importing jabatan struktural/non-struktural'))
            call_maybe_include_deleted('import_ms_jabatan_struktural')
            call_maybe_include_deleted('import_ms_jabatan_non_struktural')

        # 4) Pendidikan references (FK in Ms_daftar_pendidikan depends on Md_jenjang_pendidikan.id_bkn)
        if not skip_pendidikan:
            self.stdout.write(self.style.WARNING('\n• Importing pendidikan references (jenjang + daftar)'))
            call_maybe_include_deleted('import_md_jenjang_pendidikan')
            call_maybe_include_deleted('import_ms_daftar_pendidikan')

        # 5) Pegawai
        if not skip_pegawai:
            self.stdout.write(self.style.WARNING('\n• Importing ms_pegawai'))
            call_maybe_include_deleted('import_ms_pegawai')

            # Any extra ms_* commands that are safe after pegawai exists.
            # Example: import_ms_tata_naskah_pegawai depends on id_pegawai.
            all_commands = set(get_commands().keys())
            excluded_ms = {
                'import_ms_unit_organisasi',
                'import_ms_jabatan_struktural',
                'import_ms_jabatan_non_struktural',
                'import_ms_daftar_pendidikan',
                'import_ms_pegawai',
                # Alias for ms_daftar_pendidikan; avoid double run.
                'import_ms_pendidikan',
            }
            extra_ms_commands = sorted(
                c for c in all_commands if c.startswith('import_ms_') and c not in excluded_ms
            )
            for cmd in extra_ms_commands:
                call_maybe_include_deleted(cmd)

        # 6) Riwayat
        if not skip_riwayat:
            self.stdout.write(self.style.WARNING('\n• Importing riwayat (pangkat, jabatan, pendidikan)'))
            # Core MR imports first (commonly referenced downstream)
            core_mr_commands = [
                'import_mr_pangkat',
                'import_mr_jabatan',
                'import_mr_pendidikan',
            ]
            for cmd in core_mr_commands:
                call_maybe_include_deleted(cmd)

            # Then import any additional available MR commands.
            # This allows one-shot import to include data like diklat, skp, keluarga, hukdis, dll
            # without hardcoding them.
            all_commands = set(get_commands().keys())
            extra_mr_commands = sorted(
                c for c in all_commands
                if c.startswith('import_mr_') and c not in set(core_mr_commands)
            )
            for cmd in extra_mr_commands:
                call_maybe_include_deleted(cmd)

        # 7) Post-import seeding for Django-only flags
        try:
            self.stdout.write(self.style.WARNING('\n• Post-import seeding (flags)'))
            call_command('post_import_seed_flags')
        except Exception:
            # Non-fatal. This command may not exist in older deployments.
            pass

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Ordered import completed'))
        self.stdout.write('=' * 70)
