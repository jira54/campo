import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from django.core.management import call_command

print("Starting full migration history reset...")
with connection.cursor() as cursor:
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", ["public"])
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables found: {len(tables)}")

    # Wipe the entire migration history - we will re-fake everything
    cursor.execute("DELETE FROM django_migrations")
    count = cursor.rowcount
    print(f"Cleared {count} migration records.")
    connection.connection.commit()

print("Re-applying all migrations with --fake-initial...")
call_command("migrate", "--fake-initial", verbosity=1)
print("Done.")
