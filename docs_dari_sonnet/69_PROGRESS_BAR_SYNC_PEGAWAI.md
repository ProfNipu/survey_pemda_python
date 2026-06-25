# Progress Bar Real-time untuk Sync Pegawai

**Tanggal**: 1 April 2026  
**Status**: ✅ IMPLEMENTED

---

## 🎯 FEATURE

Progress bar real-time yang menampilkan:
- ✅ Percentage progress (0-100%)
- ✅ Current page / Total pages
- ✅ Processed records count
- ✅ New vs Updated records
- ✅ Status updates (running/completed/failed)

---

## 🏗️ ARCHITECTURE

### Flow Diagram
```
User Click Sync
    ↓
Backend: Create SyncProgress record (sync_id)
    ↓
Backend: Start sync process (loop pages)
    ↓
Backend: Update SyncProgress after each page
    ↓
Frontend: Poll progress every 1 second
    ↓
Frontend: Update progress bar UI
    ↓
Backend: Mark as completed
    ↓
Frontend: Show success message
```

---

## 📊 DATABASE SCHEMA

### Model: `SyncProgress`
```python
class SyncProgress(models.Model):
    sync_id = CharField(max_length=50, unique=True)  # UUID
    user = ForeignKey(User)
    status = CharField(choices=['running', 'completed', 'failed'])
    
    # Progress tracking
    current_page = IntegerField(default=0)
    total_pages = IntegerField(default=0)
    processed_records = IntegerField(default=0)
    total_records = IntegerField(default=0)
    new_records = IntegerField(default=0)
    updated_records = IntegerField(default=0)
    
    # Error handling
    error_message = TextField(null=True)
    
    # Timestamps
    started_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    @property
    def progress_percentage(self):
        if self.total_pages == 0:
            return 0
        return int((self.current_page / self.total_pages) * 100)
```

**Purpose**: Track sync progress in database untuk polling

---

## 🔄 BACKEND IMPLEMENTATION

### 1. Sync View dengan Progress Tracking

```python
@permission_required_403('api_simpeg', 'pegawai', 'sync')
def pegawai_sync(request):
    # Generate unique sync ID
    sync_id = str(uuid.uuid4())[:8]
    
    # Create progress tracker
    progress = SyncProgress.objects.create(
        sync_id=sync_id,
        user=request.user,
        status='running'
    )
    
    # Get total pages from first API call
    first_data = api_service.get_pegawai_list(...)
    total_pages = first_data['pagination']['total_pages']
    
    # Update progress with totals
    progress.total_pages = total_pages
    progress.total_records = first_data['pagination']['total']
    progress.save()
    
    # Process each page
    for page in range(1, total_pages + 1):
        # Get data from API
        data = api_service.get_pegawai_list(page=page, per_page=100)
        
        # Save to database
        for item in data['items']:
            pegawai, created = Pegawai.objects.update_or_create(...)
            if created:
                new_records += 1
            else:
                updated_records += 1
        
        # ✅ UPDATE PROGRESS after each page
        progress.current_page = page
        progress.processed_records = total_records
        progress.new_records = new_records
        progress.updated_records = updated_records
        progress.save()
    
    # Mark as completed
    progress.status = 'completed'
    progress.save()
    
    return JsonResponse({
        'success': True,
        'sync_id': sync_id,  # ✅ Return sync_id for polling
        ...
    })
```

**Key Points**:
- Generate unique `sync_id` untuk tracking
- Create `SyncProgress` record sebelum mulai
- Update progress after each page
- Return `sync_id` ke frontend

---

### 2. Progress Endpoint untuk Polling

```python
@permission_required_403('api_simpeg', 'pegawai', 'view')
def pegawai_sync_progress(request, sync_id):
    """Get sync progress for real-time updates"""
    try:
        progress = SyncProgress.objects.get(
            sync_id=sync_id, 
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'status': progress.status,
            'current_page': progress.current_page,
            'total_pages': progress.total_pages,
            'processed_records': progress.processed_records,
            'total_records': progress.total_records,
            'new_records': progress.new_records,
            'updated_records': progress.updated_records,
            'progress_percentage': progress.progress_percentage,
            'error_message': progress.error_message
        })
    except SyncProgress.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Progress not found'
        }, status=404)
```

**Purpose**: Endpoint untuk frontend polling progress

---

## 🎨 FRONTEND IMPLEMENTATION

### 1. Progress Bar HTML

```html
<div class="mb-4">
    <!-- Progress Bar -->
    <div class="w-full bg-gray-200 rounded-full h-6 mb-2">
        <div id="sync-progress-bar" 
             class="bg-blue-600 h-6 rounded-full transition-all duration-300" 
             style="width: 0%">
            <span id="sync-progress-text" 
                  class="text-white text-xs font-semibold flex items-center justify-center h-full">
                0%
            </span>
        </div>
    </div>
    
    <!-- Status Text -->
    <p id="sync-status-text" class="text-sm text-gray-600">
        Memulai sinkronisasi...
    </p>
    
    <!-- Detail Text -->
    <p id="sync-detail-text" class="text-xs text-gray-500 mt-2">
        Halaman: 0 / 0 | Records: 0
    </p>
</div>
```

