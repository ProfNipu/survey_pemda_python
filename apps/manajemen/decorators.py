"""
Permission Decorators
For protecting views with granular permissions
"""

from functools import wraps
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseForbidden
from .helpers import check_permission


def permission_required(module_name, control_name, function_name, redirect_url='dashboard'):
    """
    Decorator to check if user has specific permission
    
    Usage:
        @permission_required('pegawai', 'ms_pegawai', 'view')
        def my_view(request):
            # Only users with permission can access
            pass
    
    Args:
        module_name: str - Module name
        control_name: str - Control name
        function_name: str - Function name
        redirect_url: str - URL name to redirect if no permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.error(request, 'Anda harus login terlebih dahulu.')
                return redirect('login')
            
            # Check permission
            if check_permission(request.user, module_name, control_name, function_name):
                return view_func(request, *args, **kwargs)
            
            # No permission
            messages.error(request, f'Anda tidak memiliki akses untuk {function_name} {control_name}.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def any_permission_required(permissions, redirect_url='dashboard'):
    """
    Decorator to check if user has any of the specified permissions
    
    Usage:
        @any_permission_required([
            ('pegawai', 'ms_pegawai', 'view'),
            ('pegawai', 'pegawai_siasn', 'view'),
        ])
        def my_view(request):
            # User needs at least one permission
            pass
    
    Args:
        permissions: list of tuples (module, control, function)
        redirect_url: str - URL name to redirect if no permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.error(request, 'Anda harus login terlebih dahulu.')
                return redirect('login')
            
            # Check if user has any of the permissions
            for module_name, control_name, function_name in permissions:
                if check_permission(request.user, module_name, control_name, function_name):
                    return view_func(request, *args, **kwargs)
            
            # No permission
            messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def all_permissions_required(permissions, redirect_url='dashboard'):
    """
    Decorator to check if user has all of the specified permissions
    
    Usage:
        @all_permissions_required([
            ('pegawai', 'ms_pegawai', 'view'),
            ('pegawai', 'ms_pegawai', 'edit'),
        ])
        def my_view(request):
            # User needs all permissions
            pass
    
    Args:
        permissions: list of tuples (module, control, function)
        redirect_url: str - URL name to redirect if no permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.error(request, 'Anda harus login terlebih dahulu.')
                return redirect('login')
            
            # Check if user has all permissions
            for module_name, control_name, function_name in permissions:
                if not check_permission(request.user, module_name, control_name, function_name):
                    messages.error(request, 'Anda tidak memiliki akses lengkap ke halaman ini.')
                    return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def permission_required_403(module_name, control_name, function_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Anda harus login terlebih dahulu.')
                return redirect('login')
            if check_permission(request.user, module_name, control_name, function_name):
                return view_func(request, *args, **kwargs)
            context = {
                'forbidden_title': 'Tidak Memiliki Akses',
                'forbidden_message': f'Anda tidak memiliki permission untuk {function_name} pada {control_name}.',
            }
            return render(request, '403.html', context=context, status=403)
        return wrapper
    return decorator
