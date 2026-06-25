# 🎯 SIMPLE PERMISSION SYSTEM - Django Built-in

## Why Use Django Built-in?

✅ **No extra package** - Sudah include di Django  
✅ **Simple & proven** - Dipakai jutaan aplikasi  
✅ **Like Spatie** - Konsep sama dengan Laravel Spatie Permission  
✅ **Admin ready** - Terintegrasi dengan Django Admin  

---

## Quick Setup (5 Minutes!)

### 1. **Create Permissions**

Django otomatis create permissions untuk setiap model (add, change, delete, view).
Untuk custom permissions:

```python
# apps/integrations/models.py

class SiasnPermission(models.Model):
    """Dummy model to hold custom permissions"""
    
    class Meta:
        managed = False  # No database table
        permissions = [
            ('fetch_siasn_data', 'Can fetch SIASN data'),
            ('download_foto', 'Can download foto'),
            ('manage_token', 'Can manage SIASN token'),
        ]
```

Run migration:
```bash
docker exec esimpeg_python_app python manage.py makemigrations
docker exec esimpeg_python_app python manage.py migrate
```

### 2. **Create Groups (Roles)**

```python
# management/commands/setup_roles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create Operator group
        operator, _ = Group.objects.get_or_create(name='Operator SIASN')
        
        # Assign permissions
        perms = Permission.objects.filter(
            codename__in=['fetch_siasn_data', 'download_foto']
        )
        operator.permissions.set(perms)
        
        # Create Admin group
        admin, _ = Group.objects.get_or_create(name='Admin SIASN')
        admin_perms = Permission.objects.filter(
            codename__in=['fetch_siasn_data', 'download_foto', 'manage_token']
        )
        admin.permissions.set(admin_perms)
        
        self.stdout.write('✅ Roles created!')
```

Run:
```bash
docker exec esimpeg_python_app python manage.py setup_roles
```

### 3. **Assign User to Group**

```python
# In Django shell or view
from django.contrib.auth.models import User, Group

user = User.objects.get(username='admin')
group = Group.objects.get(name='Admin SIASN')
user.groups.add(group)
```

Or via Django Admin: `/admin/auth/user/{id}/change/`

### 4. **Check Permission in Views**

```python
from django.contrib.auth.decorators import permission_required

@permission_required('integrations.fetch_siasn_data')
def fetch_data(request, nip):
    # Only users with permission can access
    pass

# Or manual check
if request.user.has_perm('integrations.fetch_siasn_data'):
    # Allow
    pass
```

### 5. **Check in Templates**

```html
{% if perms.integrations.fetch_siasn_data %}
    <button>Fetch Data</button>
{% endif %}

{% if user.groups.all|length > 0 %}
    <span>Role: {{ user.groups.first.name }}</span>
{% endif %}
```

---

## Complete Example

### Create Permissions

```python
# apps/integrations/models.py

class SiasnPermission(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            # View permissions
            ('view_siasn_dashboard', 'Can view SIASN dashboard'),
            ('view_siasn_logs', 'Can view SIASN logs'),
            
            # Data permissions
            ('fetch_siasn_data', 'Can fetch SIASN data'),
            ('sync_siasn_data', 'Can sync SIASN data'),
            
            # Download permissions
            ('download_foto', 'Can download foto'),
            ('download_dokumen', 'Can download dokumen'),
            
            # Admin permissions
            ('manage_siasn_token', 'Can manage SIASN token'),
            ('delete_siasn_cache', 'Can delete SIASN cache'),
        ]
```

### Setup Script

```python
# management/commands/setup_simple_permissions.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.integrations.models import SiasnPermission

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get content type
        ct = ContentType.objects.get_for_model(SiasnPermission)
        
        # Create groups
        viewer, _ = Group.objects.get_or_create(name='SIASN Viewer')
        operator, _ = Group.objects.get_or_create(name='SIASN Operator')
        admin, _ = Group.objects.get_or_create(name='SIASN Admin')
        
        # Assign permissions
        viewer_perms = Permission.objects.filter(
            content_type=ct,
            codename__in=['view_siasn_dashboard']
        )
        viewer.permissions.set(viewer_perms)
        
        operator_perms = Permission.objects.filter(
            content_type=ct,
            codename__in=[
                'view_siasn_dashboard',
                'view_siasn_logs',
                'fetch_siasn_data',
                'download_foto',
                'download_dokumen',
            ]
        )
        operator.permissions.set(operator_perms)
        
        admin_perms = Permission.objects.filter(content_type=ct)
        admin.permissions.set(admin_perms)
        
        self.stdout.write('✅ Groups created:')
        self.stdout.write(f'  • SIASN Viewer: {viewer.permissions.count()} perms')
        self.stdout.write(f'  • SIASN Operator: {operator.permissions.count()} perms')
        self.stdout.write(f'  • SIASN Admin: {admin.permissions.count()} perms')
```

