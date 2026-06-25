"""
SIMPLE PERMISSION USAGE EXAMPLES
Django Built-in Permission System (like Spatie Laravel)
"""

# ============================================================
# 1. CHECK PERMISSION IN VIEWS
# ============================================================

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden, JsonResponse

# Using decorator (recommended)
@login_required
@permission_required('integrations.fetch_siasn_data', raise_exception=True)
def fetch_siasn_view(request, nip):
    """Only users with fetch_siasn_data permission can access"""
    # Your fetch logic here
    return JsonResponse({'success': True})


# Manual check
@login_required
def manual_check_view(request):
    if not request.user.has_perm('integrations.fetch_siasn_data'):
        return HttpResponseForbidden('You don\'t have permission to fetch data')
    
    # Your logic here
    return JsonResponse({'success': True})


# Check multiple permissions
@login_required
def admin_view(request):
    required_perms = [
        'integrations.manage_siasn_token',
        'integrations.delete_siasn_cache'
    ]
    
    if not request.user.has_perms(required_perms):
        return HttpResponseForbidden('Admin permission required')
    
    # Your admin logic here
    return JsonResponse({'success': True})


# ============================================================
# 2. CHECK PERMISSION IN TEMPLATES
# ============================================================

"""
<!-- In your Django template -->

{% if perms.integrations.fetch_siasn_data %}
    <button class="btn btn-primary" onclick="fetchData()">
        Fetch Data SIASN
    </button>
{% endif %}

{% if perms.integrations.download_siasn_foto %}
    <a href="/integrations/pegawai/foto/{{ nip }}/" class="btn">
        Download Foto
    </a>
{% endif %}

<!-- Check if user has role -->
{% if user.groups.all %}
    <span class="badge">{{ user.groups.first.name }}</span>
{% endif %}

<!-- Show menu based on permissions -->
<nav>
    {% if perms.integrations.view_siasn_dashboard %}
        <a href="/integrations/">Dashboard SIASN</a>
    {% endif %}
    
    {% if perms.integrations.fetch_siasn_data %}
        <a href="/integrations/fetch/">Fetch Data</a>
    {% endif %}
    
    {% if perms.integrations.manage_siasn_token %}
        <a href="/integrations/token/">Manage Token</a>
    {% endif %}
</nav>
"""


# ============================================================
# 3. ASSIGN ROLE TO USER (Django Shell)
# ============================================================

"""
# In Django shell: python manage.py shell

from django.contrib.auth.models import User, Group

# Get user
user = User.objects.get(username='admin')

# Get role
role = Group.objects.get(name='SIASN Admin')

# Assign role to user
user.groups.add(role)

# Check user's groups
print(user.groups.all())
# Output: <QuerySet [<Group: SIASN Admin>]>

# Check user's permissions
print(user.get_all_permissions())
# Output: {'integrations.fetch_siasn_data', 'integrations.download_siasn_foto', ...}

# Check specific permission
if user.has_perm('integrations.fetch_siasn_data'):
    print('User can fetch data')
"""


# ============================================================
# 4. ASSIGN ROLE IN VIEW (Programmatically)
# ============================================================

from django.contrib.auth.models import User, Group

def assign_role_to_user(username, role_name):
    """Assign role to user programmatically"""
    try:
        user = User.objects.get(username=username)
        role = Group.objects.get(name=role_name)
        user.groups.add(role)
        return True
    except (User.DoesNotExist, Group.DoesNotExist):
        return False


# Usage
if assign_role_to_user('john', 'SIASN Operator'):
    print('Role assigned successfully')


# ============================================================
# 5. CHECK PERMISSION IN PYTHON CODE
# ============================================================

def can_user_fetch_data(user):
    """Check if user has permission to fetch data"""
    return user.has_perm('integrations.fetch_siasn_data')


def get_user_permissions_list(user):
    """Get all permissions for user"""
    return list(user.get_all_permissions())


def get_user_roles(user):
    """Get all roles/groups for user"""
    return list(user.groups.values_list('name', flat=True))


# Usage
user = User.objects.get(username='admin')

if can_user_fetch_data(user):
    print('User can fetch data')

print('User permissions:', get_user_permissions_list(user))
print('User roles:', get_user_roles(user))


# ============================================================
# 6. DJANGO ADMIN INTEGRATION
# ============================================================

"""
Django Admin automatically integrates with permissions!

1. Go to: http://localhost:8005/admin/auth/user/{user_id}/change/
2. Scroll to "Groups" section
3. Select role (e.g., "SIASN Admin")
4. Save

Done! User now has all permissions from that role.
"""


# ============================================================
# 7. CREATE CUSTOM MIDDLEWARE (Optional)
# ============================================================

class SimplePermissionMiddleware:
    """Simple middleware to check permissions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check permissions for specific URLs
        if request.path.startswith('/integrations/fetch/'):
            if not request.user.has_perm('integrations.fetch_siasn_data'):
                return HttpResponseForbidden('Permission denied')
        
        return self.get_response(request)

# Add to settings.py MIDDLEWARE if needed


# ============================================================
# 8. COMPARISON: Laravel Spatie vs Django Built-in
# ============================================================

"""
Laravel Spatie                          Django Built-in
----------------------------------------|------------------------------------
Role::create(['name' => 'admin'])       | Group.objects.create(name='admin')
Permission::create(['name' => 'edit'])  | (auto-created from Meta.permissions)
$user->assignRole('admin')              | user.groups.add(admin_group)
$user->hasPermissionTo('edit posts')    | user.has_perm('app.edit_posts')
@role('admin')                          | @permission_required('app.perm')
@can('edit posts')                      | if user.has_perm('app.edit_posts')
$role->givePermissionTo('edit')         | group.permissions.add(permission)

SAME CONCEPTS, DIFFERENT SYNTAX!
"""
