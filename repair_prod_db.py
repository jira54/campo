import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from django.core.management import call_command

print("Starting migration repair on Supabase...")
with connection.cursor() as cursor:
    # Check existing tables
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", ["public"])
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables found: {tables}")

    # Check migration records
    try:
        cursor.execute("SELECT COUNT(*) FROM django_migrations")
        count = cursor.fetchone()[0]
        print(f"Existing migration records: {count}")
        if count > 0:
            cursor.execute("DELETE FROM django_migrations")
            print(f"Cleared {cursor.rowcount} migration records.")
            connection.connection.commit()
    except Exception as e:
        print(f"django_migrations issue: {e}")

# Fake ALL migrations since all tables already exist in Supabase
print("Faking all migrations (tables already exist in Supabase)...")
call_command("migrate", "--fake", verbosity=1)
print("Done.")
