from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import json
from django.db.models import Count, Q
from django_tables2 import RequestConfig

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.helpers import check_permission
from apps.manajemen.models import PermissionControl, PermissionRule, UserTableSelection
from apps.manajemen.tables import ControlTable
# Reuse export helpers from granular views to avoid duplication
from apps.manajemen.views_granular import (
    export_controls_csv,
    export_controls_excel,
    export_controls_pdf,
)


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'permission_control', 'view')
def control_list(request):
    """List all permission controls with reusable datatable + persistence"""

    # ---- EXPORT ALL (POST) ----
    if request.method == 'POST' and 'export_all' in request.POST:
        if not check_permission(request.user, 'pengaturan', 'permission_control', 'export'):
            messages.error(request, 'Anda tidak memiliki izin untuk export data.')
            return redirect('manajemen_aplikasi:control_list')
        export_format = request.POST.get('export_all')
        search_query = request.POST.get('search', '').strip()
        all_ctrls = PermissionControl.objects.annotate(rule_count=Count('rules'))
        if search_query:
            all_ctrls = all_ctrls.filter(
                Q(nama_kontrol__icontains=search_query) |
                Q(label_kontrol__icontains=search_query) |
                Q(deskripsi_kontrol__icontains=search_query)
            )
        all_ctrls = all_ctrls.order_by('nama_kontrol')
        if export_format == 'excel':
            try:
                return export_controls_excel(all_ctrls)
            except Exception:
                return export_controls_csv(all_ctrls)
        elif export_format == 'pdf':
            try:
                return export_controls_pdf(all_ctrls)
            except Exception:
                return export_controls_csv(all_ctrls)

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
                page_key = data.get('page_key', 'control_list')
                selected_ids = data.get('selected_ids', [])
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'control_list')
                try:
                    selection = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                    return JsonResponse({'success': True, 'selected_ids': selection.selected_ids})
                except UserTableSelection.DoesNotExist:
                    return JsonResponse({'success': True, 'selected_ids': []})

    # ---- BULK ACTIONS (POST) ----
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')

        if action in ['export_csv', 'export_excel', 'export_pdf']:
            if not check_permission(request.user, 'pengaturan', 'permission_control', 'export'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin export'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk export data.')
                return redirect('manajemen_aplikasi:control_list')
        if action == 'delete_single':
            if not check_permission(request.user, 'pengaturan', 'permission_control', 'delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus data.')
                return redirect('manajemen_aplikasi:control_list')
        if action == 'bulk_delete':
            if not check_permission(request.user, 'pengaturan', 'permission_control', 'bulk_delete'):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Tidak memiliki izin hapus banyak'}, status=403)
                messages.error(request, 'Anda tidak memiliki izin untuk menghapus banyak data.')
                return redirect('manajemen_aplikasi:control_list')

        # Support both repeated selected_ids and single id payloads
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        # Final fallback: use persisted selections if available
        if not selected_ids:
            try:
                selection = UserTableSelection.objects.get(user=request.user, page_key='control_list')
                selected_ids = selection.selected_ids or []
            except UserTableSelection.DoesNotExist:
                selected_ids = []
        if selected_ids:
            qs = PermissionControl.objects.filter(id__in=selected_ids).annotate(
                rule_count=Count('rules')
            ).order_by('nama_kontrol')
            if action == 'export_csv':
                return export_controls_csv(qs)
            elif action == 'export_excel':
                try:
                    return export_controls_excel(qs)
                except Exception:
                    return export_controls_csv(qs)
            elif action == 'export_pdf':
                try:
                    return export_controls_pdf(qs)
                except Exception:
                    return export_controls_csv(qs)
            elif action == 'bulk_delete' or action == 'delete_single':
                in_use_ids = set(
                    PermissionRule.objects.filter(control_id__in=selected_ids)
                    .values_list('control_id', flat=True)
                    .distinct()
                )
                deletable_qs = qs.exclude(id__in=in_use_ids)
                blocked_qs = qs.filter(id__in=in_use_ids)

                deleted_count = deletable_qs.count()
                deleted_names = list(deletable_qs.values_list('label_kontrol', flat=True))
                if deleted_count > 0:
                    deletable_qs.delete()
                    UserTableSelection.objects.filter(user=request.user, page_key='control_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(
                            request,
                            f'{deleted_count} control berhasil dihapus: {", ".join(deleted_names[:5])}{"..." if deleted_count > 5 else ""}'
                        )

                blocked_count = blocked_qs.count()
                if blocked_count > 0:
                    blocked_names = list(blocked_qs.values_list('label_kontrol', flat=True))
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'deleted': False, 'blocked': True, 'count': blocked_count, 'names': blocked_names}, status=400)
                    else:
                        messages.warning(
                            request,
                            f'{blocked_count} control tidak dihapus karena masih terhubung ke Rules: {", ".join(blocked_names[:5])}{"..." if blocked_count > 5 else ""}'
                        )

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'deleted': False, 'count': 0})
                else:
                    return redirect('manajemen_aplikasi:control_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('manajemen_aplikasi:control_list')

    # ---- REGULAR GET ----
    ctrls = PermissionControl.objects.annotate(rule_count=Count('rules'))
    search_query = request.GET.get('search', '').strip()
    if search_query:
        ctrls = ctrls.filter(
            Q(nama_kontrol__icontains=search_query) |
            Q(label_kontrol__icontains=search_query) |
            Q(deskripsi_kontrol__icontains=search_query)
        )
    ctrls = ctrls.order_by('nama_kontrol')

    total = ctrls.count()
    table = ControlTable(ctrls)
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
        'total': total,
        'search_query': search_query,
    }
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'manajemen_aplikasi/access/ma_ap_controls/partials/_table.html', context)
    return render(request, 'manajemen_aplikasi/access/ma_ap_controls/list.html', context)


