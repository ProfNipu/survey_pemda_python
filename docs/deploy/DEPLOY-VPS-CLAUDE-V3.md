# Panduan Deploy dasar-python ke VPS (V3)

Dokumen ini adalah versi terbaru yang **match dengan entrypoint baru** (tidak auto `makemigrations`, tidak print credential, dan step migrasi/collectstatic dilakukan secara eksplisit).

Referensi:
- `docs/database/MIGRATE_AUTO_SEED_GUIDE.md`

---

## Prasyarat
- Akses SSH ke VPS
- Docker + Docker Compose sudah terpasang
- `mysql-main` sudah running
- Project di local: `projects/dasar-python/`

Catatan istilah:
- Nama container di `docker-compose.prod.yml` adalah: `dasar-python`
- Port publik default (compose prod): `8007:8000`

---

## TAHAP 1: PREPARATION & UPLOAD

### 1) Stop container lama
```bash
ssh root@<IP_VPS> "cd /root/dasar-python && docker compose -f docker-compose.prod.yml down"
```

### 2) Upload project (rsync)
```bash
rsync -avz --progress --delete \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='staticfiles' \
  --exclude='media' \
  --exclude='.env' \
  --exclude='node_modules' \
  projects/dasar-python/ root@<IP_VPS>:/root/dasar-python/
```

### 3) Rebuild dan start container
```bash
ssh root@<IP_VPS> "cd /root/dasar-python && docker compose -f docker-compose.prod.yml up -d --build"
```

Tunggu sekitar 10-20 detik, lalu cek:
```bash
ssh root@<IP_VPS> "docker ps"
```

---

## TAHAP 2: DATABASE & BOOTSTRAP (URUTAN KRUSIAL)

> **PENTING:** Jalankan `migrate` dulu. Jangan menjalankan import dari Laravel sebelum migrasi selesai.

### 1) Migrasi schema (WAJIB PERTAMA)
```bash
ssh root@<IP_VPS> "docker exec dasar-python python manage.py migrate --noinput"
```

### 2) Seed (DB baru)
Jika database masih kosong dan kamu butuh seed dasar:
```bash
ssh root@<IP_VPS> "docker exec dasar-python python manage.py auto_seed"
ssh root@<IP_VPS> "docker exec dasar-python python manage.py seed_superadmin_full_access"
```

Jika database sudah terisi dan kamu hanya ingin sync permission/core saja:
```bash
ssh root@<IP_VPS> "docker exec dasar-python python manage.py auto_seed --sync --permissions-only"
```

### 3) Collectstatic (jika dibutuhkan)
Jika kamu deploy dengan `whitenoise` dan butuh build static manifest:
```bash
ssh root@<IP_VPS> "docker exec dasar-python python manage.py collectstatic --noinput"
```

---

## TAHAP 3: DATA MIGRATION (SYNC DARI LARAVEL)

Jika kamu memakai import ordered:
```bash
ssh root@<IP_VPS> "docker exec dasar-python python manage.py import_laravel_all_ordered --include-deleted"
```

---

## TAHAP 4: VERIFIKASI

### 1) Health check
```bash
curl -I http://<IP_VPS>:8007/health/
```

### 2) Aplikasi
```bash
curl -I http://<IP_VPS>:8007/
```

---

## Catatan penting tentang entrypoint baru
Entrypoint sekarang **tidak** menjalankan hal-hal berikut secara otomatis:
- `makemigrations`
- `migrate`
- `collectstatic`
- create superuser
- `loaddata`

Semua itu dilakukan manual seperti step di atas, atau jika kamu ingin otomatis via env flag:
- `RUN_MIGRATIONS=1`
- `RUN_COLLECTSTATIC=1`
- `CREATE_SUPERUSER=1`
- `LOAD_INITIAL_DATA=1`
- `CREATE_DB_IF_NOT_EXISTS=1`

✅ **DEPLOYMENT SELESAI & AMAN (V3)**
