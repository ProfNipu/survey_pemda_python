from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from urllib.parse import quote as urlquote
from django.db.models import Count
from django_tables2 import RequestConfig
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
import json
from django.core.exceptions import PermissionDenied

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.models import UserTableSelection
from apps.manajemen.tables import RoleTable
# Reuse existing export helpers to avoid duplication during incremental refactor
from apps.manajemen.views_granular import (
    export_roles_csv,
    export_roles_excel,
    export_roles_pdf,
)

User = get_user_model()


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'permission_role', 'view')
def role_list(request):
    """List all roles (groups) with django-tables2 + HTMX + Selection Persistence"""

    def _require(func_name: str) -> None:
        try:
            from apps.manajemen.helpers import check_permission
            if not check_permission(request.user, 'pengaturan', 'permission_role', func_name):
                raise PermissionDenied
        except PermissionDenied:
            raise
        except Exception:
            raise PermissionDenied

    # Handle download ALL data from database (POST with export_all)
    if request.method == 'POST' and 'export_all' in request.POST:
        _require('export')
        export_format = request.POST.get('export_all')
        search_query = request.POST.get('search', '').strip()
        all_roles = Group.objects.all()
        if search_query:
            all_roles = all_roles.filter(name__icontains=search_query)
        all_roles = all_roles.order_by('name')
        if export_format == 'excel':
            return export_roles_excel(all_roles)
        elif export_format == 'pdf':
            return export_roles_pdf(all_roles)

    # Handle save/load selections (AJAX POST) - only for JSON requests
    if (
        request.method == 'POST'
        and request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        and (request.headers.get('Content-Type') or '').startswith('application/json')
    ):
        import json
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'save_selection':
            page_key = data.get('page_key', 'role_list')
            selected_ids = data.get('selected_ids', [])
            UserTableSelection.objects.update_or_create(
                user=request.user,
                page_key=page_key,
                defaults={'selected_ids': selected_ids}
            )
            return JsonResponse({'success': True, 'count': len(selected_ids)})
        elif action == 'load_selection':
            page_key = data.get('page_key', 'role_list')
            try:
                selection = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                return JsonResponse({'success': True, 'selected_ids': selection.selected_ids})
            except UserTableSelection.DoesNotExist:
                return JsonResponse({'success': True, 'selected_ids': []})

    # Handle bulk actions (POST with action)
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')

        if action in {'export_csv', 'export_excel', 'export_pdf'}:
            _require('export')
        elif action == 'bulk_delete':
            _require('bulk_delete')

        selected_ids = request.POST.getlist('selected_ids')
        if selected_ids:
            selected_roles = Group.objects.filter(id__in=selected_ids).annotate(
                users_count=Count('user'),
                permissions_count=Count('permissions')
            ).order_by('name')
            if action == 'export_csv':
                return export_roles_csv(selected_roles)
            elif action == 'export_excel':
                return export_roles_excel(selected_roles)
            elif action == 'export_pdf':
                return export_roles_pdf(selected_roles)
            elif action == 'bulk_delete':
                deleted_count = selected_roles.count()
                deleted_names = list(selected_roles.values_list('name', flat=True))
                selected_roles.delete()
                UserTableSelection.objects.filter(user=request.user, page_key='role_list').delete()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'deleted': deleted_count, 'ids': selected_ids, 'names': deleted_names[:5]})
                messages.success(request, f'{deleted_count} role berhasil dihapus: {", ".join(deleted_names[:5])}{"..." if deleted_count > 5 else ""}')
                return redirect('manajemen_aplikasi:roles_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('manajemen_aplikasi:roles_list')

    # Regular GET
    roles = Group.objects.all()
    search_query = request.GET.get('search', '').strip()
    if search_query:
        roles = roles.filter(name__icontains=search_query)
    roles = roles.order_by('name')
    total = roles.count()
    active = roles.filter(user__is_active=True).distinct().count()
    table = RoleTable(roles)
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    RequestConfig(request, paginate={'per_page': per_page}).configure(table)
    context = {'table': table, 'total': total, 'active_count': active, 'search_query': search_query}

    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'manajemen_aplikasi/access/ma_ap_roles/partials/_table.html', context)
    return render(request, 'manajemen_aplikasi/access/ma_ap_roles/list.html', context)


