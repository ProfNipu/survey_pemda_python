# Documentation Index

Daftar lengkap semua dokumentasi di project ini, diurutkan berdasarkan kategori dan nomor.

---

## 📋 Quick Links

- [Quick Start Guide](./QUICK-START.md) - Panduan cepat setelah restart
- [Scripts Documentation](./SCRIPTS_DOCUMENTATION.md) - Dokumentasi lengkap scripts
- [Test Scripts Collection](./TEST_SCRIPTS_COLLECTION.md) - Kumpulan test scripts

---

## 🔧 Scripts & Utilities

| No | File | Description |
|----|------|-------------|
| - | [sh_dari_sonnet/fix-docker-network.sh](./sh_dari_sonnet/fix-docker-network.sh) | Auto-fix Docker network |
| - | [sh_dari_sonnet/README.md](./sh_dari_sonnet/README.md) | Dokumentasi script |
| - | [SCRIPTS_DOCUMENTATION.md](./SCRIPTS_DOCUMENTATION.md) | Dokumentasi lengkap |
| - | [TEST_SCRIPTS_COLLECTION.md](./TEST_SCRIPTS_COLLECTION.md) | Test scripts (archived) |

**Note**: Script original (deploy, sync, backup) tetap di `../../scripts/`

---

## 🐛 Bug Fixes & Troubleshooting

| No | File | Description |
|----|------|-------------|
| 98 | [98_VPS_LOGIN_VIA_API_SUCCESS.md](./98_VPS_LOGIN_VIA_API_SUCCESS.md) | VPS login via ESIMPEG API (Host header fix) |
| 97 | [97_VPS_DOCKER_NETWORK_FIX.md](./97_VPS_DOCKER_NETWORK_FIX.md) | VPS Docker network fix (Survey ↔ ESIMPEG) |
| 96 | [96_SIASN_IP_WHITELIST_ISSUE.md](../../ESIMPEG-Python/docs_dari_sonnet/96_SIASN_IP_WHITELIST_ISSUE.md) | SIASN IP whitelist issue (VPS) |
| 95 | [95_CREATE_DATABASE_GUIDE.md](./95_CREATE_DATABASE_GUIDE.md) | Database creation guide (local & VPS) |
| 94 | [94_VPS_DEPLOYMENT_SUMMARY.md](../../ESIMPEG-Python/docs_dari_sonnet/94_VPS_DEPLOYMENT_SUMMARY.md) | VPS deployment with database import |
| 93 | [93_VPS_CSRF_FIX_SUMMARY.md](../../ESIMPEG-Python/docs_dari_sonnet/93_VPS_CSRF_FIX_SUMMARY.md) | VPS CSRF configuration |
| 92 | [92_LOGIN_CSRF_FIX_SUMMARY.md](../../ESIMPEG-Python/docs_dari_sonnet/92_LOGIN_CSRF_FIX_SUMMARY.md) | Login CSRF fix |
| 91 | [91_FIX_LOGIN_403_CSRF_ISSUE.md](../../ESIMPEG-Python/docs_dari_sonnet/91_FIX_LOGIN_403_CSRF_ISSUE.md) | Fix 403 CSRF error |
| 90 | [90_PEGAWAI_RIWAYAT_DATA_SNAPSHOT.md](./90_PEGAWAI_RIWAYAT_DATA_SNAPSHOT.md) | Pegawai snapshot system untuk survey |
| 89 | [89_FIX_DISALLOWED_HOST_AFTER_RESTART.md](./89_FIX_DISALLOWED_HOST_AFTER_RESTART.md) | Fix DisallowedHost error setelah restart |
| 88 | [88_FIX_PASSWORD_CHANGE_COMPLETE.md](./88_FIX_PASSWORD_CHANGE_COMPLETE.md) | Fix password change functionality |
| 87 | [87_FIX_LARAVEL_PASSWORD_HASH.md](../../ESIMPEG-Python/docs_dari_sonnet/87_FIX_LARAVEL_PASSWORD_HASH.md) | Fix Laravel password hash compatibility |
| 86 | [86_LOGIN_VIA_ESIMPEG_API_SUCCESS.md](./86_LOGIN_VIA_ESIMPEG_API_SUCCESS.md) | Login via ESIMPEG API berhasil |
| 85 | [85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md](./85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md) | Authentication backend setup |
| 84 | [84_LOGIN_VIA_ESIMPEG_DATABASE.md](./84_LOGIN_VIA_ESIMPEG_DATABASE.md) | Login via ESIMPEG database |
| 83 | [83_IMPORT_USERS_FROM_LARAVEL.md](../../ESIMPEG-Python/docs_dari_sonnet/83_IMPORT_USERS_FROM_LARAVEL.md) | Import users dari Laravel |
| 82 | [82_FINAL_ORDERING_VERIFICATION.md](./82_FINAL_ORDERING_VERIFICATION.md) | Verifikasi ordering final |
| 81 | [81_FINAL_FIELD_RENAME_AND_KATEGORI_PEGAWAI.md](./81_FINAL_FIELD_RENAME_AND_KATEGORI_PEGAWAI.md) | Rename field dan kategori pegawai |
| 80 | [80_ORDERING_STATUS_AND_RESYNC_NEEDED.md](./80_ORDERING_STATUS_AND_RESYNC_NEEDED.md) | Status ordering dan resync |

