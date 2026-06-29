"""
Import ALL data from old MySQL database to PostgreSQL using raw SQL
"""
import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import pymysql
pymysql.install_as_MySQLdb()

from django.core.management.base import BaseCommand
from django.db import connection

MYSQL = {
    'host': 'mysql-main',
    'port': 3306,
    'user': 'root',
    'password': '5406@Pessel!23#',
    'database': 'survey_pemda_python_db',
}


def safe(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, str):
        if val in ('0000-00-00', '0000-00-00 00:00:00', ''):
            return None
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='replace')
    return val


def serialize(val, pg_col_type=None):
    v = safe(val)
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, int):
        if pg_col_type == 'boolean':
            return 'TRUE' if v else 'FALSE'
        return str(v)
    if isinstance(v, float):
        return str(v)
    if isinstance(v, datetime):
        return f"'{v.isoformat()}'"
    if isinstance(v, dict):
        return f"'{json.dumps(v, default=str)}'"
    if isinstance(v, (list, tuple)):
        return f"'{json.dumps(v, default=str)}'"
    s = str(v).replace("'", "''")
    return f"'{s}'"


CACHE_COL_TYPES = {}
def get_col_types(cursor, table):
    if table in CACHE_COL_TYPES:
        return CACHE_COL_TYPES[table]
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name=%s", (table,))
    result = {r[0]: r[1] for r in cursor.fetchall()}
    CACHE_COL_TYPES[table] = result
    return result


def table_exists(cursor, table):
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s)",
        (table,)
    )
    return cursor.fetchone()[0]


class Command(BaseCommand):
    help = 'Import all data from MySQL to PostgreSQL via raw SQL'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('📥 Importing data from MySQL to PostgreSQL')
        self.stdout.write('=' * 60)

        mconn = pymysql.connect(**MYSQL)
        mcursor = mconn.cursor(pymysql.cursors.DictCursor)

        mcursor.execute("SHOW TABLES")
        tables = [r[f'Tables_in_{MYSQL["database"]}'] for r in mcursor.fetchall()]

        skip_tables = {'django_migrations', 'django_session', 'django_admin_log'}

        total = 0
        with connection.cursor() as pcursor:
            for table in tables:
                if table in skip_tables:
                    self.stdout.write(f'  ⏭️  {table}: skipped (system table)')
                    continue
                if not table_exists(pcursor, table):
                    self.stdout.write(f'  ⏭️  {table}: table not found in PostgreSQL (skip)')
                    continue

                mcursor.execute(f"SELECT COUNT(*) as cnt FROM `{table}`")
                count = mcursor.fetchone()['cnt']
                if count == 0:
                    self.stdout.write(f'  ⏭️  {table}: 0 rows')
                    continue

                mcursor.execute(f"SELECT * FROM `{table}`")
                rows = mcursor.fetchall()
                if not rows:
                    continue

                col_types = get_col_types(pcursor, table)
                inserted = 0
                for row in rows:
                    cols = []
                    vals = []
                    for k, v in row.items():
                        col_name = k
                        pg_type = col_types.get(col_name, 'text')
                        cols.append(f'"{col_name}"')
                        if pg_type == 'boolean':
                            vals.append('TRUE' if v and v not in (0, '0', False) else 'FALSE')
                        else:
                            vals.append(serialize(v))

                    col_str = ', '.join(cols)
                    val_str = ', '.join(vals)

                    sql = f'INSERT INTO "{table}" ({col_str}) VALUES ({val_str}) ON CONFLICT DO NOTHING;'
                    try:
                        pcursor.execute(sql)
                        if pcursor.rowcount > 0:
                            inserted += 1
                    except Exception as e:
                        self.stdout.write(f'    ⚠️  {table}: row error - {e}')

                total += inserted
                self.stdout.write(f'  ✅ {table}: {inserted}/{count} rows imported')

        mcursor.close()
        mconn.close()
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import complete! Total: {total} rows'))
