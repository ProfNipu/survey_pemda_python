# Audit Logging - Quick Reference

**Quick copy-paste templates for CRUD audit logging**

---

## 🚀 Import

```python
from esimpeg_core.audit_logger import audit_create, audit_update, audit_delete
```

---

## 📝 CREATE

```python
# After creating record
pegawai = Pegawai.objects.create(nama='John', nip='123')
audit_create(request.user, pegawai, request)
```

---

## ✏️ UPDATE

```python
# Save old → Update → Log
old_values = {'jabatan': pegawai.jabatan}
pegawai.jabatan = 'Kepala Bagian'
pegawai.save()
audit_update(request.user, pegawai, old_values, request)
```

---

## 🗑️ DELETE

```python
# Log first → Then delete
audit_delete(request.user, pegawai, request)
pegawai.delete()
```

---

## 📦 BULK OPERATIONS

```python
from esimpeg_core.audit_logger import audit_bulk_create, audit_bulk_update, audit_bulk_delete

# Bulk create
created = Pegawai.objects.bulk_create(pegawai_list)
audit_bulk_create(request.user, Pegawai, created, request)

# Bulk update
count = Pegawai.objects.filter(status='pending').update(status='active')
audit_bulk_update(request.user, Pegawai, count, ['status'], request)

# Bulk delete
count = Pegawai.objects.filter(status='inactive').count()
Pegawai.objects.filter(status='inactive').delete()
audit_bulk_delete(request.user, Pegawai, count, request)
```

---

## 🎯 With Custom Description

```python
audit_create(request.user, pegawai, request, 
             description='Import pegawai dari API SIASN')

audit_update(request.user, pegawai, old_values, request,
             description='Promosi jabatan pegawai')

audit_delete(request.user, pegawai, request,
             description='Hapus pegawai pensiunan')
```

---

## 🔒 Exclude Sensitive Fields

```python
# Create user - exclude password
audit_create(request.user, user, request,
             fields=['username', 'email', 'is_active'])
```

---

## 📊 Query Logs

```python
from esimpeg_core.models import MsLogData

# All actions on pegawai ID 123
logs = MsLogData.objects.filter(
    table_name='pegawai',
    record_id=123
).order_by('-created_at')

# All actions by user
logs = MsLogData.objects.filter(
    username='admin'
).order_by('-created_at')

# All creates today
from django.utils import timezone
logs = MsLogData.objects.filter(
    action='create',
    created_at__date=timezone.now().date()
)
```

---

## ⚡ Django Views

```python
def create_view(request):
    if request.method == 'POST':
        form = PegawaiForm(request.POST)
        if form.is_valid():
            pegawai = form.save()
            audit_create(request.user, pegawai, request)  # ← ADD THIS
            return redirect('success')
    return render(request, 'form.html')

def update_view(request, pk):
    pegawai = get_object_or_404(Pegawai, pk=pk)
    if request.method == 'POST':
        old_values = {'jabatan': pegawai.jabatan}  # ← SAVE OLD
        form = PegawaiForm(request.POST, instance=pegawai)
        if form.is_valid():
            pegawai = form.save()
            audit_update(request.user, pegawai, old_values, request)  # ← ADD THIS
            return redirect('success')
    return render(request, 'form.html')

def delete_view(request, pk):
    pegawai = get_object_or_404(Pegawai, pk=pk)
    if request.method == 'POST':
        audit_delete(request.user, pegawai, request)  # ← ADD THIS
        pegawai.delete()
        return redirect('success')
    return render(request, 'confirm.html')
```

---

## 🔌 DRF API

```python
class PegawaiViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        pegawai = serializer.save()
        audit_create(self.request.user, pegawai, self.request)  # ← ADD THIS
    
    def perform_update(self, serializer):
        old_values = {f: getattr(serializer.instance, f) 
                     for f in serializer.validated_data.keys()}  # ← SAVE OLD
        pegawai = serializer.save()
        audit_update(self.request.user, pegawai, old_values, self.request)  # ← ADD THIS
    
    def perform_destroy(self, instance):
        audit_delete(self.request.user, instance, self.request)  # ← ADD THIS
        instance.delete()
```

---

**📖 Full examples:** `CRUD_AUDIT_EXAMPLES.md`  
**📚 Documentation:** `MS_LOG_DATA_HYBRID_GUIDE.md`