---

## 🔐 Authentication & Security

| No | File | Description |
|----|------|-------------|
| 88 | [88_FIX_PASSWORD_CHANGE_COMPLETE.md](./88_FIX_PASSWORD_CHANGE_COMPLETE.md) | Password change fix |
| 87 | [87_FIX_LARAVEL_PASSWORD_HASH.md](../../ESIMPEG-Python/docs_dari_sonnet/87_FIX_LARAVEL_PASSWORD_HASH.md) | Laravel password hash |
| 86 | [86_LOGIN_VIA_ESIMPEG_API_SUCCESS.md](./86_LOGIN_VIA_ESIMPEG_API_SUCCESS.md) | Login via API |
| 85 | [85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md](./85_LOGIN_VIA_ESIMPEG_API_FALLBACK.md) | Auth backend |
| 49 | [49_USER_ID_OPD_SYNC.md](./49_USER_ID_OPD_SYNC.md) | User ID OPD sync |
| 48 | [48_LOGIN_API_USER_ID_OPD.md](../../ESIMPEG-Python/docs_dari_sonnet/48_LOGIN_API_USER_ID_OPD.md) | Login API user ID OPD |

---

## 🔄 Data Sync & Integration

| No | File | Description |
|----|------|-------------|
| 79-76 | Pegawai Sync Series | Complete pegawai sync documentation |
| 75 | [75_ADD_TABLE_SORTING.md](./75_ADD_TABLE_SORTING.md) | Add table sorting |
| 74 | [74_COMPLETE_USER_JOURNEY_PEGAWAI_SYNC.md](./74_COMPLETE_USER_JOURNEY_PEGAWAI_SYNC.md) | User journey pegawai sync |
| 73 | [73_FINAL_SUMMARY_PEGAWAI_SYNC_COMPLETE.md](./73_FINAL_SUMMARY_PEGAWAI_SYNC_COMPLETE.md) | Final summary pegawai sync |
| 72 | [72_REFRESH_DATATABLE_NO_RELOAD.md](./72_REFRESH_DATATABLE_NO_RELOAD.md) | Refresh datatable tanpa reload |
| 71 | [71_FIX_PROGRESS_BAR_ASYNC.md](./71_FIX_PROGRESS_BAR_ASYNC.md) | Fix progress bar async |
| 70 | [70_FINAL_STATUS_PROGRESS_BAR.md](./70_FINAL_STATUS_PROGRESS_BAR.md) | Final status progress bar |
| 69 | [69_PROGRESS_BAR_SYNC_PEGAWAI.md](./69_PROGRESS_BAR_SYNC_PEGAWAI.md) | Progress bar sync pegawai |
| 68 | [68_PEGAWAI_SYNC_MANUAL_TO_DATABASE.md](./68_PEGAWAI_SYNC_MANUAL_TO_DATABASE.md) | Pegawai sync manual to database |
| 67 | [67_FIX_PAGINATION_PEGAWAI_TABLE.md](./67_FIX_PAGINATION_PEGAWAI_TABLE.md) | Fix pagination pegawai table |

---

## 🌐 API & Network

| No | File | Description |
|----|------|-------------|
| 89 | [89_FIX_DISALLOWED_HOST_AFTER_RESTART.md](./89_FIX_DISALLOWED_HOST_AFTER_RESTART.md) | Fix DisallowedHost |
| 66 | [66_FINAL_ESIMPEG_INTEGRATION_COMPLETE.md](./66_FINAL_ESIMPEG_INTEGRATION_COMPLETE.md) | ESIMPEG integration complete |
| 65 | [65_FINAL_STATUS_API_CONNECTION.md](./65_FINAL_STATUS_API_CONNECTION.md) | Final status API connection |
| 64 | [64_FIX_DISALLOWED_HOST_FINAL.md](./64_FIX_DISALLOWED_HOST_FINAL.md) | Fix DisallowedHost final |
| 62 | [62_CARA_KERJA_API_TOKEN_FLOW.md](./62_CARA_KERJA_API_TOKEN_FLOW.md) | Cara kerja API token flow |
| 60 | [60_FIX_ESIMPEG_API_CONNECTION.md](./60_FIX_ESIMPEG_API_CONNECTION.md) | Fix ESIMPEG API connection |

---

## 🎨 UI & Frontend

