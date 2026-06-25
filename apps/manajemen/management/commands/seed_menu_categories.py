from django.core.management.base import BaseCommand
from apps.manajemen.models import MenuCategory


DEFAULT_CATEGORIES = [
    # (code, name, order)
    (6, 'Beranda', 0),
    (1, 'Pengaturan Sistem', 1),
    (5, 'Master Data', 2),
    (2, 'Data Pegawai', 3),
    (3, 'Laporan Data', 4),
    (4, 'Manajemen Integrasi', 5),
    (0, 'Menu Lainnya', 99),
]


class Command(BaseCommand):
    help = 'Seed default MenuCategory records (idempotent)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Menu Categories'))
        self.stdout.write('=' * 70)

        created = 0
        updated = 0
        for code, name, order in DEFAULT_CATEGORIES:
            obj, is_created = MenuCategory.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'order': order,
                    'is_active': True,
                }
            )
            if is_created:
                created += 1
                self.stdout.write(f'  ✓ Created: [{code}] {name}')
            else:
                changed = False
                if obj.name != name:
                    obj.name = name
                    changed = True
                if obj.order != order:
                    obj.order = order
                    changed = True
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save()
                    updated += 1
                    self.stdout.write(f'  ↻ Updated: [{code}] {name}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Done. Created: {created}, Updated: {updated}'))
