# Create Database Guide - survey_pemda_python_db

## Overview
Panduan membuat database `survey_pemda_python_db` di MySQL untuk aplikasi Survey Pemda Python.

## Database Configuration

### Database Details
- **Name**: `survey_pemda_python_db`
- **Character Set**: `utf8mb4`
- **Collation**: `utf8mb4_unicode_ci`
- **MySQL Host**: `mysql-main` (Docker container)
- **MySQL Port**: `3306`
- **MySQL User**: `root`
- **MySQL Password**: `5406@Pessel!23#`

## Create Database Commands

### Local Environment

#### Option 1: Via Docker Exec (Recommended)
```bash
docker exec mysql-main mysql -uroot -p'5406@Pessel!23#' -e "CREATE DATABASE IF NOT EXISTS survey_pemda_python_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

#### Option 2: Via MySQL Client
```bash
docker exec -it mysql-main mysql -uroot -p'5406@Pessel!23#'
```

Then run:
```sql
CREATE DATABASE IF NOT EXISTS survey_pemda_python_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

SHOW DATABASES;
USE survey_pemda_python_db;
```

### VPS Environment (172.16.30.139)

#### Via SSH + Docker Exec
```bash
ssh root@172.16.30.139 'docker exec mysql-main mysql -uroot -p"5406@Pessel!23#" -e "CREATE DATABASE IF NOT EXISTS survey_pemda_python_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
```

#### Verify Database Created
```bash
ssh root@172.16.30.139 'docker exec mysql-main mysql -uroot -p"5406@Pessel!23#" -e "SHOW DATABASES LIKE \"survey_pemda_python_db\";"'
```

## Run Migrations

### Local Environment

#### Option 1: Via Docker Exec
```bash
docker exec survey_pemda_python_app python manage.py migrate --noinput
```

#### Option 2: Via Docker Compose
```bash
cd projects/survey_pemda_python
docker-compose exec app python manage.py migrate --noinput
```

### VPS Environment

#### Via SSH + Docker Exec
```bash
ssh root@172.16.30.139 "docker exec survey-pemda-python python manage.py migrate --noinput"
```

## Verify Migration

### Check Tables Created
```bash
# Local
docker exec mysql-main mysql -uroot -p'5406@Pessel!23#' -e "USE survey_pemda_python_db; SHOW TABLES;"

# VPS
ssh root@172.16.30.139 'docker exec mysql-main mysql -uroot -p"5406@Pessel!23#" -e "USE survey_pemda_python_db; SHOW TABLES;"'
```

### Check Migration Status
```bash
# Local
docker exec survey_pemda_python_app python manage.py showmigrations

# VPS
ssh root@172.16.30.139 "docker exec survey-pemda-python python manage.py showmigrations"
```

## Import Database from Local to VPS

### Step 1: Export from Local
```bash
docker exec mysql-main mysqldump -uroot -p'5406@Pessel!23#' \
  --single-transaction --quick --lock-tables=false \
  survey_pemda_python_db > /tmp/survey_pemda_python_db_backup.sql
```

### Step 2: Transfer to VPS
```bash
scp /tmp/survey_pemda_python_db_backup.sql root@172.16.30.139:/tmp/
```

### Step 3: Import to VPS
```bash
ssh root@172.16.30.139 'docker exec -i mysql-main mysql -uroot -p"5406@Pessel!23#" survey_pemda_python_db < /tmp/survey_pemda_python_db_backup.sql'
```

## Troubleshooting

### Database Already Exists Error
If you get "database exists" error, drop and recreate:
```bash
# Local
docker exec mysql-main mysql -uroot -p'5406@Pessel!23#' -e "DROP DATABASE IF EXISTS survey_pemda_python_db; CREATE DATABASE survey_pemda_python_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# VPS
ssh root@172.16.30.139 'docker exec mysql-main mysql -uroot -p"5406@Pessel!23#" -e "DROP DATABASE IF EXISTS survey_pemda_python_db; CREATE DATABASE survey_pemda_python_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
```

### Container Cannot Connect to Database
Check if MySQL container is running:
```bash
# Local
docker ps --filter 'name=mysql-main'

# VPS
ssh root@172.16.30.139 "docker ps --filter 'name=mysql-main'"
```

Check network connectivity:
```bash
# Local
docker exec survey_pemda_python_app ping -c 3 mysql-main

# VPS
ssh root@172.16.30.139 "docker exec survey-pemda-python ping -c 3 mysql-main"
```

### Migration Fails
Check Django database settings in `.env`:
```bash
# Local
cat projects/survey_pemda_python/.env | grep DB_

# VPS
ssh root@172.16.30.139 "cat /root/all-projects/projects/survey_pemda_python/.env | grep DB_"
```

Check container logs:
```bash
# Local
docker logs survey_pemda_python_app --tail 50

# VPS
ssh root@172.16.30.139 "docker logs survey-pemda-python --tail 50"
```

## Related Files

### Environment Configuration
- Local: `projects/survey_pemda_python/.env`
- VPS: `/root/all-projects/projects/survey_pemda_python/.env`

### Django Settings
- `projects/survey_pemda_python/core/settings.py`

### Docker Configuration
- `projects/survey_pemda_python/docker-compose.yml`
- `projects/survey_pemda_python/Dockerfile`
- `projects/survey_pemda_python/entrypoint.sh`

## Summary

✅ Database created: `survey_pemda_python_db`
✅ Character set: `utf8mb4` (supports emoji and international characters)
✅ Collation: `utf8mb4_unicode_ci` (case-insensitive, Unicode-aware)
✅ Ready for migrations

## Next Steps

1. ✅ Create database (DONE)
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Run seeders: `python manage.py auto_seed`
5. Test application: http://localhost:8006 (local) or http://172.16.30.139:8006 (VPS)

## Related Documentation
- `RUN_MIGRATION_GUIDE.md` - Migration execution guide
- `90_PEGAWAI_RIWAYAT_DATA_SNAPSHOT.md` - Snapshot system
- `94_VPS_DEPLOYMENT_SUMMARY.md` - VPS deployment status
