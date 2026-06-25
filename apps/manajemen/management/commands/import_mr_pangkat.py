from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from apps.pegawai.models import MrPangkat


class Command(BaseCommand):
    help = "Import/sync Mr_pangkat (riwayat pangkat) from Laravel DB (DATABASES['laravel']) into Django DB (pegawai.MrPangkat)"

    def add_arguments(self, parser):
        parser.add_argument('--include-deleted', action='store_true', help='Include soft-deleted rows (deleted_at not null)')

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  Importing Mr_pangkat into pegawai.MrPangkat'))
        self.stdout.write('=' * 70)

        with connections['laravel'].cursor() as cursor:
            sql = 'SELECT * FROM Mr_pangkat'
            if not include_deleted:
                sql += " WHERE deleted_at IS NULL OR deleted_at = '0000-00-00 00:00:00'"
            cursor.execute(sql)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        now = timezone.now()
        created = 0
        updated = 0
        skipped = 0

        model_fields = {f.name for f in MrPangkat._meta.fields}
        model_fields.discard('id')

        def _norm_str(v):
            if v is None:
                return None
            if isinstance(v, str):
                v = v.strip()
                return v if v != '' else None
            return v

        for row in rows:
            obj = {cols[i]: row[i] for i in range(len(cols))}
            rid = obj.get('id')
            if rid is None:
                skipped += 1
                continue

            defaults = {}
            for k, v in obj.items():
                if k in model_fields:
                    if k == 'id_pegawai':
                        defaults['id_pegawai_id'] = None if v in (0, '0', '') else v
                    elif k == 'PF_01':
                        defaults['PF_01_id'] = _norm_str(v)
                    elif k == 'PF_03':
                        defaults['PF_03_id'] = None if v in (0, '0', '') else v
                    elif k == 'PF_07':
                        v2 = _norm_str(v)
                        defaults['PF_07'] = v2
                        if isinstance(v2, str) and v2.isdigit() and int(v2) > 0:
                            defaults['PF_07_ref_id'] = int(v2)
                        else:
                            defaults['PF_07_ref_id'] = None
                    else:
                        defaults[k] = _norm_str(v) if isinstance(v, str) else v

            if 'updated_at' in model_fields and not defaults.get('updated_at'):
                defaults['updated_at'] = now

            _, was_created = MrPangkat.objects.update_or_create(
                id=int(rid),
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(f'  ✓ Synced rows: {len(rows)} (created: {created}, updated: {updated}, skipped: {skipped})')
        self.stdout.write(self.style.SUCCESS('✅ Import Mr_pangkat completed'))
