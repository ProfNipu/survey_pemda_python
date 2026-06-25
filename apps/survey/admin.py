from django.contrib import admin
from .models import (
    JenisSurvey, PertanyaanSurvey, RespondenSurvey, JawabanSurvey,
    PeriodeSurvey, PegawaiRiwayatData
)


@admin.register(JenisSurvey)
class JenisSurveyAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['kode', 'nama']


@admin.register(PertanyaanSurvey)
class PertanyaanSurveyAdmin(admin.ModelAdmin):
    list_display = ['jenis_survey', 'kode_pertanyaan', 'pertanyaan', 'urutan', 'bobot', 'is_active']
    list_filter = ['jenis_survey', 'is_active']
    search_fields = ['kode_pertanyaan', 'pertanyaan']
    ordering = ['jenis_survey', 'urutan']


@admin.register(RespondenSurvey)
class RespondenSurveyAdmin(admin.ModelAdmin):
    list_display = ['nip_pegawaiPenilai', 'nip_pegawaiDinilai', 'peranPenilai', 'statusData', 'created_at']
    list_filter = ['statusData', 'peranPenilai']
    search_fields = ['nip_pegawaiPenilai', 'nip_pegawaiDinilai']


@admin.register(JawabanSurvey)
class JawabanSurveyAdmin(admin.ModelAdmin):
    list_display = ['responden', 'pertanyaan', 'nilai', 'nilai_terbobot', 'created_at']
    list_filter = ['pertanyaan__jenis_survey']
    search_fields = ['responden__nip_pegawaiPenilai', 'responden__nip_pegawaiDinilai']


@admin.register(PeriodeSurvey)
class PeriodeSurveyAdmin(admin.ModelAdmin):
    list_display = ['jenis_survey', 'nama_periode', 'tanggal_mulai', 'tanggal_selesai', 'status_display', 'is_active']
    list_filter = ['jenis_survey', 'is_active']
    search_fields = ['nama_periode', 'jenis_survey__nama']
    ordering = ['-tanggal_mulai']


@admin.register(PegawaiRiwayatData)
class PegawaiRiwayatDataAdmin(admin.ModelAdmin):
    list_display = ['nip_baru', 'nama_pegawai', 'nama_jabatan', 'nm_opd', 'periode_survey', 'snapshot_at']
    list_filter = ['periode_survey', 'jenis_survey', 'kategori_pegawai', 'kode_eselon']
    search_fields = ['nip_baru', 'nip_lama', 'nama_pegawai', 'nm_opd']
    readonly_fields = ['snapshot_at', 'snapshot_by', 'raw_data']
    ordering = ['-snapshot_at']
    
    fieldsets = (
        ('Informasi Survey', {
            'fields': ('periode_survey', 'jenis_survey', 'snapshot_at', 'snapshot_by')
        }),
        ('Data Pegawai', {
            'fields': ('id_pegawai', 'nip_baru', 'nip_lama', 'nama_pegawai', 'tempat_lahir', 'tanggal_lahir', 'jenis_kelamin', 'alamat_rumah', 'no_hp')
        }),
        ('Data Jabatan', {
            'fields': ('id_jabatan', 'nama_jabatan', 'masa_kerja_jabatan', 'kode_eselon', 'nama_eselon')
        }),
        ('Data OPD', {
            'fields': ('id_opd', 'nm_opd', 'id_opd_urut', 'is_opd_induk', 'id_sub_opd', 'nm_sub_opd')
        }),
        ('Data Kepegawaian', {
            'fields': ('id_golongan', 'nama_golongan', 'nama_pangkat', 'kategori_pegawai', 'nama_kategori_pegawai', 'tmt_cpns', 'masa_kerja_tahun', 'masa_kerja_bulan', 'akhir_kerja_p3k')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
    )
