from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.db import models
from django_tables2 import RequestConfig
import csv
import json
from apps.manajemen.decorators import permission_required_403
from apps.manajemen.helpers import check_permission
from .models import JenisSurvey, PertanyaanSurvey, RespondenSurvey, JawabanSurvey, PeriodeSurvey, PenilaianJPT
from .forms import JenisSurveyForm, PertanyaanSurveyForm, RespondenSurveyForm, JawabanSurveyForm, PeriodeSurveyForm, PenilaianJPTForm
from .tables import JenisSurveyTable, PertanyaanSurveyTable, RespondenSurveyTable, JawabanSurveyTable, PeriodeSurveyTable, PenilaianJPTTable


# ============================================================================
# JENIS SURVEY VIEWS
# ============================================================================

@permission_required_403('survey', 'jenis_survey', 'view')
def jenis_survey_list(request):
    """List view untuk Jenis Survey"""
    
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
                page_key = data.get('page_key', 'jenis_survey_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'jenis_survey_list')
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
            if not check_permission(request.user, 'survey', 'jenis_survey', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:jenis_survey_list')
        
        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'jenis_survey', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:jenis_survey_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        
        if selected_ids:
            qs = JenisSurvey.objects.filter(id__in=selected_ids).order_by('nama')
            
            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="jenis_survey.csv"'
                writer = csv.writer(response)
                writer.writerow(['Kode', 'Nama', 'Deskripsi', 'Status', 'Tanggal Dibuat'])
                for item in qs:
                    writer.writerow([
                        item.kode,
                        item.nama,
                        item.deskripsi or '',
                        'Aktif' if item.is_active else 'Nonaktif',
                        item.created_at.strftime('%d/%m/%Y %H:%M')
                    ])
                return response
            
            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = list(qs.values_list('nama', flat=True))
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='jenis_survey_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} jenis survey berhasil dihapus')
                        return redirect('survey:jenis_survey_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:jenis_survey_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    qs = JenisSurvey.objects.all()
    
    if search_query:
        qs = qs.filter(
            Q(kode__icontains=search_query) |
            Q(nama__icontains=search_query) |
            Q(deskripsi__icontains=search_query)
        )
    
    qs = qs.order_by('-created_at')
    
    # Create table
    table = JenisSurveyTable(qs)
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
        return render(request, 'master_survey/jenis_survey/partials/_table.html', context)
    
    return render(request, 'master_survey/jenis_survey/list.html', context)


@permission_required_403('survey', 'jenis_survey', 'create')
def jenis_survey_create(request):
    """Create view untuk Jenis Survey"""
    
    if request.method == 'POST':
        form = JenisSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jenis Survey berhasil ditambahkan')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"jenis-survey-form-success": {"message": "Jenis Survey berhasil ditambahkan", "redirect": "%s"}}' % reverse('survey:jenis_survey_list'),
                })
            
            return redirect('survey:jenis_survey_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'jenis-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'master_survey/jenis_survey/form.html', {
            'form': form,
            'edit_mode': False
        })
    
    # GET request
    form = JenisSurveyForm()
    return render(request, 'master_survey/jenis_survey/form.html', {
        'form': form,
        'edit_mode': False
    })


@permission_required_403('survey', 'jenis_survey', 'edit')
def jenis_survey_edit(request, pk):
    """Edit view untuk Jenis Survey"""
    
    obj = get_object_or_404(JenisSurvey, id=pk)
    
    if request.method == 'POST':
        form = JenisSurveyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jenis Survey berhasil diupdate')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"jenis-survey-form-success": {"message": "Jenis Survey berhasil diupdate", "redirect": "%s"}}' % reverse('survey:jenis_survey_list'),
                })
            
            return redirect('survey:jenis_survey_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'jenis-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'master_survey/jenis_survey/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj
        })
    
    # GET request
    form = JenisSurveyForm(instance=obj)
    return render(request, 'master_survey/jenis_survey/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj
    })


@permission_required_403('survey', 'jenis_survey', 'delete')
def jenis_survey_delete(request, pk):
    """Delete view untuk Jenis Survey"""
    
    obj = get_object_or_404(JenisSurvey, id=pk)
    
    if request.method == 'POST':
        # Check if has pertanyaan
        if obj.pertanyaan.exists():
            messages.error(request, f'Tidak dapat menghapus "{obj.nama}" karena masih memiliki {obj.pertanyaan.count()} pertanyaan')
            return redirect('survey:jenis_survey_list')
        
        obj.delete()
        messages.success(request, f'Jenis Survey "{obj.nama}" berhasil dihapus')
        return redirect('survey:jenis_survey_list')
    
    # GET request - show confirmation
    context = {
        'obj': obj,
        'jumlah_pertanyaan': obj.pertanyaan.count(),
    }
    return render(request, 'master_survey/jenis_survey/delete.html', context)


# ============================================================================
# PERTANYAAN SURVEY VIEWS
# ============================================================================

