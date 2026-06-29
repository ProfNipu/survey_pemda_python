from django.core.management.base import BaseCommand
from apps.survey.models import JenisSurvey, PertanyaanSurvey
from django.utils import timezone
from datetime import datetime


class Command(BaseCommand):
    help = 'Seed data Survey 360 (Jenis Survey + 7 Pertanyaan)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('Seeding Data: Survey 360')
        self.stdout.write('=' * 70)

        jenis, created = JenisSurvey.objects.get_or_create(
            kode='SURVEY_360',
            defaults={
                'nama': 'Survey 360 Derajat',
                'deskripsi': 'Penilaian 360 derajat untuk pegawai',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write('  Created JenisSurvey: SURVEY_360')
        else:
            self.stdout.write('  JenisSurvey already exists: SURVEY_360')

        questions = [
            {'kode': 'survey01', 'judul': 'Berorientasi Pelayanan',
             'pertanyaan': 'Sejauh mana pegawai mampu memberikan pelayanan yang cepat, ramah, dan solutif kepada masyarakat/stakeholder?', 'urutan': 1, 'bobot': 1.0},
            {'kode': 'survey02', 'judul': 'Akuntabel',
             'pertanyaan': 'Sejauh mana pegawai melaksanakan tugas secara transparan, sesuai aturan, dan dapat dipertanggungjawabkan?', 'urutan': 2, 'bobot': 1.0},
            {'kode': 'survey03', 'judul': 'Kompeten',
             'pertanyaan': 'Sejauh mana pegawai menguasai bidang tugasnya serta berupaya mengembangkan pengetahuan dan keterampilan?', 'urutan': 3, 'bobot': 1.0},
            {'kode': 'survey04', 'judul': 'Harmonis',
             'pertanyaan': 'Sejauh mana pegawai mampu menjalin komunikasi yang baik, menghargai perbedaan, dan menjaga suasana kerja kondusif?', 'urutan': 4, 'bobot': 1.0},
            {'kode': 'survey05', 'judul': 'Loyal',
             'pertanyaan': 'Sejauh mana pegawai menunjukkan dedikasi, mendukung visi-misi organisasi, dan menempatkan kepentingan instansi di atas kepentingan pribadi?', 'urutan': 5, 'bobot': 1.0},
            {'kode': 'survey06', 'judul': 'Adaptif',
             'pertanyaan': 'Sejauh mana pegawai mampu menyesuaikan diri dengan perubahan kebijakan, teknologi, dan situasi kerja yang dinamis?', 'urutan': 6, 'bobot': 1.0},
            {'kode': 'survey07', 'judul': 'Kolaboratif',
             'pertanyaan': 'Sejauh mana pegawai berperan aktif dalam kerja sama lintas bidang/unit serta mendukung keberhasilan tim?', 'urutan': 7, 'bobot': 1.0},
        ]

        for q in questions:
            pt, pt_created = PertanyaanSurvey.objects.get_or_create(
                jenis_survey=jenis,
                kode_pertanyaan=q['kode'],
                defaults={
                    'judul': q['judul'],
                    'pertanyaan': q['pertanyaan'],
                    'urutan': q['urutan'],
                    'bobot': q['bobot'],
                    'is_active': True,
                }
            )
            if pt_created:
                self.stdout.write(f'  Created pertanyaan: {q["kode"]} - {q["judul"]}')

        self.stdout.write('')
        self.stdout.write('Data seeding completed!')
