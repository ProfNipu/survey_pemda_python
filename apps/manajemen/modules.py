from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import json
from django.db.models import Count, Q
from django_tables2 import RequestConfig
from django.core.exceptions import PermissionDenied

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.models import PermissionModule, PermissionRule, UserTableSelection
from apps.manajemen.tables import ModuleManageTable
# Reuse export helpers from the granular views to avoid duplication
from apps.manajemen.views_granular import (
    export_modules_csv,
    export_modules_excel,
    export_modules_pdf,
)


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'permission_module', 'view')
def module_list(request):
    """List all permission modules with reusable datatable + persistence"""

    def _require(func_name: str) -> None:
        try:
            from apps.manajemen.helpers import check_permission
            if not check_permission(request.user, 'pengaturan', 'permission_module', func_name):
                raise PermissionDenied
        except PermissionDenied:
            raise
        except Exception:
            raise PermissionDenied

    # ---- EXPORT ALL (POST) ----
    if request.method == 'POST' and 'export_all' in request.POST:
        _require('export')
        export_format = request.POST.get('export_all')
        search_query = request.POST.get('search', '').strip()
        all_modules = PermissionModule.objects.annotate(rule_count=Count('rules'))
        if search_query:
            all_modules = all_modules.filter(
                Q(label_module__icontains=search_query) |
                Q(nama_module__icontains=search_query)
            )
        all_modules = all_modules.order_by('order', 'nama_module')
        if export_format == 'excel':
            try:
                return export_modules_excel(all_modules)
            except Exception:
                return export_modules_csv(all_modules)
        elif export_format == 'pdf':
            try:
                return export_modules_pdf(all_modules)
            except Exception:
                return export_modules_csv(all_modules)

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
                page_key = data.get('page_key', 'module_list')
                selected_ids = data.get('selected_ids', [])
                UserTableSelection.objects.update_or_create(
                    user=request.user,
                    page_key=page_key,
                    defaults={'selected_ids': selected_ids}
                )
                return JsonResponse({'success': True, 'count': len(selected_ids)})
            elif action == 'load_selection':
                page_key = data.get('page_key', 'module_list')
                try:
                    sel = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                    return JsonResponse({'success': True, 'selected_ids': sel.selected_ids})
                except UserTableSelection.DoesNotExist:
                    return JsonResponse({'success': True, 'selected_ids': []})

    # ---- BULK ACTIONS (POST) ----
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')

        if action in {'export_csv', 'export_excel', 'export_pdf'}:
            _require('export')
        elif action == 'bulk_delete':
            _require('bulk_delete')
        elif action == 'delete_single':
            _require('delete')

        # Support both repeated selected_ids and single id payloads
        selected_ids = request.POST.getlist('selected_ids')
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        # Final fallback: use persisted selections if available
        if not selected_ids:
            try:
                selection = UserTableSelection.objects.get(user=request.user, page_key='module_list')
                selected_ids = selection.selected_ids or []
            except UserTableSelection.DoesNotExist:
                selected_ids = []
        if selected_ids:
            sel_modules = PermissionModule.objects.filter(id__in=selected_ids).annotate(rule_count=Count('rules')).order_by('order', 'nama_module')
            if action == 'export_csv':
                return export_modules_csv(sel_modules)
            elif action == 'export_excel':
                try:
                    return export_modules_excel(sel_modules)
                except Exception:
                    return export_modules_csv(sel_modules)
            elif action == 'export_pdf':
                try:
                    return export_modules_pdf(sel_modules)
                except Exception:
                    return export_modules_csv(sel_modules)
            elif action == 'bulk_delete' or action == 'delete_single':
                # Prevent deleting modules that are referenced by rules
                in_use_ids = set(
                    PermissionRule.objects.filter(module_id__in=selected_ids)
                    .values_list('module_id', flat=True)
                    .distinct()
                )
                deletable_qs = sel_modules.exclude(id__in=in_use_ids)
                blocked_qs = sel_modules.filter(id__in=in_use_ids)

                deleted_count = deletable_qs.count()
                deleted_names = list(deletable_qs.values_list('label_module', flat=True))
                if deleted_count > 0:
                    deletable_qs.delete()
                    UserTableSelection.objects.filter(user=request.user, page_key='module_list').delete()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'deleted': True, 'count': deleted_count, 'names': deleted_names})
                    else:
                        messages.success(request, f'{deleted_count} module berhasil dihapus: {", ".join(deleted_names[:5])}{"..." if deleted_count > 5 else ""}')

                blocked_count = blocked_qs.count()
                if blocked_count > 0:
                    blocked_names = list(blocked_qs.values_list('label_module', flat=True))
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'deleted': False, 'blocked': True, 'count': blocked_count, 'names': blocked_names}, status=400)
                    else:
                        messages.warning(request, f'{blocked_count} module tidak dihapus karena masih terhubung ke Rules: {", ".join(blocked_names[:5])}{"..." if blocked_count > 5 else ""}')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'deleted': False, 'count': 0})
                else:
                    return redirect('manajemen_aplikasi:module_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('manajemen_aplikasi:module_list')

    # ---- REGULAR GET ----
    modules_qs = PermissionModule.objects.annotate(rule_count=Count('rules'))
    search_query = request.GET.get('search', '').strip()
    if search_query:
        modules_qs = modules_qs.filter(
            Q(label_module__icontains=search_query) |
            Q(nama_module__icontains=search_query)
        )
    modules_qs = modules_qs.order_by('order', 'nama_module')

    total = modules_qs.count()
    modules_table = ModuleManageTable(modules_qs)
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    RequestConfig(request, paginate={'per_page': per_page}).configure(modules_table)

    context = {
        'table': modules_table,
        'total': total,
        'search_query': search_query,
    }
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'manajemen_aplikasi/access/ma_ap_modules/partials/_table.html', context)
    return render(request, 'manajemen_aplikasi/access/ma_ap_modules/list.html', context)