@permission_required_403('survey', 'pertanyaan_survey', 'view')
def pertanyaan_survey_list(request):
    """List view untuk Pertanyaan Survey"""
    
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
                page_key = data.get('page_key', 'pertanyaan_survey_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'pertanyaan_survey_list')
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
            if not check_permission(request.user, 'survey', 'pertanyaan_survey', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:pertanyaan_survey_list')
        
        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'pertanyaan_survey', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:pertanyaan_survey_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        
        if selected_ids:
            qs = PertanyaanSurvey.objects.filter(id__in=selected_ids).select_related('jenis_survey').order_by('jenis_survey__nama', 'urutan')
            
            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="pertanyaan_survey.csv"'
                writer = csv.writer(response)
                writer.writerow(['Jenis Survey', 'Kode Pertanyaan', 'Pertanyaan', 'Urutan', 'Bobot', 'Status', 'Tanggal Dibuat'])
                for item in qs:
                    writer.writerow([
                        item.jenis_survey.nama,
                        item.kode_pertanyaan,
                        item.pertanyaan,
                        item.urutan,
                        item.bobot,
                        'Aktif' if item.is_active else 'Nonaktif',
                        item.created_at.strftime('%d/%m/%Y %H:%M')
                    ])
                return response
            
            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = list(qs.values_list('pertanyaan', flat=True))
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='pertanyaan_survey_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} pertanyaan survey berhasil dihapus')
                        return redirect('survey:pertanyaan_survey_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:pertanyaan_survey_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    jenis_filter = request.GET.get('jenis', '').strip()
    
    qs = PertanyaanSurvey.objects.select_related('jenis_survey')
    
    if search_query:
        qs = qs.filter(
            Q(kode_pertanyaan__icontains=search_query) |
            Q(pertanyaan__icontains=search_query) |
            Q(jenis_survey__nama__icontains=search_query)
        )
    
    if jenis_filter:
        qs = qs.filter(jenis_survey_id=jenis_filter)
    
    qs = qs.order_by('jenis_survey', 'urutan')
    
    # Create table
    table = PertanyaanSurveyTable(qs)
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
    
    # Get jenis survey for filter dropdown
    jenis_survey_list = JenisSurvey.objects.filter(is_active=True).order_by('nama')
    
    context = {
        'table': table,
        'total': qs.count(),
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'jenis_survey_list': jenis_survey_list,
    }
    
    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'master_survey/pertanyaan_survey/partials/_table.html', context)
    
    return render(request, 'master_survey/pertanyaan_survey/list.html', context)


@permission_required_403('survey', 'pertanyaan_survey', 'create')
def pertanyaan_survey_create(request):
    """Create view untuk Pertanyaan Survey"""
    
    if request.method == 'POST':
        form = PertanyaanSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pertanyaan Survey berhasil ditambahkan')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"pertanyaan-survey-form-success": {"message": "Pertanyaan Survey berhasil ditambahkan", "redirect": "%s"}}' % reverse('survey:pertanyaan_survey_list'),
                })
            
            return redirect('survey:pertanyaan_survey_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'pertanyaan-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'master_survey/pertanyaan_survey/form.html', {
            'form': form,
            'edit_mode': False
        })
    
    # GET request
    form = PertanyaanSurveyForm()
    return render(request, 'master_survey/pertanyaan_survey/form.html', {
        'form': form,
        'edit_mode': False
    })


@permission_required_403('survey', 'pertanyaan_survey', 'edit')
def pertanyaan_survey_edit(request, pk):
    """Edit view untuk Pertanyaan Survey"""
    
    obj = get_object_or_404(PertanyaanSurvey, id=pk)
    
    if request.method == 'POST':
        form = PertanyaanSurveyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pertanyaan Survey berhasil diupdate')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"pertanyaan-survey-form-success": {"message": "Pertanyaan Survey berhasil diupdate", "redirect": "%s"}}' % reverse('survey:pertanyaan_survey_list'),
                })
            
            return redirect('survey:pertanyaan_survey_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'pertanyaan-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'master_survey/pertanyaan_survey/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj
        })
    
    # GET request
    form = PertanyaanSurveyForm(instance=obj)
    return render(request, 'master_survey/pertanyaan_survey/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj
    })


@permission_required_403('survey', 'pertanyaan_survey', 'delete')
def pertanyaan_survey_delete(request, pk):
    """Delete view untuk Pertanyaan Survey"""
    
    obj = get_object_or_404(PertanyaanSurvey, id=pk)
    
    if request.method == 'POST':
        jenis_survey_nama = obj.jenis_survey.nama
        kode = obj.kode_pertanyaan
        obj.delete()
        messages.success(request, f'Pertanyaan "{kode}" dari survey "{jenis_survey_nama}" berhasil dihapus')
        return redirect('survey:pertanyaan_survey_list')
    
    # GET request - show confirmation
    context = {
        'obj': obj,
    }
    return render(request, 'master_survey/pertanyaan_survey/delete.html', context)


# ============================================================================
# RESPONDEN SURVEY VIEWS
# ============================================================================

@permission_required_403('survey', 'responden_survey', 'view')
def responden_survey_list(request):
    """List view untuk Responden Survey"""

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
                page_key = data.get('page_key', 'responden_survey_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'responden_survey_list')
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
            if not check_permission(request.user, 'survey', 'responden_survey', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:responden_survey_list')

        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'responden_survey', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:responden_survey_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]

        if selected_ids:
            from .models import RespondenSurvey
            qs = RespondenSurvey.objects.filter(id__in=selected_ids).order_by('-created_at')

            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="responden_survey.csv"'
                writer = csv.writer(response)
                writer.writerow(['NIP Penilai', 'NIP Dinilai', 'Peran Penilai', 'Status', 'Jumlah Jawaban', 'Tanggal Dibuat'])
                for item in qs:
                    writer.writerow([
                        item.nip_pegawaiPenilai,
                        item.nip_pegawaiDinilai,
                        item.peranPenilai,
                        item.statusData,
                        item.jawaban.count(),
                        item.created_at.strftime('%d/%m/%Y %H:%M')
                    ])
                return response

            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = [f"{item.nip_pegawaiPenilai} → {item.nip_pegawaiDinilai}" for item in qs]
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='responden_survey_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} responden survey berhasil dihapus')
                        return redirect('survey:responden_survey_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:responden_survey_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    from .models import RespondenSurvey
    qs = RespondenSurvey.objects.all()

    if search_query:
        qs = qs.filter(
            Q(nip_pegawaiPenilai__icontains=search_query) |
            Q(nip_pegawaiDinilai__icontains=search_query) |
            Q(peranPenilai__icontains=search_query)
        )

    if status_filter:
        qs = qs.filter(statusData=status_filter)

    qs = qs.order_by('-created_at')

    # Create table
    from .tables import RespondenSurveyTable
    table = RespondenSurveyTable(qs)
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
        'status_filter': status_filter,
    }

    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'master_survey/responden_survey/partials/_table.html', context)

    return render(request, 'master_survey/responden_survey/list.html', context)