@permission_required_403('pengaturan', 'permission_control', 'create')
def control_create(request):
    """Create new control"""
    if request.method == 'POST':
        nama = (request.POST.get('nama_kontrol') or '').strip()
        label = (request.POST.get('label_kontrol') or '').strip()
        deskripsi = (request.POST.get('deskripsi_kontrol') or '').strip()

        errors = []
        field_errors = {}
        if not nama:
            errors.append('Nama kontrol harus diisi!')
            field_errors['nama_kontrol'] = ['Nama kontrol harus diisi!']
        if not label:
            errors.append('Label kontrol harus diisi!')
            field_errors['label_kontrol'] = ['Label kontrol harus diisi!']
        if nama and PermissionControl.objects.filter(nama_kontrol=nama).exists():
            dup_msg = f'Kontrol "{nama}" sudah ada!'
            errors.append(dup_msg)
            field_errors.setdefault('nama_kontrol', []).append(dup_msg)

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'control-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_controls/form.html', {
                    'errors_list': errors,
                })

        PermissionControl.objects.create(
            nama_kontrol=nama,
            label_kontrol=label,
            deskripsi_kontrol=deskripsi
        )

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'control-form-success': {
                    'message': f'Kontrol "{label}" berhasil dibuat!',
                    'redirect': reverse('manajemen_aplikasi:control_list')
                }
            })
            return resp

        messages.success(request, f'✅ Kontrol "{label}" berhasil dibuat!')
        return redirect('manajemen_aplikasi:control_list')

    return render(request, 'manajemen_aplikasi/access/ma_ap_controls/form.html')


@permission_required_403('pengaturan', 'permission_control', 'edit')
def control_edit(request, ctrl_id):
    """Edit control"""
    control = get_object_or_404(PermissionControl, id=ctrl_id)
    rule_count = PermissionRule.objects.filter(control=control).count()

    if request.method == 'POST':
        nama = (request.POST.get('nama_kontrol') or '').strip()
        label = (request.POST.get('label_kontrol') or '').strip()
        deskripsi = (request.POST.get('deskripsi_kontrol') or '').strip()

        errors = []
        field_errors = {}
        if rule_count == 0:
            if not nama:
                errors.append('Nama kontrol harus diisi!')
                field_errors['nama_kontrol'] = ['Nama kontrol harus diisi!']
            elif nama != control.nama_kontrol and PermissionControl.objects.filter(nama_kontrol=nama).exists():
                dup_msg = f'Kontrol "{nama}" sudah ada!'
                errors.append(dup_msg)
                field_errors.setdefault('nama_kontrol', []).append(dup_msg)
        if not label:
            errors.append('Label kontrol harus diisi!')
            field_errors['label_kontrol'] = ['Label kontrol harus diisi!']

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'control-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_controls/form.html', {
                    'errors_list': errors,
                    'control': control,
                    'edit_mode': True,
                    'rule_count': rule_count,
                })

        # Update allowed fields
        if rule_count == 0 and nama and (nama != control.nama_kontrol):
            control.nama_kontrol = nama
        control.label_kontrol = label
        control.deskripsi_kontrol = deskripsi
        control.save()

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'control-form-success': {
                    'message': f'Kontrol "{label}" berhasil diupdate!',
                    'redirect': reverse('manajemen_aplikasi:control_list')
                }
            })
            return resp

        messages.success(request, f'✅ Kontrol "{label}" berhasil diupdate!')
        return redirect('manajemen_aplikasi:control_list')

    context = {
        'control': control,
        'edit_mode': True,
        'rule_count': rule_count,
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_controls/form.html', context)


@permission_required_403('pengaturan', 'permission_control', 'delete')
def control_delete(request, ctrl_id):
    """Delete control"""
    control = get_object_or_404(PermissionControl, id=ctrl_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        # Block deletion if control is still used by any rules
        affected_rules = PermissionRule.objects.filter(control=control)
        if affected_rules.exists():
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'deleted': False,
                    'blocked': True,
                    'name': control.label_kontrol,
                    'rule_count': affected_rules.count(),
                }, status=400)
            messages.error(request, f'Kontrol "{control.label_kontrol}" tidak bisa dihapus karena masih dipakai pada {affected_rules.count()} rule.')
            return redirect('manajemen_aplikasi:control_delete', ctrl_id=ctrl_id)

        ctrl_name = control.label_kontrol
        control.delete()
        if is_ajax:
            return JsonResponse({'success': True, 'deleted': True, 'name': ctrl_name})
        messages.success(request, f'✅ Kontrol "{ctrl_name}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:control_list')

    # Get affected rules
    affected_rules = PermissionRule.objects.filter(control=control)

    context = {
        'control': control,
        'affected_rules': affected_rules,
        'rule_count': affected_rules.count(),
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_controls/delete.html', context)
