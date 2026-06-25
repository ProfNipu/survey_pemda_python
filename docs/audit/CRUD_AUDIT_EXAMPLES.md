# CRUD Audit Logging - Complete Examples

**Purpose:** Panduan lengkap penggunaan audit logging untuk CRUD operations  
**Created:** November 3, 2025

---

## 📚 Import

```python
from esimpeg_core.audit_logger import (
    audit_create,
    audit_update,
    audit_delete,
    audit_bulk_create,
    audit_bulk_update,
    audit_bulk_delete
)
```

---

## 1. CREATE - Tambah Data

### Example 1: Create Pegawai

```python
from apps.pegawai.models import Pegawai

def create_pegawai(request):
    # Create pegawai
    pegawai = Pegawai.objects.create(
        nama='John Doe',
        nip='198612252010011001',
        jabatan='Staff',
        status='active'
    )
    
    # Log to ms_log_data
    audit_create(request.user, pegawai, request)
    
    # Result in ms_log_data:
    # {
    #   "table_name": "pegawai",
    #   "record_id": 123,
    #   "action": "create",
    #   "username": "admin",
    #   "new_data": {
    #     "nama": "John Doe",
    #     "nip": "198612252010011001",
    #     "jabatan": "Staff",
    #     "status": "active"
    #   },
    #   "via": "web",
    #   "description": "Create Pegawai"
    # }
    
    return pegawai
```

### Example 2: Create with Custom Description

```python
def import_pegawai_from_api(request):
    pegawai = Pegawai.objects.create(
        nama='Jane Doe',
        nip='199001012015012001'
    )
    
    # Custom description
    audit_create(
        request.user, 
        pegawai, 
        request,
        description='Import pegawai dari API SIASN'
    )
    
    return pegawai
```

### Example 3: Create with Specific Fields Only

```python
def create_user(request):
    user = User.objects.create(
        username='newuser',
        email='newuser@example.com',
        password='hashed_password',
        is_active=True
    )
    
    # Log only safe fields (exclude password)
    audit_create(
        request.user,
        user,
        request,
        fields=['username', 'email', 'is_active']  # Exclude password
    )
    
    return user
```

---

## 2. UPDATE - Update Data

### Example 1: Update Jabatan

```python
def update_jabatan(request, pegawai_id):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    
    # Save old values BEFORE update
    old_values = {
        'jabatan': pegawai.jabatan
    }
    
    # Do update
    pegawai.jabatan = 'Kepala Bagian'
    pegawai.save()
    
    # Log update
    audit_update(request.user, pegawai, old_values, request)
    
    # Result in ms_log_data:
    # {
    #   "action": "update",
    #   "old_data": {"jabatan": "Staff"},
    #   "new_data": {"jabatan": "Kepala Bagian"},
    #   "description": "Update Pegawai"
    # }
    
    return pegawai
```

### Example 2: Update Multiple Fields

```python
def update_pegawai_profile(request, pegawai_id, data):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    
    # Save old values
    old_values = {
        'nama': pegawai.nama,
        'email': pegawai.email,
        'telepon': pegawai.telepon
    }
    
    # Update
    pegawai.nama = data.get('nama', pegawai.nama)
    pegawai.email = data.get('email', pegawai.email)
    pegawai.telepon = data.get('telepon', pegawai.telepon)
    pegawai.save()
    
    # Log (only changed fields akan di-log)
    audit_update(
        request.user, 
        pegawai, 
        old_values, 
        request,
        description='Update profil pegawai'
    )
    
    return pegawai
```

### Example 3: Update Status

```python
def activate_pegawai(request, pegawai_id):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    
    old_values = {'status': pegawai.status}
    
    pegawai.status = 'active'
    pegawai.save()
    
    audit_update(
        request.user,
        pegawai,
        old_values,
        request,
        description=f'Aktifkan pegawai {pegawai.nama}'
    )
```

---

## 3. DELETE - Hapus Data

### Example 1: Delete Pegawai

```python
def delete_pegawai(request, pegawai_id):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    
    # Log BEFORE delete
    audit_delete(request.user, pegawai, request)
    
    # Then delete
    pegawai.delete()
    
    # Result in ms_log_data:
    # {
    #   "action": "delete",
    #   "old_data": {
    #     "nama": "John Doe",
    #     "nip": "198612252010011001",
    #     "status": "active"
    #   },
    #   "new_data": null
    # }
```

### Example 2: Soft Delete (Status Update)

