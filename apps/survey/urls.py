from django.urls import path
from . import views

app_name = 'survey'

urlpatterns = [
    # Jenis Survey URLs
    path('jenis-survey/', views.jenis_survey_list, name='jenis_survey_list'),
    path('jenis-survey/create/', views.jenis_survey_create, name='jenis_survey_create'),
    path('jenis-survey/<int:pk>/edit/', views.jenis_survey_edit, name='jenis_survey_edit'),
    path('jenis-survey/<int:pk>/delete/', views.jenis_survey_delete, name='jenis_survey_delete'),
    
    # Pertanyaan Survey URLs
    path('pertanyaan-survey/', views.pertanyaan_survey_list, name='pertanyaan_survey_list'),
    path('pertanyaan-survey/create/', views.pertanyaan_survey_create, name='pertanyaan_survey_create'),
    path('pertanyaan-survey/<int:pk>/edit/', views.pertanyaan_survey_edit, name='pertanyaan_survey_edit'),
    path('pertanyaan-survey/<int:pk>/delete/', views.pertanyaan_survey_delete, name='pertanyaan_survey_delete'),
    
    # Responden Survey URLs
    path('responden-survey/', views.responden_survey_list, name='responden_survey_list'),
    path('responden-survey/create/', views.responden_survey_create, name='responden_survey_create'),
    path('responden-survey/<int:pk>/edit/', views.responden_survey_edit, name='responden_survey_edit'),
    path('responden-survey/<int:pk>/detail/', views.responden_survey_detail, name='responden_survey_detail'),
    path('responden-survey/<int:pk>/delete/', views.responden_survey_delete, name='responden_survey_delete'),
    
    # Jawaban Survey URLs
    path('jawaban-survey/', views.jawaban_survey_list, name='jawaban_survey_list'),
    path('jawaban-survey/create/', views.jawaban_survey_create, name='jawaban_survey_create'),
    path('jawaban-survey/<int:pk>/edit/', views.jawaban_survey_edit, name='jawaban_survey_edit'),
    path('jawaban-survey/<int:pk>/delete/', views.jawaban_survey_delete, name='jawaban_survey_delete'),
    
    # Periode Survey URLs
    path('periode-survey/', views.periode_survey_list, name='periode_survey_list'),
    path('periode-survey/create/', views.periode_survey_create, name='periode_survey_create'),
    path('periode-survey/<int:pk>/edit/', views.periode_survey_edit, name='periode_survey_edit'),
    path('periode-survey/<int:pk>/delete/', views.periode_survey_delete, name='periode_survey_delete'),
    
    # Survey JPT URLs
    path('survey-jpt/', views.penilaian_list, name='penilaian_list'),
    path('survey-jpt/create/', views.penilaian_create, name='penilaian_create'),
    path('survey-jpt/buat-penilaian/', views.buat_penilaian, name='buat_penilaian'),
    path('survey-jpt/<int:pk>/edit/', views.penilaian_edit, name='penilaian_edit'),
    path('survey-jpt/<int:pk>/detail/', views.penilaian_detail, name='penilaian_detail'),
    path('survey-jpt/<int:pk>/delete/', views.penilaian_delete, name='penilaian_delete'),
    path('survey-jpt/report/', views.penilaian_report, name='penilaian_report'),
    
    # Penilaian Atasan URLs (Employee evaluates supervisor)
    path('penilaian-atasan/', views.penilaian_atasan_form, name='penilaian_atasan_form'),
    path('penilaian-atasan/riwayat/', views.penilaian_atasan_riwayat, name='penilaian_atasan_riwayat'),
    path('penilaian-atasan/<int:pk>/edit/', views.penilaian_atasan_edit, name='penilaian_atasan_edit'),
    path('penilaian-atasan/<int:pk>/detail/', views.penilaian_atasan_detail, name='penilaian_atasan_detail'),
]
