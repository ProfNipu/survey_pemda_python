from django.core.management.base import BaseCommand
from apps.manajemen.models import MenuItem, MenuCategory


class Command(BaseCommand):
    help = 'Seed menu untuk Survey 360'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('Seeding Menu: Survey 360')
        self.stdout.write('=' * 70)

        category, created = MenuCategory.objects.get_or_create(
            code=8,
            defaults={
                'name': 'Survey 360',
                'order': 8,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('  Created category: Survey 360')
        else:
            self.stdout.write('  Using existing category: Survey 360')

        parent_survey360, created = MenuItem.objects.get_or_create(
            name='Survey 360',
            defaults={
                'permission_key': None,
                'url_name': None,
                'icon': 'fas fa-sync-alt',
                'type': 'group',
                'parent': None,
                'order': 1,
                'category': category.pk if hasattr(category, 'pk') else 8,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('  Created parent: Survey 360')
        else:
            self.stdout.write('  Parent already exists: Survey 360')

        menu_items = [
            {
                'name': 'Isi Survey 360',
                'permission_key': 'survey360.survey360_fill.view',
                'url_name': 'survey:survey360_index',
                'icon': 'fas fa-edit',
                'order': 1
            },
            {
                'name': 'Laporan Survey 360',
                'permission_key': 'survey360.survey360_report.view',
                'url_name': 'survey:survey360_laporan',
                'icon': 'fas fa-chart-bar',
                'order': 2
            },
        ]

        for item_data in menu_items:
            item, created = MenuItem.objects.update_or_create(
                name=item_data['name'],
                parent=parent_survey360,
                defaults={
                    'permission_key': item_data['permission_key'],
                    'url_name': item_data['url_name'],
                    'icon': item_data['icon'],
                    'type': 'link',
                    'order': item_data['order'],
                    'category': category.pk if hasattr(category, 'pk') else 8,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created child: {item_data["name"]}')
            else:
                self.stdout.write(f'  Updated child: {item_data["name"]}')

        self.stdout.write('')
        self.stdout.write('Menu seeding completed!')
