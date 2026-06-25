from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from apps.pegawai.models import MrJabatan


class Command(BaseCommand):
    help = "Import/sync Mr_jabatan (riwayat jabatan) from Laravel DB (DATABASES['laravel']) into Django DB (pegawai.MrJabatan)"

    def add_arguments(self, parser):
        parser.add_argument('--include-deleted', action='store_true', help='Include soft-deleted rows (deleted_at not null)')

    def handle(self, *args, **options):
        include_deleted = bool(options.get('include_deleted'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  Importing Mr_jabatan into pegawai.MrJabatan'))
        self.stdout.write('=' * 70)

        with connections['laravel'].cursor() as cursor:
            sql = 'SELECT * FROM Mr_jabatan'
            if not include_deleted:
                sql += " WHERE deleted_at IS NULL OR deleted_at = '0000-00-00 00:00:00'"
            cursor.execute(sql)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        now = timezone.now()
        created = 0
        updated = 0
        skipped = 0

        model_fields = {f.name for f in MrJabatan._meta.fields}
        model_fields.discard('id')

        def _norm_str(v):
            if v is None:
                return None
            if isinstance(v, str):
                v = v.strip()
                return v if v != '' else None
            return v

        def _norm_int(v):
            if v is None:
                return None
            if isinstance(v, str):
                v = v.strip()
                if v == '' or v == '0':
                    return None
                if v.isdigit():
                    iv = int(v)
                    return iv if iv > 0 else None
                return None
            if isinstance(v, int):
                return v if v > 0 else None
            return None

        fk_to_id = {
            'id_pegawai': 'id_pegawai_id',
            'id_jenis_jabatan': 'id_jenis_jabatan_id',
            'id_opd': 'id_opd_id',
            'id_sub_opd': 'id_sub_opd_id',
            'JF_04': 'JF_04_id',
            'JF_23': 'JF_23_id',
            'JF_24': 'JF_24_id',
            'MM_07': 'MM_07_id',
        }

        for row in rows:
            obj = {cols[i]: row[i] for i in range(len(cols))}
            rid = obj.get('id')
            if rid is None:
                skipped += 1
                continue

            defaults = {}
            jenis_jabatan = obj.get('id_jenis_jabatan')
            for k, v in obj.items():
                if k not in model_fields:
                    continue

                if k in fk_to_id:
                    key = fk_to_id[k]
                    defaults[key] = _norm_int(v)
                    continue

                if k == 'id_jabatan':
                    defaults['id_jabatan'] = None if v in (0, '0', '') else v
                    if jenis_jabatan in (1, '1'):
                        defaults['id_jabatan_struktural_id'] = None if v in (0, '0', '') else v
                        defaults['id_jabatan_non_struktural_id'] = None
                    else:
                        defaults['id_jabatan_non_struktural_id'] = None if v in (0, '0', '') else v
                        defaults['id_jabatan_struktural_id'] = None
                    continue

                if k == 'JF_01':
                    v2 = _norm_str(v)
                    defaults['JF_01'] = v2
                    if isinstance(v2, str) and v2.isdigit() and int(v2) > 0:
                        defaults['JF_01_ref_id'] = int(v2)
                    else:
                        defaults['JF_01_ref_id'] = None
                    continue

                if k == 'JF_02':
                    v2 = _norm_str(v)
                    defaults['JF_02'] = v2
                    if v2 in ('0', 0):
                        v2 = None
                    defaults['JF_02_ref_id'] = v2
                    continue

                if k == 'JF_25':
                    v2 = _norm_str(v)
                    defaults['JF_25'] = v2
                    defaults['JF_25_ref_id'] = _norm_int(v2)
                    continue

                # Normalize date/timestamp zero values
                if v in ('0000-00-00', '0000-00-00 00:00:00'):
                    v = None

                defaults[k] = _norm_str(v) if isinstance(v, str) else v

            if 'updated_at' in model_fields and not defaults.get('updated_at'):
                defaults['updated_at'] = now

            _, was_created = MrJabatan.objects.update_or_create(
                id=int(rid),
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(f'  ✓ Synced rows: {len(rows)} (created: {created}, updated: {updated}, skipped: {skipped})')
        self.stdout.write(self.style.SUCCESS('✅ Import Mr_jabatan completed'))
