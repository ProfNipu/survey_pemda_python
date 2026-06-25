"""
Permission Management Views
Centralized permission & role management for ALL modules
"""

import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django_tables2 import RequestConfig

from apps.manajemen.decorators import permission_required_403
from .models import ComboBoxConfig

User = get_user_model()


@ensure_csrf_cookie
@permission_required_403('pengaturan', 'combobox_config', 'view')
def combo_box_config_list(request):
    configs = ComboBoxConfig.objects.all().order_by('code')
    context = {
        'configs': configs,
    }
    return render(request, 'manajemen_aplikasi/access/ma_ap_combobox_config/list.html', context)


@permission_required_403('pengaturan', 'combobox_config', 'create')
def combo_box_config_create(request):
    if request.method == 'POST':
        code = (request.POST.get('code') or '').strip()
        label = (request.POST.get('label') or '').strip()
        is_active = request.POST.get('is_active') == 'on'
        cfg_raw = request.POST.get('config') or '{}'

        errors = []
        if not code:
            errors.append('Code harus diisi.')
        if not label:
            errors.append('Label harus diisi.')
        if ComboBoxConfig.objects.filter(code=code).exists():
            errors.append('Code sudah digunakan.')
        try:
            config_json = json.loads(cfg_raw or '{}')
        except Exception:
            config_json = None
            errors.append('Config harus JSON valid.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'manajemen_aplikasi/access/ma_ap_combobox_config/form.html', {'edit_mode': False, 'code': code, 'label': label, 'is_active': is_active, 'config_raw': cfg_raw})

        ComboBoxConfig.objects.create(code=code, label=label, is_active=is_active, config=config_json or {})
        messages.success(request, 'Konfigurasi berhasil dibuat')
        return redirect('manajemen_aplikasi:combobox_config_list')

    return render(request, 'manajemen_aplikasi/access/ma_ap_combobox_config/form.html', {'edit_mode': False})


@permission_required_403('pengaturan', 'combobox_config', 'edit')
def combo_box_config_edit(request, cfg_id):
    obj = get_object_or_404(ComboBoxConfig, id=cfg_id)
    if request.method == 'POST':
        code = (request.POST.get('code') or '').strip()
        label = (request.POST.get('label') or '').strip()
        is_active = request.POST.get('is_active') == 'on'
        cfg_raw = request.POST.get('config') or '{}'

        errors = []
        if not code:
            errors.append('Code harus diisi.')
        if not label:
            errors.append('Label harus diisi.')
        if ComboBoxConfig.objects.filter(code=code).exclude(id=obj.id).exists():
            errors.append('Code sudah digunakan.')
        try:
            config_json = json.loads(cfg_raw or '{}')
        except Exception:
            config_json = None
            errors.append('Config harus JSON valid.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'manajemen_aplikasi/access/ma_ap_combobox_config/form.html', {'edit_mode': True, 'obj': obj, 'code': code, 'label': label, 'is_active': is_active, 'config_raw': cfg_raw})

        obj.code = code
        obj.label = label
        obj.is_active = is_active
        obj.config = config_json or {}
        obj.save()
        messages.success(request, 'Konfigurasi berhasil diupdate')
        return redirect('manajemen_aplikasi:combobox_config_list')

    return render(
        request,
        'manajemen_aplikasi/access/ma_ap_combobox_config/form.html',
        {
            'edit_mode': True,
            'obj': obj,
            'code': obj.code,
            'label': obj.label,
            'is_active': obj.is_active,
            'config_raw': json.dumps(obj.config or {}, ensure_ascii=False, indent=2),
        },
    )


@permission_required_403('pengaturan', 'combobox_config', 'delete')
def combo_box_config_delete(request, cfg_id):
    obj = get_object_or_404(ComboBoxConfig, id=cfg_id)
    if request.method == 'POST':
        name = obj.label
        obj.delete()
        messages.success(request, f'Konfigurasi "{name}" berhasil dihapus')
        return redirect('manajemen_aplikasi:combobox_config_list')
    return render(request, 'manajemen_aplikasi/access/ma_ap_combobox_config/delete.html', {'obj': obj})


# ... rest of your code remains the same ...
@permission_required_403('pengaturan', 'permission_dashboard', 'view')
def permission_dashboard(request):
    """Dashboard overview of all permissions and roles"""
    
    # Get statistics
    total_permissions = Permission.objects.count()
    total_roles = Group.objects.count()
    total_users = User.objects.filter(is_active=True).count()
    
    # Get permissions by app
    permissions_by_app = {}
    for perm in Permission.objects.select_related('content_type').all():
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)
    
    # Get roles with permission count
    roles = Group.objects.annotate(
        perm_count=Count('permissions')
    ).order_by('name')
    
    context = {
        'total_permissions': total_permissions,
        'total_roles': total_roles,
        'total_users': total_users,
        'permissions_by_app': permissions_by_app,
        'roles': roles,
    }
    
    return render(request, 'manajemen_aplikasi/dashboard.html', context)


@permission_required_403('pengaturan', 'permission_rule', 'view')
def permission_list(request):
    """List all permissions from all apps"""
    
    # Get filter parameters
    app_filter = request.GET.get('app', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    permissions = Permission.objects.select_related('content_type').all()
    
    # Apply filters
    if app_filter:
        permissions = permissions.filter(content_type__app_label=app_filter)
    
    if search:
        permissions = permissions.filter(
            Q(name__icontains=search) | Q(codename__icontains=search)
        )
    
    # Get all apps for filter
    apps = ContentType.objects.values_list('app_label', flat=True).distinct().order_by('app_label')
    
    context = {
        'permissions': permissions.order_by('content_type__app_label', 'codename'),
        'apps': apps,
        'current_app': app_filter,
        'search': search,
        'total': permissions.count(),
    }
    
    return render(request, 'manajemen_aplikasi/list.html', context)


@permission_required_403('pengaturan', 'permission_rule', 'create')
def permission_create(request):
    """Create new permission"""
    
    if request.method == 'POST':
        app_label = request.POST.get('app_label', '').strip()
        model_name = request.POST.get('model_name', '').strip()
        codename = request.POST.get('codename', '').strip()
        name = request.POST.get('name', '').strip()
        
        if not all([app_label, model_name, codename, name]):
            messages.error(request, 'Semua field harus diisi!')
            return redirect('manajemen_aplikasi:permission_create')
        
        # Validate codename format
        if not codename.replace('_', '').isalnum():
            messages.error(request, 'Codename hanya boleh alfanumerik dan underscore!')
            return redirect('manajemen_aplikasi:permission_create')
        
        # Get or create content type
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            messages.error(request, f'Content type {app_label}.{model_name} tidak ditemukan!')
            return redirect('manajemen_aplikasi:permission_create')
        
        # Check if permission already exists
        if Permission.objects.filter(content_type=content_type, codename=codename).exists():
            messages.error(request, f'Permission "{codename}" sudah ada!')
            return redirect('manajemen_aplikasi:permission_create')
        
        # Create permission
        Permission.objects.create(
            codename=codename,
            name=name,
            content_type=content_type
        )
        
        messages.success(request, f'✅ Permission "{name}" berhasil dibuat!')
        return redirect('manajemen_aplikasi:permission_list')
    
    # Get all available content types
    content_types = ContentType.objects.order_by('app_label', 'model')
    apps = {}
    for ct in content_types:
        if ct.app_label not in apps:
            apps[ct.app_label] = []
        apps[ct.app_label].append(ct.model)
    
    context = {
        'apps': apps,
    }
    
    return render(request, 'manajemen_aplikasi/form.html', context)


@permission_required_403('pengaturan', 'permission_rule', 'edit')
def permission_edit(request, perm_id):
    """Edit existing permission"""
    
    permission = get_object_or_404(Permission, id=perm_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        if not name:
            messages.error(request, 'Display name harus diisi!')
            return redirect('manajemen_aplikasi:permission_edit', perm_id=perm_id)
        
        permission.name = name
        permission.save()
        
        messages.success(request, f'✅ Permission "{name}" berhasil diupdate!')
        return redirect('manajemen_aplikasi:permission_list')
    
    context = {
        'permission': permission,
        'edit_mode': True,
    }
    
    return render(request, 'manajemen_aplikasi/form.html', context)


@permission_required_403('pengaturan', 'permission_rule', 'delete')
def permission_delete(request, perm_id):
    """Delete permission"""
    
    permission = get_object_or_404(Permission, id=perm_id)
    
    if request.method == 'POST':
        perm_name = permission.name
        permission.delete()
        
        messages.success(request, f'✅ Permission "{perm_name}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:permission_list')
    
    # Get affected roles
    affected_roles = Group.objects.filter(permissions=permission)
    
    context = {
        'permission': permission,
        'affected_roles': affected_roles,
    }
    
    return render(request, 'manajemen_aplikasi/delete_confirm.html', context)


# ==================== ROLE MANAGEMENT ====================

@permission_required_403('pengaturan', 'permission_role', 'view')
def role_list(request):
    """List all roles"""
    
    roles = Group.objects.annotate(
        perm_count=Count('permissions'),
        user_count=Count('user')
    ).order_by('name')
    
    context = {
        'roles': roles,
        'total': roles.count(),
    }
    
    return render(request, 'manajemen_aplikasi/role_list.html', context)


@permission_required_403('pengaturan', 'permission_role', 'create')
def role_create(request):
    """Create new role"""
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        permission_ids = request.POST.getlist('permissions')
        
        if not name:
            messages.error(request, 'Nama role harus diisi!')
            return redirect('manajemen_aplikasi:role_create')
        
        if Group.objects.filter(name=name).exists():
            messages.error(request, f'Role "{name}" sudah ada!')
            return redirect('manajemen_aplikasi:role_create')
        
        # Create role
        role = Group.objects.create(name=name)
        
        # Assign permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        messages.success(request, f'✅ Role "{name}" berhasil dibuat dengan {len(permission_ids)} permissions!')
        return redirect('manajemen_aplikasi:role_list')
    
    # Get all permissions grouped by app
    permissions_by_app = {}
    for perm in Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename'):
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)
    
    context = {
        'permissions_by_app': permissions_by_app,
    }
    
    return render(request, 'manajemen_aplikasi/role_form.html', context)


@permission_required_403('pengaturan', 'permission_role', 'edit')
def role_edit(request, role_id):
    """Edit existing role"""
    
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        permission_ids = request.POST.getlist('permissions')
        
        if not name:
            messages.error(request, 'Nama role harus diisi!')
            return redirect('manajemen_aplikasi:role_edit', role_id=role_id)
        
        # Check if name changed and already exists
        if name != role.name and Group.objects.filter(name=name).exists():
            messages.error(request, f'Role "{name}" sudah ada!')
            return redirect('manajemen_aplikasi:role_edit', role_id=role_id)
        
        role.name = name
        role.save()
        
        # Update permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        else:
            role.permissions.clear()
        
        messages.success(request, f'✅ Role "{name}" berhasil diupdate!')
        return redirect('manajemen_aplikasi:role_list')
    
    # Get all permissions grouped by app
    permissions_by_app = {}
    role_permission_ids = set(role.permissions.values_list('id', flat=True))
    
    for perm in Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename'):
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        
        perm.is_selected = perm.id in role_permission_ids
        permissions_by_app[app_label].append(perm)
    
    context = {
        'role': role,
        'permissions_by_app': permissions_by_app,
        'edit_mode': True,
    }
    
    return render(request, 'manajemen_aplikasi/role_form.html', context)


@permission_required_403('pengaturan', 'permission_role', 'delete')
def role_delete(request, role_id):
    """Delete role"""
    
    role = get_object_or_404(Group, id=role_id)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        
        messages.success(request, f'✅ Role "{role_name}" berhasil dihapus!')
        return redirect('manajemen_aplikasi:role_list')
    
    # Get affected users
    affected_users = User.objects.filter(groups=role)
    
    context = {
        'role': role,
        'affected_users': affected_users,
        'user_count': affected_users.count(),
    }
    
    return render(request, 'manajemen_aplikasi/role_delete_confirm.html', context)


@permission_required_403('pengaturan', 'permission_user', 'edit')
def user_permissions(request, user_id):
    """Manage user permissions and roles"""
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        role_ids = request.POST.getlist('roles')
        
        # Update roles
        if role_ids:
            roles = Group.objects.filter(id__in=role_ids)
            user.groups.set(roles)
        else:
            user.groups.clear()
        
        messages.success(request, f'✅ Permissions untuk {user.username} berhasil diupdate!')
        return redirect('manajemen_aplikasi:permission_dashboard')
    
    # Get all roles
    all_roles = Group.objects.all()
    user_role_ids = set(user.groups.values_list('id', flat=True))
    
    for role in all_roles:
        role.is_selected = role.id in user_role_ids
    
    # Get all permissions for user
    user_permissions = user.get_all_permissions()
    
    context = {
        'user': user,
        'all_roles': all_roles,
        'user_permissions': sorted(user_permissions),
    }
    
    return render(request, 'manajemen_aplikasi/user_permissions.html', context)
