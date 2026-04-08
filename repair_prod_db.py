import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection
from django.core.management import call_command

print("Starting targeted migration repair...")

with connection.cursor() as cursor:
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", ["public"])
    tables = set(r[0] for r in cursor.fetchall())
    print(f"Tables: {sorted(tables)}")

    # Clear all migration records to start fresh
    cursor.execute("DELETE FROM django_migrations")
    print(f"Cleared {cursor.rowcount} migration records.")

    # Drop ALL tables that might have corrupt schemas, then let migrate recreate everything
    # Keep only the business data tables
    business_tables = {
        "vendors_vendor", "vendors_loginstreak",
        "customers_customer", "customers_purchase", "customers_tag",
        "customers_loyaltyprogram", "customers_receipt", "customers_reminder",
        "customers_service", "customers_customer_tags",
        "billing_subscription", "billing_payment", "billing_tillpayment",
        "credit_credittransaction",
        "notes_note",
        "promotions_promotion",
        "ngo_portal_ngoproject", "ngo_portal_projectmilestone",
        "resort_portal_department", "resort_portal_folio",
        "resort_portal_foliocharge", "resort_portal_resortguest",
        "resort_portal_room",
        "django_migrations",
    }

    for t in sorted(tables):
        if t not in business_tables:
            print(f"  Dropping {t}...")
            cursor.execute(f'DROP TABLE IF EXISTS "{t}" CASCADE')

    # Ensure crucial business columns exist if tables already exist
    if "vendors_vendor" in tables:
        print("  Checking vendors_vendor for new columns...")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'vendors_vendor'")
        existing_columns = {r[0] for r in cursor.fetchall()}
        
        if "brand_accent_color" not in existing_columns:
            print("    Adding missing column: brand_accent_color")
            cursor.execute("ALTER TABLE vendors_vendor ADD COLUMN brand_accent_color VARCHAR(7) DEFAULT '#F59E0B'")

        if "persona_type" not in existing_columns:
            print("    Adding missing column: persona_type")
            cursor.execute("ALTER TABLE vendors_vendor ADD COLUMN persona_type VARCHAR(20) DEFAULT 'msme'")

        if "logo_url" not in existing_columns:
            print("    Adding missing column: logo_url")
            cursor.execute("ALTER TABLE vendors_vendor ADD COLUMN logo_url VARCHAR(500) DEFAULT ''")

    connection.connection.commit()

print("\nMigrating core contenttypes and auth first to satisfy post_migrate signals...")
call_command("migrate", "contenttypes", verbosity=0)
call_command("migrate", "auth", verbosity=0)

print("\nFaking business app migrations (tables exist)...")
business_apps = ["vendors", "customers", "billing", "credit", "notes", "promotions"]
for app in business_apps:
    call_command("migrate", app, "--fake", verbosity=0)
    print(f"  Faked {app}")

# Check if ngo/resort tables exist
with connection.cursor() as cursor:
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", ["public"])
    current = set(r[0] for r in cursor.fetchall())

if "ngo_portal_ngoproject" in current:
    call_command("migrate", "ngo_portal", "--fake", verbosity=0)
    print("  Faked ngo_portal")

if "resort_portal_room" in current:
    call_command("migrate", "resort_portal", "--fake", verbosity=0)
    print("  Faked resort_portal")

print("\nMigrating everything else (creates missing core tables)...")
call_command("migrate", verbosity=1)
print("\nDone!")
