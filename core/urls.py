"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from apps.manajemen.admin_site import permission_admin_site

# Admin customization (applies to both default and custom admin site)
admin_brand = getattr(settings, 'APP_NAME', 'aplikasi-test')
admin.site.site_header = f'{admin_brand} Administration'
admin.site.site_title = f'{admin_brand} Admin'
admin.site.index_title = f'Welcome to {admin_brand} Administration'

# Use custom PermissionAdminSite that authorizes via permission keys
# 1) Ensure default admin discovers all registered ModelAdmins
admin.autodiscover()

# 2) Copy all registrations from default admin to custom site
from django.contrib.admin.sites import AlreadyRegistered
for model, modeladmin in admin.site._registry.items():
    try:
        permission_admin_site.register(model, type(modeladmin))
    except AlreadyRegistered:
        pass

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    # Alias for legacy reverse('login') calls
    path('login/', views.landing_page, name='login'),
    path('accounts/', include('apps.accounts.urls')),  # Custom authentication
    # Admin disabled - use custom views instead
    path('admin/', RedirectView.as_view(url='/dashboard/', permanent=False), name='admin_redirect'),
    path('health/', views.health_check, name='health_check'),
    path('session/status', views.session_status, name='session_status'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('api/', include('rest_framework.urls')),
    path('manajemen-aplikasi/', include('apps.manajemen.urls')),  # Centralized Permission Management
    path('api-simpeg/', include('apps.api_simpeg.urls')),  # API SIMPEG Integration
    path('survey/', include('apps.survey.urls')),  # Survey (Dynamic Survey System)
    # Backward-compat redirect
    path('permissions/', RedirectView.as_view(url='/manajemen-aplikasi/akses-granular/', permanent=False)),
    # Dev test error pages
    path('dev/test-400/', views.dev_test_400, name='dev_test_400'),
    path('dev/test-404/', views.dev_test_404, name='dev_test_404'),
    path('dev/test-500/', views.dev_test_500, name='dev_test_500'),
    
    # ========================================
    # API aplikasi-test v4.0 (Laravel Compatible)
    # ========================================
    path('apiaplikasi-test/4.0/login/username-aplikasi-test', views.api_login_v4, name='api_login_v4'),  # Session-based login (OLD)
    path('apiaplikasi-test/4.0/login/get-token', views.api_jwt_login_v4, name='api_jwt_login_v4'),  # JWT Login (Permanent Token)
    path('apiaplikasi-test/4.0/logout', views.api_logout_v4, name='api_logout_v4'),  # JWT Logout
    
    # ========================================
    # API aplikasi-test v5.0 (Modern API)
    # ========================================
    # Session-based
    path('apiaplikasi-test/5.0/login/username-aplikasi-test', views.api_login_v5, name='api_login_v5'),
    
    # JWT Authentication
    path('apiaplikasi-test/5.0/auth/login', views.api_jwt_login_v5, name='api_jwt_login_v5'),
    path('apiaplikasi-test/5.0/auth/verify', views.api_jwt_verify_v5, name='api_jwt_verify_v5'),
    path('apiaplikasi-test/5.0/auth/refresh', views.api_jwt_refresh_v5, name='api_jwt_refresh_v5'),
    path('apiaplikasi-test/5.0/auth/logout', views.api_logout_v5, name='api_logout_v5'),
    path('apiaplikasi-test/5.0/auth/revoke-all-tokens', views.api_revoke_all_tokens_v5, name='api_revoke_all_tokens_v5'),
    path('apiaplikasi-test/5.0/auth/revoke-by-username', views.api_revoke_by_username_v5, name='api_revoke_by_username_v5'),
    
    # Resources
    path('apiaplikasi-test/5.0/users/list', views.api_users_list_v5, name='api_users_list_v5'),
    
    # path('api/pegawai/', include('apps.pegawai.urls')),
    # path('api/master-data/', include('apps.master_data.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
