"""
One-shot script to fix production Postgres django_migrations table.
Run this locally while flyctl proxy 15432:5432 --app campo-postgres is active.

Usage:
  $env:DATABASE_URL="postgres://postgres:<PASSWORD>@localhost:15432/campo"
  python fix_prod_db.py
"""
import os
import sys

# Use the proxied DB URL
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("ERROR: Set DATABASE_URL env var first")
    sys.exit(1)

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(db_url)
conn.autocommit = False
cur = conn.cursor(cursor_factory=RealDictCursor)

print("=== Current django_migrations for admin/auth/contenttypes/vendors ===")
cur.execute("""
    SELECT id, app, name FROM django_migrations
    WHERE app IN ('admin', 'auth', 'contenttypes', 'vendors')
    ORDER BY app, id
""")
rows = cur.fetchall()
for r in rows:
    print(f"  [{r['id']}] {r['app']}.{r['name']}")

# Check for the conflict
vendors_exists = any(r['app'] == 'vendors' and r['name'] == '0001_initial' for r in rows)
admin_exists = any(r['app'] == 'admin' and r['name'] == '0001_initial' for r in rows)

print(f"\nvendors.0001_initial in DB: {vendors_exists}")
print(f"admin.0001_initial in DB: {admin_exists}")

if admin_exists and not vendors_exists:
    print("\n⚠️  CONFLICT DETECTED. Removing admin/auth/contenttypes from django_migrations...")
    cur.execute("DELETE FROM django_migrations WHERE app IN ('admin', 'auth', 'contenttypes')")
    print(f"✅ Deleted {cur.rowcount} rows. Committing...")
    conn.commit()
    print("✅ Done. Now run: python manage.py migrate --fake-initial")
else:
    print("\n✅ No conflict detected or already fixed.")
    conn.rollback()

cur.close()
conn.close()
