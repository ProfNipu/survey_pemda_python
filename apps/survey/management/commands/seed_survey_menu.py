from django.core.management.base import BaseCommand
from apps.manajemen.models import MenuItem, MenuCategory


class Command(BaseCommand):
    help = 'Seed menu untuk Survey'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🌱 Seeding Menu: Survey')
        self.stdout.write('=' * 70)

        # Cek atau buat kategori Survey
        category_survey, created = MenuCategory.objects.get_or_create(
            code=7,
            defaults={
                'name': 'Survey',
                'order': 7,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('  ✓ Created category: Survey')

        # Parent: Penilaian JPT
        parent_jpt, created = MenuItem.objects.get_or_create(
            name='Penilaian JPT',
            defaults={
                'permission_key': None,
                'url_name': None,
                'icon': 'fas fa-star',
                'type': 'group',
                'parent': None,
                'order': 1,
                'category': 7,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created parent: Penilaian JPT')
        else:
            self.stdout.write(f'  ℹ Parent already exists: Penilaian JPT')

        # Child menu items untuk Penilaian JPT
        menu_items = [
            {
                'name': 'Daftar Penilaian',
                'permission_key': 'survey.survey_jpt.view',
                'url_name': 'survey:penilaian_list',
                'icon': 'fas fa-list',
                'order': 1
            },
            {
                'name': 'Tambah Penilaian',
                'permission_key': 'survey.survey_jpt.create',
                'url_name': 'survey:penilaian_create',
                'icon': 'fas fa-plus-circle',
                'order': 2
            },
            {
                'name': 'Buat Penilaian',
                'permission_key': 'survey.survey_jpt.create',
                'url_name': 'survey:buat_penilaian',
                'icon': 'fas fa-user-check',
                'order': 3
            },
            {
                'name': 'Laporan Hasil',
                'permission_key': 'survey.survey_jpt.report',
                'url_name': 'survey:penilaian_report',
                'icon': 'fas fa-chart-bar',
                'order': 4
            },
        ]

        for item_data in menu_items:
            item, created = MenuItem.objects.update_or_create(
                name=item_data['name'],
                parent=parent_jpt,
                defaults={
                    'permission_key': item_data['permission_key'],
                    'url_name': item_data['url_name'],
                    'icon': item_data['icon'],
                    'type': 'link',
                    'order': item_data['order'],
                    'category': 7,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created child: {item_data["name"]}')
            else:
                self.stdout.write(f'  ✓ Updated child: {item_data["name"]}')

        # Parent: Master Survey (untuk kelola jenis survey & pertanyaan)
        parent_master, created = MenuItem.objects.get_or_create(
            name='Master Survey',
            defaults={
                'permission_key': None,
                'url_name': None,
                'icon': 'fas fa-cog',
                'type': 'group',
                'parent': None,
                'order': 2,
                'category': 7,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created parent: Master Survey')
        else:
            self.stdout.write(f'  ℹ Parent already exists: Master Survey')

        # Child menu items untuk Master Survey
        master_items = [
            {
                'name': 'Jenis Survey',
                'permission_key': 'survey.jenis_survey.view',
                'url_name': 'survey:jenis_survey_list',
                'icon': 'fas fa-tags',
                'order': 1
            },
            {
                'name': 'Pertanyaan Survey',
                'permission_key': 'survey.pertanyaan_survey.view',
                'url_name': 'survey:pertanyaan_survey_list',
                'icon': 'fas fa-question-circle',
                'order': 2
            },
            {
                'name': 'Responden Survey',
                'permission_key': 'survey.responden_survey.view',
                'url_name': 'survey:responden_survey_list',
                'icon': 'fas fa-users',
                'order': 3
            },
            {
                'name': 'Jawaban Survey',
                'permission_key': 'survey.jawaban_survey.view',
                'url_name': 'survey:jawaban_survey_list',
                'icon': 'fas fa-clipboard-list',
                'order': 4
            },
            {
                'name': 'Periode Survey',
                'permission_key': 'survey.periode_survey.view',
                'url_name': 'survey:periode_survey_list',
                'icon': 'fas fa-calendar-alt',
                'order': 5
            },
        ]

        for item_data in master_items:
            item, created = MenuItem.objects.update_or_create(
                name=item_data['name'],
                parent=parent_master,
                defaults={
                    'permission_key': item_data['permission_key'],
                    'url_name': item_data['url_name'],
                    'icon': item_data['icon'],
                    'type': 'link',
                    'order': item_data['order'],
                    'category': 7,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created child: {item_data["name"]}')
            else:
                self.stdout.write(f'  ✓ Updated child: {item_data["name"]}')

        self.stdout.write('')
        self.stdout.write('✅ Menu seeding completed!')

