"""
Seed Initial Permission Data
Creates initial functions, controls, modules, and example rules
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.manajemen.models import (
    PermissionFunction,
    PermissionControl,
    PermissionModule,
    PermissionRule,
    RoleRule
)


class Command(BaseCommand):
    help = 'Seed initial permission data (functions, controls, modules)'
    
    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding Permission Data'))
        self.stdout.write('=' * 70)
        
        # Seed Functions
        self.seed_functions()
        
        # Seed Controls
        self.seed_controls()
        
        # Seed Modules
        self.seed_modules()
        
        # Create example rules
        self.create_example_rules()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Permission seeding completed!'))
        self.stdout.write('')
    
    def seed_functions(self):
        """Seed common functions/actions"""
        self.stdout.write('\n📋 Seeding Functions...')
        
        functions = [
            ('view', 'Lihat', 'Melihat/menampilkan data'),
            ('create', 'Tambah', 'Menambah data baru'),
            ('edit', 'Edit', 'Mengubah data yang ada'),
            ('delete', 'Hapus', 'Menghapus data'),
            ('bulk_delete', 'Hapus Banyak', 'Menghapus banyak data sekaligus (bulk/multi delete)'),
            ('export', 'Export', 'Export data ke file (Excel/PDF)'),
            ('import', 'Import', 'Import data dari file'),
            ('approve', 'Approve', 'Menyetujui data/pengajuan'),
            ('reject', 'Reject', 'Menolak data/pengajuan'),
            ('print', 'Cetak', 'Mencetak data/laporan'),
            ('sync', 'Sinkronisasi', 'Sinkronisasi data dengan sistem lain'),
        ]
        
        for nama, label, desk in functions:
            func, created = PermissionFunction.objects.get_or_create(
                nama_fungsi=nama,
                defaults={
                    'label_fungsi': label,
                    'deskripsi_fungsi': desk
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created function: {label} ({nama})')
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Total functions: {PermissionFunction.objects.count()}'))
    
    def seed_controls(self):
        """Seed common controls/resources"""
        self.stdout.write('\n📋 Seeding Controls...')
        
        controls = [
            # Dashboard
            ('dashboard_main', 'Dashboard Utama', 'Halaman dashboard utama'),
            ('dashboard_analytics', 'Dashboard Analytics', 'Analytics dan statistik'),
            
            # Pegawai
            ('ms_pegawai', 'Master Pegawai', 'Data master pegawai'),
            ('pegawai_siasn', 'Pegawai SIASN', 'Data pegawai dari SIASN'),
            ('pegawai_profil', 'Profil Pegawai', 'Profil detail pegawai'),
            
            # Riwayat
            ('riwayat_jabatan', 'Riwayat Jabatan', 'Riwayat jabatan pegawai'),
            ('riwayat_pendidikan', 'Riwayat Pendidikan', 'Riwayat pendidikan pegawai'),
            ('riwayat_penghargaan', 'Riwayat Penghargaan', 'Riwayat penghargaan pegawai'),
            
            # SIASN
            ('siasn_dashboard', 'SIASN Dashboard', 'Dashboard integrasi SIASN'),
            ('siasn_cache', 'SIASN Cache', 'Data cache SIASN'),
            ('siasn_logs', 'SIASN Logs', 'Log API SIASN'),
            ('siasn_token', 'SIASN Token', 'Token akses SIASN'),
            
            # Laporan
            ('laporan_pegawai', 'Laporan Pegawai', 'Laporan data pegawai'),
            ('laporan_statistik', 'Laporan Statistik', 'Laporan statistik'),
            
            # Settings
            ('manajemen_user', 'Manajemen User', 'Manajemen pengguna sistem'),
            ('manajemen_permission', 'Manajemen Permission', 'Manajemen permission & roles'),
        ]
        
        for nama, label, desk in controls:
            ctrl, created = PermissionControl.objects.get_or_create(
                nama_kontrol=nama,
                defaults={
                    'label_kontrol': label,
                    'deskripsi_kontrol': desk
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created control: {label} ({nama})')
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Total controls: {PermissionControl.objects.count()}'))
    
    def seed_modules(self):
        """Seed sidebar modules"""
        self.stdout.write('\n📋 Seeding Modules...')
        
        modules = [
            ('dashboard', 'Dashboard', 'Dashboard utama sistem', 'fas fa-tachometer-alt', 1),
            ('pegawai', 'Data Pegawai', 'Manajemen data pegawai', 'fas fa-users', 2),
            ('riwayat', 'Riwayat', 'Riwayat pegawai', 'fas fa-history', 3),
            ('siasn', 'SIASN Integration', 'Integrasi dengan SIASN', 'fas fa-sync-alt', 4),
            ('laporan', 'Laporan', 'Laporan dan analytics', 'fas fa-chart-bar', 5),
            ('pengaturan', 'Pengaturan', 'Pengaturan sistem', 'fas fa-cogs', 6),
        ]
        
        for nama, label, desk, icon, order in modules:
            mod, created = PermissionModule.objects.get_or_create(
                nama_module=nama,
                defaults={
                    'label_module': label,
                    'deskripsi_module': desk,
                    'icon': icon,
                    'order': order
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created module: {label} ({nama})')
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Total modules: {PermissionModule.objects.count()}'))
    
    def create_example_rules(self):
        """Create some example permission rules"""
        self.stdout.write('\n📋 Creating Example Rules...')
        
        # Get objects
        view_func = PermissionFunction.objects.get(nama_fungsi='view')
        create_func = PermissionFunction.objects.get(nama_fungsi='create')
        edit_func = PermissionFunction.objects.get(nama_fungsi='edit')
        
        dashboard_module = PermissionModule.objects.get(nama_module='dashboard')
        pegawai_module = PermissionModule.objects.get(nama_module='pegawai')
        siasn_module = PermissionModule.objects.get(nama_module='siasn')
        
        dashboard_ctrl = PermissionControl.objects.get(nama_kontrol='dashboard_main')
        ms_pegawai_ctrl = PermissionControl.objects.get(nama_kontrol='ms_pegawai')
        siasn_dashboard_ctrl = PermissionControl.objects.get(nama_kontrol='siasn_dashboard')
        
        # Example rules
        example_rules = [
            (dashboard_module, dashboard_ctrl, view_func),
            (pegawai_module, ms_pegawai_ctrl, view_func),
            (pegawai_module, ms_pegawai_ctrl, create_func),
            (pegawai_module, ms_pegawai_ctrl, edit_func),
            (siasn_module, siasn_dashboard_ctrl, view_func),
        ]
        
        created_count = 0
        for module, control, function in example_rules:
            rule, created = PermissionRule.objects.get_or_create(
                module=module,
                control=control,
                function=function
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created rule: {rule}')
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Total rules: {PermissionRule.objects.count()} ({created_count} new)'))