@permission_required_403('survey', 'responden_survey', 'create')
def responden_survey_create(request):
    """Create view untuk Responden Survey"""

    if request.method == 'POST':
        from .forms import RespondenSurveyForm
        form = RespondenSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Responden Survey berhasil ditambahkan')

            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"responden-survey-form-success": {"message": "Responden Survey berhasil ditambahkan", "redirect": "%s"}}' % reverse('survey:responden_survey_list'),
                })

            return redirect('survey:responden_survey_list')

        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']

            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'responden-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp

        return render(request, 'master_survey/responden_survey/form.html', {
            'form': form,
            'edit_mode': False
        })

    # GET request
    from .forms import RespondenSurveyForm
    form = RespondenSurveyForm()
    return render(request, 'master_survey/responden_survey/form.html', {
        'form': form,
        'edit_mode': False
    })


@permission_required_403('survey', 'responden_survey', 'edit')
def responden_survey_edit(request, pk):
    """Edit view untuk Responden Survey"""

    from .models import RespondenSurvey
    obj = get_object_or_404(RespondenSurvey, id=pk)

    if request.method == 'POST':
        from .forms import RespondenSurveyForm
        form = RespondenSurveyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Responden Survey berhasil diupdate')

            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"responden-survey-form-success": {"message": "Responden Survey berhasil diupdate", "redirect": "%s"}}' % reverse('survey:responden_survey_list'),
                })

            return redirect('survey:responden_survey_list')

        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']

            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'responden-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp

        return render(request, 'master_survey/responden_survey/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj
        })

    # GET request
    from .forms import RespondenSurveyForm
    form = RespondenSurveyForm(instance=obj)
    return render(request, 'master_survey/responden_survey/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj
    })


@permission_required_403('survey', 'responden_survey', 'view')
def responden_survey_detail(request, pk):
    """Detail view untuk Responden Survey"""

    from .models import RespondenSurvey
    obj = get_object_or_404(RespondenSurvey, id=pk)

    context = {
        'obj': obj,
        'jawaban_list': obj.jawaban.select_related('pertanyaan__jenis_survey').order_by('pertanyaan__urutan'),
    }
    return render(request, 'master_survey/responden_survey/detail.html', context)


@permission_required_403('survey', 'responden_survey', 'delete')
def responden_survey_delete(request, pk):
    """Delete view untuk Responden Survey"""

    from .models import RespondenSurvey
    obj = get_object_or_404(RespondenSurvey, id=pk)

    if request.method == 'POST':
        # Check if has jawaban
        jawaban_count = obj.jawaban.count()
        if jawaban_count > 0:
            messages.error(request, f'Tidak dapat menghapus responden "{obj}" karena masih memiliki {jawaban_count} jawaban')
            return redirect('survey:responden_survey_list')

        obj.delete()
        messages.success(request, f'Responden Survey "{obj}" berhasil dihapus')
        return redirect('survey:responden_survey_list')

    # GET request - show confirmation
    context = {
        'obj': obj,
        'jumlah_jawaban': obj.jawaban.count(),
    }
    return render(request, 'master_survey/responden_survey/delete.html', context)


# ============================================================================
# JAWABAN SURVEY VIEWS
# ============================================================================

@permission_required_403('survey', 'jawaban_survey', 'view')
def jawaban_survey_list(request):
    """List view untuk Jawaban Survey"""

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
                page_key = data.get('page_key', 'jawaban_survey_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'jawaban_survey_list')
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
            if not check_permission(request.user, 'survey', 'jawaban_survey', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:jawaban_survey_list')

        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'jawaban_survey', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:jawaban_survey_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]

        if selected_ids:
            from .models import JawabanSurvey
            qs = JawabanSurvey.objects.filter(id__in=selected_ids).select_related('responden', 'pertanyaan__jenis_survey').order_by('-created_at')

            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="jawaban_survey.csv"'
                writer = csv.writer(response)
                writer.writerow(['Penilai', 'Dinilai', 'Kode Pertanyaan', 'Pertanyaan', 'Nilai', 'Nilai Terbobot', 'Tanggal Jawab'])
                for item in qs:
                    writer.writerow([
                        item.responden.nip_pegawaiPenilai,
                        item.responden.nip_pegawaiDinilai,
                        item.pertanyaan.kode_pertanyaan,
                        item.pertanyaan.pertanyaan,
                        item.nilai,
                        item.nilai_terbobot,
                        item.created_at.strftime('%d/%m/%Y %H:%M')
                    ])
                return response

            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = [f"{item.responden.nip_pegawaiPenilai} - {item.pertanyaan.kode_pertanyaan}" for item in qs]
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='jawaban_survey_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} jawaban survey berhasil dihapus')
                        return redirect('survey:jawaban_survey_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:jawaban_survey_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    responden_filter = request.GET.get('responden', '').strip()

    from .models import JawabanSurvey
    qs = JawabanSurvey.objects.select_related('responden', 'pertanyaan__jenis_survey')

    if search_query:
        qs = qs.filter(
            Q(responden__nip_pegawaiPenilai__icontains=search_query) |
            Q(responden__nip_pegawaiDinilai__icontains=search_query) |
            Q(pertanyaan__kode_pertanyaan__icontains=search_query) |
            Q(pertanyaan__pertanyaan__icontains=search_query)
        )

    if responden_filter:
        qs = qs.filter(responden_id=responden_filter)

    qs = qs.order_by('-created_at')

    # Create table
    from .tables import JawabanSurveyTable
    table = JawabanSurveyTable(qs)
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
        'responden_filter': responden_filter,
    }

    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'master_survey/jawaban_survey/partials/_table.html', context)

    return render(request, 'master_survey/jawaban_survey/list.html', context)