```python
def soft_delete_pegawai(request, pegawai_id):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    
    # Soft delete (just update status)
    old_values = {'status': pegawai.status}
    pegawai.status = 'deleted'
    pegawai.save()
    
    # Log as update with custom description
    audit_update(
        request.user,
        pegawai,
        old_values,
        request,
        description=f'Soft delete pegawai {pegawai.nama}'
    )
```

---

## 4. BULK OPERATIONS

### Example 1: Bulk Create

```python
def import_pegawai_bulk(request, pegawai_data_list):
    # Prepare instances
    pegawai_list = [
        Pegawai(
            nama=data['nama'],
            nip=data['nip'],
            jabatan=data.get('jabatan')
        )
        for data in pegawai_data_list
    ]
    
    # Bulk create
    created = Pegawai.objects.bulk_create(pegawai_list)
    
    # Log bulk create
    audit_bulk_create(
        request.user,
        Pegawai,
        created,
        request,
        description=f'Import {len(created)} pegawai dari Excel'
    )
    
    return created
```

### Example 2: Bulk Update

```python
def activate_all_pending(request):
    # Bulk update
    updated_count = Pegawai.objects.filter(
        status='pending'
    ).update(status='active')
    
    # Log bulk update
    audit_bulk_update(
        request.user,
        Pegawai,
        updated_count,
        fields=['status'],
        request,
        description=f'Aktifkan {updated_count} pegawai pending'
    )
    
    return updated_count
```

### Example 3: Bulk Delete

```python
def delete_inactive_pegawai(request):
    # Get count before delete
    to_delete = Pegawai.objects.filter(status='inactive')
    count = to_delete.count()
    
    # Delete
    to_delete.delete()
    
    # Log bulk delete
    audit_bulk_delete(
        request.user,
        Pegawai,
        count,
        request,
        description=f'Hapus {count} pegawai inactive'
    )
    
    return count
```

---

## 5. FORM-BASED CRUD

### Example: Django Form with Audit

```python
from django import forms
from apps.pegawai.models import Pegawai

class PegawaiForm(forms.ModelForm):
    class Meta:
        model = Pegawai
        fields = ['nama', 'nip', 'jabatan', 'email']

def create_pegawai_view(request):
    if request.method == 'POST':
        form = PegawaiForm(request.POST)
        if form.is_valid():
            # Save
            pegawai = form.save()
            
            # Audit log
            audit_create(request.user, pegawai, request)
            
            messages.success(request, 'Pegawai berhasil ditambahkan')
            return redirect('pegawai:list')
    else:
        form = PegawaiForm()
    
    return render(request, 'pegawai/form.html', {'form': form})

def update_pegawai_view(request, pk):
    pegawai = get_object_or_404(Pegawai, pk=pk)
    
    if request.method == 'POST':
        # Save old values
        old_values = {
            'nama': pegawai.nama,
            'nip': pegawai.nip,
            'jabatan': pegawai.jabatan,
            'email': pegawai.email
        }
        
        form = PegawaiForm(request.POST, instance=pegawai)
        if form.is_valid():
            # Update
            pegawai = form.save()
            
            # Audit log
            audit_update(request.user, pegawai, old_values, request)
            
            messages.success(request, 'Pegawai berhasil diupdate')
            return redirect('pegawai:detail', pk=pegawai.pk)
    else:
        form = PegawaiForm(instance=pegawai)
    
    return render(request, 'pegawai/form.html', {'form': form})
```

---

## 6. API-BASED CRUD

### Example: DRF ViewSet with Audit

```python
from rest_framework import viewsets
from rest_framework.response import Response

class PegawaiViewSet(viewsets.ModelViewSet):
    queryset = Pegawai.objects.all()
    serializer_class = PegawaiSerializer
    
    def perform_create(self, serializer):
        # Create
        pegawai = serializer.save()
        
        # Audit log
        audit_create(
            self.request.user,
            pegawai,
            self.request,
            description='Create pegawai via API'
        )
    
    def perform_update(self, serializer):
        # Get old values
        old_values = {
            field: getattr(serializer.instance, field)
            for field in serializer.validated_data.keys()
        }
        
        # Update
        pegawai = serializer.save()
        
        # Audit log
        audit_update(
            self.request.user,
            pegawai,
            old_values,
            self.request,
            description='Update pegawai via API'
        )
    
    def perform_destroy(self, instance):
        # Audit log BEFORE delete
        audit_delete(
            self.request.user,
            instance,
            self.request,
            description='Delete pegawai via API'
        )
        
        # Delete
        instance.delete()
```

---

