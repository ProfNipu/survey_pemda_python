from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Custom User Admin - match Laravel users table
    
    CATATAN: is_staff dan is_superuser TIDAK ADA
    Permission management menggunakan custom system dari apps/permissions
    """
    
    list_display = ('username', 'email', 'name', 'id_pegawai', 'user_id_opd', 'is_active', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('username', 'email', 'name', 'id_pegawai')
    ordering = ('-date_joined',)
    
    # Tidak ada groups dan permissions
    filter_horizontal = ()
    filter_vertical = ()
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('name', 'email')}),
        ('Data', {'fields': ('id_pegawai', 'user_id_opd', 'image')}),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Permission management menggunakan custom role system'
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'email', 'password1', 'password2'),
        }),
        ('Data', {
            'fields': ('id_pegawai', 'user_id_opd', 'image'),
        }),
    )
    
    readonly_fields = ('date_joined', 'updated_at', 'last_login')
