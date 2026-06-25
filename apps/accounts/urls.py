"""
URLs untuk accounts app
"""
from django.urls import path
from . import views, webhooks

app_name = 'accounts'

urlpatterns = [
    # Login removed - menggunakan landing page (root URL /)
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('force-change-password/', views.force_change_password_view, name='force_change_password'),
    
    # Webhook for password sync from ESIMPEG
    path('webhooks/password-changed/', webhooks.handle_password_changed, name='webhook_password_changed'),
]
