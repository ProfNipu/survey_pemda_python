# Survey Pemda Python - Quick Start Guide

## 🚀 Start Application

```bash
# Start containers
docker compose up -d

# Check status
docker ps | grep survey_pemda_python

# View logs
docker logs -f survey_pemda_python_app
```

## 🌐 Access URLs

- **Application**: http://localhost:8006
- **Admin Panel**: http://localhost:8006/admin/
- **Jenis Survey**: http://localhost:8006/admin/survey_jpt/jenissurvey/
- **Pertanyaan Survey**: http://localhost:8006/admin/survey_jpt/pertanyaansurvey/

## 🔑 Default Credentials

Create superadmin first:
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin --user admin@example.com
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

## 📊 Menu Locations

### Survey System
```
Sidebar → Survey
  ├── Penilaian JPT
  │   ├── Daftar Penilaian (TODO)
  │   ├── Tambah Penilaian (TODO)
  │   └── Laporan Hasil (TODO)
  └── Master Survey
      ├── Jenis Survey ✓
      └── Pertanyaan Survey ✓
```

### API SIMPEG
```
Sidebar → Manajemen Integrasi
  └── ESIMPEG
      └── Pegawai ✓
```

## 🛠️ Common Commands

### Database
```bash
# Run migrations
docker exec survey_pemda_python_app python manage.py migrate

# Create migrations
docker exec survey_pemda_python_app python manage.py makemigrations

# Shell
docker exec -it survey_pemda_python_app python manage.py shell
```

### Seeding
```bash
# Core setup (permissions + menu)
docker exec survey_pemda_python_app python manage.py seed_core_setup

# Survey data (JPT + 7 questions)
docker exec survey_pemda_python_app python manage.py seed_survey_jpt

# Survey menu
docker exec survey_pemda_python_app python manage.py seed_survey_menu

# Superadmin access
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### Container Management
```bash
# Restart
docker restart survey_pemda_python_app

# Stop
docker stop survey_pemda_python_app

# Remove (careful!)
docker rm -f survey_pemda_python_app

# Rebuild
docker compose up -d --build
```

## 📝 Quick Tasks

### Add New Survey Type
1. Go to: http://localhost:8006/admin/survey_jpt/jenissurvey/
2. Click "Add Jenis Survey"
3. Fill: Kode, Nama, Deskripsi
4. Save

### Add Questions
1. Go to: http://localhost:8006/admin/survey_jpt/pertanyaansurvey/
2. Click "Add Pertanyaan Survey"
3. Select Jenis Survey
4. Fill: Kode, Pertanyaan, Urutan, Bobot
5. Save

### Check Survey Data
```bash
docker exec survey_pemda_python_app python manage.py shell -c "
from apps.survey_jpt.models import JenisSurvey, PertanyaanSurvey
print('Jenis Survey:', JenisSurvey.objects.count())
print('Pertanyaan:', PertanyaanSurvey.objects.count())
"
```

## 🐛 Troubleshooting

### Menu not showing
```bash
docker exec survey_pemda_python_app python manage.py seed_survey_menu
docker restart survey_pemda_python_app
```

### Permission denied
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### Database error
```bash
# Check connection
docker exec survey_pemda_python_app python manage.py dbshell

# Reset database (careful!)
docker exec survey_pemda_python_app python manage.py flush --noinput
docker exec survey_pemda_python_app python manage.py migrate
```

### Container not starting
```bash
# Check logs
docker logs survey_pemda_python_app

# Check MySQL
docker logs survey_pemda_python_mysql_check

# Check Redis
docker exec survey-pemda-python-redis redis-cli ping
```

## 📚 Documentation

- **Full Guide**: `docs/SEEDING_GUIDE_SURVEY.md`
- **Menu Guide**: `docs/MENU_SURVEY_GUIDE.md`
- **Architecture**: `docs/SURVEY_SYSTEM_OVERVIEW.md`
- **Status**: `docs/PROJECT_STATUS.md`

## 🎯 Next Steps

1. ✅ System is ready
2. 📝 Implement input form (Tambah Penilaian)
3. 📝 Implement list view (Daftar Penilaian)
4. 📝 Implement report (Laporan Hasil)

## 💡 Tips

- Use Django Admin for quick CRUD operations
- Check `docs/` folder for detailed documentation
- All seeders are idempotent (safe to run multiple times)
- Menu structure is dynamic (stored in database)

---

**Need Help?** Check the documentation in `docs/` folder or run:
```bash
docker exec survey_pemda_python_app python manage.py help
```