## 7. TRANSACTION-SAFE LOGGING

### Example: Atomic Operations

```python
from django.db import transaction

@transaction.atomic
def transfer_pegawai(request, pegawai_id, new_opd_id):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    old_opd_id = pegawai.id_opd
    
    # Update
    pegawai.id_opd = new_opd_id
    pegawai.save()
    
    # Log (akan rollback jika ada error)
    audit_update(
        request.user,
        pegawai,
        {'id_opd': old_opd_id},
        request,
        description=f'Transfer pegawai ke OPD {new_opd_id}'
    )
    
    # If any error occurs, both update and log will rollback ✅
```

---

## 8. CONDITIONAL LOGGING

### Example: Log Only Important Changes

```python
def update_pegawai_smart(request, pegawai_id, data):
    pegawai = Pegawai.objects.get(id=pegawai_id)
    
    important_fields = ['jabatan', 'status', 'golongan']
    old_values = {}
    
    # Collect only important field changes
    for field in important_fields:
        if field in data:
            old_values[field] = getattr(pegawai, field)
    
    # Update all fields
    for field, value in data.items():
        setattr(pegawai, field, value)
    pegawai.save()
    
    # Log only if important fields changed
    if old_values:
        audit_update(
            request.user,
            pegawai,
            old_values,
            request,
            description='Update data penting pegawai'
        )
```

---

## 9. BACKGROUND JOB LOGGING

### Example: Celery Task

```python
from celery import shared_task

@shared_task
def sync_pegawai_from_api():
    # Get data from external API
    api_data = fetch_pegawai_from_api()
    
    created_count = 0
    for data in api_data:
        pegawai, created = Pegawai.objects.update_or_create(
            nip=data['nip'],
            defaults=data
        )
        
        if created:
            # Log without request (background job)
            audit_create(
                user=None,  # System user
                instance=pegawai,
                request=None,
                description='Auto-sync from API SIASN'
            )
            created_count += 1
    
    return f'Synced {created_count} new pegawai'
```

---

## 10. QUERY AUDIT LOGS

### Example: View Pegawai History

```python
from esimpeg_core.models import MsLogData

def pegawai_history(request, pegawai_id):
    # Get all logs for this pegawai
    logs = MsLogData.objects.filter(
        table_name='pegawai',
        record_id=pegawai_id
    ).order_by('-created_at')
    
    # Result:
    # [
    #   {action: 'update', old: {jabatan: 'Staff'}, new: {jabatan: 'Kabag'}},
    #   {action: 'update', old: {email: 'old@'}, new: {email: 'new@'}},
    #   {action: 'create', new: {nama: 'John', nip: '123'}}
    # ]
    
    return render(request, 'pegawai/history.html', {'logs': logs})

def user_activity(request, username):
    # Get all actions by this user
    activities = MsLogData.objects.filter(
        username=username
    ).order_by('-created_at')[:50]
    
    return render(request, 'user/activity.html', {'activities': activities})
```

---

## ✅ Best Practices

1. **Always log BEFORE delete**
   ```python
   audit_delete(user, instance, request)  # ✅ First
   instance.delete()                       # Then delete
   ```

2. **Save old values BEFORE update**
   ```python
   old_values = {'field': instance.field}  # ✅ First
   instance.field = new_value              # Then update
   instance.save()
   audit_update(user, instance, old_values, request)
   ```

3. **Use transactions for critical operations**
   ```python
   @transaction.atomic
   def critical_update(request):
       # Both will rollback on error ✅
       instance.save()
       audit_update(...)
   ```

4. **Don't log sensitive data**
   ```python
   audit_create(user, user_instance, request, 
                fields=['username', 'email'])  # ✅ Exclude password
   ```

5. **Use custom descriptions for clarity**
   ```python
   audit_update(user, instance, old_values, request,
                description='Promosi jabatan dari Staff ke Kabag')  # ✅ Clear
   ```

---

## 📊 Summary

| Operation | Function | When to Call |
|-----------|----------|--------------|
| **Create** | `audit_create()` | After `.create()` or `.save()` |
| **Update** | `audit_update()` | After `.save()` with old values |
| **Delete** | `audit_delete()` | BEFORE `.delete()` |
| **Bulk Create** | `audit_bulk_create()` | After `.bulk_create()` |
| **Bulk Update** | `audit_bulk_update()` | After `.update()` |
| **Bulk Delete** | `audit_bulk_delete()` | After `.delete()` (get count first) |

---

**Status: ✅ READY TO USE**  
**Last Updated: November 3, 2025**
