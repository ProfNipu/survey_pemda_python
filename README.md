# Survey Pemda Python

Sistem Penilaian Pegawai berbasis web dengan fokus pada Survey JPT (Jabatan Pimpinan Tinggi) dan sistem survey dinamis.

## 🎯 Fitur Utama

### ✅ Sistem Survey Dinamis
- Tambah jenis survey baru tanpa coding
- Pertanyaan dapat dikonfigurasi per jenis survey
- Bobot pertanyaan dapat disesuaikan
- Perhitungan nilai otomatis dengan weighted scoring
- Support multiple survey types (JPT, 360, dll)

### ✅ Integrasi API SIMPEG
- Import data pegawai dari database BKPSDM
- Tabel reusable dengan django-tables2
- Data pegawai dalam format JSON (API-ready)

### ✅ UI/UX Modern
- Sidebar dengan gradient green-teal (emerald → teal → cyan)
- Preloader dengan animasi heartbeat/EKG
- Dashboard khusus survey (berbeda dari project lain)
- Responsive design dengan Tailwind CSS
- Animated icons dan floating cards

## 🚀 Quick Start

### 1. Start Application
```bash
docker compose up -d
```

### 2. Access Application
- **URL**: http://localhost:8006
- **Admin**: http://localhost:8006/admin/

### 3. Create Superadmin
```bash
docker exec survey_pemda_python_app python manage.py seed_superadmin --user admin@example.com
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### 4. Access "Jenis Survey" Menu
**Via Sidebar**: Survey → Master Survey → Jenis Survey  
**Via URL**: http://localhost:8006/admin/survey_jpt/jenissurvey/

## 📋 Menu Structure

```
📊 Survey
├── ⭐ Penilaian JPT
│   ├── 📋 Daftar Penilaian (TODO)
│   ├── ➕ Tambah Penilaian (TODO)
│   └── 📊 Laporan Hasil (TODO)
└── ⚙️ Master Survey
    ├── 🏷️ Jenis Survey ✓
    └── ❓ Pertanyaan Survey ✓

🔧 Manajemen Integrasi
└── 📡 ESIMPEG
    └── 👥 Pegawai ✓
```

## 🗂️ Database Schema

### survey_jenis
Master jenis survey (JPT, 360, dll)
- `kode` (unique) - Kode survey
- `nama` - Nama lengkap
- `deskripsi` - Deskripsi (optional)
- `is_active` - Status

### survey_pertanyaan
Pertanyaan per jenis survey
- `jenis_survey_id` (FK)
- `kode_pertanyaan` - Kode pertanyaan
- `pertanyaan` - Teks pertanyaan
- `urutan` - Nomor urut
- `bobot` - Bobot untuk perhitungan
- `is_active` - Status

### survey_responden
Data responden (penilai & yang dinilai)
- `id_pegawaiPenilai` - ID penilai
- `nip_pegawaiPenilai` - NIP penilai
- `id_pegawaiDinilai` - ID yang dinilai
- `nip_pegawaiDinilai` - NIP yang dinilai
- `peranPenilai` - Peran (atasan, rekan, bawahan)
- `statusData` - Status (draft, submitted, approved)

### survey_jawaban
Jawaban survey dengan nilai 1-5
- `responden_id` (FK)
- `pertanyaan_id` (FK)
- `nilai` - Nilai 1-5
- Automatic: `nilai_terbobot` = nilai × bobot

## 🛠️ Tech Stack

### Backend
- Django 5.2.7
- MySQL 8.4.6
- Redis 7.x (DB 4)
- Django REST Framework

### Frontend
- Tailwind CSS 3.x
- Font Awesome 6.x
- HTMX
- Chart.js (planned)

### DevOps
- Docker + Docker Compose
- Gunicorn
- Nginx (via nginx-proxy)

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[docs/SEEDING_GUIDE_SURVEY.md](docs/database/SEEDING_GUIDE_SURVEY.md)** - Complete seeding guide
- **[docs/MENU_SURVEY_GUIDE.md](docs/MENU_SURVEY_GUIDE.md)** - Menu navigation guide
- **[docs/SURVEY_SYSTEM_OVERVIEW.md](docs/SURVEY_SYSTEM_OVERVIEW.md)** - Architecture & design
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** - Current status & roadmap

## 🔧 Common Commands

### Seeding
```bash
# Core setup
docker exec survey_pemda_python_app python manage.py seed_core_setup

