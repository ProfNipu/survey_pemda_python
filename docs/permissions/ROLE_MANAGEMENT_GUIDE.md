# 🎯 ROLE MANAGEMENT GUIDE

## Lokasi Manajemen Role & Permission

### 1. Django Admin (GUI) - **PALING MUDAH** ⭐

#### Dashboard Admin
```
URL: http://localhost:8005/admin/
```

Setelah login, akan muncul:

```
┌─────────────────────────────────────────────────┐
│ ESIMPEG Python Administration                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ AUTHENTICATION AND AUTHORIZATION                │
│                                                 │
│   → Groups                        [+ Add]       │  ← MANAGE ROLES DI SINI!
│   → Users                         [+ Add]       │  ← ASSIGN ROLE KE USER
│   → Permissions                                 │  ← VIEW PERMISSIONS
│                                                 │
│ INTEGRATIONS                                    │
│   → Siasn api logs                              │
│   → Siasn pegawais                              │
│   → Ws siasn tokens                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

### 2. Manage Roles (Groups)

#### URL: http://localhost:8005/admin/auth/group/

```
┌────────────────────────────────────────────────────────────┐
│ Select group to change                                     │
├────────────────────────────────────────────────────────────┤
│ [Add Group +]                                              │
│                                                            │
│ Filter: [_______] [Search]                                │
│                                                            │
│ ┌───────────────────────┬──────────────────────────────┐  │
│ │ Name                  │ Actions                      │  │
│ ├───────────────────────┼──────────────────────────────┤  │
│ │ SIASN Admin           │ [Change] [Delete]            │  │
│ │ SIASN Manager         │ [Change] [Delete]            │  │
│ │ SIASN Operator        │ [Change] [Delete]            │  │
│ │ SIASN Viewer          │ [Change] [Delete]            │  │
│ └───────────────────────┴──────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Yang bisa dilakukan:**
- ✅ Create role baru (klik "Add Group")
- ✅ Edit role (klik "Change")
- ✅ Delete role (klik "Delete")
- ✅ Assign/remove permissions

---

### 3. Edit Role (Assign Permissions)

Klik "Change" pada role yang mau di-edit:

```
┌────────────────────────────────────────────────────────────┐
│ Change group: SIASN Operator                               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Name: [SIASN Operator___________________]                 │
│                                                            │
│ Permissions:                                               │
│                                                            │
│ Hold down "Control", or "Command" on a Mac, to select     │
│ more than one.                                             │
│                                                            │
│ ┌─────────────────────┬──────────────────────────────┐    │
│ │ Available           │ Chosen                       │    │
│ │ permissions         │ permissions                  │    │
│ ├─────────────────────┼──────────────────────────────┤    │
│ │                     │ ↑ delete_siasn_cache        │    │
│ │ manage_siasn_token →│   download_siasn_dokumen    │    │
│ │ view_siasn_token    │   download_siasn_foto       │    │
│ │                     │   fetch_siasn_data          │    │
│ │                     │   fetch_siasn_minimal       │    │
│ │                     │   sync_siasn_data           │    │
│ │                     │   view_siasn_cache          │    │
│ │                     │   view_siasn_dashboard      │    │
│ │                     │   view_siasn_logs           │    │
│ │                     │ ↓                           │    │
│ └─────────────────────┴──────────────────────────────┘    │
│      [Choose all] [Remove all]                            │
│                                                            │
│ [Save] [Save and add another] [Save and continue editing] │
│                                                            │
│ [Delete]                                                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Cara assign permission:**
1. Pilih permission di kolom kiri (Available)
2. Klik "→" untuk pindah ke kanan (Chosen)
3. Atau klik "Choose all" untuk select semua
4. Klik "Save"

---

### 4. Assign Role to User

#### URL: http://localhost:8005/admin/auth/user/

Pilih user yang mau di-assign role, lalu:

```
┌────────────────────────────────────────────────────────────┐
│ Change user: admin                                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Username: [admin______________] (required)                │
│ Password: **** [Change password]                          │
│                                                            │
│ First name: [__________________]                          │
│ Last name:  [__________________]                          │
│ Email:      [admin@example.com_]                          │
│                                                            │
│ Permissions:                                               │
│   ☑ Active                                                │
│   ☐ Staff status                                          │
│   ☑ Superuser status                                      │
│                                                            │
│ Groups:                          ← ASSIGN ROLE DI SINI!   │
│ ┌─────────────────────┬──────────────────────────────┐    │
│ │ Available groups    │ Chosen groups                │    │
│ ├─────────────────────┼──────────────────────────────┤    │
│ │ SIASN Manager      →│   SIASN Admin                │    │
│ │ SIASN Operator      │                              │    │
│ │ SIASN Viewer        │                              │    │
│ │                     │                              │    │
│ └─────────────────────┴──────────────────────────────┘    │
│      [Choose all] [Remove all]                            │
│                                                            │
│ [Save] [Save and add another] [Save and continue editing] │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Cara assign role:**
1. Pilih role di kolom kiri (Available groups)
2. Klik "→" untuk pindah ke kanan (Chosen groups)
3. User bisa punya multiple roles
4. Klik "Save"

