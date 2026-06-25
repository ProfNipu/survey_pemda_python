from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django_tables2 import RequestConfig
from apps.manajemen.decorators import permission_required_403
from apps.accounts.services import EsimpegAPIService
from .tables import PegawaiTable
from .models import Pegawai, SyncLog, SyncProgress
import logging
import time
import uuid
import threading

logger = logging.getLogger(__name__)


@permission_required_403('api_simpeg', 'pegawai', 'view')
def pegawai_list(request):
    """
    View untuk menampilkan daftar pegawai dari DATABASE (bukan API)
    Data di-sync manual dari API ESIMPEG menggunakan tombol Sinkronisasi
    """
    
    # Get parameters - EXACTLY like manajemen fungsi
    search = request.GET.get('search', '').strip()
    id_opd = request.GET.get('id_opd', '')
    kode_eselon = request.GET.get('kode_eselon', '')
    
    # Query from DATABASE (not API)
    pegawai_qs = Pegawai.objects.all()
    
    # Apply filters
    if search:
        pegawai_qs = pegawai_qs.filter(
            Q(nama_pegawai__icontains=search) |
            Q(nip_baru__icontains=search) |
            Q(nip_lama__icontains=search) |
            Q(nama_jabatan__icontains=search) |
            Q(nm_opd__icontains=search)
        )
    
    if id_opd:
        try:
            pegawai_qs = pegawai_qs.filter(id_opd=int(id_opd))
        except (ValueError, TypeError):
            pass
    
    if kode_eselon:
        try:
            pegawai_qs = pegawai_qs.filter(kode_eselon=int(kode_eselon))
        except (ValueError, TypeError):
            pass
    
    # Default ordering - SAMA SEPERTI ESIMPEG
    # Order by: Eselon Group Priority → OPD (id_opd_urut) → Eselon → Status → Golongan → ID Pegawai
    from django.db.models import Case, When, Value, IntegerField, Q
    
    pegawai_qs = pegawai_qs.annotate(
        _eselon_group_priority=Case(
            When(kode_eselon__in=[11, 12], then=Value(1)),      # Eselon II.a, II.b
            When(kode_eselon__in=[21, 22], then=Value(2)),      # Eselon III.a, III.b
            When(kode_eselon__isnull=True, then=Value(99)),     # Non-Eselon
            default=Value(3),                                    # Eselon lainnya
            output_field=IntegerField(),
        ),
        _status_priority=Case(
            When(kategori_pegawai=2, then=Value(1)),            # PNS
            When(kategori_pegawai=1, then=Value(2)),            # CPNS
            When(akhir_kerja_p3k__isnull=False, then=Value(3)), # P3K
            default=Value(4),                                    # Others
            output_field=IntegerField(),
        )
    ).order_by(
        '_eselon_group_priority',   # 1. Eselon group priority (1, 2, 3, 99)
        'id_opd_urut',              # 2. OPD by id_opd_urut (A_12 - URUTAN RESMI OPD!)
        'kode_eselon',              # 3. Eselon ID (ascending)
        '_status_priority',         # 4. Status priority (PNS=1, CPNS=2, P3K=3)
        'id_golongan',              # 5. Golongan (ascending)
        'id_pegawai',               # 6. ID Pegawai (tie-breaker)
    )
    
    total = pegawai_qs.count()
    
    # Create django-tables2 table
    table = PegawaiTable(pegawai_qs)
    
    # Configure pagination - EXACTLY like manajemen fungsi
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    RequestConfig(request, paginate={'per_page': per_page}).configure(table)
    
    # Get last sync info
    last_sync = SyncLog.objects.filter(status='success').first()
    
    context = {
        'table': table,
        'total': total,
        'search_query': search,
        'id_opd': id_opd,
        'kode_eselon': kode_eselon,
        'last_sync': last_sync,
    }
    
    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'api_simpeg/partials/_pegawai_table.html', context)
    
    return render(request, 'api_simpeg/pegawai_list.html', context)


@permission_required_403('api_simpeg', 'pegawai', 'sync')
def pegawai_sync(request):
    """
    Sync data pegawai dari API ESIMPEG ke database Survey Pemda
    Dengan progress tracking real-time menggunakan background thread
    """
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    # Get token from session
    esimpeg_token = request.session.get('esimpeg_access_token')
    
    # If no token, check if password provided in request
    if not esimpeg_token:
        password = request.POST.get('password')
        
        if not password:
            # No token and no password - return error to trigger popup
            return JsonResponse({
                'success': False,
                'error': 'Token ESIMPEG tidak ditemukan. Silakan masukkan password ESIMPEG Anda.',
                'code': 'PASSWORD_REQUIRED'
            }, status=401)
        
        # Try to login with provided password
        logger.info(f"No ESIMPEG token found for user {request.user.username}, attempting login with password...")
        
        api_service = EsimpegAPIService()
        login_result = api_service.login(
            username=request.user.username,
            password=password
        )
        
        if login_result and 'access_token' in login_result:
            esimpeg_token = login_result['access_token']
            request.session['esimpeg_access_token'] = esimpeg_token
            request.session['esimpeg_refresh_token'] = login_result.get('refresh_token')
            logger.info(f"Login successful for user {request.user.username}")
        else:
            return JsonResponse({
                'success': False,
                'error': 'Login ke ESIMPEG gagal. Password salah atau akun tidak ditemukan di ESIMPEG.',
                'code': 'LOGIN_FAILED'
            }, status=401)
    
    # Generate unique sync ID
    sync_id = str(uuid.uuid4())[:8]
    
    # Create progress tracker
    progress = SyncProgress.objects.create(
        sync_id=sync_id,
        user=request.user,
        status='running'
    )
    
    # Start sync in background thread
    sync_thread = threading.Thread(
        target=_run_sync_in_background,
        args=(sync_id, request.user.id, esimpeg_token)
    )
    sync_thread.daemon = True
    sync_thread.start()
    
    # Return immediately with sync_id
    return JsonResponse({
        'success': True,
        'sync_id': sync_id,
        'message': 'Sync started in background'
    })


