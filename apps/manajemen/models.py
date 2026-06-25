"""
Permission Models - Granular 5-Layer System
Inspired by Laravel permission structure
"""

from django.db import models
from django.contrib.auth.models import Group


class PermissionFunction(models.Model):
    """
    Manajemen Fungsi - Functions/Actions
    Examples: view, create, edit, delete, export, import, approve
    """
    nama_fungsi = models.CharField(max_length=100, unique=True)
    label_fungsi = models.CharField(max_length=100)
    deskripsi_fungsi = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permission_functions'
        verbose_name = 'Permission Function'
        verbose_name_plural = 'Permission Functions'
        ordering = ['nama_fungsi']
    
    def __str__(self):
        return f"{self.label_fungsi} ({self.nama_fungsi})"


class PermissionControl(models.Model):
    """
    Manajemen Kontrol - Controls/Resources
    Examples: ms_pegawai, pegawai_siasn, siasn_cache, riwayat_jabatan
    """
    nama_kontrol = models.CharField(max_length=100, unique=True)
    label_kontrol = models.CharField(max_length=100)
    deskripsi_kontrol = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permission_controls'
        verbose_name = 'Permission Control'
        verbose_name_plural = 'Permission Controls'
        ordering = ['nama_kontrol']
    
    def __str__(self):
        return f"{self.label_kontrol} ({self.nama_kontrol})"


class PermissionModule(models.Model):
    """
    Manajemen Module - Modules/Sidebar Menu
    Examples: Dashboard, Pegawai, SIASN, Riwayat, Laporan
    """
    nama_module = models.CharField(max_length=100, unique=True)
    label_module = models.CharField(max_length=100)
    deskripsi_module = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='fas fa-folder', help_text='FontAwesome icon class')
    order = models.IntegerField(default=0, help_text='Order in sidebar')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permission_modules'
        verbose_name = 'Permission Module'
        verbose_name_plural = 'Permission Modules'
        ordering = ['order', 'nama_module']
    
    def __str__(self):
        return f"{self.label_module} ({self.nama_module})"


class PermissionRule(models.Model):
    """
    Manajemen Rules - Permission Rules
    Rule = Module + Control + Function
    Example: Module "Pegawai" + Control "ms_pegawai" + Function "view"
    """
    module = models.ForeignKey(PermissionModule, on_delete=models.CASCADE, related_name='rules')
    control = models.ForeignKey(PermissionControl, on_delete=models.CASCADE, related_name='rules')
    function = models.ForeignKey(PermissionFunction, on_delete=models.CASCADE, related_name='rules')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permission_rules'
        verbose_name = 'Permission Rule'
        verbose_name_plural = 'Permission Rules'
        unique_together = ['module', 'control', 'function']
        ordering = ['module__order', 'control__nama_kontrol', 'function__nama_fungsi']
    
    def __str__(self):
        return f"{self.module.label_module} → {self.control.label_kontrol} → {self.function.label_fungsi}"
    
    @property
    def permission_string(self):
        """Generate permission string for checking"""
        return f"{self.module.nama_module}.{self.control.nama_kontrol}.{self.function.nama_fungsi}"


class RoleRule(models.Model):
    """
    Manajemen Roles - Role to Rules assignment
    Links Django Groups (Roles) to Permission Rules
    """
    role = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='permission_rules')
    rule = models.ForeignKey(PermissionRule, on_delete=models.CASCADE, related_name='role_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'role_rules'
        verbose_name = 'Role Rule'
        verbose_name_plural = 'Role Rules'
        unique_together = ['role', 'rule']
        ordering = ['role__name', 'rule__module__order']
    
    def __str__(self):
        return f"{self.role.name} → {self.rule}"


class UserTableSelection(models.Model):
    """
    Store user table selections (checkboxes) per page
    Reusable for any table page in the system
    """
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='table_selections')
    page_key = models.CharField(max_length=100, help_text='Unique identifier for the page/table (e.g., user_list, role_list)')
    selected_ids = models.JSONField(default=list, help_text='List of selected item IDs')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_table_selections'
        verbose_name = 'User Table Selection'
        verbose_name_plural = 'User Table Selections'
        unique_together = ['user', 'page_key']
        indexes = [
            models.Index(fields=['user', 'page_key']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.page_key} ({len(self.selected_ids)} items)"


class MenuCategory(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_categories'
        ordering = ['order', 'name']
        verbose_name = 'Menu Category'
        verbose_name_plural = 'Menu Categories'
    
    def __str__(self):
        return self.name


class ApiDocumentation(models.Model):
    method_type = models.CharField(max_length=191)
    url = models.CharField(max_length=191)
    parameters = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_documentation'
        verbose_name = 'API Documentation'
        verbose_name_plural = 'API Documentation'
        ordering = ['-id']
        unique_together = ['method_type', 'url']
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['method_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.method_type} {self.url}"


class ComboBoxConfig(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'combo_box_configs'
        verbose_name = 'Combo Box Config'
        verbose_name_plural = 'Combo Box Configs'
        ordering = ['code']

    def __str__(self):
        return f"{self.label} ({self.code})"


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    permission_key = models.CharField(max_length=150, blank=True, null=True)
    url_name = models.CharField(max_length=150, blank=True, null=True)
    external_url = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')
    type = models.CharField(max_length=20, default='module')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)
    category = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['category', 'parent_id', 'order', 'name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
    
    def __str__(self):
        return self.name