---

### 5. View All Permissions

#### URL: http://localhost:8005/admin/auth/permission/

```
┌────────────────────────────────────────────────────────────┐
│ Select permission to change                                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Filter by: [Content type ▼] [Codename contains: siasn_] │
│                                                            │
│ ┌──────────────────────┬─────────────┬──────────────┐     │
│ │ Name                 │ Content type│ Codename     │     │
│ ├──────────────────────┼─────────────┼──────────────┤     │
│ │ Delete cached data   │ siasn perm  │ delete_...   │     │
│ │ Download dokumen     │ siasn perm  │ download_... │     │
│ │ Download foto        │ siasn perm  │ download_... │     │
│ │ Fetch SIASN data     │ siasn perm  │ fetch_...    │     │
│ │ Fetch minimal data   │ siasn perm  │ fetch_...    │     │
│ │ Manage token         │ siasn perm  │ manage_...   │     │
│ │ ...                  │ ...         │ ...          │     │
│ └──────────────────────┴─────────────┴──────────────┘     │
└────────────────────────────────────────────────────────────┘
```

---

## Via Django Shell (Command Line)

### List All Roles

```bash
docker exec -it esimpeg_python_app python manage.py shell
```

```python
>>> from django.contrib.auth.models import Group
>>> Group.objects.all()
<QuerySet [<Group: SIASN Viewer>, <Group: SIASN Operator>, <Group: SIASN Manager>, <Group: SIASN Admin>]>

# Detail satu role
>>> role = Group.objects.get(name='SIASN Operator')
>>> role.name
'SIASN Operator'
>>> role.permissions.all()
<QuerySet [<Permission: Can fetch SIASN data>, ...]>
>>> role.permissions.count()
9
```

### Create New Role

```python
>>> from django.contrib.auth.models import Group, Permission
>>> new_role = Group.objects.create(name='Custom Role')

# Assign permissions
>>> perm1 = Permission.objects.get(codename='fetch_siasn_data')
>>> perm2 = Permission.objects.get(codename='view_siasn_dashboard')
>>> new_role.permissions.add(perm1, perm2)

# Check
>>> new_role.permissions.count()
2
```

### Assign Role to User

```python
>>> from django.contrib.auth.models import User, Group

# Get user
>>> user = User.objects.get(username='admin')

# Get role
>>> role = Group.objects.get(name='SIASN Admin')

# Assign
>>> user.groups.add(role)

# Check
>>> user.groups.all()
<QuerySet [<Group: SIASN Admin>]>

# Check permissions
>>> user.get_all_permissions()
{'integrations.fetch_siasn_data', 'integrations.download_siasn_foto', ...}

# Check specific permission
>>> user.has_perm('integrations.fetch_siasn_data')
True
```

### Remove Role from User

```python
>>> user = User.objects.get(username='admin')
>>> role = Group.objects.get(name='SIASN Admin')
>>> user.groups.remove(role)
```

---

## Re-run Setup Command

Untuk reset semua roles & permissions ke default:

```bash
docker exec esimpeg_python_app python manage.py setup_siasn_roles
```

Output:
```
Setting up SIASN roles & permissions...
✓ Created role: SIASN Viewer
  → Assigned 3 permissions
✓ Created role: SIASN Operator
  → Assigned 9 permissions
✓ Created role: SIASN Manager
  → Assigned 11 permissions
✓ Created role: SIASN Admin
  → Assigned 12 permissions (all)
```

---

## Quick Commands

### Check Current Setup

```bash
# List all roles
docker exec esimpeg_python_app python manage.py shell -c "
from django.contrib.auth.models import Group
for g in Group.objects.all():
    print(f'{g.name}: {g.permissions.count()} permissions')
"

# List users with roles
docker exec esimpeg_python_app python manage.py shell -c "
from django.contrib.auth.models import User
for u in User.objects.all():
    roles = ', '.join([g.name for g in u.groups.all()])
    print(f'{u.username}: {roles or \"No roles\"}')
"
```

### Quick Assign

```bash
# Assign admin role to user 'john'
docker exec esimpeg_python_app python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.get(username='john')
role = Group.objects.get(name='SIASN Admin')
user.groups.add(role)
print(f'✓ Assigned SIASN Admin to john')
"
```

---

## Summary

| Method | Location | Difficulty | Best For |
|--------|----------|------------|----------|
| **Django Admin** | http://localhost:8005/admin/auth/group/ | ⭐ Easy | GUI, Visual management |
| **Django Shell** | Command line | ⭐⭐ Medium | Bulk operations, Scripts |
| **Code** | views.py / Python code | ⭐⭐⭐ Advanced | Automation, Integration |

**Recommended:** Start with **Django Admin** for easy visual management! 🎯
