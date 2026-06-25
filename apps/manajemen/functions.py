from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import json
from django.db.models import Count, Q
from django_tables2 import RequestConfig

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.models import PermissionFunction, PermissionRule, UserTableSelection
from apps.manajemen.tables import FunctionTable
from apps.manajemen.helpers import check_permission
# Reuse export helpers from the existing granular views
from apps.manajemen.views_granular import (
    export_functions_csv,
    export_functions_excel,
    export_functions_pdf,
)


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'permission_function', 'view')
def function_list(request):
    """List all permission functions with reusable datatable + persistence"""

    # ---- EXPORT ALL (POST) ----
    if request.method == 'POST' and 'export_all' in request.POST:
        if not check_permission(request.user, 'pengaturan', 'permission_function', 'export'):
            messages.error(request, 'Anda tidak memiliki izin untuk export data.')
            return redirect('manajemen_aplikasi:function_list')
        export_format = request.POST.get('export_all')
        search_query = request.POST.get('search', '').strip()

        all_funcs = PermissionFunction.objects.annotate(
            rule_count=Count('rules')
        )
        if search_query:
            all_funcs = all_funcs.filter(
                Q(nama_fungsi__icontains=search_query) |
                Q(label_fungsi__icontains=search_query) |
                Q(deskripsi_fungsi__icontains=search_query)
            )
        all_funcs = all_funcs.order_by('nama_fungsi')

        if export_format == 'excel':
            try:
                return export_functions_excel(all_funcs)
            except Exception:
                return export_functions_csv(all_funcs)
        elif export_format == 'pdf':
            try:
                return export_functions_pdf(all_funcs)
            except Exception:
                return export_functions_csv(all_funcs)

    # ---- AJAX SAVE/LOAD SELECTIONS ----
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Only handle JSON-based AJAX for selection persistence.
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
                page_key = data.get('page_key', 'function_list')
                selected_ids = data.get('selected_ids', [])
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'function_list')
                try:
                    selection = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                    return JsonResponse({'success': True, 'selected_ids': selection.selected_ids})
                except UserTableSelection.DoesNotExist:
                    return JsonResponse({'success': True, 'selected_ids': []})

    # ---- BULK ACTIONS (POST) ----
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')

        if action in ['export_csv', 'export_excel', 'export_pdf']:
            if not check_permission(request.user, 'pengaturan', 'permission_function', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('manajemen_aplikasi:function_list')
        if action == 'delete_single':
            if not check_permission(request.user, 'pengaturan', 'permission_function', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('manajemen_aplikasi:function_list')
        if action == 'bulk_delete':
            if not check_permission(request.user, 'pengaturan', 'permission_function', 'bulk_delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus banyak'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus banyak data.')
                return redirect('manajemen_aplikasi:function_list')

        # Support both repeated selected_ids and single id payloads
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        # Final fallback: use persisted selections if available
        if not selected_ids:
            try:
                selection = UserTableSelection.objects.get(user=request.user, page_key='function_list')
                selected_ids = selection.selected_ids or []
            except UserTableSelection.DoesNotExist:
                selected_ids = []
        if selected_ids:
            qs = PermissionFunction.objects.filter(id__in=selected_ids).annotate(
                rule_count=Count('rules')
            ).order_by('nama_fungsi')
            if action == 'export_csv':
                return export_functions_csv(qs)
            elif action == 'export_excel':
                try:
                    return export_functions_excel(qs)
                except Exception:
                    return export_functions_csv(qs)
            elif action == 'export_pdf':
                try:
                    return export_functions_pdf(qs)
                except Exception:
                    return export_functions_csv(qs)
            elif action == 'bulk_delete' or action == 'delete_single':
                # Only delete functions that are not referenced by any rules
                in_use_ids = set(
                    PermissionRule.objects.filter(function_id__in=selected_ids)
                    .values_list('function_id', flat=True)
                    .distinct()
                )
                deletable_qs = qs.exclude(id__in=in_use_ids)
                blocked_qs = qs.filter(id__in=in_use_ids)

                deleted_count = deletable_qs.count()
                deleted_names = list(deletable_qs.values_list('label_fungsi', flat=True))
                if deleted_count > 0:
                    deletable_qs.delete()
                    UserTableSelection.objects.filter(user=request.user, page_key='function_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(
                            request,
                            f'{deleted_count} function berhasil dihapus: {", ".join(deleted_names[:5])}{"..." if deleted_count > 5 else ""}'
                        )

                blocked_count = blocked_qs.count()
                if blocked_count > 0:
                    blocked_names = list(blocked_qs.values_list('label_fungsi', flat=True))
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'deleted': False, 'blocked': True, 'count': blocked_count, 'names': blocked_names}, status=400)
                    else:
                        messages.warning(
                            request,
                            f'{blocked_count} function tidak dihapus karena masih terhubung ke Rules: {", ".join(blocked_names[:5])}{"..." if blocked_count > 5 else ""}'
                        )

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # If nothing deleted and nothing blocked (unlikely), return ok but no-op
                    return JsonResponse({'success': True, 'deleted': False, 'count': 0})
                else:
                    return redirect('manajemen_aplikasi:function_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('manajemen_aplikasi:function_list')

    # ---- REGULAR GET ----
    funcs = PermissionFunction.objects.annotate(
        rule_count=Count('rules')
    )
    search_query = request.GET.get('search', '').strip()
    if search_query:
        funcs = funcs.filter(
            Q(nama_fungsi__icontains=search_query) |
            Q(label_fungsi__icontains=search_query) |
            Q(deskripsi_fungsi__icontains=search_query)
        )
    funcs = funcs.order_by('nama_fungsi')

    total = funcs.count()
    table = FunctionTable(funcs)
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    RequestConfig(request, paginate={'per_page': per_page}).configure(table)

    current_category = None

    context = {
        'table': table,
        'total': total,
        'search_query': search_query,
        'current_category': current_category,
    }
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'manajemen_aplikasi/access/ma_ap_functions/partials/_table.html', context)
    return render(request, 'manajemen_aplikasi/access/ma_ap_functions/list.html', context)


@permission_required_403('pengaturan', 'permission_function', 'create')
def function_create(request):
    """Create new function"""
    if request.method == 'POST':
        nama = (request.POST.get('nama_fungsi') or '').strip()
        label = (request.POST.get('label_fungsi') or '').strip()
        deskripsi = (request.POST.get('deskripsi_fungsi') or '').strip()

        errors = []
        field_errors = {}
        if not nama:
            errors.append('Nama fungsi harus diisi!')
            field_errors['nama_fungsi'] = ['Nama fungsi harus diisi!']
        if not label:
            errors.append('Label fungsi harus diisi!')
            field_errors['label_fungsi'] = ['Label fungsi harus diisi!']
        if nama and PermissionFunction.objects.filter(nama_fungsi=nama).exists():
            dup_msg = f'Fungsi "{nama}" sudah ada!'
            errors.append(dup_msg)
            field_errors.setdefault('nama_fungsi', []).append(dup_msg)

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'function-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_functions/form.html', {
                    'errors_list': errors,
                })

        PermissionFunction.objects.create(
            nama_fungsi=nama,
            label_fungsi=label,
            deskripsi_fungsi=deskripsi
        )

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'function-form-success': {
                    'message': f'Fungsi "{label}" berhasil dibuat!',
                    'redirect': reverse('manajemen_aplikasi:function_list')
                }
            })
            return resp

        messages.success(request, f'✅ Fungsi "{label}" berhasil dibuat!')
        return redirect('manajemen_aplikasi:function_list')

    return render(request, 'manajemen_aplikasi/access/ma_ap_functions/form.html')