@permission_required_403('survey', 'jawaban_survey', 'create')
def jawaban_survey_create(request):
    """Create view untuk Jawaban Survey"""

    if request.method == 'POST':
        from .forms import JawabanSurveyForm
        form = JawabanSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jawaban Survey berhasil ditambahkan')

            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"jawaban-survey-form-success": {"message": "Jawaban Survey berhasil ditambahkan", "redirect": "%s"}}' % reverse('survey:jawaban_survey_list'),
                })

            return redirect('survey:jawaban_survey_list')

        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']

            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'jawaban-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp

        return render(request, 'master_survey/jawaban_survey/form.html', {
            'form': form,
            'edit_mode': False
        })

    # GET request
    from .forms import JawabanSurveyForm
    form = JawabanSurveyForm()
    return render(request, 'master_survey/jawaban_survey/form.html', {
        'form': form,
        'edit_mode': False
    })


@permission_required_403('survey', 'jawaban_survey', 'edit')
def jawaban_survey_edit(request, pk):
    """Edit view untuk Jawaban Survey"""

    from .models import JawabanSurvey
    obj = get_object_or_404(JawabanSurvey, id=pk)

    if request.method == 'POST':
        from .forms import JawabanSurveyForm
        form = JawabanSurveyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jawaban Survey berhasil diupdate')

            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"jawaban-survey-form-success": {"message": "Jawaban Survey berhasil diupdate", "redirect": "%s"}}' % reverse('survey:jawaban_survey_list'),
                })

            return redirect('survey:jawaban_survey_list')

        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']

            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'jawaban-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp

        return render(request, 'master_survey/jawaban_survey/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj
        })

    # GET request
    from .forms import JawabanSurveyForm
    form = JawabanSurveyForm(instance=obj)
    return render(request, 'master_survey/jawaban_survey/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj
    })


@permission_required_403('survey', 'jawaban_survey', 'delete')
def jawaban_survey_delete(request, pk):
    """Delete view untuk Jawaban Survey"""

    from .models import JawabanSurvey
    obj = get_object_or_404(JawabanSurvey, id=pk)

    if request.method == 'POST':
        responden_info = f"{obj.responden.nip_pegawaiPenilai} → {obj.responden.nip_pegawaiDinilai}"
        pertanyaan_kode = obj.pertanyaan.kode_pertanyaan
        obj.delete()
        messages.success(request, f'Jawaban "{pertanyaan_kode}" dari responden "{responden_info}" berhasil dihapus')
        return redirect('survey:jawaban_survey_list')

    # GET request - show confirmation
    context = {
        'obj': obj,
    }
    return render(request, 'master_survey/jawaban_survey/delete.html', context)


# ============================================================================
# PERIODE SURVEY VIEWS
# ============================================================================

@permission_required_403('survey', 'periode_survey', 'view')
def periode_survey_list(request):
    """List view untuk Periode Survey"""
    
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
                page_key = data.get('page_key', 'periode_survey_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'periode_survey_list')
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
            if not check_permission(request.user, 'survey', 'periode_survey', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:periode_survey_list')
        
        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'periode_survey', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:periode_survey_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        
        if selected_ids:
            from .models import PeriodeSurvey
            qs = PeriodeSurvey.objects.filter(id__in=selected_ids).select_related('jenis_survey').order_by('-tanggal_mulai')
            
            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="periode_survey.csv"'
                writer = csv.writer(response)
                writer.writerow(['Jenis Survey', 'Nama Periode', 'Tanggal Mulai', 'Tanggal Selesai', 'Status', 'Aktif', 'Tanggal Dibuat'])
                for item in qs:
                    writer.writerow([
                        item.jenis_survey.nama,
                        item.nama_periode,
                        item.tanggal_mulai.strftime('%d/%m/%Y %H:%M'),
                        item.tanggal_selesai.strftime('%d/%m/%Y %H:%M'),
                        item.status_display,
                        'Ya' if item.is_active else 'Tidak',
                        item.created_at.strftime('%d/%m/%Y %H:%M')
                    ])
                return response
            
            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = [f"{item.jenis_survey.nama} - {item.nama_periode}" for item in qs]
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='periode_survey_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} periode survey berhasil dihapus')
                        return redirect('survey:periode_survey_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:periode_survey_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    jenis_filter = request.GET.get('jenis', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    from .models import PeriodeSurvey
    qs = PeriodeSurvey.objects.select_related('jenis_survey')
    
    if search_query:
        qs = qs.filter(
            Q(nama_periode__icontains=search_query) |
            Q(jenis_survey__nama__icontains=search_query) |
            Q(deskripsi__icontains=search_query)
        )
    
    if jenis_filter:
        qs = qs.filter(jenis_survey_id=jenis_filter)
    
    if status_filter:
        # Filter berdasarkan status akan dilakukan di Python karena status adalah property
        pass
    
    qs = qs.order_by('-tanggal_mulai')
    
    # Create table
    from .tables import PeriodeSurveyTable
    table = PeriodeSurveyTable(qs)
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
    
    # Get jenis survey for filter dropdown
    jenis_survey_list = JenisSurvey.objects.filter(is_active=True).order_by('nama')
    
    context = {
        'table': table,
        'total': qs.count(),
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'status_filter': status_filter,
        'jenis_survey_list': jenis_survey_list,
    }
    
    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'master_survey/periode_survey/partials/_table.html', context)
    
    return render(request, 'master_survey/periode_survey/list.html', context)


@permission_required_403('survey', 'periode_survey', 'create')
def periode_survey_create(request):
    """Create view untuk Periode Survey"""
    
    if request.method == 'POST':
        from .forms import PeriodeSurveyForm
        form = PeriodeSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Periode Survey berhasil ditambahkan')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"periode-survey-form-success": {"message": "Periode Survey berhasil ditambahkan", "redirect": "%s"}}' % reverse('survey:periode_survey_list'),
                })
            
            return redirect('survey:periode_survey_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'periode-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'master_survey/periode_survey/form.html', {
            'form': form,
            'edit_mode': False
        })
    
    # GET request
    from .forms import PeriodeSurveyForm
    form = PeriodeSurveyForm()
    return render(request, 'master_survey/periode_survey/form.html', {
        'form': form,
        'edit_mode': False
    })