@permission_required_403('pengaturan', 'permission_role', 'create')
def role_create(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        errors = []
        field_errors = {}
        if not name:
            errors.append('Nama role harus diisi!')
            field_errors['name'] = ['Nama role harus diisi!']
        elif Group.objects.filter(name=name).exists():
            dup_msg = f'Role "{name}" sudah ada!'
            errors.append(dup_msg)
            field_errors['name'] = [dup_msg]

        # HTMX detection
        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = render(request, 'manajemen_aplikasi/access/ma_ap_roles/form.html', {
                    'errors_list': errors,
                    'role_name': name,
                    'edit_mode': False,
                })
                resp['HX-Trigger-After-Swap'] = json.dumps({'role-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_roles/form.html', {
                    'errors_list': errors,
                    'role_name': name,
                    'edit_mode': False,
                })

        # Create role
        Group.objects.create(name=name)

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'role-form-success': {
                    'message': f'Role "{name}" berhasil dibuat!',
                    'redirect': reverse('manajemen_aplikasi:roles_list')
                }
            })
            return resp
        # Non-HTMX fallback: redirect with SweetAlert query param (consistent with users_create)
        msg = f'Role "{name}" berhasil dibuat!'
        return redirect(f"{reverse('manajemen_aplikasi:roles_list')}?swal=success&msg={urlquote(msg)}")

    return render(request, 'manajemen_aplikasi/access/ma_ap_roles/form.html')


@permission_required_403('pengaturan', 'permission_role', 'edit')
def role_edit(request, role_id):
    role = get_object_or_404(Group, id=role_id)
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        errors = []
        field_errors = {}
        if not name:
            errors.append('Nama role harus diisi!')
            field_errors['name'] = ['Nama role harus diisi!']
        elif name != role.name and Group.objects.filter(name=name).exists():
            dup_msg = f'Role "{name}" sudah ada!'
            errors.append(dup_msg)
            field_errors['name'] = [dup_msg]

        # HTMX detection
        is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if errors:
            if is_htmx:
                resp = render(request, 'manajemen_aplikasi/access/ma_ap_roles/form.html', {
                    'errors_list': errors,
                    'role_name': name,
                    'role': role,
                    'edit_mode': True,
                })
                resp['HX-Trigger-After-Swap'] = json.dumps({'role-form-invalid': {'errors': errors, 'fieldErrors': field_errors}})
                return resp
            else:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'manajemen_aplikasi/access/ma_ap_roles/form.html', {
                    'errors_list': errors,
                    'role_name': name,
                    'role': role,
                    'edit_mode': True,
                })

        # Update role
        role.name = name
        role.save()

        if is_htmx:
            resp = HttpResponse(status=204)
            resp['HX-Trigger'] = json.dumps({
                'role-form-success': {
                    'message': f'Role "{name}" berhasil diupdate!',
                    'redirect': reverse('manajemen_aplikasi:roles_list')
                }
            })
            return resp
        # Non-HTMX fallback
        msg = f'Role "{name}" berhasil diupdate!'
        return redirect(f"{reverse('manajemen_aplikasi:roles_list')}?swal=success&msg={urlquote(msg)}")

    return render(request, 'manajemen_aplikasi/access/ma_ap_roles/form.html', { 'role': role, 'edit_mode': True })


@permission_required_403('pengaturan', 'permission_role', 'delete')
def role_delete(request, role_id):
    role = get_object_or_404(Group, id=role_id)
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'deleted': role_id, 'name': role_name})
        messages.success(request, f'✅ Role "{role_name}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:roles_list')
    affected_users = User.objects.filter(groups=role)
    return render(request, 'manajemen_aplikasi/access/ma_ap_roles/delete.html', {
        'role': role,
        'affected_users': affected_users,
        'user_count': affected_users.count(),
    })
