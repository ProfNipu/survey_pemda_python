# Quick Guide: Run Pegawai Riwayat Data Migration

## Step-by-Step

### 1. Masuk ke Docker Container
```bash
docker exec -it survey_pemda_python_app bash
```

### 2. Run Migration
```bash
python manage.py migrate survey
```

Expected output:
```
Running migrations:
  Applying survey.0003_add_pegawai_riwayat_data... OK
```

### 3. Verify Table Created
```bash
python manage.py dbshell
```

In MySQL:
```sql
SHOW TABLES LIKE 'pegawai_riwayat_data';
DESCRIBE pegawai_riwayat_data;
EXIT;
```

### 4. Test Snapshot Creation

#### Option A: Via Django Shell
```bash
python manage.py shell
```

```python
from apps.survey.models import JenisSurvey, PeriodeSurvey
from django.utils import timezone
from datetime import timedelta

# Create test jenis survey
jenis = JenisSurvey.objects.create(
    kode='TEST_SNAPSHOT',
    nama='Test Snapshot Survey',
    deskripsi='Testing snapshot creation',
    is_active=True
)

# Create test periode (will trigger snapshot automatically)
periode = PeriodeSurvey.objects.create(
    jenis_survey=jenis,
    nama_periode='Test Periode - Januari 2026',
    tanggal_mulai=timezone.now(),
    tanggal_selesai=timezone.now() + timedelta(days=30),
    deskripsi='Testing automatic snapshot',
    is_active=True
)

print(f"Periode created: {periode}")
print(f"Status: {periode.status}")

# Wait a moment for signal to complete
import time
time.sleep(5)

# Check snapshot
from apps.survey.models import PegawaiRiwayatData
count = PegawaiRiwayatData.objects.filter(periode_survey=periode).count()
print(f"\nSnapshot created: {count} pegawai")

if count > 0:
    sample = PegawaiRiwayatData.objects.filter(periode_survey=periode).first()
    print(f"Sample: {sample.nama_pegawai} - {sample.nama_jabatan}")
    print("✅ Snapshot creation SUCCESS!")
else:
    print("⚠️ No snapshot created - check logs")

exit()
```

#### Option B: Via Management Command
```bash
# Get periode ID from previous step or create via admin
python manage.py create_pegawai_snapshot --periode-id=1
```

### 5. Check Logs
```bash
# Exit container first
exit

# Check logs
docker logs survey_pemda_python_app | grep -i snapshot
```

### 6. Verify in Admin
1. Open browser: http://localhost:8000/admin/
2. Login as admin
3. Go to: Survey > Pegawai Riwayat Data
4. Should see snapshot records

## Troubleshooting

### Migration Error: "No such table"
```bash
# Check current migrations
python manage.py showmigrations survey

# If 0003 not applied, run:
python manage.py migrate survey 0003_add_pegawai_riwayat_data
```

### Signal Not Working
```bash
# Check if signal registered
python manage.py shell
```

```python
from django.apps import apps
config = apps.get_app_config('survey')
print(config.ready)  # Should show method exists

# Check signal receivers
from django.db.models.signals import post_save
from apps.survey.models import PeriodeSurvey
receivers = post_save._live_receivers(PeriodeSurvey)
print(f"Receivers: {len(receivers)}")
```

### API Connection Error
```bash
python manage.py shell
```

```python
from apps.accounts.services import EsimpegAPIService
api = EsimpegAPIService()

try:
    pegawai = api.get_pegawai_list()
    print(f"✅ API OK: {len(pegawai)} pegawai")
except Exception as e:
    print(f"❌ API Error: {e}")
```

### Force Re-create Snapshot
```bash
# If snapshot wrong or incomplete
python manage.py create_pegawai_snapshot --periode-id=1 --force
```

## Quick Commands Reference

```bash
# Enter container
docker exec -it survey_pemda_python_app bash

# Run migration
python manage.py migrate survey

# Check migrations
python manage.py showmigrations survey

# Create snapshot manually
python manage.py create_pegawai_snapshot --periode-id=1

# Force recreate
python manage.py create_pegawai_snapshot --periode-id=1 --force

# Check logs
docker logs survey_pemda_python_app | tail -100

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell
```

## Success Indicators

✅ Migration applied without errors
✅ Table `pegawai_riwayat_data` exists
✅ Snapshot created when periode activated
✅ Data visible in admin
✅ No errors in logs

## If Everything Fails

1. Check ESIMPEG API connection
2. Check database connection
3. Check signal registration in apps.py
4. Create snapshot manually with command
5. Check logs for detailed error messages

## Next Steps After Migration

1. Test with real periode survey
2. Update report views to use PegawaiRiwayatData
3. Add UI for viewing snapshots
4. Monitor snapshot creation in production