@permission_required_403('survey', 'periode_survey', 'edit')
def periode_survey_edit(request, pk):
    """Edit view untuk Periode Survey"""
    
    from .models import PeriodeSurvey
    obj = get_object_or_404(PeriodeSurvey, id=pk)
    
    if request.method == 'POST':
        from .forms import PeriodeSurveyForm
        form = PeriodeSurveyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Periode Survey berhasil diupdate')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"periode-survey-form-success": {"message": "Periode Survey berhasil diupdate", "redirect": "%s"}}' % reverse('survey:periode_survey_list'),
                })
            
            return redirect('survey:periode_survey_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            import json
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'periode-survey-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'master_survey/periode_survey/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj
        })
    
    # GET request
    from .forms import PeriodeSurveyForm
    form = PeriodeSurveyForm(instance=obj)
    return render(request, 'master_survey/periode_survey/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj
    })


@permission_required_403('survey', 'periode_survey', 'delete')
def periode_survey_delete(request, pk):
    """Delete view untuk Periode Survey"""
    
    from .models import PeriodeSurvey
    obj = get_object_or_404(PeriodeSurvey, id=pk)
    
    if request.method == 'POST':
        jenis_survey_nama = obj.jenis_survey.nama
        nama_periode = obj.nama_periode
        obj.delete()
        messages.success(request, f'Periode "{nama_periode}" untuk survey "{jenis_survey_nama}" berhasil dihapus')
        return redirect('survey:periode_survey_list')
    
    # GET request - show confirmation
    context = {
        'obj': obj,
    }
    return render(request, 'master_survey/periode_survey/delete.html', context)


# ============================================================================
# SURVEY ACCESS VALIDATION HELPER
# ============================================================================

def check_survey_access(jenis_survey_id):
    """
    Helper function untuk mengecek apakah survey bisa diakses
    Returns: (can_access: bool, message: str)
    """
    try:
        jenis_survey = JenisSurvey.objects.get(id=jenis_survey_id, is_active=True)
        if jenis_survey.can_access:
            return True, jenis_survey.get_access_message()
        else:
            return False, jenis_survey.get_access_message()
    except JenisSurvey.DoesNotExist:
        return False, "Jenis survey tidak ditemukan atau tidak aktif."


# ========================================
# PENILAIAN JPT VIEWS
# ========================================

@permission_required_403('survey', 'survey_jpt', 'view')
def penilaian_list(request):
    """List view untuk Survey JPT"""
    
    # ---- AJAX SAVE/LOAD SELECTIONS ----
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        content_type = request.headers.get('Content-Type', '') or ''
        if 'application/json' in content_type:
            try:
                payload = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else (request.body or '')
                data = json.loads(payload or '{}')
            except Exception:
                data = {}
            action = data.get('action')
            if action == 'save_selection':
                page_key = data.get('page_key', 'survey_jpt_list')
                selected_ids = data.get('selected_ids', [])
                from apps.manajemen.models import UserTableSelection
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'survey_jpt_list')
                try:
                    from apps.manajemen.models import UserTableSelection
                    selection = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                    return JsonResponse({'success': True, 'selected_ids': selection.selected_ids})
                except:
                    return JsonResponse({'success': True, 'selected_ids': []})

    # ---- BULK ACTIONS (POST) ----
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')

        if action in ['export_csv', 'export_excel', 'export_pdf']:
            if not check_permission(request.user, 'survey', 'survey_jpt', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('survey:penilaian_list')
        
        if action in ['delete_single', 'bulk_delete']:
            if not check_permission(request.user, 'survey', 'survey_jpt', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('survey:penilaian_list')

        # Get selected IDs
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        
        if selected_ids:
            qs = PenilaianJPT.objects.filter(id__in=selected_ids).order_by('-created_at')
            
            if action == 'export_csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="survey_jpt.csv"'
                writer = csv.writer(response)
                writer.writerow(['Yang Dinilai', 'Penilai', 'Periode', 'Kepemimpinan', 'Kerjasama', 'Komunikasi', 'Inovasi', 'Integritas', 'Orientasi Hasil', 'Rata-rata', 'Kategori', 'Status', 'Tanggal Dibuat'])
                for item in qs:
                    writer.writerow([
                        item.nama_dinilai,
                        item.nama_penilai,
                        f"{item.periode_mulai.strftime('%d/%m/%Y')} - {item.periode_selesai.strftime('%d/%m/%Y')}",
                        item.kepemimpinan,
                        item.kerjasama,
                        item.komunikasi,
                        item.inovasi,
                        item.integritas,
                        item.orientasi_hasil,
                        item.rata_rata,
                        item.kategori_nilai,
                        item.get_status_display(),
                        item.created_at.strftime('%d/%m/%Y %H:%M')
                    ])
                return response
            
            elif action in ['bulk_delete', 'delete_single']:
                deleted_count = qs.count()
                deleted_names = [f"{item.nama_dinilai} (oleh {item.nama_penilai})" for item in qs]
                if deleted_count > 0:
                    qs.delete()
                    from apps.manajemen.models import UserTableSelection
                    UserTableSelection.objects.filter(user=request.user, page_key='survey_jpt_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} penilaian JPT berhasil dihapus')
                        return redirect('survey:penilaian_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('survey:penilaian_list')

    # ---- REGULAR GET ----
    # Handle search
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    qs = PenilaianJPT.objects.all()
    
    if search_query:
        qs = qs.filter(
            Q(nama_dinilai__icontains=search_query) |
            Q(nama_penilai__icontains=search_query) |
            Q(nip_dinilai__icontains=search_query) |
            Q(nip_penilai__icontains=search_query) |
            Q(jabatan_dinilai__icontains=search_query) |
            Q(jabatan_penilai__icontains=search_query)
        )
    
    if status_filter:
        qs = qs.filter(status=status_filter)
    
    qs = qs.order_by('-created_at')
    
    # Create table
    table = PenilaianJPTTable(qs)
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
        'status_filter': status_filter,
    }
    
    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'survey_jpt/partials/_table.html', context)
    
    return render(request, 'survey_jpt/list.html', context)


@permission_required_403('survey', 'survey_jpt', 'create')
def penilaian_create(request):
    """Create view untuk Survey JPT"""
    
    if request.method == 'POST':
        form = PenilaianJPTForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Penilaian JPT untuk {obj.nama_dinilai} berhasil dibuat')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"penilaian-jpt-form-success": {"message": "Penilaian JPT berhasil dibuat", "redirect": "%s"}}' % reverse('survey:penilaian_list'),
                })
            
            return redirect('survey:penilaian_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'penilaian-jpt-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'survey_jpt/form.html', {
            'form': form,
            'edit_mode': False
        })
    
    # GET request
    form = PenilaianJPTForm()
    return render(request, 'survey_jpt/form.html', {
        'form': form,
        'edit_mode': False
    })


