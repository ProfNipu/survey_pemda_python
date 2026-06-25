from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    """Dashboard utama"""
    
    # Calculate statistics
    today = timezone.now().date()
    
    # Minimal stats (instance dasar_python only)
    total_pegawai = 0
    pegawai_aktif = 0
    
    # Calculate retirement (assuming retirement at 58 years old)
    retirement_date = today + timedelta(days=730)  # 2 years from now
    menuju_pensiun = 5  # Placeholder - will calculate from birth dates
    
    # SIASN sync status (disabled in minimal instance)
    last_sync_hours = 0
    
    # Status distribution placeholders
    pns_count = 0
    cpns_count = 0
    pppk_count = 0
    honorer_count = 0
    
    # Calculate percentages
    pns_percentage = (pns_count / total_pegawai * 100) if total_pegawai > 0 else 0
    pppk_percentage = (pppk_count / total_pegawai * 100) if total_pegawai > 0 else 0
    honorer_percentage = (honorer_count / total_pegawai * 100) if total_pegawai > 0 else 0
    
    siasn_status = {
        'class': 'warning',
        'icon': 'exclamation-triangle',
        'text': 'Disconnected'
    }
    
    # Recent activities (sample data)
    recent_activities = [
        {
            'title': 'Data pegawai berhasil disinkronkan',
            'description': 'Sinkronisasi data dari SIASN berhasil untuk 25 pegawai',
            'icon': 'fas fa-sync-alt',
            'type': 'success',
            'created_at': timezone.now() - timedelta(minutes=30)
        },
        {
            'title': 'Pegawai baru ditambahkan',
            'description': 'John Doe berhasil ditambahkan ke sistem',
            'icon': 'fas fa-user-plus',
            'type': 'primary',
            'created_at': timezone.now() - timedelta(hours=2)
        },
        {
            'title': 'Laporan bulanan dibuat',
            'description': 'Laporan kepegawaian bulan Oktober 2024 telah dibuat',
            'icon': 'fas fa-file-pdf',
            'type': 'info',
            'created_at': timezone.now() - timedelta(hours=5)
        }
    ]
    
    stats = {
        'total_pegawai': total_pegawai,
        'pegawai_aktif': pegawai_aktif,
        'menuju_pensiun': menuju_pensiun,
        'last_sync_hours': last_sync_hours,
        'pns_count': pns_count,
        'pppk_count': pppk_count,
        'honorer_count': honorer_count,
        'pns_percentage': pns_percentage,
        'pppk_percentage': pppk_percentage,
        'honorer_percentage': honorer_percentage,
    }
    
    context = {
        'today': today,
        'stats': stats,
        'recent_activities': recent_activities,
        'siasn_status': siasn_status,
    }
    
    return render(request, 'dashboard/index.html', context)
