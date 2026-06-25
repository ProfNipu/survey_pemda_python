from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from apps.pegawai.models import MrOrtu


class Command(BaseCommand):
    help = "Import/sync Mr_ortu (riwayat ortu) from Laravel table Mr_ortu (DATABASES['laravel']) into Django DB (pegawai.MrOrtu)"

    def add_arguments(self, parser):
        parser.add_argument('--include-deleted', action='store_true', help='Include soft-deleted rows (deleted_at not null)')

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  Importing Mr_ortu into pegawai.MrOrtu'))
        self.stdout.write('=' * 70)

        with connections['laravel'].cursor() as cursor:
            sql = 'SELECT * FROM Mr_ortu'
            if not include_deleted:
                sql += " WHERE deleted_at IS NULL OR deleted_at = '0000-00-00 00:00:00'"
            cursor.execute(sql)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        now = timezone.now()
        created = 0
        updated = 0
        skipped = 0

        model_fields = {f.name for f in MrOrtu._meta.fields}
        model_fields.discard('id')

        fk_to_id = {
            'id_pegawai': 'id_pegawai_id',
        }

        for row in rows:
            obj = {cols[i]: row[i] for i in range(len(cols))}
            rid = obj.get('id')
            if rid is None:
                skipped += 1
                continue

            defaults = {}
            for k, v in obj.items():
                if k == 'id':
                    continue
                if k not in model_fields:
                    continue

                if k in fk_to_id:
                    key = fk_to_id[k]
                    defaults[key] = None if v in (0, '0', '') else v
                    continue

                if v in ('0000-00-00', '0000-00-00 00:00:00'):
                    v = None

                defaults[k] = v

            if 'updated_at' in model_fields and not defaults.get('updated_at'):
                defaults['updated_at'] = now

            _, was_created = MrOrtu.objects.update_or_create(
                id=int(rid),
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(f'  ✓ Synced rows: {len(rows)} (created: {created}, updated: {updated}, skipped: {skipped})')
        self.stdout.write(self.style.SUCCESS('✅ Import Mr_ortu completed'))
