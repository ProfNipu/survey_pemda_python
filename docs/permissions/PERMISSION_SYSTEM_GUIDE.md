# 🛡️ Granular Permission System - User Guide

## 📋 Overview

Sistem permission granular 5-layer yang terinspirasi dari Laravel ESIMPEG.

### Struktur:
1. **Function** - Actions (view, create, edit, delete, etc.)
2. **Control** - Resources (ms_pegawai, siasn_dashboard, etc.)
3. **Module** - Sidebar Menu (Dashboard, Pegawai, SIASN, etc.)
4. **Rule** - Permission = Module + Control + Function
5. **Role** - Assignment of Rules to Groups

---

## 🚀 Quick Start

### 1. Seed Initial Data
```bash
docker exec esimpeg_python_app python manage.py seed_permissions
```

Creates:
- ✅ 10 Functions (view, create, edit, delete, export, etc.)
- ✅ 16 Controls (ms_pegawai, siasn_dashboard, etc.)
- ✅ 6 Modules (Dashboard, Pegawai, SIASN, etc.)
- ✅ 5 Example Rules

### 2. Manage via Django Admin
```
http://localhost:8005/admin/permissions/
```

You can manage:
- Permission Functions
- Permission Controls  
- Permission Modules
- Permission Rules
- Role Rules

---

## 📚 Usage Examples

### In Views (Decorators)

```python
from apps.permissions.decorators import permission_required

# Simple permission check
@permission_required('pegawai', 'ms_pegawai', 'view')
def pegawai_list(request):
    # Only users with "view ms_pegawai in pegawai module" can access
    return render(request, 'pegawai/list.html')

# Check if user can create
@permission_required('pegawai', 'ms_pegawai', 'create')
def pegawai_create(request):
    # Only users with create permission can access
    return render(request, 'pegawai/create.html')

# Multiple permissions (any)
from apps.permissions.decorators import any_permission_required

@any_permission_required([
    ('pegawai', 'ms_pegawai', 'view'),
    ('pegawai', 'pegawai_siasn', 'view'),
])
def pegawai_dashboard(request):
    # User needs at least ONE of the permissions
    return render(request, 'pegawai/dashboard.html')

# Multiple permissions (all)
from apps.permissions.decorators import all_permissions_required

@all_permissions_required([
    ('pegawai', 'ms_pegawai', 'view'),
    ('pegawai', 'ms_pegawai', 'edit'),
])
def pegawai_edit(request, id):
    # User needs ALL permissions
    return render(request, 'pegawai/edit.html')
```

### In Views (Manual Check)

```python
from apps.permissions.helpers import check_permission, get_user_modules

def my_view(request):
    # Check permission manually
    if check_permission(request.user, 'pegawai', 'ms_pegawai', 'view'):
        # User has permission
        data = Pegawai.objects.all()
    else:
        # No permission
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('dashboard')
    
    # Get user's modules for sidebar
    modules = get_user_modules(request.user)
    
    context = {
        'data': data,
        'modules': modules
    }
    return render(request, 'pegawai/list.html', context)
```

### In Templates

```django
{% load permission_tags %}

{# Check permission #}
{% has_permission 'pegawai' 'ms_pegawai' 'view' as can_view %}
{% if can_view %}
    <a href="{% url 'pegawai_list' %}">Lihat Pegawai</a>
{% endif %}

{# Show button only if user has permission #}
{% has_permission 'pegawai' 'ms_pegawai' 'create' as can_create %}
{% if can_create %}
    <a href="{% url 'pegawai_create' %}" class="btn btn-success">
        <i class="fas fa-plus"></i> Tambah Pegawai
    </a>
{% endif %}

{# Using filter syntax #}
{% if request.user|can:'pegawai.ms_pegawai.edit' %}
    <button class="btn btn-warning">Edit</button>
{% endif %}

{# Show module in sidebar if user has any permission #}
{% can_access_module 'pegawai' as can_access_pegawai %}
{% if can_access_pegawai %}
    <div class="menu-item">
        <a href="{% url 'pegawai_dashboard' %}">
            <i class="fas fa-users"></i> Pegawai
        </a>
    </div>
{% endif %}

{# Get user's modules for sidebar #}
{% user_modules as modules %}
{% for module in modules %}
    <div class="menu-item">
        <a href="#">
            <i class="{{ module.icon }}"></i> {{ module.label_module }}
        </a>
    </div>
{% endfor %}

{# Permission button (auto-hide if no permission) #}
{% permission_button 'pegawai' 'ms_pegawai' 'export' 'Export Excel' '/pegawai/export/' 'btn btn-info' %}

{# Permission link (auto-hide if no permission) #}
{% permission_link 'pegawai' 'ms_pegawai' 'view' 'Detail Pegawai' '/pegawai/1/' 'fas fa-eye' %}
```

