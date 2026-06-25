# 🎯 CARA MENAMBAH PERMISSION BARU

## Step-by-Step Guide

### STEP 1: Tambah Permission di Model

Edit file: `apps/integrations/models.py`

```python
class SiasnPermission(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            # Existing permissions...
            ('manage_siasn_token', 'Can manage SIASN token (refresh)'),
            
            # ===== TAMBAH PERMISSION BARU DI SINI =====
            ('export_siasn_data', 'Can export SIASN data to Excel/CSV'),
            ('view_siasn_reports', 'Can view SIASN reports'),
            ('manage_siasn_config', 'Can manage SIASN configuration'),
        ]
```

**Format:**
```python
('codename', 'Human readable name')
```

**Naming Convention:**
- Gunakan `snake_case`
- Prefix: `view_`, `add_`, `edit_`, `delete_`, `manage_`, `export_`, dll
- Suffix: `_siasn_xxx` untuk SIASN related

---

### STEP 2: Create Migration

```bash
docker exec esimpeg_python_app python manage.py makemigrations integrations
```

Output:
```
Migrations for 'integrations':
  apps/integrations/migrations/0009_alter_siasnpermission_options.py
    ~ Change Meta options on siasnpermission
```

---

### STEP 3: Apply Migration

```bash
docker exec esimpeg_python_app python manage.py migrate integrations
```

Output:
```
Operations to perform:
  Apply all migrations: integrations
Running migrations:
  Applying integrations.0009_alter_siasnpermission_options... OK
```

**✅ Permission sudah dibuat!** Sekarang ada di database.

---

### STEP 4: Assign ke Role

#### Cara A: Via Django Admin (GUI) - **MUDAH** ⭐

1. Buka: http://localhost:8005/admin/auth/group/

2. Pilih role (contoh: "SIASN Admin")

3. Di bagian "Permissions":
   ```
   Available permissions    →    Chosen permissions
   ┌──────────────────────┐    ┌──────────────────────┐
   │ export_siasn_data   →│    │ (existing perms)     │
   │ view_siasn_reports  →│    │                      │
   │ manage_siasn_config →│    │                      │
   └──────────────────────┘    └──────────────────────┘
   ```

4. Pilih permission baru & pindahkan ke kanan

5. Klik "Save"

#### Cara B: Via Django Shell

```bash
docker exec -it esimpeg_python_app python manage.py shell
```

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.integrations.models import SiasnPermission

# Get content type
ct = ContentType.objects.get_for_model(SiasnPermission)

# Get new permissions
new_perms = Permission.objects.filter(
    content_type=ct,
    codename__in=['export_siasn_data', 'view_siasn_reports', 'manage_siasn_config']
)

# Assign to Admin role
admin_role = Group.objects.get(name='SIASN Admin')
admin_role.permissions.add(*new_perms)

# Check
print(f"SIASN Admin now has {admin_role.permissions.count()} permissions")

exit()
```

#### Cara C: Update setup_siasn_roles.py (Optional)

Edit: `apps/integrations/management/commands/setup_siasn_roles.py`

```python
# In the admin section
admin_perms = [
    # Existing...
    'manage_siasn_token',
    # Add new ones
    'export_siasn_data',
    'view_siasn_reports',
    'manage_siasn_config',
]
```

Lalu re-run:
```bash
docker exec esimpeg_python_app python manage.py setup_siasn_roles
```

---

### STEP 5: Gunakan di Code

#### A. Check Permission di View

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

# Using decorator
@login_required
@permission_required('integrations.export_siasn_data', raise_exception=True)
def export_data_view(request):
    """Only users with export permission can access"""
    # Your export logic here
    return JsonResponse({'success': True})

# Manual check
@login_required
def export_view(request):
    if not request.user.has_perm('integrations.export_siasn_data'):
        return JsonResponse({'error': 'No permission'}, status=403)
    
    # Your logic
    pass
```

#### B. Check di Template

```html
<!-- Show button only if user has permission -->
{% if perms.integrations.export_siasn_data %}
    <a href="/export/" class="btn btn-success">
        <i class="ik ik-download"></i> Export Data
    </a>
{% endif %}

{% if perms.integrations.view_siasn_reports %}
    <a href="/reports/" class="btn btn-primary">
        View Reports
    </a>
{% endif %}
```

#### C. Check di Python Code

```python
from django.contrib.auth.models import User

user = User.objects.get(username='admin')

# Check single permission
if user.has_perm('integrations.export_siasn_data'):
    print('User can export data')

# Check multiple permissions
required_perms = [
    'integrations.export_siasn_data',
    'integrations.view_siasn_reports'
]

if user.has_perms(required_perms):
    print('User has all required permissions')
```

---

## Contoh Lengkap: Menambah Export Permission

### 1. Tambah di Model

