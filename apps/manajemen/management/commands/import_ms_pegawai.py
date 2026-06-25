from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from apps.pegawai.models import MsPegawai


class Command(BaseCommand):
    help = "Import/sync ms_pegawai from Laravel DB (DATABASES['laravel']) into Django DB (MsPegawai)"

    def add_arguments(self, parser):
        parser.add_argument('--include-deleted', action='store_true', help='Include soft-deleted rows (deleted_at not null)')

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  Importing ms_pegawai into pegawai.MsPegawai'))
        self.stdout.write('=' * 70)

        with connections['laravel'].cursor() as cursor:
            sql = 'SELECT * FROM ms_pegawai'
            if not include_deleted:
                sql += " WHERE deleted_at IS NULL OR deleted_at = '0000-00-00 00:00:00'"
            cursor.execute(sql)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        now = timezone.now()
        created = 0
        updated = 0
        skipped = 0

        model_fields = {f.name for f in MsPegawai._meta.fields}
        model_fields.discard('id_pegawai')
        fk_fields = {f.name: f for f in MsPegawai._meta.fields if f.is_relation and f.many_to_one}

        def _norm_fk(v):
            if v is None:
                return None
            if v in (0, '0', ''):
                return None
            if isinstance(v, str):
                vv = v.strip()
                if vv in ('', '0'):
                    return None
                if vv.isdigit():
                    iv = int(vv)
                    return iv if iv > 0 else None
                return None
            if isinstance(v, int):
                return v if v > 0 else None
            return None

        for row in rows:
            obj = {cols[i]: row[i] for i in range(len(cols))}
            rid = obj.get('id_pegawai')
            if rid is None:
                skipped += 1
                continue

            defaults = {}
            for k, v in obj.items():
                if k not in model_fields:
                    continue

                # Normalize FK columns: store NULL instead of 0/empty.
                if k in fk_fields:
                    defaults[fk_fields[k].attname] = _norm_fk(v)
                    continue

                defaults[k] = v

            if 'updated_at' in model_fields and not defaults.get('updated_at'):
                defaults['updated_at'] = now

            _, was_created = MsPegawai.objects.update_or_create(
                id_pegawai=int(rid),
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(f'  ✓ Synced rows: {len(rows)} (created: {created}, updated: {updated}, skipped: {skipped})')
        self.stdout.write(self.style.SUCCESS('✅ Import ms_pegawai completed'))
