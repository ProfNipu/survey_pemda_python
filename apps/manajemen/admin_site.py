from django.contrib.admin import AdminSite
from django.conf import settings
from .helpers import check_permission


class PermissionAdminSite(AdminSite):
    _brand = getattr(settings, 'APP_NAME', 'aplikasi-test')
    site_header = f'{_brand} Administration'
    site_title = f'{_brand} Admin'
    index_title = f'Welcome to {_brand} Administration'

    def has_permission(self, request):
        # Allow login page to render
        if not request.user.is_authenticated:
            return False
        keys = getattr(settings, 'ADMIN_ACCESS_PERMISSION_KEYS', [
            'pengaturan.manajemen_user.view',
            'pengaturan.manajemen_permission.view',
        ])
        for k in keys:
            parts = [p.strip() for p in k.split('.') if p.strip()]
            if len(parts) == 3 and check_permission(request.user, parts[0], parts[1], parts[2]):
                return True
        return False


permission_admin_site = PermissionAdminSite(name='permissions_admin')
