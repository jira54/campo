import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def inspect_db():
    with connection.cursor() as cursor:
        # Check tables
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")

        # Check migrations
        cursor.execute("SELECT app, name, applied FROM django_migrations")
        migrations = cursor.fetchall()
        print("\nApplied Migrations:")
        for m in migrations:
            print(f"  {m[0]}.{m[1]} ({m[2]})")

        # Check contenttypes schema
        if 'django_content_type' in tables:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'django_content_type'")
            cols = [row[0] for row in cursor.fetchall()]
            print(f"\ndjango_content_type columns: {cols}")

if __name__ == "__main__":
    inspect_db()
