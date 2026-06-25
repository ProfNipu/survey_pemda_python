# 🚀 Quick Reference - Pegawai Sync

**Last Updated**: 1 April 2026

---

## ⚡ Quick Start

### 1. Access Page
```
URL: http://localhost:8006/api-simpeg/pegawai/
Menu: API SIMPEG → Data Pegawai ESIMPEG
```

### 2. Sync Data
```
1. Click button "Sinkronisasi" (biru, kanan atas)
2. Confirm dialog
3. Wait ~3 minutes (progress bar akan bergerak)
4. Click OK setelah selesai
5. Done! Table refresh otomatis
```

---

## 📊 What You'll See

### Progress Bar
```
┌─────────────────────────────────────┐
│  Sedang Menyinkronkan...            │
│  ████████████████░░░░░░░░  51%     │
│  Mengambil data dari ESIMPEG API... │
│  Halaman: 50 / 98 | Records: 2500   │
│  (1200 baru, 1300 update)           │
└─────────────────────────────────────┘
```

### Success Message
```
┌─────────────────────────────────────┐
│  Berhasil!                          │
│  Berhasil sync 4867 pegawai         │
│  (2400 baru, 2467 diupdate)         │
│                                     │
│  Total Records: 4867                │
│  Records Baru: 2400                 │
│  Records Diupdate: 2467             │
│                                     │
│           [OK]                      │
└─────────────────────────────────────┘
```

---

## 🔧 Features

✅ **Manual Sync** - Click button untuk sync (bukan auto)
✅ **Progress Bar** - Real-time progress 0% → 100%
✅ **Historical Data** - Data lama tidak hilang
✅ **No Page Reload** - Table refresh smooth tanpa reload
✅ **Update or Create** - No duplicate records

---

## ⏱️ Performance

- **Sync Time**: ~3 minutes untuk 4867 records
- **Refresh Time**: ~0.8 seconds (no page reload)
- **Update Frequency**: Every 1 second

---

## 🐛 Troubleshooting

### Progress bar stuck at 0%?
- Check browser console (F12)
- Check backend logs: `docker logs survey_pemda_python_app -f`

### Token expired?
- Login ulang ke Survey Pemda

### Sync failed?
- Check ESIMPEG container running
- Check network connection
- Check error message in SweetAlert

---

## 📁 Key Files

### Backend
- `apps/api_simpeg/models.py` - Database models
- `apps/api_simpeg/views.py` - Sync logic
- `apps/api_simpeg/urls.py` - URL routes

### Frontend
- `apps/api_simpeg/templates/api_simpeg/pegawai_list.html` - Main page
- `apps/api_simpeg/templates/api_simpeg/partials/_pegawai_table.html` - Table partial

### Documentation
- `73_FINAL_SUMMARY_PEGAWAI_SYNC_COMPLETE.md` - Complete summary
- `71_FIX_PROGRESS_BAR_ASYNC.md` - Threading implementation
- `72_REFRESH_DATATABLE_NO_RELOAD.md` - HTMX refresh

---

## 🔍 Debugging

### Browser Console
```javascript
// Check sync started
console.log('Sync started with ID:', syncId);

// Check polling
console.log('Poll 1: 1% (Page 1/98)');

// Check refresh
console.log('Refreshing datatable...');
console.log('Datatable refreshed successfully');
```

### Backend Logs
```bash
docker logs survey_pemda_python_app -f | grep "Sync"

# Expected output:
# [Sync abc12345] Starting sync: 98 pages, 4867 records
# [Sync abc12345] Processing page 1/98...
# [Sync abc12345] Progress: 1% (1/98 pages, 100 records)
# ...
# [Sync abc12345] Completed: 4867 records in 196.5s
```

### Database Check
```bash
docker exec survey_pemda_python_app python manage.py shell

>>> from apps.api_simpeg.models import SyncProgress, Pegawai
>>> SyncProgress.objects.last()
>>> Pegawai.objects.count()
```

---

## 📞 Support

### Quick Checks
1. ✅ Container running? `docker ps`
2. ✅ Migrations applied? `docker exec survey_pemda_python_app python manage.py showmigrations api_simpeg`
3. ✅ No errors? `docker logs survey_pemda_python_app --tail 50`

### Documentation
- Full Summary: `73_FINAL_SUMMARY_PEGAWAI_SYNC_COMPLETE.md`
- Progress Bar: `69_PROGRESS_BAR_SYNC_PEGAWAI.md`
- Threading Fix: `71_FIX_PROGRESS_BAR_ASYNC.md`
- HTMX Refresh: `72_REFRESH_DATATABLE_NO_RELOAD.md`

---

## ✅ Status

**Container**: Up 8 minutes (healthy)
**Migrations**: All applied (0001, 0002, 0003)
**Errors**: None
**Status**: ✅ PRODUCTION READY

---

**Ready to test!** 🚀

Silakan buka http://localhost:8006/api-simpeg/pegawai/ dan klik "Sinkronisasi"!