@permission_required_403('pengaturan', 'permission_function', 'edit')
def function_edit(request, func_id):
    """Edit function"""
    function = get_object_or_404(PermissionFunction, id=func_id)
    rule_count = PermissionRule.objects.filter(function=function).count()

    if request.method == 'POST':
        nama = (request.POST.get('nama_fungsi') or '').strip()
        label = (request.POST.get('label_fungsi') or '').strip()
        deskripsi = (request.POST.get('deskripsi_fungsi') or '').strip()

        errors = []
        field_errors = {}
        # Only allow editing nama_fungsi when no rules are attached
        if rule_count == 0:
            if not nama:
                errors.append('Nama fungsi harus diisi!')
                field_errors['nama_fungsi'] = ['Nama fungsi harus diisi!']
            else:
                if nama != function.nama_fungsi and PermissionFunction.objects.filter(nama_fungsi=nama).exists():
                    dup_msg = f'Fungsi "{nama}" sudah ada!'
                    errors.append(dup_msg)
                    field_errors.setdefault('nama_fungsi', []).append(dup_msg)
        if not label:
            errors.append('Label fungsi harus diisi!')
            field_errors['label_fungsi'] = ['Label fungsi harus diisi!']

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'function-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_functions/form.html', {
                    'errors_list': errors,
                    'function': function,
                    'edit_mode': True,
                })

        # Update allowed fields
        if rule_count == 0 and nama and (nama != function.nama_fungsi):
            function.nama_fungsi = nama
        function.label_fungsi = label
        function.deskripsi_fungsi = deskripsi
        function.save()

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'function-form-success': {
                    'message': f'Fungsi "{label}" berhasil diupdate!',
                    'redirect': reverse('manajemen_aplikasi:function_list')
                }
            })
            return resp

        messages.success(request, f'✅ Fungsi "{label}" berhasil diupdate!')
        return redirect('manajemen_aplikasi:function_list')

    context = {
        'function': function,
        'edit_mode': True,
        'rule_count': rule_count,
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_functions/form.html', context)


@permission_required_403('pengaturan', 'permission_function', 'delete')
def function_delete(request, func_id):
    """Delete function"""
    function = get_object_or_404(PermissionFunction, id=func_id)

    # Get affected rules (dependencies)
    affected_rules = PermissionRule.objects.filter(function=function)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        # Block deletion if function is still used by any rules
        if affected_rules.exists():
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'deleted': False,
                    'blocked': True,
                    'name': function.label_fungsi,
                    'rule_count': affected_rules.count(),
                }, status=400)
            messages.error(
                request,
                f'Fungsi "{function.label_fungsi}" tidak bisa dihapus karena masih dipakai pada {affected_rules.count()} rule.'
            )
            return redirect('manajemen_aplikasi:function_delete', func_id=func_id)

        func_name = function.label_fungsi
        function.delete()

        if is_ajax:
            return JsonResponse({'success': True, 'deleted': True, 'name': func_name})
        messages.success(request, f'✅ Fungsi "{func_name}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:function_list')

    context = {
        'function': function,
        'affected_rules': affected_rules,
        'rule_count': affected_rules.count(),
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_functions/delete.html', context)