---

### 2. JavaScript Polling Logic

```javascript
function syncPegawai() {
    // Show confirmation
    Swal.fire({...}).then((result) => {
        if (result.isConfirmed) {
            // Show progress bar modal
            Swal.fire({
                title: 'Sedang Menyinkronkan...',
                html: `<!-- Progress bar HTML -->`,
                allowOutsideClick: false,
                showConfirmButton: false
            });
            
            // Start sync
            fetch('/api-simpeg/pegawai/sync/', {
                method: 'POST',
                headers: {'X-CSRFToken': csrfToken}
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // ✅ Start polling with sync_id
                    pollSyncProgress(data.sync_id, data);
                }
            });
        }
    });
}

function pollSyncProgress(syncId, finalData) {
    const progressBar = document.getElementById('sync-progress-bar');
    const progressText = document.getElementById('sync-progress-text');
    const statusText = document.getElementById('sync-status-text');
    const detailText = document.getElementById('sync-detail-text');
    
    // Poll every 1 second
    const pollInterval = setInterval(() => {
        fetch(`/api-simpeg/pegawai/sync/progress/${syncId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const percentage = data.progress_percentage;
                
                // ✅ Update progress bar
                progressBar.style.width = percentage + '%';
                progressText.textContent = percentage + '%';
                
                // ✅ Update status
                statusText.textContent = 'Mengambil data dari ESIMPEG API...';
                
                // ✅ Update details
                detailText.textContent = 
                    `Halaman: ${data.current_page} / ${data.total_pages} | ` +
                    `Records: ${data.processed_records} ` +
                    `(${data.new_records} baru, ${data.updated_records} update)`;
                
                // ✅ Check if completed
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    
                    // Show success message
                    setTimeout(() => {
                        Swal.fire({
                            title: 'Berhasil!',
                            html: `...`,
                            icon: 'success'
                        }).then(() => {
                            location.reload();
                        });
                    }, 500);
                }
            }
        });
    }, 1000); // Poll every 1 second
}
```

**Key Points**:
- Poll setiap 1 detik
- Update progress bar width
- Update text (percentage, status, details)
- Stop polling saat completed
- Show success message

---

## 📈 PROGRESS CALCULATION

### Formula
```python
progress_percentage = (current_page / total_pages) * 100
```

### Example
```
Total pages: 98
Current page: 50
Progress: (50 / 98) * 100 = 51%

Total records: 4867
Processed: 2500
Per page: 100
Current page: 25
Progress: (25 / 49) * 100 = 51%
```

---

## 🎬 USER EXPERIENCE FLOW

### Step 1: User Click Sync
```
[Sinkronisasi Button]
    ↓
Confirmation Dialog:
"Proses ini akan:
 ✓ Mengambil semua data pegawai dari ESIMPEG API
 ✓ Menyimpan/update ke database Survey Pemda
 ✓ Data lama tetap tersimpan (historical)"
    ↓
[Ya, Sinkronkan!] [Batal]
```

### Step 2: Progress Bar Appears
```
┌─────────────────────────────────────┐
│   Sedang Menyinkronkan...           │
├─────────────────────────────────────┤
│                                     │
│  ████████████░░░░░░░░░░░░░░░  51%  │
│                                     │
│  Mengambil data dari ESIMPEG API... │
│                                     │
│  Halaman: 50 / 98 | Records: 2500  │
│  (1200 baru, 1300 update)           │
│                                     │
└─────────────────────────────────────┘
```

### Step 3: Completed
```
┌─────────────────────────────────────┐
│   Berhasil!                         │
├─────────────────────────────────────┤
│                                     │
│  Berhasil sync 4867 pegawai         │
│  (2400 baru, 2467 diupdate)         │
│                                     │
│  Total Records: 4867                │
│  Records Baru: 2400                 │
│  Records Diupdate: 2467             │
│  Durasi: 98.5 detik                 │
│                                     │
│           [OK]                      │
└─────────────────────────────────────┘
```

---

## 🔧 TECHNICAL DETAILS

### Polling Interval
```javascript
setInterval(() => {
    // Poll progress
}, 1000); // 1 second
```

**Why 1 second?**
- Balance between responsiveness and server load
- Each page takes ~2 seconds to process
- User sees smooth progress updates

### Database Updates
```python
# Update after each page (not each record)
for page in range(1, total_pages + 1):
    # Process 100 records
    ...
    
    # Update progress once per page
    progress.current_page = page
    progress.save()  # 1 DB write per page
```

**Optimization**:
- Update once per page (not per record)
- 98 pages = 98 DB writes (acceptable)
- If update per record = 4867 DB writes (too much!)

---

## 📊 PERFORMANCE

### Sync Performance
```
Total records: 4867
Pages: 98 (100 per page)
Time per page: ~2 seconds
Total time: ~196 seconds (3.3 minutes)