```python
# apps/integrations/models.py

permissions = [
    # ... existing ...
    
    # Export permissions
    ('export_siasn_excel', 'Can export SIASN data to Excel'),
    ('export_siasn_pdf', 'Can export SIASN data to PDF'),
    ('export_siasn_csv', 'Can export SIASN data to CSV'),
]
```

### 2. Migrate

```bash
docker exec esimpeg_python_app python manage.py makemigrations integrations
docker exec esimpeg_python_app python manage.py migrate integrations
```

### 3. Assign ke Role

```python
# Via shell
from django.contrib.auth.models import Group, Permission

operator = Group.objects.get(name='SIASN Operator')
admin = Group.objects.get(name='SIASN Admin')

# Get export permissions
export_perms = Permission.objects.filter(
    codename__startswith='export_siasn_'
)

# Assign
operator.permissions.add(*export_perms)
admin.permissions.add(*export_perms)
```

### 4. Buat View

```python
# apps/integrations/views.py

from django.contrib.auth.decorators import permission_required
import pandas as pd
from django.http import HttpResponse

@permission_required('integrations.export_siasn_excel')
def export_to_excel(request):
    """Export SIASN data to Excel"""
    from .siasn.models_cache import SiasnPegawai
    
    # Get data
    data = SiasnPegawai.objects.all()
    
    # Create DataFrame
    df = pd.DataFrame(list(data.values()))
    
    # Export to Excel
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="siasn_data.xlsx"'
    df.to_excel(response, index=False)
    
    return response

@permission_required('integrations.export_siasn_csv')
def export_to_csv(request):
    """Export SIASN data to CSV"""
    # Similar logic
    pass
```

### 5. Add URL

```python
# apps/integrations/urls.py

urlpatterns = [
    # ... existing ...
    path('export/excel/', views.export_to_excel, name='export_excel'),
    path('export/csv/', views.export_to_csv, name='export_csv'),
]
```

### 6. Add Button di Template

```html
<!-- In your template -->
<div class="export-buttons">
    {% if perms.integrations.export_siasn_excel %}
        <a href="{% url 'integrations:export_excel' %}" class="btn btn-success">
            <i class="ik ik-file"></i> Export to Excel
        </a>
    {% endif %}
    
    {% if perms.integrations.export_siasn_csv %}
        <a href="{% url 'integrations:export_csv' %}" class="btn btn-info">
            <i class="ik ik-download"></i> Export to CSV
        </a>
    {% endif %}
    
    {% if not perms.integrations.export_siasn_excel and not perms.integrations.export_siasn_csv %}
        <p class="text-muted">You don't have permission to export data</p>
    {% endif %}
</div>
```

---

## Verify Permission Created

```bash
# Check all SIASN permissions
docker exec esimpeg_python_app python manage.py shell -c "
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.integrations.models import SiasnPermission

ct = ContentType.objects.get_for_model(SiasnPermission)
perms = Permission.objects.filter(content_type=ct)

print(f'Total: {perms.count()} permissions')
for p in perms.order_by('codename'):
    print(f'  • {p.codename}')
"
```

---

## Best Practices

### 1. Naming Convention

```python
# Good ✅
('view_siasn_dashboard', 'Can view SIASN dashboard')
('export_siasn_excel', 'Can export SIASN data to Excel')
('manage_siasn_config', 'Can manage SIASN configuration')

# Bad ❌
('dashboard', 'Dashboard')
('export', 'Export')
('config', 'Config')
```

### 2. Grouping

Kelompokkan permissions berdasarkan function:

```python
permissions = [
    # View permissions
    ('view_xxx', '...'),
    ('view_yyy', '...'),
    
    # Edit permissions
    ('edit_xxx', '...'),
    ('edit_yyy', '...'),
    
    # Export permissions
    ('export_xxx', '...'),
    ('export_yyy', '...'),
]
```

### 3. Documentation

Tambahkan komentar untuk permission yang kompleks:

```python
permissions = [
    # Allows user to export sensitive data including salary info
    # Should only be assigned to HR managers
    ('export_salary_data', 'Can export salary information'),
]
```

### 4. Testing

Test permission di unit test:

```python
def test_export_permission(self):
    user = User.objects.get(username='operator')
    
    # Check user has permission
    self.assertTrue(user.has_perm('integrations.export_siasn_data'))
    
    # Test view with permission
    response = self.client.get('/export/')
    self.assertEqual(response.status_code, 200)
```

---

## Summary

**3 Steps to Add Permission:**

1. **Edit Model** - Add to `permissions = [...]`
2. **Migrate** - `makemigrations` & `migrate`
3. **Assign** - Via Django Admin or shell

**Then use:**
- `@permission_required()` decorator
- `user.has_perm()` check
- `{% if perms.app.perm %}` in templates

**Easy! 🚀**
