from django.urls import path
from django.views.generic import RedirectView
from . import views, views_granular
from apps.manajemen import roles as views_roles
from apps.manajemen import users as views_users
from apps.manajemen import rules as views_rules
from apps.manajemen import functions as views_functions
from apps.manajemen import controls as views_controls
from apps.manajemen import modules as views_modules
from apps.manajemen import role_rules as views_role_rules
from apps.manajemen import menu_categories as views_menu_categories
from apps.manajemen import menu as views_menu
from apps.manajemen import api_documentation as views_api_documentation

app_name = 'manajemen_aplikasi'

urlpatterns = [
    # Main Dashboard - Granular System
    path('', RedirectView.as_view(pattern_name='manajemen_aplikasi:dashboard', permanent=False)),
    # Canonical route
    path('akses-granular/', views_granular.granular_dashboard, name='dashboard'),
    # Backward compatibility
    path('permissions-roles/', RedirectView.as_view(pattern_name='manajemen_aplikasi:dashboard', permanent=False)),
    
    # OLD Permission Management (Django built-in)
    path('old/manajemen_aplikasi/', views.permission_list, name='permission_list'),
    path('old/manajemen_aplikasi/create/', views.permission_create, name='permission_create'),
    path('old/manajemen_aplikasi/<int:perm_id>/edit/', views.permission_edit, name='permission_edit'),
    path('old/manajemen_aplikasi/<int:perm_id>/delete/', views.permission_delete, name='permission_delete'),
    
    path('old/roles/', views.role_list, name='role_list'),
    path('old/roles/create/', views.role_create, name='role_create'),
    path('old/roles/<int:role_id>/edit/', views.role_edit, name='role_edit'),
    path('old/roles/<int:role_id>/delete/', views.role_delete, name='role_delete'),
    
    path('old/users/<int:user_id>/manajemen_aplikasi/', views.user_permissions, name='user_permissions'),
    
    # ===== GRANULAR PERMISSION MANAGEMENT =====
    
    # Functions Management (NEW!) - routed to manajemen_aplikasi.functions module
    path('functions/', views_functions.function_list, name='function_list'),
    path('functions/create/', views_functions.function_create, name='function_create'),
    path('functions/<int:func_id>/edit/', views_functions.function_edit, name='function_edit'),
    path('functions/<int:func_id>/delete/', views_functions.function_delete, name='function_delete'),
    
    # Controls Management (NEW!) - routed to manajemen_aplikasi.controls module
    path('controls/', views_controls.control_list, name='control_list'),
    path('controls/create/', views_controls.control_create, name='control_create'),
    path('controls/<int:ctrl_id>/edit/', views_controls.control_edit, name='control_edit'),
    path('controls/<int:ctrl_id>/delete/', views_controls.control_delete, name='control_delete'),
    
    # Modules Management (NEW!) - routed to manajemen_aplikasi.modules module
    path('modules/', views_modules.module_list, name='module_list'),
    path('modules/create/', views_modules.module_create, name='module_create'),
    path('modules/<int:mod_id>/edit/', views_modules.module_edit, name='module_edit'),
    path('modules/<int:mod_id>/delete/', views_modules.module_delete, name='module_delete'),

    # Menu Items Management (Custom UI) - routed to manajemen_aplikasi.menu module
    path('menu/', views_menu.menu_list, name='menu_list'),
    path('menu/create/', views_menu.menu_create, name='menu_create'),
    path('menu/<int:menu_id>/edit/', views_menu.menu_edit, name='menu_edit'),
    path('menu/<int:menu_id>/delete/', views_menu.menu_delete, name='menu_delete'),
    # Menu Categories Management (NEW!) - routed to manajemen_aplikasi.menu_categories module
    path('menu/categories/', views_menu_categories.menu_category_list, name='menu_category_list'),
    path('menu/categories/create/', views_menu_categories.menu_category_create, name='menu_category_create'),
    path('menu/categories/<int:cat_id>/edit/', views_menu_categories.menu_category_edit, name='menu_category_edit'),
    path('menu/categories/<int:cat_id>/delete/', views_menu_categories.menu_category_delete, name='menu_category_delete'),

    # API Documentation (read-only) - sourced from laravel DB (api_documentation table)
    path('api-documentation/', views_api_documentation.api_documentation_list, name='api_documentation_list'),
    path('ajax-documentation/', views_api_documentation.ajax_documentation_list, name='ajax_documentation_list'),
    path('api-documentation/<int:doc_id>/', views_api_documentation.api_documentation_detail, name='api_documentation_detail'),
    path('api-documentation/create/', views_api_documentation.api_documentation_create, name='api_documentation_create'),
    path('api-documentation/tester/', views_api_documentation.api_documentation_tester, name='api_documentation_tester'),
    path('api-documentation/seed/siasn/', views_api_documentation.api_documentation_seed_siasn_endpoints, name='api_documentation_seed_siasn_endpoints'),
    path('api-documentation/seed/internal-ajax/', views_api_documentation.api_documentation_seed_internal_ajax_endpoints, name='api_documentation_seed_internal_ajax_endpoints'),
    path('api-documentation/<int:doc_id>/edit/', views_api_documentation.api_documentation_edit, name='api_documentation_edit'),
    path('api-documentation/<int:doc_id>/delete/', views_api_documentation.api_documentation_delete, name='api_documentation_delete'),
    
    # Rules Management (NEW!) - routed to manajemen_aplikasi.rules module
    path('rules/', views_rules.rule_list, name='rule_list'),
    path('rules/create/', views_rules.rule_create, name='rule_create'),
    path('rules/<int:rule_id>/edit/', views_rules.rule_edit, name='rule_edit'),
    path('rules/<int:rule_id>/delete/', views_rules.rule_delete, name='rule_delete'),
    # Rules AJAX search endpoints
    path('rules/ajax/controls/', views_rules.ajax_controls_search, name='rules_controls_search'),
    path('rules/ajax/functions/', views_rules.ajax_functions_search, name='rules_functions_search'),
    
    # Role-Rule Assignment (NEW!) - routed to manajemen_aplikasi.role_rules module
    path('roles/<int:role_id>/rules/', views_role_rules.role_rule_manage, name='role_rule_manage'),
    
    # Role Management (NEW!) - routed to manajemen_aplikasi.roles module
    path('roles/', views_roles.role_list, name='roles_list'),
    path('roles/create/', views_roles.role_create, name='roles_create'),
    path('roles/<int:role_id>/edit/', views_roles.role_edit, name='roles_edit'),
    path('roles/<int:role_id>/delete/', views_roles.role_delete, name='roles_delete'),
    
    # User Management (NEW!) - routed to manajemen_aplikasi.users module
    path('users/', views_users.user_list, name='users_list'),
    path('users/create/', views_users.users_create, name='users_create'),
    path('users/<int:user_id>/edit/', views_users.users_edit, name='users_edit'),
    path('users/<int:user_id>/delete/', views_users.users_delete, name='users_delete'),
    path('users/<int:user_id>/roles/', views_users.users_assign_roles, name='users_assign_roles'),
    
    # User Profile & Password (migrated to accounts). Keep redirect for backward compatibility
]
