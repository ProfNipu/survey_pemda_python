from django.urls import path
from . import views

app_name = 'api_simpeg'

urlpatterns = [
    path('pegawai/', views.pegawai_list, name='pegawai_list'),
    path('pegawai/sync/', views.pegawai_sync, name='pegawai_sync'),
    path('pegawai/sync/progress/<str:sync_id>/', views.pegawai_sync_progress, name='pegawai_sync_progress'),
]