---

## 🎯 Common Scenarios

### Scenario 1: Add New Module

```python
# Via Django Admin or Shell
from apps.permissions.models import PermissionModule

PermissionModule.objects.create(
    nama_module='master_data',
    label_module='Master Data',
    deskripsi_module='Manajemen data master',
    icon='fas fa-database',
    order=7,
    is_active=True
)
```

### Scenario 2: Add New Control

```python
from apps.permissions.models import PermissionControl

PermissionControl.objects.create(
    nama_kontrol='jabatan',
    label_kontrol='Master Jabatan',
    deskripsi_kontrol='Data master jabatan'
)
```

### Scenario 3: Create Permission Rule

```python
from apps.permissions.models import (
    PermissionModule,
    PermissionControl,
    PermissionFunction,
    PermissionRule
)

# Get objects
module = PermissionModule.objects.get(nama_module='pegawai')
control = PermissionControl.objects.get(nama_kontrol='ms_pegawai')
function = PermissionFunction.objects.get(nama_fungsi='view')

# Create rule
rule = PermissionRule.objects.create(
    module=module,
    control=control,
    function=function,
    is_active=True
)

print(f"Created rule: {rule.permission_string}")
# Output: pegawai.ms_pegawai.view
```

### Scenario 4: Assign Rules to Role

```python
from django.contrib.auth.models import Group
from apps.permissions.models import PermissionRule, RoleRule

# Get or create role
role, _ = Group.objects.get_or_create(name='Operator Pegawai')

# Get rules
rules = PermissionRule.objects.filter(
    module__nama_module='pegawai',
    function__nama_fungsi__in=['view', 'create']
)

# Assign rules to role
for rule in rules:
    RoleRule.objects.get_or_create(
        role=role,
        rule=rule
    )

print(f"Assigned {rules.count()} rules to {role.name}")
```

### Scenario 5: Assign Role to User

```python
from django.contrib.auth.models import User, Group

# Get user and role
user = User.objects.get(username='prakom')
role = Group.objects.get(name='Operator Pegawai')

# Assign role
user.groups.add(role)

print(f"Assigned role '{role.name}' to user '{user.username}'")
```

---

## 🔍 Helper Functions

### check_permission(user, module, control, function)
Check if user has specific permission.

```python
from apps.permissions.helpers import check_permission

if check_permission(request.user, 'pegawai', 'ms_pegawai', 'view'):
    # Has permission
    pass
```

### get_user_modules(user)
Get modules user has access to (for sidebar).

```python
from apps.permissions.helpers import get_user_modules

modules = get_user_modules(request.user)
for module in modules:
    print(f"{module.label_module} - {module.icon}")
```

### get_user_controls(user, module_name)
Get controls user has access to in a module.

```python
from apps.permissions.helpers import get_user_controls

controls = get_user_controls(request.user, 'pegawai')
for control in controls:
    print(control.label_kontrol)
```

### get_user_functions(user, module_name, control_name)
Get functions user can perform on a control.

```python
from apps.permissions.helpers import get_user_functions

functions = get_user_functions(request.user, 'pegawai', 'ms_pegawai')
for func in functions:
    print(func.label_fungsi)
```

### has_any_permission(user, module_name)
Check if user has any permission in a module.

```python
from apps.permissions.helpers import has_any_permission

if has_any_permission(request.user, 'pegawai'):
    # Show Pegawai menu in sidebar
    pass
```

