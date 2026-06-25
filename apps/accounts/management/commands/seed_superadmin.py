"""
Management command untuk seed super admin account
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed super admin account untuk aplikasi-test'

    def handle(self, *args, **options):
        # Data super admin
        admin_data = {
            'username': 'admin',
            'name': 'Super Administrator',
            'email': 'admin@aplikasi-test.local',
            'password': 'admin123',  # Password akan di-hash otomatis
            'id_pegawai': None,
            'user_id_opd': None,
            'image': '',
            'id_status': 1,
            'is_active': True,
        }
        
        # Cek apakah user sudah ada
        if User.objects.filter(username=admin_data['username']).exists():
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  User "{admin_data["username"]}" sudah ada!'
            ))
            
            # Tampilkan info user
            user = User.objects.get(username=admin_data['username'])
            self.stdout.write(f'\nInfo User:')
            self.stdout.write(f'  - Username: {user.username}')
            self.stdout.write(f'  - Name: {user.name}')
            self.stdout.write(f'  - Email: {user.email}')
            self.stdout.write(f'  - Active: {user.is_active}')
            self.stdout.write(f'  - Created: {user.date_joined}')
            
            # Tanya apakah mau reset password
            self.stdout.write(self.style.WARNING(
                f'\nJika mau reset password, hapus dulu user ini dan run command lagi.'
            ))
            return
        
        # Create super admin
        self.stdout.write('\n🔐 Creating super admin account...\n')
        
        user = User.objects.create_user(
            username=admin_data['username'],
            email=admin_data['email'],
            password=admin_data['password'],  # create_user akan hash password
            name=admin_data['name'],
            id_pegawai=admin_data['id_pegawai'],
            user_id_opd=admin_data['user_id_opd'],
            image=admin_data['image'],
            id_status=admin_data['id_status'],
            is_active=admin_data['is_active'],
        )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Super admin created successfully!\n'))
        
        # Tampilkan kredensial
        self.stdout.write('=' * 50)
        self.stdout.write(self.style.SUCCESS('LOGIN CREDENTIALS:'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'Username : {admin_data["username"]}')
        self.stdout.write(f'Password : {admin_data["password"]}')
        self.stdout.write(f'Name     : {admin_data["name"]}')
        self.stdout.write(f'Email    : {admin_data["email"]}')
        self.stdout.write('=' * 50)
        
        self.stdout.write('\n📝 Catatan:')
        self.stdout.write('  - Password di-hash dengan bcrypt')
        self.stdout.write('  - User dapat login ke dashboard')
        self.stdout.write('  - Permission di-manage via apps/permissions')
        self.stdout.write('  - Ganti password setelah first login!\n')
