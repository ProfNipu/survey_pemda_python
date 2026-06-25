
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count, Q
from django.db import IntegrityError
from django_tables2 import RequestConfig
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
import json
from urllib.parse import quote as urlquote
from django.core.exceptions import PermissionDenied

from apps.manajemen.decorators import permission_required_403
from apps.manajemen.models import UserTableSelection
from apps.manajemen.tables import UserTable
# Reuse existing export helpers to avoid duplication during incremental refactor
from apps.manajemen.views_granular import (
    export_users_csv,
    export_users_excel,
    export_users_pdf,
)

from apps.manajemen.forms import UserCreateForm, UserEditForm

User = get_user_model()


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'permission_user', 'view')
def user_list(request):
    """List all users with django-tables2 + HTMX support + Search + Export"""

    def _require(func_name: str) -> None:
        try:
            from apps.manajemen.helpers import check_permission
            if not check_permission(request.user, 'pengaturan', 'permission_user', func_name):
                raise PermissionDenied
        except PermissionDenied:
            raise
        except Exception:
            raise PermissionDenied
    # Get search query from GET or POST (POST for download with filter)
    search_query = request.GET.get('search', '').strip() or request.POST.get('search', '').strip()

    # Get status filter from POST (download) or GET (datatable), prioritize POST
    status_filter = request.POST.get('status') or request.GET.get('status', 'all')

    # Queryset with group count annotation
    users = User.objects.annotate(group_count=Count('groups'))

    # Handle JSON selection save/load (AJAX only)
    if (
        request.method == 'POST'
        and request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        and (request.headers.get('Content-Type') or '').startswith('application/json')
    ):
        import json
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'save_selection':
            page_key = data.get('page_key', 'user_list')
            selected_ids = data.get('selected_ids', [])
            UserTableSelection.objects.update_or_create(
                user=request.user,
                page_key=page_key,
                defaults={'selected_ids': selected_ids}
            )
            return JsonResponse({'success': True, 'count': len(selected_ids)})
        elif action == 'load_selection':
            page_key = data.get('page_key', 'user_list')
            try:
                selection = UserTableSelection.objects.get(user=request.user, page_key=page_key)
                return JsonResponse({'success': True, 'selected_ids': selection.selected_ids})
            except UserTableSelection.DoesNotExist:
                return JsonResponse({'success': True, 'selected_ids': []})

    # Handle selected actions (form-encoded POST)
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')

        if action in {'export_csv', 'export_excel', 'export_pdf'}:
            _require('export')
        elif action == 'bulk_delete':
            _require('bulk_delete')

        selected_ids = request.POST.getlist('selected_ids')
        # Support single id payloads as well
        if not selected_ids:
            single_id = request.POST.get('id')
            if single_id:
                selected_ids = [single_id]
        # Final fallback: use persisted selections if available (like functions page)
        if not selected_ids:
            try:
                selection = UserTableSelection.objects.get(user=request.user, page_key='user_list')
                selected_ids = selection.selected_ids or []
            except UserTableSelection.DoesNotExist:
                selected_ids = []

        if selected_ids:
            selected_users = User.objects.filter(id__in=selected_ids).annotate(
                group_count=Count('groups')
            ).order_by('-is_active', 'username')

            if action == 'export_csv':
                return export_users_csv(selected_users)
            elif action == 'export_excel':
                return export_users_excel(selected_users)
            elif action == 'export_pdf':
                return export_users_pdf(selected_users)
            elif action == 'bulk_delete':
                deleted_count = selected_users.count()
                deleted_usernames = list(selected_users.values_list('username', flat=True))
                selected_users.delete()
                UserTableSelection.objects.filter(user=request.user, page_key='user_list').delete()
                # AJAX: return JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'deleted': deleted_count,
                        'ids': selected_ids,
                        'names': deleted_usernames[:5],
                    })
                messages.success(request, f'{deleted_count} user berhasil dihapus: {", ".join(deleted_usernames[:5])}{"..." if deleted_count > 5 else ""}')
                return redirect('manajemen_aplikasi:users_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Tidak ada item yang dipilih'}, status=400)
            messages.error(request, 'Tidak ada item yang dipilih')
            return redirect('manajemen_aplikasi:users_list')

    # Apply filters for GET
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    status_filter_value = status_filter
    if status_filter_value == 'active':
        users = users.filter(is_active=True)
    elif status_filter_value == 'inactive':
        users = users.filter(is_active=False)

    users = users.order_by('id')

    # Handle export ALL (form posts from table header buttons)
    if request.method == 'POST' and request.POST.get('export_all'):
        _require('export')
        fmt = (request.POST.get('export_all') or '').lower()
        # Use filtered queryset (already annotated & filtered above), with a stable order
        export_qs = users.annotate(group_count=Count('groups')).order_by('id')
        if fmt == 'excel':
            return export_users_excel(export_qs)
        elif fmt == 'csv':
            return export_users_csv(export_qs)
        elif fmt == 'pdf':
            return export_users_pdf(export_qs)
        else:
            # Unknown format -> default to Excel
            return export_users_excel(export_qs)

    table = UserTable(users)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)

    context = {
        'table': table,
        'total': users.count(),
        'active_count': users.filter(is_active=True).count(),
        'search_query': search_query,
        'status_list': [
            {'value': 'active', 'label': 'Active'},
            {'value': 'inactive', 'label': 'Inactive'},
        ],
    }

    # HTMX partial
    is_htmx = request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_htmx:
        return render(request, 'manajemen_aplikasi/access/ma_ap_users/partials/_table.html', context)
    return render(request, 'manajemen_aplikasi/access/ma_ap_users/list.html', context)


