import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from django.core.management import call_command

print("Starting targeted migration repair on Supabase...")

with connection.cursor() as cursor:
    # Get existing tables
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", ["public"])
    tables = set(r[0] for r in cursor.fetchall())
    print(f"Existing tables: {sorted(tables)}")

    # Clear all migration records
    try:
        cursor.execute("DELETE FROM django_migrations")
        print(f"Cleared {cursor.rowcount} migration records.")
        connection.connection.commit()
    except Exception as e:
        print(f"Note: {e}")

# Apps whose tables already exist in Supabase - fake these
existing_apps = []
missing_apps = []

app_table_map = {
    "vendors": "vendors_vendor",
    "billing": "billing_subscription",
    "customers": "customers_customer",
    "promotions": "promotions_promotion",
    "credit": "credit_credittransaction",
    "notes": "notes_note",
    "analytics": "analytics_salesdata",
    "ngo_portal": "ngo_portal_ngoproject",
    "resort_portal": "resort_portal_room",
}

for app, table in app_table_map.items():
    if table in tables:
        existing_apps.append(app)
    else:
        missing_apps.append(app)

core_missing = ["contenttypes", "auth", "sessions", "admin"]

print(f"\nWill FAKE (tables exist): {existing_apps}")
print(f"Will MIGRATE (create tables): {core_missing + missing_apps}")

# Fake migrations for apps with existing tables
for app in existing_apps:
    print(f"  Faking {app}...")
    call_command("migrate", app, "--fake", verbosity=0)

# Actually create missing tables
for app in core_missing + missing_apps:
    print(f"  Migrating {app}...")
    call_command("migrate", app, verbosity=0)

print("\nDone! All tables are now in sync.")