### Usage in Views

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

# Function-based view
@login_required
@permission_required('integrations.fetch_siasn_data', raise_exception=True)
def fetch_siasn_view(request, nip):
    # Fetch data
    pass

# Class-based view
class FetchDataView(PermissionRequiredMixin, ListView):
    permission_required = 'integrations.fetch_siasn_data'
    # ...

# Manual check
@login_required
def my_view(request):
    if not request.user.has_perm('integrations.fetch_siasn_data'):
        return HttpResponseForbidden('No permission')
    # ...

# Check multiple permissions
@login_required
def admin_view(request):
    if not request.user.has_perms([
        'integrations.manage_siasn_token',
        'integrations.delete_siasn_cache'
    ]):
        return HttpResponseForbidden()
    # ...
```

### Dynamic Sidebar (Simple)

```python
# context_processors.py

def user_menu(request):
    if not request.user.is_authenticated:
        return {'user_menu': []}
    
    menu = []
    
    # Dashboard - always visible
    menu.append({
        'label': 'Dashboard',
        'url': '/dashboard/',
        'icon': 'ik ik-home'
    })
    
    # SIASN menu - check permissions
    if request.user.has_perm('integrations.view_siasn_dashboard'):
        siasn_menu = {
            'label': 'Integrasi SIASN',
            'icon': 'ik ik-database',
            'children': []
        }
        
        if request.user.has_perm('integrations.fetch_siasn_data'):
            siasn_menu['children'].append({
                'label': 'Fetch Data',
                'url': '/integrations/fetch/'
            })
        
        if request.user.has_perm('integrations.view_siasn_logs'):
            siasn_menu['children'].append({
                'label': 'Logs',
                'url': '/integrations/logs/'
            })
        
        menu.append(siasn_menu)
    
    # Admin menu
    if request.user.is_staff:
        menu.append({
            'label': 'Admin',
            'url': '/admin/',
            'icon': 'ik ik-settings'
        })
    
    return {'user_menu': menu}
```

```html
<!-- templates/sidebar.html -->
{% for item in user_menu %}
    <li>
        <a href="{{ item.url }}">
            <i class="{{ item.icon }}"></i>
            {{ item.label }}
        </a>
        {% if item.children %}
            <ul>
                {% for child in item.children %}
                    <li><a href="{{ child.url }}">{{ child.label }}</a></li>
                {% endfor %}
            </ul>
        {% endif %}
    </li>
{% endfor %}
```

---

## Django Admin Integration

Django Admin otomatis support permissions!

1. Go to: `/admin/auth/user/{id}/change/`
2. Assign groups di section "Groups"
3. Atau assign individual permissions di "User permissions"

Done! ✅

---

## Comparison: Custom vs Built-in

| Feature | Custom System | Django Built-in |
|---------|--------------|-----------------|
| Setup complexity | ⭐⭐⭐⭐ (Complex) | ⭐ (Simple) |
| Code lines | ~2000 lines | ~100 lines |
| Database tables | 5 tables | Uses existing tables |
| Learning curve | High | Low |
| Flexibility | Very high | Medium-High |
| Admin integration | Need custom | Built-in ✅ |
| Maintenance | Custom | Django core team |

---

## Migration from Custom to Built-in

Jika sudah terlanjur pakai custom system, bisa migrate:

```python
# Migrate data
from apps.permissions.models import Role, Permission as CustomPerm
from django.contrib.auth.models import Group, Permission

for role in Role.objects.all():
    # Create group
    group, _ = Group.objects.get_or_create(name=role.display_name)
    
    # Migrate permissions
    for perm in role.get_permissions():
        # Find or create matching Django permission
        django_perm = Permission.objects.filter(
            codename=perm.name.replace('.', '_')
        ).first()
        
        if django_perm:
            group.permissions.add(django_perm)
```

---

## Summary

**Django Built-in Permission System:**

✅ **Simple** - ~100 lines of code vs 2000 lines  
✅ **Standard** - Used by millions of Django apps  
✅ **Proven** - Battle-tested by Django core team  
✅ **Admin ready** - Works out of the box with Django Admin  
✅ **Enough** - Covers 90% of use cases  

**Recommendation:**
Start with Django built-in. Only create custom if you need:
- Complex hierarchical permissions
- Dynamic menu system from database
- Per-object permissions
- Custom permission logic

**For SIASN system:** Django built-in is enough! ✅
