"""
Management command untuk fresh database
Drop SEMUA table Django tapi keep Laravel tables
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fresh database - Drop Django tables, keep Laravel tables (ms_pegawai, ms_opd, etc)'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('\n🗑️  Dropping Python/Django tables...\n')
            
            # Get ALL tables
            cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            # Keep Laravel tables (ms_* prefix and specific tables)
            keep_tables = [
                t for t in all_tables 
                if t.startswith('ms_') or t in ['migrations']  # Laravel migrations
            ]
            
            # Drop everything else
            drop_tables = [t for t in all_tables if t not in keep_tables]
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            for table in drop_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    self.stdout.write(f'  ✅ Dropped: {table}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  Skip: {table} ({e})')
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.stdout.write(self.style.SUCCESS(
                '\n✅ Done! Database is fresh.'
            ))
            
            # Show remaining tables (should be Laravel tables only)
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write('\nRemaining tables (Laravel tables):')
            for table in tables:
                if table.startswith('ms_') or table in ['users']:
                    self.stdout.write(f'  - {table}')
            
            self.stdout.write('\nNext: python manage.py migrate\n')
