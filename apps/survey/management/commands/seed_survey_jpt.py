from django.core.management.base import BaseCommand
from apps.survey_jpt.models import JenisSurvey, PertanyaanSurvey


class Command(BaseCommand):
    help = 'Seed data awal untuk Survey JPT (Dinamis)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🌱 Seeding Survey JPT - Sistem Dinamis')
        self.stdout.write('=' * 70)

        # Buat Jenis Survey JPT
        jenis_jpt, created = JenisSurvey.objects.get_or_create(
            kode='JPT',
            defaults={
                'nama': 'Penilaian JPT (Jabatan Pimpinan Tinggi)',
                'deskripsi': 'Survey penilaian untuk JPT dengan 7 aspek penilaian',
                'is_active': True
            }
        )
        if created:
            self.stdout.write('  ✓ Created: Jenis Survey JPT')
        else:
            self.stdout.write('  ℹ Already exists: Jenis Survey JPT')

        # Pertanyaan Survey JPT (7 aspek)
        pertanyaan_list = [
            {
                'kode': 'survey01',
                'pertanyaan': 'Berorientasi Pelayanan (1-5)',
                'urutan': 1,
                'bobot': 1.0
            },
            {
                'kode': 'survey02',
                'pertanyaan': 'Akuntabel (1-5)',
                'urutan': 2,
                'bobot': 1.0
            },
            {
                'kode': 'survey03',
                'pertanyaan': 'Kompeten (1-5)',
                'urutan': 3,
                'bobot': 1.0
            },
            {
                'kode': 'survey04',
                'pertanyaan': 'Harmonis (1-5)',
                'urutan': 4,
                'bobot': 1.0
            },
            {
                'kode': 'survey05',
                'pertanyaan': 'Loyal (1-5)',
                'urutan': 5,
                'bobot': 1.0
            },
            {
                'kode': 'survey06',
                'pertanyaan': 'Adaptif (1-5)',
                'urutan': 6,
                'bobot': 1.0
            },
            {
                'kode': 'survey07',
                'pertanyaan': 'Kolaboratif (1-5)',
                'urutan': 7,
                'bobot': 1.0
            },
        ]

        created_count = 0
        for data in pertanyaan_list:
            pertanyaan, created = PertanyaanSurvey.objects.get_or_create(
                jenis_survey=jenis_jpt,
                kode_pertanyaan=data['kode'],
                defaults={
                    'pertanyaan': data['pertanyaan'],
                    'urutan': data['urutan'],
                    'bobot': data['bobot'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f'  ✓ Created {created_count} pertanyaan (total: {len(pertanyaan_list)})')
        
        self.stdout.write('')
        self.stdout.write('✅ Survey JPT seeding completed!')
        self.stdout.write('')
        self.stdout.write('💡 Keuntungan Sistem Dinamis:')
        self.stdout.write('   - Bisa tambah jenis survey baru (360, Kinerja, dll)')
        self.stdout.write('   - Bisa tambah/edit pertanyaan tanpa ubah kode')
        self.stdout.write('   - Perhitungan otomatis dengan bobot')
        self.stdout.write('   - Scalable untuk berbagai jenis penilaian')
