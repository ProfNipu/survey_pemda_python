# 📝 Changelog - Survey Pemda Python

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-03-11

### Changed
- **BREAKING**: Disabled `/admin/` route - now redirects to `/dashboard/`
- All menu items now point to custom views instead of Django Admin
- Updated all documentation to reflect the change
- **FIXED**: Enabled `PERMISSIONS_SUPERADMIN_OVERRIDE=True` in `.env` so superadmin can access all features

### Why This Change?
- Custom views provide better UX and consistent design with the rest of the application
- Django Admin is kept as backup but not exposed to users
- All CRUD operations now use Tailwind CSS styled forms with HTMX
- Superadmin override allows superadmin to access all features without explicit permission assignment

### Migration Guide
If you were using `/admin/` URLs, update them:

**Old URLs (Django Admin)**:
- ❌ `/admin/survey_jpt/jenissurvey/` 
- ❌ `/admin/survey_jpt/pertanyaansurvey/`

**New URLs (Custom Views)**:
- ✅ `/survey/jenis-survey/`
- ✅ `/survey/pertanyaan-survey/`

### Files Modified
- `core/urls.py` - Disabled admin route, added redirect
- `.env` - Added `PERMISSIONS_SUPERADMIN_OVERRIDE=True`
- `docs_dari_sonnet/00_INDEX.md` - Updated access information
- `docs_dari_sonnet/01_QUICK_START.md` - Updated URLs
- `docs_dari_sonnet/07_PROJECT_STATUS.md` - Updated access section
- `docs_dari_sonnet/SUMMARY.md` - Added changelog
- `docs_dari_sonnet/08_CHANGELOG.md` - Created this file

---

## [1.0.0] - 2026-03-10

### Added
- ✅ Initial project setup from `dasar-python` template
- ✅ Docker configuration (port 8006, MySQL, Redis DB 4)
- ✅ Custom landing page with survey theme
- ✅ Preloader with heartbeat/EKG animation
- ✅ Dashboard redesigned for survey system
- ✅ Sidebar with green-teal gradient (emerald → teal → cyan)
- ✅ Dynamic survey system (4 models)
  - `JenisSurvey` - Master survey types
  - `PertanyaanSurvey` - Questions per survey type
  - `RespondenSurvey` - Respondent data
  - `JawabanSurvey` - Answers with weighted scoring
- ✅ API SIMPEG integration
  - `PegawaiDataSementara` model
  - Reusable datatable with django-tables2
- ✅ Complete CRUD system for survey management
  - Jenis Survey (list, create, edit, delete)
  - Pertanyaan Survey (list, create, edit, delete)
- ✅ Permission system (8 permission rules)
- ✅ Menu structure (7 menu items)
- ✅ Seeding commands
  - `seed_survey_jpt` - Seed JPT survey + 7 questions
  - `seed_survey_permissions` - Seed 8 permission rules
  - `seed_survey_menu` - Seed menu structure
- ✅ Comprehensive documentation (10 files)
  - Quick Start Guide
  - README
  - Seeding Guide
  - Menu Guide
  - System Overview
  - System Diagrams
  - Project Status
  - Index
  - Summary
  - Changelog (this file)

### Technical Stack
- **Backend**: Django 5.2.7
- **Database**: MySQL 8.4.6
- **Cache**: Redis 7.x (DB 4)
- **Frontend**: Tailwind CSS 3.x
- **Icons**: Font Awesome 6.x
- **Tables**: django-tables2
- **HTMX**: For dynamic interactions
- **SweetAlert2**: For notifications
- **Container**: Docker + Docker Compose

### Design Decisions
1. **Custom Views over Django Admin**
   - Better UX for end users
   - Consistent design with Tailwind CSS
   - HTMX integration for smooth interactions
   - Permission-based access control

2. **Dynamic Survey System**
   - Add new survey types without code changes
   - Configurable questions per survey type
   - Weighted scoring system
   - Flexible and scalable

3. **Documentation First**
   - Complete documentation created alongside code
   - Step-by-step guides for users and developers
   - Visual diagrams for architecture
   - Organized in dedicated folder

### Known Issues
- None at the moment ✓

---

## [Unreleased]

### TODO - Priority 1: Survey Input Form
- [ ] Create form for input penilaian (Tambah Penilaian)
  - [ ] Select pegawai yang dinilai
  - [ ] Dynamic form based on jenis survey
  - [ ] Validation (nilai 1-5)
  - [ ] Save to survey_responden & survey_jawaban
- [ ] Create list view (Daftar Penilaian)
  - [ ] Filter by pegawai, periode, status
  - [ ] Pagination
  - [ ] Edit/delete actions
- [ ] Create detail view
  - [ ] Show all jawaban
  - [ ] Show calculated score
  - [ ] Print/export option

### TODO - Priority 2: Reporting & Analytics
- [ ] Create report view (Laporan Hasil)
  - [ ] Filter by pegawai, periode, jenis survey
  - [ ] Charts (Chart.js)
  - [ ] Statistics (avg, min, max)
  - [ ] Comparison view
- [ ] Export functionality
  - [ ] Export to Excel
  - [ ] Export to PDF
  - [ ] Email report

### TODO - Priority 3: Advanced Features
- [ ] Multi-rater support (360 degree)
  - [ ] Atasan, rekan, bawahan, self
  - [ ] Aggregate scores
- [ ] Workflow management
  - [ ] Draft → Submitted → Approved
  - [ ] Notification system
- [ ] API endpoints (REST)
  - [ ] GET /api/survey/jenis/
  - [ ] GET /api/survey/pertanyaan/{jenis_id}/
  - [ ] POST /api/survey/penilaian/
  - [ ] GET /api/survey/laporan/

### TODO - Priority 4: Integration
- [ ] Import pegawai from BKPSDM
  - [ ] Command: import_pegawai_from_bkpsdm
  - [ ] Sync schedule (cron)
- [ ] Integration with SIASN (optional)
  - [ ] Fetch pegawai data
  - [ ] Update pegawai info

---

## Version History Summary

| Version | Date | Status | Completion |
|---------|------|--------|------------|
| 1.0.1 | 2026-03-11 | Current | 60% |
| 1.0.0 | 2026-03-10 | Released | 60% |

---

## How to Read This Changelog

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

---

**Last Updated**: 2026-03-11  
**Maintained By**: Claude Sonnet  
**Project**: Survey Pemda Python