---

## 📊 Database Structure

```
permission_functions
├─ id
├─ nama_fungsi (unique)      # view, create, edit, delete
├─ label_fungsi              # Lihat, Tambah, Edit, Hapus
└─ deskripsi_fungsi

permission_controls
├─ id
├─ nama_kontrol (unique)     # ms_pegawai, siasn_dashboard
├─ label_kontrol             # Master Pegawai, SIASN Dashboard
└─ deskripsi_kontrol

permission_modules
├─ id
├─ nama_module (unique)      # pegawai, siasn
├─ label_module              # Data Pegawai, SIASN Integration
├─ deskripsi_module
├─ icon                      # fas fa-users, fas fa-sync
├─ order                     # Sidebar order
└─ is_active

permission_rules
├─ id
├─ module_id (FK)
├─ control_id (FK)
├─ function_id (FK)
└─ is_active
    unique: (module, control, function)

role_rules
├─ id
├─ role_id (FK to auth_group)
└─ rule_id (FK to permission_rules)
    unique: (role, rule)
```

---

## ✅ Benefits

1. ✅ **Granular Control** - Fine-grained permission management
2. ✅ **Scalable** - Easy to add new modules/controls/functions
3. ✅ **Organized** - Clear structure (Module → Control → Function)
4. ✅ **Reusable** - Functions can be used across controls
5. ✅ **Sidebar Auto-generate** - Modules determine sidebar menu
6. ✅ **Consistent** - Same structure as Laravel ESIMPEG
7. ✅ **Easy Management** - Django Admin interface
8. ✅ **Template Tags** - Easy to use in templates

---

## 🎨 Example: Complete Flow

### 1. Create Module
```python
PermissionModule.objects.create(
    nama_module='laporan',
    label_module='Laporan',
    icon='fas fa-chart-bar',
    order=5
)
```

### 2. Create Controls
```python
PermissionControl.objects.create(
    nama_kontrol='laporan_pegawai',
    label_kontrol='Laporan Pegawai'
)
```

### 3. Create Rules
```python
# Get objects
module = PermissionModule.objects.get(nama_module='laporan')
control = PermissionControl.objects.get(nama_kontrol='laporan_pegawai')
view = PermissionFunction.objects.get(nama_fungsi='view')
export = PermissionFunction.objects.get(nama_fungsi='export')

# Create rules
PermissionRule.objects.create(module=module, control=control, function=view)
PermissionRule.objects.create(module=module, control=control, function=export)
```

### 4. Assign to Role
```python
role = Group.objects.get(name='Manager')
rules = PermissionRule.objects.filter(
    module__nama_module='laporan',
    control__nama_kontrol='laporan_pegawai'
)

for rule in rules:
    RoleRule.objects.create(role=role, rule=rule)
```

### 5. Use in View
```python
from apps.permissions.decorators import permission_required

@permission_required('laporan', 'laporan_pegawai', 'view')
def laporan_pegawai(request):
    return render(request, 'laporan/pegawai.html')

@permission_required('laporan', 'laporan_pegawai', 'export')
def laporan_export(request):
    # Export logic
    return FileResponse(...)
```

### 6. Use in Template
```django
{% load permission_tags %}

{% has_permission 'laporan' 'laporan_pegawai' 'view' as can_view %}
{% if can_view %}
    <h1>Laporan Pegawai</h1>
    
    {% has_permission 'laporan' 'laporan_pegawai' 'export' as can_export %}
    {% if can_export %}
        <a href="{% url 'laporan_export' %}" class="btn btn-success">
            <i class="fas fa-file-excel"></i> Export Excel
        </a>
    {% endif %}
{% endif %}
```

---

## 🎉 Summary

✅ **5-Layer System** implemented  
✅ **10 Functions** seeded  
✅ **16 Controls** seeded  
✅ **6 Modules** seeded  
✅ **Helper functions** ready  
✅ **Decorators** ready  
✅ **Template tags** ready  
✅ **Django Admin** registered  

**System ready to use!** 🚀