@permission_required_403('survey', 'survey_jpt', 'create')
def buat_penilaian(request):
    """Buat Penilaian view untuk Survey JPT - Dynamic from Database with Periode Check"""
    
    # Get pertanyaan from database
    # Ambil jenis survey "Penilaian JPT" atau yang pertama
    jenis_survey = JenisSurvey.objects.filter(is_active=True).first()
    if not jenis_survey:
        messages.error(request, 'Belum ada jenis survey yang aktif. Silakan hubungi administrator.')
        return redirect('survey:penilaian_list')
    
    # Cek periode aktif
    periode_aktif = jenis_survey.periode.filter(
        is_active=True,
        tanggal_mulai__lte=timezone.now(),
        tanggal_selesai__gte=timezone.now()
    ).first()
    
    if not periode_aktif:
        # Cek apakah ada periode yang akan datang
        periode_mendatang = jenis_survey.periode.filter(
            is_active=True,
            tanggal_mulai__gt=timezone.now()
        ).order_by('tanggal_mulai').first()
        
        if periode_mendatang:
            messages.warning(
                request, 
                f'Survey "{jenis_survey.nama}" akan dibuka pada {periode_mendatang.tanggal_mulai.strftime("%d %B %Y pukul %H:%M")}.'
            )
        else:
            messages.error(request, f'Survey "{jenis_survey.nama}" belum memiliki periode yang aktif. Silakan hubungi administrator.')
        
        return redirect('survey:penilaian_list')
    
    # Ambil pertanyaan yang aktif
    pertanyaan_list = PertanyaanSurvey.objects.filter(
        jenis_survey=jenis_survey,
        is_active=True
    ).order_by('urutan')
    
    if not pertanyaan_list.exists():
        messages.error(request, 'Belum ada pertanyaan survey yang aktif. Silakan hubungi administrator.')
        return redirect('survey:penilaian_list')
    
    if request.method == 'POST':
        # Get penilai data from POST
        nip_penilai = request.POST.get('nip_penilai')
        nama_penilai = request.POST.get('nama_penilai')
        nip_dinilai = request.POST.get('nip_dinilai')
        nama_dinilai = request.POST.get('nama_dinilai')
        
        # Validate required fields
        if not all([nip_penilai, nama_penilai, nip_dinilai, nama_dinilai]):
            messages.error(request, 'Data penilai dan yang dinilai harus diisi lengkap.')
            return redirect('survey:buat_penilaian')
        
        # Cek apakah sudah pernah menilai di periode ini
        existing = RespondenSurvey.objects.filter(
            jenis_survey=jenis_survey,
            periode=periode_aktif,
            nip_pegawaiPenilai=nip_penilai,
            nip_pegawaiDinilai=nip_dinilai
        ).first()
        
        if existing:
            messages.warning(
                request, 
                f'Anda sudah pernah menilai {nama_dinilai} pada periode ini. Silakan edit penilaian yang sudah ada.'
            )
            return redirect('survey:penilaian_list')
        
        # Create RespondenSurvey
        responden = RespondenSurvey.objects.create(
            jenis_survey=jenis_survey,
            periode=periode_aktif,
            id_pegawaiPenilai=0,  # Default value, bisa diupdate nanti
            nip_pegawaiPenilai=nip_penilai,
            id_pegawaiDinilai=0,  # Default value, bisa diupdate nanti
            nip_pegawaiDinilai=nip_dinilai,
            peranPenilai='atasan',  # Default, bisa disesuaikan
            statusData='submitted'
        )
        
        # Save jawaban for each pertanyaan
        jawaban_count = 0
        for pertanyaan in pertanyaan_list:
            nilai_key = f'pertanyaan_{pertanyaan.id}'
            nilai = request.POST.get(nilai_key)
            
            if nilai:
                try:
                    nilai_int = int(nilai)
                    if 1 <= nilai_int <= 5:
                        JawabanSurvey.objects.create(
                            responden=responden,
                            pertanyaan=pertanyaan,
                            nilai=nilai_int
                        )
                        jawaban_count += 1
                except (ValueError, TypeError):
                    pass
        
        messages.success(
            request, 
            f'Penilaian untuk {nama_dinilai} berhasil disimpan dengan {jawaban_count} jawaban pada periode "{periode_aktif.nama_periode}"'
        )
        
        # HTMX response
        if request.headers.get('HX-Request'):
            return HttpResponse('', headers={
                'HX-Trigger': '{"penilaian-jpt-form-success": {"message": "Penilaian berhasil disimpan", "redirect": "%s"}}' % reverse('survey:penilaian_list'),
            })
        
        return redirect('survey:penilaian_list')
    
    # GET request - Prepare form data
    initial_data = {}
    
    # GET request - Pre-fill penilai data
    # Try to get data from user's pegawai relation or database
    try:
        if request.user and hasattr(request.user, 'pegawai') and request.user.pegawai:
            pegawai = request.user.pegawai
            initial_data = {
                'nip_penilai': pegawai.nip,
                'nama_penilai': pegawai.nama,
                'jabatan_penilai': pegawai.jabatan,
                'unit_kerja_penilai': pegawai.unit_kerja,
            }
        else:
            # Try to get from MsPegawai based on user's username (assuming username is NIP)
            from apps.manajemen.models_kepegawaian import MsPegawai
            
            # Assume username is NIP
            user_nip = request.user.username if request.user else None
            if user_nip:
                pegawai = MsPegawai.objects.filter(
                    models.Q(B_02B=user_nip) | models.Q(B_02=user_nip)
                ).first()
                
                if pegawai:
                    # Get unit kerja name
                    unit_kerja = ""
                    if pegawai.id_opd:
                        unit_kerja = str(pegawai.id_opd)
                    
                    # Get jabatan name
                    jabatan = ""
                    if pegawai.I_JB:
                        jabatan = pegawai.I_JB
                    elif pegawai.id_jabatan:
                        jabatan = str(pegawai.id_jabatan)
                    
                    initial_data = {
                        'nip_penilai': pegawai.nip,
                        'nama_penilai': pegawai.nama_lengkap,
                        'jabatan_penilai': jabatan,
                        'unit_kerja_penilai': unit_kerja,
                    }
    except (AttributeError, Exception) as e:
        print(f"Error getting pegawai data: {e}")
        pass
    
    # If no pegawai data found, use default data untuk testing
    if not initial_data:
        from datetime import date
        current_year = date.today().year
        
        initial_data = {
            'nip_penilai': '199411192019031001',
            'nama_penilai': 'BRAHMANA ADIPUTRA, S.Kom.',
            'jabatan_penilai': 'Pranata Komputer Ahli Pertama / Pertama',
            'unit_kerja_penilai': 'BADAN KEPEGAWAIAN DAN PENGEMBANGAN SUMBER DAYA MANUSIA',
            'periode_mulai': f'{current_year}-01-01',
            'periode_selesai': f'{current_year}-12-31',
        }
    else:
        # Add periode data
        from datetime import date
        current_year = date.today().year
        initial_data.update({
            'periode_mulai': f'{current_year}-01-01',
            'periode_selesai': f'{current_year}-12-31',
        })
    
    # Render dynamic template
    return render(request, 'survey_jpt/buat_penilaian_form_dynamic.html', {
        'initial_data': initial_data,
        'pertanyaan_list': pertanyaan_list,
        'jenis_survey': jenis_survey,
    })


