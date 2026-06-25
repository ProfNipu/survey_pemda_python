"""
Permission Admin Interface
For managing permissions through Django Admin
"""

from django.contrib import admin
from .models import (
    PermissionFunction,
    PermissionControl,
    PermissionModule,
    PermissionRule,
    RoleRule,
    MenuItem,
)


@admin.register(PermissionFunction)
class PermissionFunctionAdmin(admin.ModelAdmin):
    list_display = ['nama_fungsi', 'label_fungsi', 'deskripsi_fungsi', 'created_at']
    search_fields = ['nama_fungsi', 'label_fungsi']
    list_filter = ['created_at']
    ordering = ['nama_fungsi']
    
    fieldsets = (
        ('Informasi Fungsi', {
            'fields': ('nama_fungsi', 'label_fungsi', 'deskripsi_fungsi')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PermissionControl)
class PermissionControlAdmin(admin.ModelAdmin):
    list_display = ['nama_kontrol', 'label_kontrol', 'deskripsi_kontrol', 'created_at']
    search_fields = ['nama_kontrol', 'label_kontrol']
    list_filter = ['created_at']
    ordering = ['nama_kontrol']
    
    fieldsets = (
        ('Informasi Kontrol', {
            'fields': ('nama_kontrol', 'label_kontrol', 'deskripsi_kontrol')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PermissionModule)
class PermissionModuleAdmin(admin.ModelAdmin):
    list_display = ['order', 'nama_module', 'label_module', 'icon', 'is_active', 'created_at']
    list_display_links = ['nama_module', 'label_module']  # Fix: Set clickable links
    search_fields = ['nama_module', 'label_module']
    list_filter = ['is_active', 'created_at']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'nama_module']
    
    fieldsets = (
        ('Informasi Module', {
            'fields': ('nama_module', 'label_module', 'deskripsi_module')
        }),
        ('Tampilan', {
            'fields': ('icon', 'order', 'is_active')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PermissionRule)
class PermissionRuleAdmin(admin.ModelAdmin):
    list_display = ['module', 'control', 'function', 'permission_string', 'is_active', 'created_at']
    search_fields = ['module__nama_module', 'control__nama_kontrol', 'function__nama_fungsi']
    list_filter = ['is_active', 'module', 'created_at']
    list_editable = ['is_active']
    ordering = ['module__order', 'control__nama_kontrol', 'function__nama_fungsi']
    
    fieldsets = (
        ('Permission Rule', {
            'fields': ('module', 'control', 'function', 'is_active')
        }),
        ('Info', {
            'fields': ('permission_string',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['permission_string', 'created_at', 'updated_at']
    
    def permission_string(self, obj):
        return obj.permission_string
    permission_string.short_description = 'Permission String'


@admin.register(RoleRule)
class RoleRuleAdmin(admin.ModelAdmin):
    list_display = ['role', 'rule', 'created_at']
    search_fields = ['role__name', 'rule__module__nama_module', 'rule__control__nama_kontrol']
    list_filter = ['role', 'rule__module', 'created_at']
    ordering = ['role__name', 'rule__module__order']
    
    fieldsets = (
        ('Role Assignment', {
            'fields': ('role', 'rule')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rule":
            kwargs["queryset"] = PermissionRule.objects.select_related(
                'module', 'control', 'function'
            ).order_by('module__order', 'control__nama_kontrol', 'function__nama_fungsi')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

try:
    admin.site.unregister(MenuItem)
except admin.sites.NotRegistered:
    pass
