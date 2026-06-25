from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from django_tables2 import RequestConfig
import csv
from apps.manajemen.decorators import permission_required_403
from .models_survey_config import SurveyConfiguration, SurveyAspek, SurveyResponse
from .forms_survey_config import SurveyConfigurationForm, SurveyAspekFormSet, DynamicSurveyResponseForm
from .tables import SurveyConfigurationTable


# ============================================================================
# SURVEY CONFIGURATION VIEWS (Super Admin)
# ============================================================================

@permission_required_403('survey', 'survey_config', 'view')
def survey_config_list(request):
    """List view untuk Konfigurasi Survey"""
    
    # ---- AJAX SAVE/LOAD SELECTIONS ----
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        content_type = request.headers.get('Content-Type', '') or ''
        if 'application/json' in content_type:
            import json
            try:
                payload = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else (request.body or '')
                data = json.loads(payload or '{}')
            except Exception:
                data = {}
            action = data.get('action')
            if action == 'save_selection':
                page_key = data.get('page_key', 'survey_config_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'survey_config_list')
                try:
                    from apps.manajemen.models import UserTableSelection
                    selection = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                    return JsonResponse({'success': True, 'selected_ids': selection.selected_ids})
                except:
                    return JsonResponse({'success': True, 'selected_ids': []})

    # ---- BULK ACTIONS (POST) ----
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')
        from apps.manajemen.helpers import check_permission

        if action in ['export_csv', 'export_excel', 'export_pdf']:
            if not check_permission(request.user, 'survey', 'survey_config', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:survey_config_list')
        
        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'survey_config', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:survey_config_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        
        if selected_ids:
            qs = SurveyConfiguration.objects.filter(id__in=selected_ids).order_by('nama_survey')
            
            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="survey_config.csv"'
                writer = csv.writer(response)
                writer.writerow(['Nama Survey', 'Tahun', 'Periode Mulai', 'Periode Selesai', 'Aspek', 'Response', 'Status'])
                for item in qs:
                    writer.writerow([
                        item.nama_survey,
                        item.tahun,
                        item.periode_mulai.strftime('%d/%m/%Y'),
                        item.periode_selesai.strftime('%d/%m/%Y'),
                        item.aspek_penilaian.count(),
                        item.responses.count(),
                        'Aktif' if item.is_active else 'Nonaktif'
                    ])
                return response
            
            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = list(qs.values_list('nama_survey', flat=True))
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='survey_config_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} konfigurasi survey berhasil dihapus')
                        return redirect('survey:survey_config_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:survey_config_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    qs = SurveyConfiguration.objects.all()
    
    if search_query:
        qs = qs.filter(
            Q(nama_survey__icontains=search_query) |
            Q(deskripsi__icontains=search_query) |
            Q(tahun__icontains=search_query)
        )
    
    qs = qs.order_by('-tahun', '-created_at')
    
    # Create table
    table = SurveyConfigurationTable(qs)
    table.request = request
    
    # Pagination
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    RequestConfig(request, paginate={'per_page': per_page}).configure(table)
    
    context = {
        'table': table,
        'total': qs.count(),
        'search_query': search_query,
    }
    
    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'survey_config/partials/_table.html', context)
    
    return render(request, 'survey_config/list.html', context)


@permission_required_403('survey', 'survey_config', 'create')
def survey_config_create(request):
    """Create konfigurasi survey baru"""
    
    if request.method == 'POST':
        form = SurveyConfigurationForm(request.POST)
        formset = SurveyAspekFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                config = form.save(commit=False)
                config.created_by = request.user
                config.save()
                
                formset.instance = config
                formset.save()
                
                messages.success(request, f'Konfigurasi survey "{config.nama_survey}" berhasil dibuat')
                return redirect('survey:survey_config_list')
    else:
        form = SurveyConfigurationForm()
        formset = SurveyAspekFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'edit_mode': False,
    }
    
    return render(request, 'survey_config/form.html', context)


