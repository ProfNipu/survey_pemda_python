from django.core.management.base import BaseCommand
from apps.manajemen.models import MenuItem


class Command(BaseCommand):
    help = 'Cleanup menu items yang tidak dipakai (Konfigurasi Survey & Riwayat Penilaian)'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('🧹 Cleaning up unused menu items')
        self.stdout.write('=' * 70)

        # Hapus menu "Konfigurasi Survey"
        deleted_config = MenuItem.objects.filter(name='Konfigurasi Survey').delete()
        if deleted_config[0] > 0:
            self.stdout.write(f'  ✓ Deleted: Konfigurasi Survey ({deleted_config[0]} items)')
        else:
            self.stdout.write('  ℹ Menu "Konfigurasi Survey" not found')

        # Hapus menu "Riwayat Penilaian"
        deleted_riwayat = MenuItem.objects.filter(name='Riwayat Penilaian').delete()
        if deleted_riwayat[0] > 0:
            self.stdout.write(f'  ✓ Deleted: Riwayat Penilaian ({deleted_riwayat[0]} items)')
        else:
            self.stdout.write('  ℹ Menu "Riwayat Penilaian" not found')

        self.stdout.write('')
        self.stdout.write('✅ Cleanup completed!')
