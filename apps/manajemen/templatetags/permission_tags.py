"""
Permission Template Tags
For checking permissions in Django templates
"""

from django import template
from apps.manajemen.helpers import (
    check_permission,
    get_user_modules,
    has_any_permission
)

register = template.Library()


@register.simple_tag(takes_context=True)
def has_permission(context, module_name, control_name, function_name):
    """
    Check if current user has specific permission
    
    Usage in template:
        {% load permission_tags %}
        {% has_permission 'pegawai' 'ms_pegawai' 'view' as can_view %}
        {% if can_view %}
            <a href="...">View Pegawai</a>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    return check_permission(request.user, module_name, control_name, function_name)


@register.simple_tag(takes_context=True)
def user_modules(context):
    """
    Get list of modules user has access to (for sidebar)
    
    Usage in template:
        {% load permission_tags %}
        {% user_modules as modules %}
        {% for module in modules %}
            <a href="{{ module.url }}">{{ module.label_module }}</a>
        {% endfor %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return []
    
    return get_user_modules(request.user)


@register.simple_tag(takes_context=True)
def can_access_module(context, module_name):
    """
    Check if user has any permission in a module (for showing/hiding menu)
    
    Usage in template:
        {% load permission_tags %}
        {% can_access_module 'pegawai' as can_access %}
        {% if can_access %}
            <li class="menu-item">Pegawai</li>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    return has_any_permission(request.user, module_name)


@register.filter
def can(user, permission_string):
    """
    Filter to check permission using string format
    
    Usage in template:
        {% load permission_tags %}
        {% if request.user|can:'pegawai.ms_pegawai.view' %}
            <button>View</button>
        {% endif %}
    
    Args:
        user: User object
        permission_string: str in format 'module.control.function'
    """
    if not user.is_authenticated:
        return False
    
    try:
        parts = permission_string.split('.')
        if len(parts) != 3:
            return False
        
        module_name, control_name, function_name = parts
        return check_permission(user, module_name, control_name, function_name)
    except:
        return False


@register.inclusion_tag('manajemen_aplikasi/tags/permission_button.html', takes_context=True)
def permission_button(context, module, control, function, label, url, css_class='btn btn-primary'):
    """
    Render a button only if user has permission
    
    Usage in template:
        {% load permission_tags %}
        {% permission_button 'pegawai' 'ms_pegawai' 'create' 'Tambah Pegawai' '/pegawai/create/' 'btn btn-success' %}
    """
    request = context.get('request')
    has_perm = False
    
    if request and request.user.is_authenticated:
        has_perm = check_permission(request.user, module, control, function)
    
    return {
        'has_permission': has_perm,
        'label': label,
        'url': url,
        'css_class': css_class,
    }


@register.inclusion_tag('manajemen_aplikasi/tags/permission_link.html', takes_context=True)
def permission_link(context, module, control, function, label, url, icon=''):
    """
    Render a link only if user has permission
    
    Usage in template:
        {% load permission_tags %}
        {% permission_link 'pegawai' 'ms_pegawai' 'view' 'Lihat Pegawai' '/pegawai/' 'fas fa-eye' %}
    """
    request = context.get('request')
    has_perm = False
    
    if request and request.user.is_authenticated:
        has_perm = check_permission(request.user, module, control, function)
    
    return {
        'has_permission': has_perm,
        'label': label,
        'url': url,
        'icon': icon,
    }
