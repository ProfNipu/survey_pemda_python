"""
Django Tables2 Definitions for Permission Management
"""

import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from .models import PermissionFunction, PermissionModule, MenuItem, MenuCategory, PermissionControl, PermissionRule, ApiDocumentation

from apps.common.table_attrs import (
    dt_actions_attrs,
    dt_checkbox_attrs,
    dt_checkbox_attrs_with,
    dt_col_attrs,
    dt_render_badge,
    dt_render_actions,
    dt_render_row_number,
    dt_row_number_attrs,
)

User = get_user_model()


class UserTable(tables.Table):
    """Table for displaying users with sorting, searching, and pagination"""
    
    # Checkbox column for bulk selection
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs_with(
            th_width='3%',
            th_input_extra={
                'onclick': 'if(window.userToggleAllRows){window.userToggleAllRows(this.checked)}',
                'onchange': 'if(window.userToggleAllRows){window.userToggleAllRows(this.checked)}',
            },
        ),
        orderable=False
    )
    
    # Row number column (auto-increment with pagination)
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    # Custom columns - Full Width with Proportional Sizing & Borders
    username = tables.Column(
        verbose_name='Username',
        attrs=dt_col_attrs(width='18%', td_weight='medium', td_color='gray-900')
    )
    
    email = tables.Column(
        verbose_name='Email',
        attrs=dt_col_attrs(width='22%', td_color='gray-500')
    )
    
    name = tables.Column(
        verbose_name='Name',
        attrs=dt_col_attrs(width='30%', td_color='gray-700'),
        orderable=True
    )
    
    group_count = tables.Column(
        verbose_name='Roles',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='7%'),
        orderable=False
    )
    
    is_active = tables.BooleanColumn(
        verbose_name='Status',
        attrs=dt_col_attrs(width='10%')
    )
    
    
    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='9%', th_align='center', td_align='center')
    )
    
    class Meta:
        model = User
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'username', 'email', 'name', 'group_count', 'is_active', 'actions')
        attrs = {
            'id': 'users_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_is_active(self, value):
        """Custom rendering for active status"""
        if value:
            return dt_render_badge(
                'Active',
                bg_class='bg-green-100',
                text_class='text-green-800',
                extra_class='text-xs px-2 py-1 rounded',
                icon_class='fas fa-check-circle',
            )
        return dt_render_badge(
            'Inactive',
            bg_class='bg-red-100',
            text_class='text-red-800',
            extra_class='text-xs px-2 py-1 rounded',
            icon_class='fas fa-times-circle',
        )
    
    def render_is_staff(self, value):
        """Custom rendering for staff status"""
        if value:
            return dt_render_badge(
                'Yes',
                bg_class='bg-blue-100',
                text_class='text-blue-800',
                extra_class='text-xs px-2 py-1 rounded',
                icon_class='fas fa-user-shield',
            )
        return dt_render_badge(
            'No',
            bg_class='bg-gray-100',
            text_class='text-gray-600',
            extra_class='text-xs px-2 py-1 rounded',
        )
    
    def render_group_count(self, record):
        """Display group count as badge"""
        count = record.groups.count()
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-purple-100',
                text_class='text-purple-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )
    
    def render_actions(self, record, table):
        """Render action buttons (permission-aware)"""
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        can_assign_roles = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'pengaturan', 'permission_user', 'edit')
                can_delete = check_permission(user, 'pengaturan', 'permission_user', 'delete')
                # Assign roles is part of editing user access
                can_assign_roles = check_permission(user, 'pengaturan', 'permission_user', 'edit')
        except Exception:
            can_edit = False
            can_delete = False
            can_assign_roles = False

        # Additional safety: never show delete for superuser/self
        if getattr(record, 'is_superuser', False):
            can_delete = False
        if user and getattr(user, 'is_authenticated', False) and getattr(record, 'id', None) == getattr(user, 'id', None):
            can_delete = False

        edit_link = (
            {
                'url': reverse('manajemen_aplikasi:users_edit', args=[record.id]),
                'title': 'Edit User',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        roles_link = (
            {
                'url': reverse('manajemen_aplikasi:users_assign_roles', args=[record.id]),
                'title': 'Assign Roles',
                'a_class': 'text-gray-600 hover:text-gray-800',
                'icon_class': 'fas fa-user-tag',
            }
            if can_assign_roles
            else None
        )
        delete_link = (
            {
                'url': reverse('manajemen_aplikasi:users_delete', args=[record.id]),
                'title': 'Delete User',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, roles_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class MenuCategoryTable(tables.Table):
    """Table for displaying menu categories."""

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False
    )

    code = tables.Column(
        verbose_name='Code',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%')
    )

    name = tables.Column(
        verbose_name='Nama Kategori',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900')
    )

    order = tables.Column(
        verbose_name='Order',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )

    is_active = tables.BooleanColumn(
        verbose_name='Active',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )

    menus_count = tables.Column(
        verbose_name='Jumlah Menu',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='12%', th_align='center', td_align='center')
    )

    class Meta:
        model = MenuCategory
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number','code','name','order','is_active','menus_count','actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_actions(self, record):
        edit_url = reverse('manajemen_aplikasi:menu_category_edit', args=[record.id])
        delete_url = reverse('manajemen_aplikasi:menu_category_delete', args=[record.id])
        count = getattr(record, 'menus_count', 0)
        if count and count > 0:
            # Disable delete when linked menus exist
            return dt_render_actions(
                {
                    'url': edit_url,
                    'title': 'Edit Category',
                    'a_class': 'text-orange-600 hover:text-orange-800',
                    'icon_class': 'fas fa-edit',
                },
                {
                    'html': format_html(
                        '<span class="text-gray-400 cursor-not-allowed" title="Tidak bisa dihapus (dipakai {} menu)">'
                        '<i class="fas fa-trash"></i>'
                        '</span>',
                        count,
                    ),
                },
                container_class='flex gap-2 justify-center',
            )

        return dt_render_actions(
            {
                'url': edit_url,
                'title': 'Edit Category',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            },
            {
                'url': delete_url,
                'title': 'Delete Category',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            },
            container_class='flex gap-2 justify-center',
        )

    def render_menus_count(self, record):
        count = getattr(record, 'menus_count', 0)
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-blue-100',
                text_class='text-blue-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )

class FunctionTable(tables.Table):
    """Table for displaying permission functions with selection and actions"""
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    id = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='5%', td_weight='medium', td_color='gray-700')
    )

    nama_fungsi = tables.Column(
        verbose_name='Nama Fungsi',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900')
    )

    label_fungsi = tables.Column(
        verbose_name='Label',
        attrs=dt_col_attrs(width='20%', td_color='gray-700')
    )

    deskripsi_fungsi = tables.Column(
        verbose_name='Deskripsi',
        attrs=dt_col_attrs(width='28%', td_color='gray-700', td_extra_class='text-gray-600'),
        orderable=False
    )

    rule_count = tables.Column(
        verbose_name='Rules',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )

    class Meta:
        model = PermissionFunction
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id', 'nama_fungsi', 'label_fungsi', 'deskripsi_fungsi', 'rule_count', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_rule_count(self, record):
        count = getattr(record, 'rule_count', 0)
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-purple-100',
                text_class='text-purple-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )

    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'pengaturan', 'permission_function', 'edit')
                can_delete = check_permission(user, 'pengaturan', 'permission_function', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('manajemen_aplikasi:function_edit', args=[record.id]),
                'title': 'Edit Function',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('manajemen_aplikasi:function_delete', args=[record.id]),
                'title': 'Delete Function',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class ApiDocumentationTable(tables.Table):
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False,
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False,
    )

    id = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='5%', td_weight='medium', td_color='gray-700')
    )

    method_type = tables.Column(
        verbose_name='Method',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%')
    )

    url = tables.Column(
        verbose_name='URL',
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False, td_extra_class='break-words')
    )

    description = tables.Column(
        verbose_name='Deskripsi',
        attrs=dt_col_attrs(width='28%', td_color='gray-700', td_extra_class='text-gray-600'),
        orderable=False,
    )

    is_active = tables.BooleanColumn(
        verbose_name='Aktif',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='7%')
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )

    class Meta:
        model = ApiDocumentation
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id', 'method_type', 'url', 'description', 'is_active', 'actions')
        attrs = {
            'id': 'api_docs_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_url(self, value, record):
        url = (getattr(record, 'url', None) or value or '').strip()
        if not url:
            return ''
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" class="text-blue-600 hover:text-blue-800 underline break-words" title="Open/Test endpoint">{}</a>',
            url,
            url,
        )

    def render_actions(self, record):
        edit_url = reverse('manajemen_aplikasi:api_documentation_edit', args=[record.id])
        delete_url = reverse('manajemen_aplikasi:api_documentation_delete', args=[record.id])
        open_url = (getattr(record, 'url', None) or '').strip() or '#'
        return dt_render_actions(
            {
                'url': open_url,
                'title': 'Open/Test Endpoint',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-external-link-alt',
            },
            {
                'url': edit_url,
                'title': 'Edit API',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            },
            {
                'url': delete_url,
                'title': 'Delete API',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            },
            container_class='flex gap-2 justify-center',
        )

