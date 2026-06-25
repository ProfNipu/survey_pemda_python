from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from apps.pegawai.models import MrHukumanDisiplin
from apps.master_data.models import BknAlasanHukuman, BknJenisHukuman, BknNomorppHukdis, BknTingkatHukdis


class Command(BaseCommand):
    help = "Import/sync Mr_hukuman_disiplin from Laravel table Mr_hukuman_disiplin (DATABASES['laravel']) into Django DB (pegawai.MrHukumanDisiplin)"

    def add_arguments(self, parser):
        parser.add_argument('--include-deleted', action='store_true', help='Include soft-deleted rows (deleted_at not null)')

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  Importing Mr_hukuman_disiplin into pegawai.MrHukumanDisiplin'))
        self.stdout.write('=' * 70)

        with connections['laravel'].cursor() as cursor:
            sql = 'SELECT * FROM Mr_hukuman_disiplin'
            if not include_deleted:
                sql += " WHERE deleted_at IS NULL OR deleted_at = '0000-00-00 00:00:00'"
            cursor.execute(sql)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        now = timezone.now()
        created = 0
        updated = 0
        skipped = 0

        model_fields = {f.name for f in MrHukumanDisiplin._meta.fields}
        model_fields.discard('id')

        fk_to_id = {
            'id_pegawai': 'id_pegawai_id',
            'F_03': 'F_03_id',
        }

        def _resolve_bkn_pk(model_cls, id_bkn_value):
            if id_bkn_value in (None, 0, '0', ''):
                return None
            try:
                s = str(id_bkn_value).strip()
                if not s:
                    return None
            except Exception:
                return None
            try:
                obj = model_cls.objects.filter(id_bkn=s).order_by('-id').first()
            except Exception:
                obj = None
            return getattr(obj, 'id', None) if obj else None

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

                if k == 'HD_01':
                    defaults['HD_01_id'] = _resolve_bkn_pk(BknJenisHukuman, v)
                    continue
                elif k == 'HD_08':
                    defaults['HD_08_id'] = _resolve_bkn_pk(BknNomorppHukdis, v)
                    continue
                elif k == 'HD_09':
                    defaults['HD_09_id'] = _resolve_bkn_pk(BknAlasanHukuman, v)
                    continue
                elif k == 'HD_11':
                    defaults['HD_11_id'] = _resolve_bkn_pk(BknTingkatHukdis, v)
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

            _, was_created = MrHukumanDisiplin.objects.update_or_create(
                id=int(rid),
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(f'  ✓ Synced rows: {len(rows)} (created: {created}, updated: {updated}, skipped: {skipped})')
        self.stdout.write(self.style.SUCCESS('✅ Import Mr_hukuman_disiplin completed'))