@permission_required_403('pengaturan', 'permission_module', 'create')
def module_create(request):
    """Create new module"""
    if request.method == 'POST':
        nama = (request.POST.get('nama_module') or '').strip()
        label = (request.POST.get('label_module') or '').strip()
        deskripsi = (request.POST.get('deskripsi_module') or '').strip()
        icon = (request.POST.get('icon') or 'fas fa-folder').strip()
        order = (request.POST.get('order') or '0')
        is_active = request.POST.get('is_active') == 'on'

        errors = []
        field_errors = {}
        if not nama:
            errors.append('Nama module harus diisi!')
            field_errors['nama_module'] = ['Nama module harus diisi!']
        if not label:
            errors.append('Label module harus diisi!')
            field_errors['label_module'] = ['Label module harus diisi!']
        if nama and PermissionModule.objects.filter(nama_module=nama).exists():
            dup_msg = f'Module "{nama}" sudah ada!'
            errors.append(dup_msg)
            field_errors.setdefault('nama_module', []).append(dup_msg)

        try:
            order_int = int(order)
        except ValueError:
            order_int = 0

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'module-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_modules/form.html', {
                    'errors_list': errors,
                })

        PermissionModule.objects.create(
            nama_module=nama,
            label_module=label,
            deskripsi_module=deskripsi,
            icon=icon,
            order=order_int,
            is_active=is_active
        )

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'module-form-success': {
                    'message': f'Module "{label}" berhasil dibuat!',
                    'redirect': reverse('manajemen_aplikasi:module_list')
                }
            })
            return resp

        messages.success(request, f'✅ Module "{label}" berhasil dibuat!')
        return redirect('manajemen_aplikasi:module_list')

    return render(request, 'manajemen_aplikasi/access/ma_ap_modules/form.html')


@permission_required_403('pengaturan', 'permission_module', 'edit')
def module_edit(request, mod_id):
    """Edit module"""
    module = get_object_or_404(PermissionModule, id=mod_id)
    rule_count = PermissionRule.objects.filter(module=module).count()

    if request.method == 'POST':
        nama = (request.POST.get('nama_module') or '').strip()
        label = (request.POST.get('label_module') or '').strip()
        deskripsi = (request.POST.get('deskripsi_module') or '').strip()
        icon = (request.POST.get('icon') or 'fas fa-folder').strip()
        order = (request.POST.get('order') or '0')
        is_active = request.POST.get('is_active') == 'on'

        errors = []
        field_errors = {}
        # Only allow editing nama_module when no rules are attached
        if rule_count == 0:
            if not nama:
                errors.append('Nama module harus diisi!')
                field_errors['nama_module'] = ['Nama module harus diisi!']
            else:
                if nama != module.nama_module and PermissionModule.objects.filter(nama_module=nama).exists():
                    dup_msg = f'Module "{nama}" sudah ada!'
                    errors.append(dup_msg)
                    field_errors.setdefault('nama_module', []).append(dup_msg)
        if not label:
            errors.append('Label module harus diisi!')
            field_errors['label_module'] = ['Label module harus diisi!']

        try:
            order_int = int(order)
        except ValueError:
            order_int = 0

        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'module-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_modules/form.html', {
                    'errors_list': errors,
                    'module': module,
                    'edit_mode': True,
                    'rule_count': rule_count,
                })

        # Update allowed fields
        if rule_count == 0 and nama and (nama != module.nama_module):
            module.nama_module = nama
        module.label_module = label
        module.deskripsi_module = deskripsi
        module.icon = icon
        module.order = order_int
        module.is_active = is_active
        module.save()

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'module-form-success': {
                    'message': f'Module "{label}" berhasil diupdate!',
                    'redirect': reverse('manajemen_aplikasi:module_list')
                }
            })
            return resp

        messages.success(request, f'✅ Module "{label}" berhasil diupdate!')
        return redirect('manajemen_aplikasi:module_list')

    context = {
        'module': module,
        'edit_mode': True,
        'rule_count': rule_count,
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_modules/form.html', context)


@permission_required_403('pengaturan', 'permission_module', 'delete')
def module_delete(request, mod_id):
    """Delete module"""
    module = get_object_or_404(PermissionModule, id=mod_id)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        # Get affected rules
        affected_rules = PermissionRule.objects.filter(module=module)
        if affected_rules.exists():
            if is_ajax:
                return JsonResponse({'success': False, 'deleted': False, 'blocked': True, 'name': module.label_module, 'rule_count': affected_rules.count()}, status=400)
            messages.error(request, f'Module "{module.label_module}" tidak bisa dihapus karena masih dipakai pada {affected_rules.count()} rule.')
            return redirect('manajemen_aplikasi:module_delete', mod_id=mod_id)

        mod_name = module.label_module
        module.delete()
        if is_ajax:
            return JsonResponse({'success': True, 'deleted': True, 'name': mod_name})
        messages.success(request, f'✅ Module "{mod_name}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:module_list')

    # Get affected rules
    affected_rules = PermissionRule.objects.filter(module=module)

    context = {
        'module': module,
        'affected_rules': affected_rules,
        'rule_count': affected_rules.count(),
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_modules/delete.html', context)