class ControlTable(tables.Table):
    """Table for displaying permission controls with selection and actions"""
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    id = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='5%', td_weight='medium', td_color='gray-700')
    )

    nama_kontrol = tables.Column(
        verbose_name='Nama Kontrol',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900')
    )

    label_kontrol = tables.Column(
        verbose_name='Label',
        attrs=dt_col_attrs(width='20%', td_color='gray-700')
    )

    deskripsi_kontrol = tables.Column(
        verbose_name='Deskripsi',
        attrs=dt_col_attrs(width='28%', td_color='gray-700', td_extra_class='text-gray-600'),
        orderable=False
    )

    rule_count = tables.Column(
        verbose_name='Rules',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )

    class Meta:
        model = PermissionControl
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id', 'nama_kontrol', 'label_kontrol', 'deskripsi_kontrol', 'rule_count', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_rule_count(self, record):
        count = getattr(record, 'rule_count', 0)
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-purple-100',
                text_class='text-purple-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )

    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'pengaturan', 'permission_control', 'edit')
                can_delete = check_permission(user, 'pengaturan', 'permission_control', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('manajemen_aplikasi:control_edit', args=[record.id]),
                'title': 'Edit Control',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('manajemen_aplikasi:control_delete', args=[record.id]),
                'title': 'Delete Control',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class RuleTable(tables.Table):
    """Table for displaying permission rules with selection and actions"""
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    id = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='6%', td_weight='medium', td_color='gray-700')
    )

    module = tables.Column(
        accessor='module.label_module',
        verbose_name='Module',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900')
    )

    control = tables.Column(
        accessor='control.label_kontrol',
        verbose_name='Control',
        attrs=dt_col_attrs(td_color='gray-700')
    )

    function = tables.Column(
        accessor='function.label_fungsi',
        verbose_name='Function',
        attrs=dt_col_attrs(td_color='gray-700')
    )

    permission_string = tables.Column(
        verbose_name='Permission String',
        attrs=dt_col_attrs(td_color='gray-700', td_extra_class='text-xs'),
        orderable=False
    )

    is_active = tables.BooleanColumn(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%')
    )

    role_count = tables.Column(
        verbose_name='Roles',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%'),
        orderable=False
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='12%', th_align='center', td_align='center')
    )

    class Meta:
        model = PermissionRule
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection','row_number','id','module','control','function','permission_string','is_active','role_count','actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_is_active(self, value):
        if value:
            return dt_render_badge(
                'Active',
                bg_class='bg-green-100',
                text_class='text-green-800',
                extra_class='text-xs px-2 py-1 rounded',
                icon_class='fas fa-check-circle',
            )
        return dt_render_badge(
            'Inactive',
            bg_class='bg-gray-100',
            text_class='text-gray-600',
            extra_class='text-xs px-2 py-1 rounded',
        )

    def render_role_count(self, record):
        count = getattr(record, 'role_count', 0)
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-purple-100',
                text_class='text-purple-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )

    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'pengaturan', 'permission_rule', 'edit')
                can_delete = check_permission(user, 'pengaturan', 'permission_rule', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        count = getattr(record, 'role_count', 0)

        edit_link = (
            {
                'url': reverse('manajemen_aplikasi:rule_edit', args=[record.id]),
                'title': 'Edit Rule',
                'a_class': 'text-amber-600 hover:text-amber-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )

        delete_link = None
        if can_delete:
            if count and count > 0:
                delete_link = {
                    'html': format_html(
                        '<span class="text-gray-400 cursor-not-allowed" title="Tidak bisa dihapus (dipakai {} role)">'
                        '<i class="fas fa-trash"></i>'
                        '</span>',
                        count,
                    )
                }
            else:
                delete_link = {
                    'url': reverse('manajemen_aplikasi:rule_delete', args=[record.id]),
                    'title': 'Delete Rule',
                    'a_class': 'text-red-600 hover:text-red-800',
                    'icon_class': 'fas fa-trash',
                }

        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )

class RoleTable(tables.Table):
    """Table for displaying roles/groups with sorting, searching, and pagination"""
    
    # Checkbox column for bulk selection
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    # Row number column (auto-increment with pagination)
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    # ID column
    id = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='5%', td_weight='medium', td_color='gray-700')
    )
    
    # Role name column
    name = tables.Column(
        verbose_name='Nama Role',
        attrs=dt_col_attrs(width='30%', td_weight='medium', td_color='gray-900')
    )
    
    # Users count column
    users_count = tables.Column(
        verbose_name='Users',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )
    
    # Permissions count column
    permissions_count = tables.Column(
        verbose_name='Permissions',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )
    
    # Actions column
    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )
    
    class Meta:
        model = Group
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id', 'name', 'users_count', 'permissions_count', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_users_count(self, record):
        """Display users count as badge"""
        count = record.user_set.count()
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-blue-100',
                text_class='text-blue-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
                icon_class='fas fa-users',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )
    
    def render_permissions_count(self, record):
        """Display permissions count as badge"""
        count = record.permissions.count()
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-green-100',
                text_class='text-green-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
                icon_class='fas fa-shield-alt',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )
    
    def render_actions(self, record, table):
        """Render action buttons (permission-aware)"""
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        can_assign_rules = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'pengaturan', 'permission_role', 'edit')
                can_delete = check_permission(user, 'pengaturan', 'permission_role', 'delete')
                can_assign_rules = check_permission(user, 'pengaturan', 'permission_role_rule', 'view')
        except Exception:
            can_edit = False
            can_delete = False
            can_assign_rules = False

        edit_link = (
            {
                'url': reverse('manajemen_aplikasi:roles_edit', args=[record.id]),
                'title': 'Edit Role',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        permissions_link = (
            {
                'url': reverse('manajemen_aplikasi:role_rule_manage', args=[record.id]),
                'title': 'Assign Permissions',
                'a_class': 'text-green-600 hover:text-green-800',
                'icon_class': 'fas fa-shield-alt',
            }
            if can_assign_rules
            else None
        )
        delete_link = (
            {
                'url': reverse('manajemen_aplikasi:roles_delete', args=[record.id]),
                'title': 'Delete Role',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, permissions_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class ModuleTable(tables.Table):
    """Table for displaying modules with rules count (no selection checkbox for dashboard)"""

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    order = tables.Column(
        verbose_name='Order',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='6%', td_weight='medium', td_color='gray-700')
    )

    module = tables.Column(
        empty_values=(),
        verbose_name='Module',
        order_by=('label_module',),
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900')
    )

    icon = tables.Column(
        verbose_name='Icon',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%'),
        orderable=False
    )

    status = tables.Column(
        empty_values=(),
        verbose_name='Status',
        order_by=('is_active',),
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%')
    )

    rule_count = tables.Column(
        verbose_name='Rules',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )

    class Meta:
        model = PermissionModule
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number','order','module','icon','status','rule_count','actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_module(self, record):
        return format_html(
            '<div class="font-semibold text-gray-800">{}</div>'
            '<div class="text-gray-500 text-xs">{}</div>',
            record.label_module,
            record.nama_module
        )

    def render_icon(self, record):
        return format_html('<i class="{}"></i>', record.icon)

    def render_status(self, record):
        if record.is_active:
            return dt_render_badge(
                'Active',
                bg_class='bg-green-100',
                text_class='text-green-700',
                extra_class='px-2 py-1 rounded text-xs font-medium',
            )
        return dt_render_badge(
            'Inactive',
            bg_class='bg-gray-100',
            text_class='text-gray-600',
            extra_class='px-2 py-1 rounded text-xs font-medium',
        )

    def render_rule_count(self, record):
        count = getattr(record, 'rule_count', 0)
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-purple-100',
                text_class='text-purple-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )

    def render_actions(self, record):
        edit_url = reverse('manajemen_aplikasi:module_edit', args=[record.id])
        return dt_render_actions(
            {
                'url': edit_url,
                'title': 'Edit Module',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            },
            container_class='flex gap-2 justify-center',
        )


class ModuleManageTable(tables.Table):
    """Table for modules on the dedicated modules list page (with selection)."""

    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    order = tables.Column(
        verbose_name='Order',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='6%', td_weight='medium', td_color='gray-700')
    )

    module = tables.Column(
        empty_values=(),
        verbose_name='Module',
        order_by=('label_module',),
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900')
    )

    icon = tables.Column(
        verbose_name='Icon',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%'),
        orderable=False
    )

    status = tables.Column(
        empty_values=(),
        verbose_name='Status',
        order_by=('is_active',),
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%')
    )

    rule_count = tables.Column(
        verbose_name='Rules',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )

    class Meta:
        model = PermissionModule
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection','row_number','order','module','icon','status','rule_count','actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_module(self, record):
        return format_html(
            '<div class="font-semibold text-gray-800">{}</div>'
            '<div class="text-gray-500 text-xs">{}</div>',
            record.label_module,
            record.nama_module
        )

    def render_icon(self, record):
        return format_html('<i class="{}"></i>', record.icon)

    def render_status(self, record):
        if record.is_active:
            return dt_render_badge(
                'Active',
                bg_class='bg-green-100',
                text_class='text-green-700',
                extra_class='px-2 py-1 rounded text-xs font-medium',
            )
        return dt_render_badge(
            'Inactive',
            bg_class='bg-gray-100',
            text_class='text-gray-600',
            extra_class='px-2 py-1 rounded text-xs font-medium',
        )

    def render_rule_count(self, record):
        count = getattr(record, 'rule_count', 0)
        if count > 0:
            return dt_render_badge(
                count,
                bg_class='bg-purple-100',
                text_class='text-purple-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        return dt_render_badge(
            0,
            bg_class='bg-gray-100',
            text_class='text-gray-500',
            extra_class='text-xs px-2 py-1 rounded',
        )

    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'pengaturan', 'permission_module', 'edit')
                can_delete = check_permission(user, 'pengaturan', 'permission_module', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('manajemen_aplikasi:module_edit', args=[record.id]),
                'title': 'Edit Module',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('manajemen_aplikasi:module_delete', args=[record.id]),
                'title': 'Delete Module',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class MenuItemTable(tables.Table):
    """Table for displaying MenuItem records."""

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    order = tables.Column(
        verbose_name='Order',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='6%', td_weight='medium', td_color='gray-700')
    )

    name = tables.Column(
        verbose_name='Nama Menu',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900')
    )

    type = tables.Column(
        verbose_name='Type',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%')
    )

    category = tables.Column(
        verbose_name='Category',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )

    parent = tables.Column(
        verbose_name='Parent',
        attrs=dt_col_attrs(td_color='gray-700')
    )

    permission_key = tables.Column(
        verbose_name='Permission Key',
        attrs=dt_col_attrs(td_color='gray-700', td_extra_class='text-xs'),
        orderable=False
    )

    link = tables.Column(
        empty_values=(),
        verbose_name='Link',
        attrs=dt_col_attrs(td_extra_class='text-xs text-blue-700'),
        orderable=False
    )

    is_active = tables.BooleanColumn(
        verbose_name='Active',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center')
    )

    class Meta:
        model = MenuItem
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number','order','name','type','category','parent','permission_key','link','is_active','actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_parent(self, record):
        return record.parent.name if record.parent else '-'

    def render_type(self, value):
        v = str(value or '').lower()
        return 'Submenu' if v == 'menuitem' else 'Module'

    def render_category(self, record):
        try:
            cat = MenuCategory.objects.filter(code=record.category).first()
            if cat:
                url = reverse('manajemen_aplikasi:menu_category_edit', args=[cat.id])
                return format_html('<a href="{}" class="text-blue-600 hover:underline">{}</a>', url, cat.name)
        except Exception:
            pass
        mapping = {1: 'SUPER ADMIN', 2: 'Data Pegawai', 3: 'Laporan Data', 4: 'Manajemen Integrasi', 0: 'Menu Lainnya'}
        return mapping.get(record.category or 0, 'Menu Lainnya')

    def render_link(self, record):
        if record.url_name:
            return dt_render_badge(
                record.url_name,
                bg_class='bg-blue-100',
                text_class='text-blue-800',
                extra_class='px-2 py-1 rounded',
            )
        if record.external_url:
            return format_html('<a href="{}" target="_blank" class="underline">{}</a>', record.external_url, record.external_url)
        return '-'

    def render_is_active(self, value):
        if value:
            return dt_render_badge(
                'Active',
                bg_class='bg-green-100',
                text_class='text-green-700',
                extra_class='px-2 py-1 rounded text-xs font-medium',
            )
        return dt_render_badge(
            'Inactive',
            bg_class='bg-gray-100',
            text_class='text-gray-600',
            extra_class='px-2 py-1 rounded text-xs font-medium',
        )

    def render_actions(self, record):
        edit_url = reverse('manajemen_aplikasi:menu_edit', args=[record.id])
        delete_url = reverse('manajemen_aplikasi:menu_delete', args=[record.id])
        return dt_render_actions(
            {
                'url': edit_url,
                'title': 'Edit Menu',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            },
            {
                'url': delete_url,
                'title': 'Delete Menu',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            },
            container_class='flex gap-2 justify-center',
        )
