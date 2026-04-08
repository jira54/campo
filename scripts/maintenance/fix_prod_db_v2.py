"""
Surgical production DB fix script.
Run while proxy is active: flyctl proxy 15432:5432 --app campo-postgres

The issue: django_content_type table has old schema (no app_label column),
and django_migrations has no records for contenttypes/auth/admin/vendors.
Solution: Drop the old contenttypes table so migrate can recreate it cleanly,
and fake all other existing tables.

Usage:
  $env:DATABASE_URL="postgres://postgres:<PASSWORD>@localhost:15432/campo"
  python fix_prod_db_v2.py
"""
import os, sys
import psycopg2
from psycopg2.extras import RealDictCursor

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("ERROR: Set DATABASE_URL env var pointing to localhost:15432")
    sys.exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = False
cur = conn.cursor(cursor_factory=RealDictCursor)

print("=== Step 1: Check existing tables ===")
cur.execute("""
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename
""")
tables = [r['tablename'] for r in cur.fetchall()]
print("Existing tables:", tables)

print("\n=== Step 2: Check django_content_type columns ===")
if 'django_content_type' in tables:
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'django_content_type'
        ORDER BY ordinal_position
    """)
    cols = [r['column_name'] for r in cur.fetchall()]
    print("django_content_type columns:", cols)

    if 'app_label' not in cols:
        print("\n⚠️  OLD SCHEMA DETECTED. Dropping django_content_type for recreation...")
        cur.execute("DROP TABLE django_content_type CASCADE")
        print("✅ Dropped django_content_type")

print("\n=== Step 3: Check django_migrations ===")
cur.execute("SELECT app, name FROM django_migrations ORDER BY app, id")
rows = cur.fetchall()
print(f"Total migration records: {len(rows)}")
for r in rows:
    print(f"  {r['app']}.{r['name']}")

conn.commit()
print("\n✅ Done. Now run: python manage.py migrate --fake-initial")
cur.close()
conn.close()
