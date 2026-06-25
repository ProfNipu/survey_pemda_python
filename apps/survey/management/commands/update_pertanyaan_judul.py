"""
Management command untuk update data pertanyaan survey
Menambahkan judul dan pertanyaan lengkap
"""

from django.core.management.base import BaseCommand
from apps.survey.models import PertanyaanSurvey


class Command(BaseCommand):
    help = 'Update pertanyaan survey dengan judul dan pertanyaan lengkap'

    def handle(self, *args, **options):
        self.stdout.write('Updating pertanyaan survey...')
        
        # Data pertanyaan lengkap
        pertanyaan_data = {
            'survey01': {
                'judul': 'Berorientasi Pelayanan',
                'pertanyaan': 'Sejauh mana pegawai mampu memberikan pelayanan yang baik, responsif, dan berkualitas kepada masyarakat atau stakeholder?'
            },
            'survey02': {
                'judul': 'Akuntabel',
                'pertanyaan': 'Sejauh mana pegawai bertanggung jawab atas tugas dan keputusan yang diambil, serta dapat mempertanggungjawabkan hasilnya?'
            },
            'survey03': {
                'judul': 'Kompeten',
                'pertanyaan': 'Sejauh mana pegawai memiliki pengetahuan, keterampilan, dan kemampuan yang diperlukan untuk melaksanakan tugasnya dengan baik?'
            },
            'survey04': {
                'judul': 'Harmonis',
                'pertanyaan': 'Sejauh mana pegawai mampu menciptakan dan memelihara hubungan kerja yang baik dengan rekan kerja dan atasan?'
            },
            'survey05': {
                'judul': 'Loyal',
                'pertanyaan': 'Sejauh mana pegawai menunjukkan kesetiaan dan dedikasi terhadap organisasi serta komitmen dalam melaksanakan tugas?'
            },
            'survey06': {
                'judul': 'Adaptif',
                'pertanyaan': 'Sejauh mana pegawai mampu menyesuaikan diri dengan perubahan, belajar hal baru, dan berinovasi dalam bekerja?'
            },
            'survey07': {
                'judul': 'Kolaboratif',
                'pertanyaan': 'Sejauh mana pegawai mampu bekerja sama dengan tim, berbagi pengetahuan, dan berkontribusi dalam pencapaian tujuan bersama?'
            },
        }
        
        updated_count = 0
        for kode, data in pertanyaan_data.items():
            try:
                pertanyaan = PertanyaanSurvey.objects.get(kode_pertanyaan=kode)
                pertanyaan.judul = data['judul']
                pertanyaan.pertanyaan = data['pertanyaan']
                pertanyaan.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated: {kode} - {data["judul"]}')
                )
            except PertanyaanSurvey.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'✗ Not found: {kode}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal updated: {updated_count} pertanyaan')
        )
