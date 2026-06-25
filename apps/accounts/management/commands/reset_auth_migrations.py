"""
Management command untuk reset auth migrations
Gunakan ini saat switch ke custom User model
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reset auth migrations untuk support custom User model'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Delete conflicting migrations
            self.stdout.write('Deleting conflicting migrations...')
            
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app IN ('admin', 'auth', 'contenttypes', 'sessions', 'permissions', 'integrations', 'pegawai')
            """)
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ Deleted {cursor.rowcount} migration records'
            ))
            
            # Show remaining
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
            rows = cursor.fetchall()
            
            self.stdout.write('\nRemaining migrations:')
            for app, name in rows:
                self.stdout.write(f'  - {app}.{name}')
            
            self.stdout.write(self.style.SUCCESS(
                '\n✅ Done! Now run: python manage.py migrate'
            ))