@permission_required_403('survey', 'survey_jpt', 'edit')
def penilaian_edit(request, pk):
    """Edit view untuk Survey JPT"""
    
    obj = get_object_or_404(PenilaianJPT, id=pk)
    
    if request.method == 'POST':
        form = PenilaianJPTForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Penilaian JPT untuk {obj.nama_dinilai} berhasil diupdate')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"penilaian-jpt-form-success": {"message": "Penilaian JPT berhasil diupdate", "redirect": "%s"}}' % reverse('survey:penilaian_list'),
                })
            
            return redirect('survey:penilaian_list')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'penilaian-jpt-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'survey_jpt/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj
        })
    
    # GET request
    form = PenilaianJPTForm(instance=obj)
    return render(request, 'survey_jpt/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj
    })


@permission_required_403('survey', 'survey_jpt', 'view')
def penilaian_detail(request, pk):
    """Detail view untuk Survey JPT"""
    
    obj = get_object_or_404(PenilaianJPT, id=pk)
    
    context = {
        'obj': obj,
    }
    return render(request, 'survey_jpt/detail.html', context)


@permission_required_403('survey', 'survey_jpt', 'delete')
def penilaian_delete(request, pk):
    """Delete view untuk Survey JPT"""
    
    obj = get_object_or_404(PenilaianJPT, id=pk)
    
    if request.method == 'POST':
        nama_dinilai = obj.nama_dinilai
        nama_penilai = obj.nama_penilai
        obj.delete()
        messages.success(request, f'Penilaian JPT untuk {nama_dinilai} oleh {nama_penilai} berhasil dihapus')
        return redirect('survey:penilaian_list')
    
    # GET request - show confirmation
    context = {
        'obj': obj,
    }
    return render(request, 'survey_jpt/delete.html', context)