@permission_required_403('survey', 'survey_config', 'edit')
def survey_config_edit(request, pk):
    """Edit konfigurasi survey"""
    
    config = get_object_or_404(SurveyConfiguration, id=pk)
    
    if request.method == 'POST':
        form = SurveyConfigurationForm(request.POST, instance=config)
        formset = SurveyAspekFormSet(request.POST, instance=config)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                
                messages.success(request, f'Konfigurasi survey "{config.nama_survey}" berhasil diupdate')
                return redirect('survey:survey_config_list')
    else:
        form = SurveyConfigurationForm(instance=config)
        formset = SurveyAspekFormSet(instance=config)
    
    context = {
        'form': form,
        'formset': formset,
        'config': config,
        'edit_mode': True,
    }
    
    return render(request, 'survey_config/form.html', context)


@permission_required_403('survey', 'survey_config', 'delete')
def survey_config_delete(request, pk):
    """Delete konfigurasi survey"""
    
    config = get_object_or_404(SurveyConfiguration, id=pk)
    
    if request.method == 'POST':
        nama_survey = config.nama_survey
        config.delete()
        messages.success(request, f'Konfigurasi survey "{nama_survey}" berhasil dihapus')
        return redirect('survey:survey_config_list')
    
    context = {
        'config': config,
        'response_count': config.responses.count(),
    }
    
    return render(request, 'survey_config/delete.html', context)


# ============================================================================
# DYNAMIC SURVEY VIEWS (Pegawai)
# ============================================================================

def survey_form_dynamic(request, config_id=None):
    """Form survey dinamis berdasarkan konfigurasi"""
    
    # Get active survey config
    if config_id:
        survey_config = get_object_or_404(SurveyConfiguration, id=config_id, is_active=True)
    else:
        survey_config = SurveyConfiguration.objects.filter(is_active=True).first()
        if not survey_config:
            messages.error(request, 'Tidak ada survey yang aktif saat ini')
            return redirect('survey:penilaian_list')
    
    if request.method == 'POST':
        form = DynamicSurveyResponseForm(survey_config, request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            
            # Set data penilai dari user yang login
            if request.user:
                response.nip_penilai = request.user.username
                response.nama_penilai = getattr(request.user, 'name', request.user.username)
                response.jabatan_penilai = 'Pegawai'  # Default, bisa diambil dari database
                response.unit_kerja_penilai = 'Unit Kerja'  # Default, bisa diambil dari database
            
            response.status = 'submitted'
            response.save()
            form.save()  # Save detail jawaban
            
            messages.success(request, f'Penilaian untuk {response.nama_dinilai} berhasil disimpan')
            return redirect('survey:survey_response_list')
    else:
        form = DynamicSurveyResponseForm(survey_config)
    
    context = {
        'survey_config': survey_config,
        'form': form,
        'aspek_list': survey_config.aspek_penilaian.filter(is_active=True).order_by('urutan'),
    }
    
    return render(request, 'survey_dynamic/form.html', context)


def survey_response_list(request):
    """List response survey user yang login"""
    
    responses = SurveyResponse.objects.all().order_by('-created_at')
    
    # Filter by user if not admin
    if not request.user.groups.filter(name='Super Admin').exists():
        responses = responses.filter(nip_penilai=request.user.username)
    
    context = {
        'responses': responses,
        'total': responses.count(),
    }
    
    return render(request, 'survey_dynamic/response_list.html', context)


def survey_response_detail(request, pk):
    """Detail response survey"""
    
    response = get_object_or_404(SurveyResponse, id=pk)
    
    # Check permission
    if not request.user.groups.filter(name='Super Admin').exists():
        if response.nip_penilai != request.user.username:
            messages.error(request, 'Anda tidak memiliki akses ke data ini')
            return redirect('survey:survey_response_list')
    
    context = {
        'response': response,
        'detail_jawaban': response.detail_jawaban.select_related('aspek').order_by('aspek__urutan'),
    }
    
    return render(request, 'survey_dynamic/response_detail.html', context)