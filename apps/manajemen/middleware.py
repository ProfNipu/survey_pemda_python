"""
Custom Middleware for Admin Access Restriction
Only superusers can access /admin/
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .helpers import check_permission


class AdminAccessMiddleware:
    """
    Middleware to restrict /admin/ access to superusers only
    Regular staff users will be redirected to custom dashboard
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if accessing /admin/
        if request.path.startswith('/admin/'):
            # Redirect login page to landing with next
            if request.path.startswith('/admin/login'):
                from urllib.parse import quote
                next_url = request.GET.get('next') or '/admin/'
                login_url = getattr(settings, 'LOGIN_URL', '/')
                return redirect(f"{login_url}?next={quote(next_url)}")
            
            # Redirect others to custom dashboard
            if request.user.is_authenticated:
                keys = getattr(settings, 'ADMIN_ACCESS_PERMISSION_KEYS', [
                    'pengaturan.manajemen_user.view',
                    'pengaturan.manajemen_permission.view',
                ])
                allowed = False
                for k in keys:
                    parts = [p.strip() for p in k.split('.') if p.strip()]
                    if len(parts) == 3 and check_permission(request.user, parts[0], parts[1], parts[2]):
                        allowed = True
                        break
                if allowed:
                    return self.get_response(request)
                messages.warning(
                    request,
                    '⚠️ Akses /admin/ memerlukan permission yang sesuai.'
                )
                return redirect('manajemen_aplikasi:dashboard')
            else:
                # Not authenticated, redirect to login
                return redirect('login')
        
        return self.get_response(request)
