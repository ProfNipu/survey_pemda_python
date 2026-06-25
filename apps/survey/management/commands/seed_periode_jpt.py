"""
Management command untuk seed periode survey JPT
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.survey.models import JenisSurvey, PeriodeSurvey


class Command(BaseCommand):
    help = 'Seed periode survey untuk Penilaian JPT'

    def handle(self, *args, **options):
        self.stdout.write('Creating periode survey...')
        
        # Get Jenis Survey JPT
        try:
            jenis_jpt = JenisSurvey.objects.get(kode='JPT')
        except JenisSurvey.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Jenis Survey JPT tidak ditemukan. Jalankan seed_survey_jpt terlebih dahulu.')
            )
            return
        
        # Create periode aktif (sekarang sampai 3 bulan ke depan)
        now = timezone.now()
        periode_aktif, created = PeriodeSurvey.objects.get_or_create(
            jenis_survey=jenis_jpt,
            nama_periode='Periode Penilaian JPT 2026',
            defaults={
                'tanggal_mulai': now,
                'tanggal_selesai': now + timedelta(days=90),  # 3 bulan
                'deskripsi': 'Periode penilaian kinerja JPT tahun 2026',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created: {periode_aktif.nama_periode}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Mulai: {periode_aktif.tanggal_mulai.strftime("%d %B %Y %H:%M")}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Selesai: {periode_aktif.tanggal_selesai.strftime("%d %B %Y %H:%M")}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'✓ Already exists: {periode_aktif.nama_periode}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\nPeriode survey berhasil dibuat!')
        )