def _run_sync_in_background(sync_id, user_id, esimpeg_token):
    """
    Background function untuk sync pegawai
    Runs in separate thread
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    start_time = time.time()
    api_service = EsimpegAPIService()
    
    try:
        # Get progress object
        progress = SyncProgress.objects.get(sync_id=sync_id)
        user = User.objects.get(id=user_id)
        
        # Create sync log
        sync_log = SyncLog.objects.create(
            synced_by=user,
            status='partial'
        )
        
        total_records = 0
        new_records = 0
        updated_records = 0
        
        # First, get total pages
        first_data = api_service.get_pegawai_list(
            token=esimpeg_token,
            page=1,
            per_page=100,
            search=None,
            id_opd=None
        )
        
        if not first_data:
            raise Exception("Gagal mengambil data dari API ESIMPEG")
        
        total_pages = first_data.get('pagination', {}).get('total_pages', 1)
        total_items = first_data.get('pagination', {}).get('total', 0)
        
        # Update progress with totals
        progress.total_pages = total_pages
        progress.total_records = total_items
        progress.save()
        
        logger.info(f"[Sync {sync_id}] Starting sync: {total_pages} pages, {total_items} records")
        
        # Process first page
        items = first_data.get('items', [])
        for item in items:
            id_pegawai = item.get('id_pegawai')
            if not id_pegawai:
                continue
            
            # Prepare data with validation for numeric fields
            kode_golongan = item.get('kodeGolongan')
            kode_eselon = item.get('kodeEselon')
            kategori_pegawai_raw = item.get('kategoriPegawai')
            
            pegawai_data = {
                'nip_baru': item.get('nipBaru'),
                'nip_lama': item.get('nipLama'),
                'nama_pegawai': item.get('namaPegawai', ''),
                'tempat_lahir': item.get('tempatLahir'),
                'tanggal_lahir': item.get('tanggalLahir'),
                'jenis_kelamin': item.get('jenisKelamin'),
                'alamat_rumah': item.get('alamatRumah'),
                'no_hp': item.get('nohp'),
                'id_jabatan': item.get('id_jabatan'),
                'nama_jabatan': item.get('namaJabatan'),
                'masa_kerja_jabatan': item.get('masaKerjaJabatan'),
                'kode_eselon': int(kode_eselon) if kode_eselon and str(kode_eselon).strip() else None,
                'id_opd': item.get('id_opd'),
                'nm_opd': item.get('nm_opd'),
                'id_opd_urut': item.get('no_urut') or None,
                'is_opd_induk': bool(item.get('is_opd_induk', False)),
                'id_sub_opd': item.get('id_sub_opd'),
                'nm_sub_opd': item.get('nm_sub_opd'),
                'id_golongan': int(kode_golongan) if kode_golongan and str(kode_golongan).strip() else None,
                'nama_golongan': item.get('namaGolongan'),
                'nama_pangkat': item.get('namaPangkat'),
                'kategori_pegawai': int(kategori_pegawai_raw) if kategori_pegawai_raw and str(kategori_pegawai_raw).strip() else None,
                'nama_kategori_pegawai': item.get('namaKategoriPegawai'),
                'tmt_cpns': item.get('tmtCPNS'),
                'masa_kerja_tahun': item.get('masaKerjaTahun') or None,
                'masa_kerja_bulan': item.get('masaKerjaBulan') or None,
                'akhir_kerja_p3k': item.get('akhirKerjaP3K'),
                'raw_data': item,
                'synced_by': user,
            }
            
            pegawai, created = Pegawai.objects.update_or_create(
                id_pegawai=id_pegawai,
                defaults=pegawai_data
            )
            
            if created:
                new_records += 1
            else:
                updated_records += 1
            
            total_records += 1
        
        # Update progress after first page
        progress.current_page = 1
        progress.processed_records = total_records
        progress.new_records = new_records
        progress.updated_records = updated_records
        progress.save()
        
        logger.info(f"[Sync {sync_id}] Page 1/{total_pages} completed: {total_records} records")
        
        # Process remaining pages
        for page in range(2, total_pages + 1):
            logger.info(f"[Sync {sync_id}] Processing page {page}/{total_pages}...")
            
            data = api_service.get_pegawai_list(
                token=esimpeg_token,
                page=page,
                per_page=100,
                search=None,
                id_opd=None
            )
            
            if not data or not data.get('items'):
                logger.warning(f"[Sync {sync_id}] No data on page {page}, skipping...")
                continue
            
            items = data.get('items', [])
            
            for item in items:
                id_pegawai = item.get('id_pegawai')
                if not id_pegawai:
                    continue
                
                # Prepare data with validation for numeric fields
                kode_golongan = item.get('kodeGolongan')
                kode_eselon = item.get('kodeEselon')
                kategori_pegawai_raw = item.get('kategoriPegawai')
                
                pegawai_data = {
                    'nip_baru': item.get('nipBaru'),
                    'nip_lama': item.get('nipLama'),
                    'nama_pegawai': item.get('namaPegawai', ''),
                    'tempat_lahir': item.get('tempatLahir'),
                    'tanggal_lahir': item.get('tanggalLahir'),
                    'jenis_kelamin': item.get('jenisKelamin'),
                    'alamat_rumah': item.get('alamatRumah'),
                    'no_hp': item.get('nohp'),
                    'id_jabatan': item.get('id_jabatan'),
                    'nama_jabatan': item.get('namaJabatan'),
                    'masa_kerja_jabatan': item.get('masaKerjaJabatan'),
                    'kode_eselon': int(kode_eselon) if kode_eselon and str(kode_eselon).strip() else None,
                    'id_opd': item.get('id_opd'),
                    'nm_opd': item.get('nm_opd'),
                    'id_opd_urut': item.get('no_urut') or None,
                    'is_opd_induk': bool(item.get('is_opd_induk', False)),
                    'id_sub_opd': item.get('id_sub_opd'),
                    'nm_sub_opd': item.get('nm_sub_opd'),
                    'id_golongan': int(kode_golongan) if kode_golongan and str(kode_golongan).strip() else None,
                    'nama_golongan': item.get('namaGolongan'),
                    'nama_pangkat': item.get('namaPangkat'),
                    'kategori_pegawai': int(kategori_pegawai_raw) if kategori_pegawai_raw and str(kategori_pegawai_raw).strip() else None,
                    'nama_kategori_pegawai': item.get('namaKategoriPegawai'),
                    'tmt_cpns': item.get('tmtCPNS'),
                    'masa_kerja_tahun': item.get('masaKerjaTahun') or None,
                    'masa_kerja_bulan': item.get('masaKerjaBulan') or None,
                    'akhir_kerja_p3k': item.get('akhirKerjaP3K'),
                    'raw_data': item,
                    'synced_by': user,
                }
                
                pegawai, created = Pegawai.objects.update_or_create(
                    id_pegawai=id_pegawai,
                    defaults=pegawai_data
                )
                
                if created:
                    new_records += 1
                else:
                    updated_records += 1
                
                total_records += 1
            
            # Update progress after each page
            progress.current_page = page
            progress.processed_records = total_records
            progress.new_records = new_records
            progress.updated_records = updated_records
            progress.save()
            
            # Log progress
            progress_pct = int((page / total_pages) * 100)
            logger.info(f"[Sync {sync_id}] Progress: {progress_pct}% ({page}/{total_pages} pages, {total_records} records)")
        
        # Mark progress as completed
        progress.status = 'completed'
        progress.save()
        
        # Update sync log
        duration = time.time() - start_time
        sync_log.total_records = total_records
        sync_log.new_records = new_records
        sync_log.updated_records = updated_records
        sync_log.status = 'success'
        sync_log.duration_seconds = duration
        sync_log.save()
        
        logger.info(f"[Sync {sync_id}] Completed: {total_records} records in {duration:.2f}s")
    
    except Exception as e:
        logger.error(f"[Sync {sync_id}] Error: {str(e)}", exc_info=True)
        
        # Mark progress as failed
        try:
            progress = SyncProgress.objects.get(sync_id=sync_id)
            progress.status = 'failed'
            progress.error_message = str(e)
            progress.save()
        except:
            pass
        
        # Update sync log with error
        try:
            if 'sync_log' in locals():
                sync_log.status = 'failed'
                sync_log.error_message = str(e)
                sync_log.duration_seconds = time.time() - start_time
                sync_log.save()
        except:
            pass


@permission_required_403('api_simpeg', 'pegawai', 'view')
def pegawai_sync_progress(request, sync_id):
    """
    Get sync progress for real-time updates
    """
    try:
        progress = SyncProgress.objects.get(sync_id=sync_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'status': progress.status,
            'current_page': progress.current_page,
            'total_pages': progress.total_pages,
            'processed_records': progress.processed_records,
            'total_records': progress.total_records,
            'new_records': progress.new_records,
            'updated_records': progress.updated_records,
            'progress_percentage': progress.progress_percentage,
            'error_message': progress.error_message
        })
    except SyncProgress.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Progress not found'
        }, status=404)