@permission_required_403('survey', 'survey_jpt', 'report')
def penilaian_report(request):
    """Report view untuk Survey JPT"""
    from django.db.models import Avg, Count
    
    # Get statistics
    total_penilaian = PenilaianJPT.objects.count()
    
    # Calculate average scores
    avg_scores = PenilaianJPT.objects.aggregate(
        avg_kepemimpinan=Avg('kepemimpinan'),
        avg_kerjasama=Avg('kerjasama'),
        avg_komunikasi=Avg('komunikasi'),
        avg_inovasi=Avg('inovasi'),
        avg_integritas=Avg('integritas'),
        avg_orientasi_hasil=Avg('orientasi_hasil')
    )
    
    # Status distribution
    status_stats = PenilaianJPT.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Category distribution
    penilaian_list = PenilaianJPT.objects.all()
    kategori_stats = {}
    for penilaian in penilaian_list:
        kategori = penilaian.kategori_nilai
        kategori_stats[kategori] = kategori_stats.get(kategori, 0) + 1
    
    # Recent penilaian
    recent_penilaian = PenilaianJPT.objects.order_by('-created_at')[:10]
    
    context = {
        'total_penilaian': total_penilaian,
        'avg_scores': avg_scores,
        'status_stats': status_stats,
        'kategori_stats': kategori_stats,
        'recent_penilaian': recent_penilaian,
    }
    return render(request, 'survey_jpt/report.html', context)


# ============================================================================
# PENILAIAN ATASAN VIEWS (Employee evaluates their supervisor)
# ============================================================================

def penilaian_atasan_form(request):
    """Form untuk pegawai menilai atasannya"""
    
    # Get current user info (in real app, get from session/auth)
    # For now, we'll use form input
    
    if request.method == 'POST':
        form = PenilaianJPTForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Penilaian atasan "{obj.nama_dinilai}" berhasil disimpan')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"penilaian-atasan-form-success": {"message": "Penilaian atasan berhasil disimpan", "redirect": "%s"}}' % reverse('survey:penilaian_atasan_riwayat'),
                })
            
            return redirect('survey:penilaian_atasan_riwayat')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'penilaian-atasan-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'survey_jpt/penilaian_atasan/form.html', {
            'form': form,
            'page_title': 'Penilaian Atasan'
        })
    
    # GET request - Pre-fill penilai data if user is logged in
    initial_data = {}
    if hasattr(request.user, 'pegawai'):
        # If user has pegawai relation, pre-fill data
        pegawai = request.user.pegawai
        initial_data = {
            'nip_penilai': pegawai.nip,
            'nama_penilai': pegawai.nama,
            'jabatan_penilai': pegawai.jabatan,
            'unit_kerja_penilai': pegawai.unit_kerja,
        }
    
    form = PenilaianJPTForm(initial=initial_data)
    return render(request, 'survey_jpt/penilaian_atasan/form.html', {
        'form': form,
        'page_title': 'Penilaian Atasan'
    })


def penilaian_atasan_riwayat(request):
    """Riwayat penilaian atasan yang sudah dibuat oleh pegawai yang login"""
    
    # Handle search
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    qs = PenilaianJPT.objects.all()
    
    # Filter by current user as penilai (in real app)
    # For now, show all data
    # if hasattr(request.user, 'pegawai'):
    #     qs = qs.filter(nip_penilai=request.user.pegawai.nip)

    if search_query:
        qs = qs.filter(
            Q(nama_dinilai__icontains=search_query) |
            Q(jabatan_dinilai__icontains=search_query) |
            Q(unit_kerja_dinilai__icontains=search_query)
        )

    if status_filter:
        qs = qs.filter(status=status_filter)

    qs = qs.order_by('-created_at')

    # Create table
    table = PenilaianJPTTable(qs)
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
        'status_filter': status_filter,
        'page_title': 'Riwayat Penilaian Atasan'
    }

    # HTMX request - return partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'survey_jpt/penilaian_atasan/partials/_table.html', context)

    return render(request, 'survey_jpt/penilaian_atasan/riwayat.html', context)


def penilaian_atasan_edit(request, pk):
    """Edit penilaian atasan (hanya bisa edit penilaian sendiri)"""
    
    obj = get_object_or_404(PenilaianJPT, id=pk)
    
    # Check if user can edit this penilaian (in real app)
    # if hasattr(request.user, 'pegawai') and obj.nip_penilai != request.user.pegawai.nip:
    #     messages.error(request, 'Anda hanya bisa mengedit penilaian yang Anda buat sendiri')
    #     return redirect('survey:penilaian_atasan_riwayat')
    
    if request.method == 'POST':
        form = PenilaianJPTForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Penilaian atasan "{obj.nama_dinilai}" berhasil diupdate')
            
            # HTMX response
            if request.headers.get('HX-Request'):
                return HttpResponse('', headers={
                    'HX-Trigger': '{"penilaian-atasan-form-success": {"message": "Penilaian atasan berhasil diupdate", "redirect": "%s"}}' % reverse('survey:penilaian_atasan_riwayat'),
                })
            
            return redirect('survey:penilaian_atasan_riwayat')
        
        # Form invalid - HTMX response
        if request.headers.get('HX-Request'):
            errors = []
            field_errors = {}
            try:
                for name, errs in form.errors.items():
                    if name == '__all__':
                        errors.extend([str(e) for e in errs])
                    else:
                        field_errors[name] = [str(e) for e in errs]
                        errors.extend([str(e) for e in errs])
            except Exception:
                errors = ['Periksa kembali input Anda.']
            
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'penilaian-atasan-form-invalid': {
                    'errors': errors,
                    'fieldErrors': field_errors
                }
            })
            return resp
        
        return render(request, 'survey_jpt/penilaian_atasan/form.html', {
            'form': form,
            'edit_mode': True,
            'obj': obj,
            'page_title': 'Edit Penilaian Atasan'
        })
    
    # GET request
    form = PenilaianJPTForm(instance=obj)
    return render(request, 'survey_jpt/penilaian_atasan/form.html', {
        'form': form,
        'edit_mode': True,
        'obj': obj,
        'page_title': 'Edit Penilaian Atasan'
    })


def penilaian_atasan_detail(request, pk):
    """Detail penilaian atasan"""
    
    obj = get_object_or_404(PenilaianJPT, id=pk)
    
    context = {
        'obj': obj,
        'page_title': 'Detail Penilaian Atasan'
    }
    return render(request, 'survey_jpt/penilaian_atasan/detail.html', context)