# Runtime Setup - survey_pemda_python

## Container utama

- App: `survey_pemda_python_app` (port `8006:8000`)
- MySQL (shared): `mysql-main` (port `3306`)
- Redis (shared): `redis-main` (port `6379`)

## Compose yang dipakai

- `projects/survey_pemda_python/docker-compose.yml`

Jalankan dari folder project:

```bash
docker compose -f docker-compose.yml up -d
```

## Env penting (ringkas)

- MySQL: `DB_HOST=mysql-main`, `DB_NAME=survey_pemda_python_db`
- Redis: `REDIS_HOST=redis-main`, `REDIS_DB=4`

