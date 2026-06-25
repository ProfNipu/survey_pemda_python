"""
Management command untuk check progress password migration
dari Laravel hash ke Universal hash (Argon2)

Usage:
    python manage.py check_password_migration
    python manage.py check_password_migration --detailed
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from accounts.models import User


class Command(BaseCommand):
    help = 'Check password hash migration progress (Laravel → Universal)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed breakdown by hash algorithm',
        )
        parser.add_argument(
            '--sample',
            type=int,
            default=0,
            help='Show sample of users still using Laravel hash (default: 0)',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('PASSWORD MIGRATION PROGRESS'))
        self.stdout.write('=' * 70)
        self.stdout.write('')

        # Total users
        total_users = User.objects.count()
        
        # Count by hash type
        argon2_count = User.objects.filter(password__startswith='argon2').count()
        bcrypt_count = User.objects.filter(password__startswith='bcrypt$').count()
        bcrypt_sha256_count = User.objects.filter(password__startswith='bcrypt_sha256').count()
        laravel_count = User.objects.filter(password__startswith='laravel_bcrypt').count()
        pbkdf2_count = User.objects.filter(password__startswith='pbkdf2').count()
        other_count = total_users - (argon2_count + bcrypt_count + bcrypt_sha256_count + laravel_count + pbkdf2_count)

        # Calculate percentages
        argon2_pct = (argon2_count / total_users * 100) if total_users > 0 else 0
        laravel_pct = (laravel_count / total_users * 100) if total_users > 0 else 0
        migrated_count = argon2_count + bcrypt_count
        migrated_pct = (migrated_count / total_users * 100) if total_users > 0 else 0

        # Summary
        self.stdout.write(f'Total Users: {total_users:,}')
        self.stdout.write('')
        
        self.stdout.write('Hash Types:')
        self.stdout.write(f'  ✅ Argon2 (Modern):        {argon2_count:>6,} ({argon2_pct:>5.1f}%)')
        self.stdout.write(f'  ✅ Bcrypt (Universal):     {bcrypt_count:>6,} ({bcrypt_count/total_users*100:>5.1f}%)')
        self.stdout.write(f'  ⚠️  Laravel Bcrypt (Old):   {laravel_count:>6,} ({laravel_pct:>5.1f}%)')
        
        if options['detailed']:
            self.stdout.write(f'  ℹ️  Bcrypt SHA256:          {bcrypt_sha256_count:>6,} ({bcrypt_sha256_count/total_users*100:>5.1f}%)')
            self.stdout.write(f'  ℹ️  PBKDF2:                 {pbkdf2_count:>6,} ({pbkdf2_count/total_users*100:>5.1f}%)')
            if other_count > 0:
                self.stdout.write(f'  ℹ️  Other:                  {other_count:>6,} ({other_count/total_users*100:>5.1f}%)')
        
        self.stdout.write('')
        self.stdout.write('-' * 70)
        self.stdout.write('')
        
        # Migration status
        self.stdout.write('Migration Status:')
        self.stdout.write(f'  ✅ Migrated (Universal):   {migrated_count:>6,} ({migrated_pct:>5.1f}%)')
        self.stdout.write(f'  ⏳ Pending (Laravel):      {laravel_count:>6,} ({laravel_pct:>5.1f}%)')
        self.stdout.write('')
        
        # Progress bar
        bar_width = 50
        migrated_bar = int(migrated_pct / 100 * bar_width)
        pending_bar = bar_width - migrated_bar
        
        self.stdout.write('Progress:')
        progress_bar = f'  [{"█" * migrated_bar}{"░" * pending_bar}] {migrated_pct:.1f}%'
        self.stdout.write(self.style.SUCCESS(progress_bar))
        self.stdout.write('')
        
        # Status message
        if migrated_pct >= 90:
            self.stdout.write(self.style.SUCCESS('🎉 Migration hampir selesai!'))
        elif migrated_pct >= 50:
            self.stdout.write(self.style.WARNING('⏳ Migration berjalan...'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Migration baru dimulai'))
        
        self.stdout.write('')
        self.stdout.write('-' * 70)
        self.stdout.write('')
        
        # Recommendation
        self.stdout.write('Recommendations:')
        if laravel_pct > 50:
            self.stdout.write('  • Password akan otomatis migrate saat user login')
            self.stdout.write('  • Tidak perlu action manual')
            self.stdout.write('  • Biarkan auto-migration berjalan natural')
        elif laravel_pct > 10:
            self.stdout.write('  • Mayoritas user sudah migrate!')
            self.stdout.write('  • Sisa user akan migrate saat mereka login')
        else:
            self.stdout.write('  ✅ Migration hampir complete!')
            self.stdout.write('  ✅ Semua password baru menggunakan Argon2')
        
        # Sample users with Laravel hash
        if options['sample'] > 0 and laravel_count > 0:
            self.stdout.write('')
            self.stdout.write('-' * 70)
            self.stdout.write('')
            self.stdout.write(f'Sample Users (masih Laravel hash): {options["sample"]} users')
            self.stdout.write('')
            
            sample_users = User.objects.filter(
                password__startswith='laravel_bcrypt'
            )[:options['sample']]
            
            for idx, user in enumerate(sample_users, 1):
                self.stdout.write(
                    f'  {idx}. {user.username:<20} | {user.name[:30]:<30} | '
                    f'{user.password[:40]}...'
                )
        
        self.stdout.write('')
        self.stdout.write('=' * 70)
        self.stdout.write('')
        
        # Info
        self.stdout.write('ℹ️  Info:')
        self.stdout.write('  • Argon2: OWASP recommended, most secure')
        self.stdout.write('  • Bcrypt: Standard, universal format')
        self.stdout.write('  • Laravel: Old format, backward compatibility only')
        self.stdout.write('')
        self.stdout.write('📖 Full guide: PASSWORD_MIGRATION_GUIDE.md')
        self.stdout.write('')
