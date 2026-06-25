"""
Import users from ESIMPEG database (esim_pegawai.users) to Survey Pemda database (esimpeg_python_db.users)

This command syncs user data from the ESIMPEG system to Survey Pemda system.
"""
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Import/sync users from ESIMPEG database (esim_pegawai.users) to Survey Pemda (esimpeg_python_db.users)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Include inactive users (is_active=0)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        include_inactive = bool(options.get('include_inactive'))
        dry_run = bool(options.get('dry_run'))

        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('⬇️  Importing Users from ESIMPEG database'))
        self.stdout.write('=' * 70)

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be made'))

        # Connect to ESIMPEG database (esim_pegawai)
        with connections['esimpeg_source'].cursor() as cursor:
            # Build SQL query
            sql = '''
                SELECT 
                    id,
                    password,
                    last_login,
                    name,
                    email,
                    username,
                    is_active,
                    date_joined,
                    id_pegawai,
                    user_id_opd,
                    image,
                    updated_at
                FROM users
            '''
            
            if not include_inactive:
                sql += ' WHERE is_active = 1'
            
            sql += ' ORDER BY id'
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            desc_cols = [d[0] for d in cursor.description]

        self.stdout.write(f'📊 Found {len(rows)} users in ESIMPEG database')

        if dry_run:
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write('Sample of users that would be imported:')
            self.stdout.write('=' * 70)
            for row in rows[:5]:  # Show first 5
                data = dict(zip(desc_cols, row))
                self.stdout.write(
                    f"  • ID: {data['id']}, Username: {data['username']}, "
                    f"Name: {data['name']}, Active: {data['is_active']}"
                )
            if len(rows) > 5:
                self.stdout.write(f"  ... and {len(rows) - 5} more users")
            self.stdout.write('\n' + self.style.WARNING('🔍 DRY RUN - No changes made'))
            return

        created = 0
        updated = 0
        skipped = 0
        now = timezone.now()

        for row in rows:
            data = dict(zip(desc_cols, row))
            user_id = data.get('id')
            username = data.get('username')
            
            if not username:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Skipping user ID {user_id}: No username')
                )
                skipped += 1
                continue

            try:
                # Prepare user data
                user_data = {
                    'password': data.get('password') or '',
                    'last_login': data.get('last_login'),
                    'name': data.get('name') or '',
                    'email': data.get('email') or '',
                    'is_active': bool(data.get('is_active', 1)),
                    'date_joined': data.get('date_joined') or now,
                    'id_pegawai': data.get('id_pegawai'),
                    'user_id_opd': data.get('user_id_opd'),
                    'image': data.get('image') or '',
                    'updated_at': data.get('updated_at') or now,
                }

                # Use update_or_create to sync
                user, was_created = User.objects.update_or_create(
                    id=user_id,
                    defaults=user_data
                )

                if was_created:
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Created user: {username} (ID: {user_id})')
                    )
                else:
                    updated += 1
                    if options.get('verbosity', 1) >= 2:
                        self.stdout.write(f'  ↻ Updated user: {username} (ID: {user_id})')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error importing user {username} (ID: {user_id}): {str(e)}')
                )
                skipped += 1
                continue

        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 Import Summary:')
        self.stdout.write('=' * 70)
        self.stdout.write(f'  Total users found: {len(rows)}')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {created}'))
        self.stdout.write(f'  ↻ Updated: {updated}')
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Skipped: {skipped}'))
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Import users completed'))
