"""
Permission Helper Functions
For checking permissions and getting user access
"""

from django.contrib.auth.models import User
from django.conf import settings
from .models import PermissionModule, PermissionRule, RoleRule


def is_superadmin(user):
    """Return True if user is considered super admin.
    Super admin if either:
      - user.is_superuser is True, OR
      - user belongs to any group listed in settings.SUPERADMIN_GROUPS
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    groups = getattr(settings, 'SUPERADMIN_GROUPS', ['Super Admin'])
    try:
        group_list = [g.strip() for g in groups] if isinstance(groups, (list, tuple)) else [str(groups)]
    except Exception:
        group_list = ['Super Admin']
    return user.groups.filter(name__in=group_list).exists()


def check_permission(user, module_name, control_name, function_name):
    """
    Check if user has permission for specific module, control, and function
    
    Args:
        user: User object
        module_name: str - Module name (e.g., 'pegawai')
        control_name: str - Control name (e.g., 'ms_pegawai')
        function_name: str - Function name (e.g., 'view')
    
    Returns:
        bool: True if user has permission, False otherwise
    
    Example:
        if check_permission(request.user, 'pegawai', 'ms_pegawai', 'view'):
            # User can view ms_pegawai
    """
    # Superuser/group override (only if enabled)
    if getattr(settings, 'PERMISSIONS_SUPERADMIN_OVERRIDE', False) and is_superadmin(user):
        return True
    
    # Get user's roles (groups)
    user_roles = user.groups.all()
    
    if not user_roles.exists():
        return False
    
    # Check if user has permission through any of their roles
    return RoleRule.objects.filter(
        role__in=user_roles,
        rule__module__nama_module=module_name,
        rule__control__nama_kontrol=control_name,
        rule__function__nama_fungsi=function_name,
        rule__is_active=True,
        rule__module__is_active=True
    ).exists()


def get_user_modules(user):
    """
    Get list of modules (sidebar menu) that user has access to
    
    Args:
        user: User object
    
    Returns:
        QuerySet: PermissionModule objects that user has access to
    
    Example:
        modules = get_user_modules(request.user)
        for module in modules:
            print(module.label_module, module.icon)
    """
    # Superuser/group override (only if enabled)
    if getattr(settings, 'PERMISSIONS_SUPERADMIN_OVERRIDE', False) and is_superadmin(user):
        return PermissionModule.objects.filter(is_active=True)
    
    # Get user's roles (groups)
    user_roles = user.groups.all()
    
    if not user_roles.exists():
        return PermissionModule.objects.none()
    
    # Get unique modules from user's role rules
    module_ids = RoleRule.objects.filter(
        role__in=user_roles,
        rule__is_active=True,
        rule__module__is_active=True
    ).values_list('rule__module_id', flat=True).distinct()
    
    return PermissionModule.objects.filter(id__in=module_ids)


def get_user_controls(user, module_name):
    """
    Get list of controls that user has access to within a module
    
    Args:
        user: User object
        module_name: str - Module name
    
    Returns:
        QuerySet: PermissionControl objects that user has access to
    
    Example:
        controls = get_user_controls(request.user, 'pegawai')
        for control in controls:
            print(control.label_kontrol)
    """
    # Superuser/group override (only if enabled)
    if getattr(settings, 'PERMISSIONS_SUPERADMIN_OVERRIDE', False) and is_superadmin(user):
        from .models import PermissionControl
        control_ids = PermissionRule.objects.filter(
            module__nama_module=module_name,
            is_active=True
        ).values_list('control_id', flat=True).distinct()
        return PermissionControl.objects.filter(id__in=control_ids)
    
    # Get user's roles (groups)
    user_roles = user.groups.all()
    
    if not user_roles.exists():
        from .models import PermissionControl
        return PermissionControl.objects.none()
    
    # Get unique controls from user's role rules for this module
    from .models import PermissionControl
    control_ids = RoleRule.objects.filter(
        role__in=user_roles,
        rule__module__nama_module=module_name,
        rule__is_active=True
    ).values_list('rule__control_id', flat=True).distinct()
    
    return PermissionControl.objects.filter(id__in=control_ids)


def get_user_functions(user, module_name, control_name):
    """
    Get list of functions that user has access to for a specific control
    
    Args:
        user: User object
        module_name: str - Module name
        control_name: str - Control name
    
    Returns:
        QuerySet: PermissionFunction objects that user has access to
    
    Example:
        functions = get_user_functions(request.user, 'pegawai', 'ms_pegawai')
        if 'view' in [f.nama_fungsi for f in functions]:
            # User can view
    """
    # Superuser/group override (only if enabled)
    if getattr(settings, 'PERMISSIONS_SUPERADMIN_OVERRIDE', False) and is_superadmin(user):
        from .models import PermissionFunction
        function_ids = PermissionRule.objects.filter(
            module__nama_module=module_name,
            control__nama_kontrol=control_name,
            is_active=True
        ).values_list('function_id', flat=True).distinct()
        return PermissionFunction.objects.filter(id__in=function_ids)
    
    # Get user's roles (groups)
    user_roles = user.groups.all()
    
    if not user_roles.exists():
        from .models import PermissionFunction
        return PermissionFunction.objects.none()
    
    # Get unique functions from user's role rules
    from .models import PermissionFunction
    function_ids = RoleRule.objects.filter(
        role__in=user_roles,
        rule__module__nama_module=module_name,
        rule__control__nama_kontrol=control_name,
        rule__is_active=True
    ).values_list('rule__function_id', flat=True).distinct()
    
    return PermissionFunction.objects.filter(id__in=function_ids)


def get_user_rules(user):
    """
    Get all permission rules for a user
    
    Args:
        user: User object
    
    Returns:
        QuerySet: PermissionRule objects that user has access to
    
    Example:
        rules = get_user_rules(request.user)
        for rule in rules:
            print(rule.permission_string)
    """
    # Superuser/group override (only if enabled)
    if getattr(settings, 'PERMISSIONS_SUPERADMIN_OVERRIDE', False) and is_superadmin(user):
        return PermissionRule.objects.filter(is_active=True)
    
    # Get user's roles (groups)
    user_roles = user.groups.all()
    
    if not user_roles.exists():
        return PermissionRule.objects.none()
    
    # Get all rules from user's role assignments
    rule_ids = RoleRule.objects.filter(
        role__in=user_roles
    ).values_list('rule_id', flat=True).distinct()
    
    return PermissionRule.objects.filter(id__in=rule_ids, is_active=True)


def has_any_permission(user, module_name):
    """
    Check if user has any permission in a module
    Useful for showing/hiding module in sidebar
    
    Args:
        user: User object
        module_name: str - Module name
    
    Returns:
        bool: True if user has any permission in the module
    
    Example:
        if has_any_permission(request.user, 'pegawai'):
            # Show Pegawai menu in sidebar
    """
    # Superuser/group override (only if enabled)
    if getattr(settings, 'PERMISSIONS_SUPERADMIN_OVERRIDE', False) and is_superadmin(user):
        return True
    
    # Get user's roles (groups)
    user_roles = user.groups.all()
    
    if not user_roles.exists():
        return False
    
    # Check if user has any permission in this module
    return RoleRule.objects.filter(
        role__in=user_roles,
        rule__module__nama_module=module_name,
        rule__is_active=True,
        rule__module__is_active=True
    ).exists()
