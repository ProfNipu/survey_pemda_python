from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.survey.models_survey_config import SurveyConfiguration, SurveyAspek
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed sample survey configuration for testing'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🌱 Seeding Sample Survey Configuration')
        self.stdout.write('=' * 70)

        # Get or create a user for created_by
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        except:
            user = None

        # Create sample survey configuration
        config, created = SurveyConfiguration.objects.get_or_create(
            nama_survey='Survey 360° - Penilaian Kinerja Pegawai',
            tahun=2024,
            defaults={
                'deskripsi': 'Survey penilaian kinerja pegawai secara menyeluruh dari berbagai aspek kompetensi dan perilaku kerja.',
                'periode_mulai': date.today(),
                'periode_selesai': date.today() + timedelta(days=30),
                'is_active': True,
                'show_pegawai_penilai': False,
                'show_foto_pegawai': True,
                'created_by': user
            }
        )

        if created:
            self.stdout.write('  ✓ Created survey configuration: Survey 360° - Penilaian Kinerja Pegawai')
            
            # Create sample aspects
            aspects_data = [
                {
                    'nama_aspek': 'Berorientasi Pelayanan',
                    'deskripsi': 'Sejauh mana pegawai mampu memberikan pelayanan yang cepat, ramah, dan solutif kepada masyarakat atau rekan kerja.',
                    'urutan': 1,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                },
                {
                    'nama_aspek': 'Akuntabel',
                    'deskripsi': 'Kemampuan pegawai untuk bertanggung jawab atas pekerjaan yang dilakukan dan hasilnya.',
                    'urutan': 2,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                },
                {
                    'nama_aspek': 'Kompeten',
                    'deskripsi': 'Tingkat kemampuan teknis dan pengetahuan pegawai dalam menjalankan tugas dan fungsinya.',
                    'urutan': 3,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                },
                {
                    'nama_aspek': 'Harmonis',
                    'deskripsi': 'Kemampuan pegawai dalam menjalin hubungan kerja yang baik dan harmonis dengan rekan kerja.',
                    'urutan': 4,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                },
                {
                    'nama_aspek': 'Loyal',
                    'deskripsi': 'Tingkat kesetiaan dan komitmen pegawai terhadap organisasi dan tugas yang diberikan.',
                    'urutan': 5,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                },
                {
                    'nama_aspek': 'Adaptif',
                    'deskripsi': 'Kemampuan pegawai untuk menyesuaikan diri dengan perubahan dan tantangan baru dalam pekerjaan.',
                    'urutan': 6,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                },
                {
                    'nama_aspek': 'Kolaboratif',
                    'deskripsi': 'Kemampuan pegawai untuk bekerja sama secara efektif dalam tim dan lintas unit kerja.',
                    'urutan': 7,
                    'skala_min': 1,
                    'skala_max': 5,
                    'label_min': 'Sangat Kurang',
                    'label_max': 'Sangat Baik'
                }
            ]

            created_aspects = 0
            for aspect_data in aspects_data:
                aspect, created = SurveyAspek.objects.get_or_create(
                    survey_config=config,
                    nama_aspek=aspect_data['nama_aspek'],
                    defaults=aspect_data
                )
                if created:
                    created_aspects += 1
                    self.stdout.write(f'    ✓ Created aspect: {aspect_data["nama_aspek"]}')

            self.stdout.write(f'  ✓ Created {created_aspects} aspects')
        else:
            self.stdout.write('  ℹ Survey configuration already exists')

        # Create another sample for different year
        config2, created2 = SurveyConfiguration.objects.get_or_create(
            nama_survey='Survey Kepuasan Pelayanan',
            tahun=2024,
            defaults={
                'deskripsi': 'Survey untuk mengukur tingkat kepuasan masyarakat terhadap pelayanan publik.',
                'periode_mulai': date.today() + timedelta(days=7),
                'periode_selesai': date.today() + timedelta(days=37),
                'is_active': False,  # Inactive for testing
                'show_pegawai_penilai': True,
                'show_foto_pegawai': True,
                'created_by': user
            }
        )

        if created2:
            self.stdout.write('  ✓ Created survey configuration: Survey Kepuasan Pelayanan')
            
            # Create different aspects for this survey
            aspects_data2 = [
                {
                    'nama_aspek': 'Kecepatan Pelayanan',
                    'deskripsi': 'Seberapa cepat pegawai memberikan pelayanan kepada masyarakat.',
                    'urutan': 1,
                    'skala_min': 1,
                    'skala_max': 10,
                    'label_min': 'Sangat Lambat',
                    'label_max': 'Sangat Cepat'
                },
                {
                    'nama_aspek': 'Keramahan',
                    'deskripsi': 'Tingkat keramahan dan kesopanan pegawai dalam memberikan pelayanan.',
                    'urutan': 2,
                    'skala_min': 1,
                    'skala_max': 10,
                    'label_min': 'Sangat Tidak Ramah',
                    'label_max': 'Sangat Ramah'
                },
                {
                    'nama_aspek': 'Ketepatan Informasi',
                    'deskripsi': 'Keakuratan dan kelengkapan informasi yang diberikan pegawai.',
                    'urutan': 3,
                    'skala_min': 1,
                    'skala_max': 10,
                    'label_min': 'Sangat Tidak Tepat',
                    'label_max': 'Sangat Tepat'
                }
            ]

            created_aspects2 = 0
            for aspect_data in aspects_data2:
                aspect, created = SurveyAspek.objects.get_or_create(
                    survey_config=config2,
                    nama_aspek=aspect_data['nama_aspek'],
                    defaults=aspect_data
                )
                if created:
                    created_aspects2 += 1
                    self.stdout.write(f'    ✓ Created aspect: {aspect_data["nama_aspek"]}')

            self.stdout.write(f'  ✓ Created {created_aspects2} aspects')
        else:
            self.stdout.write('  ℹ Survey configuration already exists')

        self.stdout.write('')
        self.stdout.write('✅ Sample survey configuration seeding completed!')
        self.stdout.write('')
        self.stdout.write('📋 Summary:')
        self.stdout.write(f'   • Total Survey Configurations: {SurveyConfiguration.objects.count()}')
        self.stdout.write(f'   • Total Survey Aspects: {SurveyAspek.objects.count()}')
        self.stdout.write('')
        self.stdout.write('🌐 You can now access:')
        self.stdout.write('   • Survey Config List: http://localhost:8006/survey/config/')
        self.stdout.write('   • Dynamic Survey Form: http://localhost:8006/survey/form/')
        self.stdout.write('   • Response List: http://localhost:8006/survey/responses/')