@permission_required_403('pengaturan', 'permission_user', 'create')
def users_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            full_name = f"{cd.get('first_name') or ''} {cd.get('last_name') or ''}".strip() or cd['username']
            try:
                user = User.objects.create_user(
                    username=cd['username'],
                    email=(cd.get('email') or None),
                    password=cd['password'],
                    name=full_name,
                    is_active=bool(cd.get('is_active')),
                )
            except IntegrityError:
                # Likely email/username uniqueness
                if cd.get('email'):
                    form.add_error('email', 'Email sudah digunakan.')
                else:
                    form.add_error('username', 'Username sudah digunakan.')
                errors_list = []
                field_errors = {}
                for field, errors in form.errors.items():
                    field_errors[field] = [str(e) for e in errors]
                    for err in errors:
                        errors_list.append(str(err))
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'user-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
                return resp

            # HTMX-friendly success: show SweetAlert then redirect
            if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({
                    'user-form-success': {
                        'message': f'User "{user.username}" berhasil dibuat!',
                        'redirect': reverse('manajemen_aplikasi:users_list')
                    }
                })
                return resp
            # Non-HTMX: redirect with SweetAlert query params (no toast)
            msg = f'User "{user.username}" berhasil dibuat!'
            return redirect(f"{reverse('manajemen_aplikasi:users_list')}?swal=success&msg={urlquote(msg)}")
        pass
        errors_list = []
        field_errors = {}
        for field, errors in form.errors.items():
            field_errors[field] = [str(e) for e in errors]
            for err in errors:
                errors_list.append(str(err))
        resp = HttpResponse(status=204)
        resp['HX-Trigger'] = json.dumps({'user-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
        return resp
    form = UserCreateForm(initial={'is_active': True})
    return render(request, 'manajemen_aplikasi/access/ma_ap_users/form.html', {
        'form': form,
        'edit_mode': False,
    })


@permission_required_403('pengaturan', 'permission_user', 'edit')
def users_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, user=user)
        if form.is_valid():
            cd = form.cleaned_data
            new_username = cd.get('username') or user.username
            new_email = (cd.get('email') or None)
            fname = cd.get('first_name') or ''
            lname = cd.get('last_name') or ''
            new_name = (f"{fname} {lname}".strip() or (user.name or user.username))
            new_is_active = bool(cd.get('is_active'))
            pwd = cd.get('password') or ''

            # If nothing changes, treat as success (no-op) and show SweetAlert success
            has_changes = (
                new_username != user.username or
                (new_email or '') != (user.email or '') or
                (new_name or '') != (user.name or '') or
                new_is_active != bool(user.is_active) or
                bool(pwd)
            )
            if not has_changes:
                if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    resp = HttpResponse(status=204)
                    resp['HX-Trigger'] = json.dumps({
                        'user-form-success': {
                            'message': f'User "{user.username}" tidak ada perubahan.',
                            'redirect': reverse('manajemen_aplikasi:users_list')
                        }
                    })
                    return resp
                msg = f'User "{user.username}" tidak ada perubahan.'
                return redirect(f"{reverse('manajemen_aplikasi:users_list')}?swal=success&msg={urlquote(msg)}")

            # Apply changes and save
            user.username = new_username
            user.email = new_email
            user.name = new_name
            user.is_active = new_is_active
            if pwd:
                user.set_password(pwd)
            try:
                user.save()
            except IntegrityError:
                if cd.get('email'):
                    form.add_error('email', 'Email sudah digunakan.')
                else:
                    form.add_error('username', 'Username sudah digunakan.')
                errors_list = []
                field_errors = {}
                for field, errors in form.errors.items():
                    field_errors[field] = [str(e) for e in errors]
                    for err in errors:
                        errors_list.append(str(err))
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({'user-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
                return resp
            # HTMX-friendly success: show SweetAlert then redirect
            if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                resp = HttpResponse(status=204)
                resp['HX-Trigger'] = json.dumps({
                    'user-form-success': {
                        'message': f'User "{user.username}" berhasil diupdate!',
                        'redirect': reverse('manajemen_aplikasi:users_list')
                    }
                })
                return resp
            # Non-HTMX: redirect with SweetAlert query params (no toast)
            msg = f'User "{user.username}" berhasil diupdate!'
            return redirect(f"{reverse('manajemen_aplikasi:users_list')}?swal=success&msg={urlquote(msg)}")
        pass
        errors_list = []
        field_errors = {}
        for field, errors in form.errors.items():
            field_errors[field] = [str(e) for e in errors]
            for err in errors:
                errors_list.append(str(err))
        resp = HttpResponse(status=204)
        resp['HX-Trigger'] = json.dumps({'user-form-invalid': {'errors': errors_list, 'fieldErrors': field_errors}})
        return resp
    form = UserEditForm(initial={
        'username': user.username,
        'first_name': user.name,
        'last_name': '',
        'email': user.email or '',
        'is_active': user.is_active,
    }, user=user)
    user_obj = {
        'username': user.username,
        'first_name': user.name,
        'last_name': '',
        'email': user.email or '',
        'is_active': user.is_active,
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_users/form.html', {
        'form': form,
        'user_obj': user_obj,
        'edit_mode': True,
    })


@permission_required_403('pengaturan', 'permission_user', 'delete')
def users_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    from apps.manajemen.helpers import is_superadmin
    if is_superadmin(user):
        messages.error(request, 'Tidak bisa menghapus superuser!')
        return redirect('manajemen_aplikasi:users_list')
    if user.id == request.user.id:
        messages.error(request, 'Tidak bisa menghapus diri sendiri!')
        return redirect('manajemen_aplikasi:users_list')
    if request.method == 'POST':
        username = user.username
        user.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'deleted': user_id, 'name': username})
        messages.success(request, f'✅ User "{username}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:users_list')
    return render(request, 'manajemen_aplikasi/access/ma_ap_users/delete.html', { 'user_obj': user })


@permission_required_403('pengaturan', 'permission_user', 'edit')
def users_assign_roles(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        role_ids = request.POST.getlist('roles')
        user.groups.clear()
        if role_ids:
            roles = Group.objects.filter(id__in=role_ids)
            user.groups.set(roles)
        messages.success(request, f'✅ Roles untuk user "{user.username}" berhasil diupdate!')
        return redirect('manajemen_aplikasi:users_list')
    all_roles = Group.objects.all().order_by('name')
    user_role_ids = set(user.groups.values_list('id', flat=True))
    for role in all_roles:
        role.is_selected = role.id in user_role_ids
    return render(request, 'manajemen_aplikasi/access/ma_ap_users/assign_roles.html', {
        'user_obj': user,
        'all_roles': all_roles,
        'selected_count': len(user_role_ids),
    })
