import json
import os
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.utils import timezone as tz
from apps.survey.models import JenisSurvey, RespondenSurvey, JawabanSurvey, PertanyaanSurvey, PeriodeSurvey
from apps.survey.models_pegawai_riwayat import PegawaiRiwayatData


class Command(BaseCommand):
    help = 'Import data Survey 360 dari Laravel MySQL (JSON export)'

    def add_arguments(self, parser):
        parser.add_argument('--survey-file', default='/tmp/pegawai360.json')
        parser.add_argument('--riwayat-file', default='/tmp/pegawaiRiwayat.json')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        survey_file = options['survey_file']
        riwayat_file = options['riwayat_file']
        dry_run = options['dry_run']

        if not os.path.exists(survey_file):
            self.stderr.write(f"File tidak ditemukan: {survey_file}")
            return
        if not os.path.exists(riwayat_file):
            self.stderr.write(f"File tidak ditemukan: {riwayat_file}")
            return

        jenis = JenisSurvey.objects.filter(kode='SURVEY_360').first()
        if not jenis:
            self.stderr.write("JenisSurvey SURVEY_360 tidak ditemukan. Jalankan seed_survey360_data dulu.")
            return

        questions = list(PertanyaanSurvey.objects.filter(
            jenis_survey=jenis, is_active=True
        ).order_by('urutan'))

        if len(questions) != 7:
            self.stderr.write(f"Harus ada 7 pertanyaan, ditemukan {len(questions)}")
            return

        with open(survey_file) as f:
            surveys_data = json.load(f)

        with open(riwayat_file) as f:
            riwayat_data = json.load(f)

        self.stdout.write(f"Data Survey: {len(surveys_data)} records")
        self.stdout.write(f"Data Riwayat: {len(riwayat_data)} records")
        if dry_run:
            self.stdout.write("DRY RUN - tidak ada perubahan database")

        # --- Import Riwayat ---
        # Need a dummy periode for old data
        active_periode = PeriodeSurvey.objects.filter(
            jenis_survey=jenis, is_active=True
        ).first()
        if not active_periode:
            self.stdout.write("Membuat PeriodeSurvey untuk SURVEY_360 (2025)...")
            if not dry_run:
                active_periode = PeriodeSurvey.objects.create(
                    jenis_survey=jenis,
                    nama_periode='Periode 2025',
                    tanggal_mulai=datetime(2025, 1, 1),
                    tanggal_selesai=datetime(2025, 12, 31),
                    is_active=True,
                )

        riwayat_created = 0
        riwayat_skipped = 0

        for item in riwayat_data:
            id_pegawai = item['id_pegawai']
            dp_raw = item.get('data_pegawai', '{}')

            try:
                dp = json.loads(dp_raw) if isinstance(dp_raw, str) else dp_raw
            except json.JSONDecodeError:
                dp = {}

            created_str = item.get('created_at', '')
            try:
                snap_at = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S')
                snap_at = snap_at.replace(tzinfo=tz.get_current_timezone())
            except (ValueError, TypeError):
                snap_at = tz.now()

            existing = PegawaiRiwayatData.objects.filter(
                id_pegawai=id_pegawai,
                snapshot_at__year=snap_at.year,
            ).first()
            if existing:
                riwayat_skipped += 1
                continue

            if dry_run:
                riwayat_created += 1
                continue

            obj = PegawaiRiwayatData.objects.create(
                periode_survey=active_periode,
                jenis_survey=jenis,
                id_pegawai=id_pegawai,
                nip_baru=dp.get('nipBaru') or dp.get('nip_baru') or '',
                nip_lama=dp.get('nipLama') or dp.get('nip_lama') or '',
                nama_pegawai=dp.get('namaPegawai', ''),
                nama_jabatan=dp.get('namaJabatan', ''),
                kode_eselon=dp.get('kodeEselon'),
                nama_eselon=dp.get('namaEselon', ''),
                id_opd=item.get('id_opd') or dp.get('id_opd'),
                nm_opd=dp.get('nm_opd', ''),
                nm_sub_opd=dp.get('nm_sub_opd', ''),
                nama_golongan=dp.get('namaGolongan', ''),
                nama_pangkat=dp.get('namaPangkat', ''),
                kategori_pegawai=dp.get('kategoriPegawai'),
                nama_kategori_pegawai=dp.get('namaKategoriPegawai', ''),
                id_sub_opd=item.get('id_sub_opd') or dp.get('id_sub_opd'),
                tempat_lahir=dp.get('tempatLahir', ''),
                tanggal_lahir=dp.get('tanggalLahir', ''),
                jenis_kelamin=dp.get('jenisKelamin'),
                no_hp=dp.get('nohp', ''),
                raw_data=dp,
            )
            PegawaiRiwayatData.objects.filter(id=obj.id).update(snapshot_at=snap_at)
            riwayat_created += 1

        self.stdout.write(self.style.SUCCESS(f"Riwayat: {riwayat_created} created, {riwayat_skipped} skipped"))

        # --- Import Survey ---
        survey_created = 0
        jawaban_created = 0
        survey_skipped = 0

        status_map = {0: 'draft', 1: 'submitted'}
        peran_map = {10: '10', 20: '20', 30: '30'}
        survey_fields = ['survey01', 'survey02', 'survey03', 'survey04',
                         'survey05', 'survey06', 'survey07']

        for item in surveys_data:
            existing = RespondenSurvey.objects.filter(
                id_pegawaiPenilai=item['id_pegawaiPenilai'],
                id_pegawaiDinilai=item['id_pegawaiDinilai'],
                jenis_survey=jenis,
            ).first()
            if existing:
                survey_skipped += 1
                continue

            created_str = item.get('created_at', '')
            updated_str = item.get('updated_at', '')
            try:
                created_dt = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                created_dt = tz.now()
            try:
                updated_dt = datetime.strptime(updated_str, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                updated_dt = created_dt

            status_val = item.get('statusData', 0)
            status_str = status_map.get(status_val, 'draft')
            peran_val = item.get('peranPenilai', 0)
            peran_str = peran_map.get(peran_val, str(peran_val))
            nip_penilai = str(item['nip_pegawaiPenilai']).strip()
            nip_dinilai = str(item['nip_pegawaiDinilai']).strip()

            if dry_run:
                survey_created += 1
                jawaban_created += 7
                continue

            responden = RespondenSurvey.objects.create(
                jenis_survey=jenis,
                id_pegawaiPenilai=item['id_pegawaiPenilai'],
                nip_pegawaiPenilai=nip_penilai,
                id_pegawaiDinilai=item['id_pegawaiDinilai'],
                nip_pegawaiDinilai=nip_dinilai,
                peranPenilai=peran_str,
                statusData=status_str,
            )
            RespondenSurvey.objects.filter(id=responden.id).update(
                created_at=created_dt, updated_at=updated_dt
            )
            survey_created += 1

            for i, field in enumerate(survey_fields):
                nilai = item.get(field, 0)
                if i < len(questions):
                    j = JawabanSurvey.objects.create(
                        responden=responden,
                        pertanyaan=questions[i],
                        nilai=nilai,
                    )
                    JawabanSurvey.objects.filter(id=j.id).update(
                        created_at=created_dt, updated_at=updated_dt
                    )
                    jawaban_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Survey: {survey_created} created, {jawaban_created} jawaban, {survey_skipped} skipped"
        ))