| No | File | Description |
|----|------|-------------|
| 75 | [75_ADD_TABLE_SORTING.md](./75_ADD_TABLE_SORTING.md) | Add table sorting |
| 59 | [59_PEGAWAI_DATATABLE_FORMAT.md](./59_PEGAWAI_DATATABLE_FORMAT.md) | Pegawai datatable format |
| 58 | [58_FIX_TAILWIND_CSS.md](./58_FIX_TAILWIND_CSS.md) | Fix Tailwind CSS |
| 57 | [57_FINAL_SUMMARY_PEGAWAI_LIST.md](./57_FINAL_SUMMARY_PEGAWAI_LIST.md) | Final summary pegawai list |

---

## 🔑 Password Management

| No | File | Description |
|----|------|-------------|
| 88 | [88_FIX_PASSWORD_CHANGE_COMPLETE.md](./88_FIX_PASSWORD_CHANGE_COMPLETE.md) | Password change fix |
| 43 | [43_SESSION_SUMMARY_PASSWORD_SYNC.md](./43_SESSION_SUMMARY_PASSWORD_SYNC.md) | Session summary password sync |
| 41 | [41_PASSWORD_SYNC_KESIMPULAN.md](./41_PASSWORD_SYNC_KESIMPULAN.md) | Password sync kesimpulan |
| 40 | [40_PASSWORD_SYNC_VISUAL_GUIDE.md](./40_PASSWORD_SYNC_VISUAL_GUIDE.md) | Password sync visual guide |
| 39 | [39_PASSWORD_SYNC_EXPLAINED.md](./39_PASSWORD_SYNC_EXPLAINED.md) | Password sync explained |
| 38 | [38_PASSWORD_SYNC_SETUP.md](./38_PASSWORD_SYNC_SETUP.md) | Password sync setup |

---

## � Setup & Deployment

| No | File | Description |
|----|------|-------------|
| 52 | [52_API_SIMPEG_PEGAWAI_SETUP.md](./52_API_SIMPEG_PEGAWAI_SETUP.md) | API SIMPEG pegawai setup |
| 37 | [37_SESSION_SUMMARY_ESIMPEG_INTEGRATION.md](./37_SESSION_SUMMARY_ESIMPEG_INTEGRATION.md) | Session summary ESIMPEG integration |
| 36 | [36_DEPLOY_VPS_GUIDE.md](./36_DEPLOY_VPS_GUIDE.md) | Deploy VPS guide |
| 35 | [35_TROUBLESHOOTING_API_CONNECTION.md](./35_TROUBLESHOOTING_API_CONNECTION.md) | Troubleshooting API connection |
| 03 | [03_SEEDING_GUIDE_SURVEY.md](./03_SEEDING_GUIDE_SURVEY.md) | Seeding guide survey |

---

## 📝 Summary Documents

| File | Description |
|------|-------------|
| [SUMMARY_COMPLETE_PEGAWAI_SYNC.md](./SUMMARY_COMPLETE_PEGAWAI_SYNC.md) | Complete pegawai sync summary |
| [SUMMARY_ESELON_UPDATE.md](./SUMMARY_ESELON_UPDATE.md) | Eselon update summary |
| [QUICK_REFERENCE_PEGAWAI_SYNC.md](./QUICK_REFERENCE_PEGAWAI_SYNC.md) | Quick reference pegawai sync |
| [QUICK_FIX_PRAKOM_USER.md](./QUICK_FIX_PRAKOM_USER.md) | Quick fix prakom user |

---

## 🔍 How to Use This Index

1. **By Category**: Lihat section yang sesuai dengan topik yang dicari
2. **By Number**: Dokumentasi diurutkan berdasarkan nomor (terbaru di atas)
3. **By Problem**: Cari di section Bug Fixes & Troubleshooting
4. **By Feature**: Cari di section yang relevan (Auth, Sync, UI, dll)

---

## 📚 External Documentation

- **ESIMPEG Python**: `projects/ESIMPEG-Python/docs_dari_sonnet/`
- **Scripts**: `scripts/README.md`
- **Quick Start**: `QUICK-START.md` (root)

---

## 🆕 Latest Updates

| Date | Doc | Description |
|------|-----|-------------|
| 2026-04-07 | 98 | VPS login via ESIMPEG API (Host header fix) |
| 2026-04-07 | 97 | VPS Docker network fix (Survey ↔ ESIMPEG connection) |
| 2026-04-07 | 96 | SIASN IP whitelist issue (103.143.152.98) |
| 2026-04-06 | 89 | Fix DisallowedHost after restart (auto-fix script) |
| 2026-04-06 | 88 | Fix password change functionality |
| 2026-04-06 | SCRIPTS_DOCUMENTATION | Complete scripts documentation |
| 2026-04-06 | TEST_SCRIPTS_COLLECTION | Archive all test scripts |

---

**Last Updated**: 2026-04-06