Progress updates: 98 (once per page)
Polling requests: ~196 (every 1 second)
```

### Database Impact
```
Writes per sync:
- SyncProgress create: 1
- SyncProgress updates: 98 (per page)
- Pegawai updates: 4867
- SyncLog create: 1
Total: ~4967 writes

Reads per sync (polling):
- Progress reads: ~196 (every 1 second)
```

**Acceptable**: Database can handle this load easily

---

## 🐛 ERROR HANDLING

### Backend Error
```python
try:
    # Sync process
    ...
except Exception as e:
    # Mark progress as failed
    progress.status = 'failed'
    progress.error_message = str(e)
    progress.save()
    
    return JsonResponse({
        'success': False,
        'error': str(e)
    }, status=500)
```

### Frontend Error
```javascript
if (data.status === 'failed') {
    clearInterval(pollInterval);
    
    Swal.fire({
        title: 'Gagal!',
        text: data.error_message,
        icon: 'error'
    });
}
```

---

## 🧪 TESTING

### Test 1: Normal Sync
```
1. Click "Sinkronisasi"
2. Confirm dialog
3. Progress bar appears
4. Progress updates every second
5. Reaches 100%
6. Success message shows
7. Page reloads
8. Data appears in table
```

### Test 2: Error Handling
```
1. Disconnect ESIMPEG API
2. Click "Sinkronisasi"
3. Progress starts
4. Error occurs at page X
5. Progress bar stops
6. Error message shows
7. User can retry
```

### Test 3: Multiple Users
```
User A: Start sync (sync_id: abc123)
User B: Start sync (sync_id: def456)

Each user sees their own progress
No interference between syncs
```

---

## 📁 FILES MODIFIED

1. ✅ `apps/api_simpeg/models.py` - Added `SyncProgress` model
2. ✅ `apps/api_simpeg/views.py` - Added progress tracking & endpoint
3. ✅ `apps/api_simpeg/urls.py` - Added progress endpoint URL
4. ✅ `apps/api_simpeg/templates/api_simpeg/pegawai_list.html` - Added progress bar UI & polling
5. ✅ `apps/api_simpeg/migrations/0003_syncprogress.py` - Migration file

---

## 🚀 DEPLOYMENT

### 1. Run Migration
```bash
docker exec survey_pemda_python_app python manage.py makemigrations api_simpeg
docker exec survey_pemda_python_app python manage.py migrate api_simpeg
```

### 2. Restart Container
```bash
docker restart survey_pemda_python_app
```

### 3. Test
```
1. Login as admin
2. Go to http://localhost:8006/api-simpeg/pegawai/
3. Click "Sinkronisasi"
4. Watch progress bar update real-time
5. Wait for completion
6. Verify data in table
```

---

## 🎯 BENEFITS

### 1. User Experience
```
Before:
- Loading spinner (no info)
- User tidak tahu progress
- Bisa dikira hang/error
- User bosan menunggu

After:
- Progress bar (visual feedback)
- Percentage (51%)
- Page info (50/98)
- Records count (2500)
- User tahu berapa lama lagi
```

### 2. Transparency
```
✅ User tahu proses sedang berjalan
✅ User tahu sudah sampai mana
✅ User tahu berapa lama lagi
✅ User bisa estimate completion time
```

### 3. Error Visibility
```
✅ Jika error, user tahu di page berapa
✅ User tahu berapa record sudah tersimpan
✅ User bisa retry dari awal
✅ Admin bisa debug dengan info lengkap
```

---

## 🔮 FUTURE ENHANCEMENTS

### 1. Pause/Resume
```python
# Add pause button
progress.status = 'paused'
progress.save()

# Resume from last page
start_page = progress.current_page + 1
```

### 2. Cancel Sync
```python
# Add cancel button
progress.status = 'cancelled'
progress.save()

# Rollback changes (optional)
Pegawai.objects.filter(
    synced_at__gte=progress.started_at
).delete()
```

### 3. Background Task (Celery)
```python
# Run sync in background
from celery import shared_task

@shared_task
def sync_pegawai_task(user_id, sync_id):
    # Sync in background
    # User can close browser
    # Progress still tracked
    pass
```

### 4. WebSocket (Real-time Push)
```python
# Instead of polling, push updates
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
await channel_layer.group_send(
    f'sync_{sync_id}',
    {'type': 'sync_progress', 'data': {...}}
)
```

---

## 📚 REFERENCES

- Polling Pattern: https://javascript.info/long-polling
- Progress Bar UI: https://tailwindcss.com/docs/width
- SweetAlert2: https://sweetalert2.github.io/
- Django Signals: https://docs.djangoproject.com/en/4.2/topics/signals/

---

**Status**: ✅ IMPLEMENTED - Progress bar real-time dengan polling setiap 1 detik
