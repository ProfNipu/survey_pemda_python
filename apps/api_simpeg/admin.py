from django.contrib import admin
from .models import PegawaiDataSementara


@admin.register(PegawaiDataSementara)
class PegawaiDataSementaraAdmin(admin.ModelAdmin):
    list_display = ['id', 'nipPegawai', 'id_pegawai', 'id_opd', 'created_at']
    list_filter = ['id_opd', 'created_at']
    search_fields = ['nipPegawai', 'id_pegawai']
    readonly_fields = ['created_at', 'updated_at']
