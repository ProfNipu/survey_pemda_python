"""
Management command untuk sync dengan table users dari Laravel
Table users sudah ada di database (created by Laravel migrations)
Command ini akan fake migrate agar Django recognize table users
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Sync custom User model dengan existing Laravel users table'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            '\n⚠️  PASTIKAN table users sudah ada (created by Laravel)'
        ))
        
        # Fake migrate accounts (users table sudah ada)
        self.stdout.write('\n📦 Fake migrating accounts app...')
        call_command('migrate', 'accounts', '--fake', verbosity=1)
        
        self.stdout.write(self.style.SUCCESS(
            '\n✅ Done! Django sekarang bisa pakai table users dari Laravel'
        ))
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('  1. Test login dengan user dari Laravel')
        self.stdout.write('  2. Password hash Laravel akan otomatis terdeteksi')
        self.stdout.write('  3. Buat superuser: python manage.py createsuperuser\n')