# Survey data (JPT + 7 questions)
docker exec survey_pemda_python_app python manage.py seed_survey_jpt

# Survey menu
docker exec survey_pemda_python_app python manage.py seed_survey_menu

# Superadmin access
docker exec survey_pemda_python_app python manage.py seed_superadmin_full_access
```

### Database
```bash
# Run migrations
docker exec survey_pemda_python_app python manage.py migrate

# Shell
docker exec -it survey_pemda_python_app python manage.py shell
```

### Container
```bash
# Restart
docker restart survey_pemda_python_app

# Logs
docker logs -f survey_pemda_python_app

# Rebuild
docker compose up -d --build
```

## 💡 How to Add New Survey Type

### 1. Via Django Admin
1. Go to: http://localhost:8006/admin/survey_jpt/jenissurvey/
2. Click "Add Jenis Survey"
3. Fill:
   - Kode: `SURVEY_360`
   - Nama: `Survey 360 Derajat`
   - Deskripsi: `Penilaian dari berbagai sudut pandang`
   - Is Active: ✓
4. Save

### 2. Add Questions
1. Go to: http://localhost:8006/admin/survey_jpt/pertanyaansurvey/
2. Click "Add Pertanyaan Survey"
3. Fill:
   - Jenis Survey: Select from dropdown
   - Kode Pertanyaan: `q01`
   - Pertanyaan: `Bagaimana kemampuan komunikasi?`
   - Urutan: `1`
   - Bobot: `1.5` (can be different per question)
   - Is Active: ✓
4. Save

### 3. Done!
The system will automatically:
- Show questions in the form
- Calculate weighted scores
- Generate reports

## 📊 Current Status

### ✅ Completed (60%)
- Core system setup
- Survey system (dynamic)
- API SIMPEG integration
- UI/UX customization
- Documentation

### 📝 TODO (40%)
- Survey input form (Tambah Penilaian)
- List view (Daftar Penilaian)
- Report view (Laporan Hasil)
- Export functionality (Excel/PDF)

## 🎨 Design System

### Colors
- **Primary**: Emerald (#059669) → Teal (#0d9488) → Cyan (#0891b2)
- **Sidebar**: Green-teal gradient
- **Header**: Solid gradient background

### Icons
- **Survey**: fa-poll-h (with pulse)
- **Features**: clipboard-list, chart-pie, users
- **Background**: Animated survey-themed icons

### Animations
- **Preloader**: Heartbeat/EKG line
- **Cards**: Floating animation
- **Icons**: Pulse animation

## 🔐 Security

- Session-based authentication
- Password hashing (Argon2)
- CSRF protection
- Session timeout (30 minutes)
- Permission-based access control

## 📈 Performance

- Redis for session & cache
- Static files compression (Whitenoise)
- Database indexes on key fields
- Optimized queries with select_related

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
docker exec survey_pemda_python_app python manage.py migrate
```

## 📞 Support

For detailed documentation, check the `docs/` folder:
- Architecture: `docs/SURVEY_SYSTEM_OVERVIEW.md`
- Seeding: `docs/database/SEEDING_GUIDE_SURVEY.md`
- Menu Guide: `docs/MENU_SURVEY_GUIDE.md`
- Status: `docs/PROJECT_STATUS.md`

## 📝 License

Internal use only.

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-10  
**Status**: Development - Core System Ready ✓
