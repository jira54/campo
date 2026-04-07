import os
import django
import sys
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def repair():
    """Surgically fix the production Postgres database from migration corruption."""
    print("🚀 Starting surgical production DB repair...")
    
    with connection.cursor() as cursor:
        # Step 1: Check existing tables
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Current tables: {len(tables)}")

        # Step 2: Surgical Drops
        # We drop the core Django metadata tables that have schema mismatches.
        # These tables do NOT contain business data.
        core_tables = [
            'django_admin_log',
            'auth_permission',
            'django_content_type',
            'django_session'
        ]
        
        print("\n🏥 Dropping corrupted core metadata tables...")
        for table in core_tables:
            if table in tables:
                print(f"  Dropping {table}...")
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        # Step 3: Clear Migration History for core apps
        core_apps = ['admin', 'auth', 'contenttypes', 'sessions']
        print("\n🧹 Cleaning migration records for core apps...")
        cursor.execute(
            "DELETE FROM django_migrations WHERE app IN %s",
            [tuple(core_apps)]
        )
        print(f"  Cleared migration records for: {', '.join(core_apps)}")

        # Step 4: Handle Vendors app - the core of the inconsistent migration history
        # If 'vendors' table exists, we must fake the initial migration to avoid "already exists" error
        if 'vendors_vendor' in tables:
            print("\n🔍 Vendors table found. Ensuring migrations are synced correctly...")
            # Delete any 'vendors' records first so we can re-apply cleanly
            cursor.execute("DELETE FROM django_migrations WHERE app = 'vendors'")
            print("  Cleared vendors migration history to allow fresh faking.")

        connection.commit()
        print("\n✅ Surgical DB cleanup complete.")

    # Step 5: Run fresh migrations
    print("\n📦 Running django migrations (fake-initial)...")
    from django.core.management import call_command
    try:
        # First fake the vendors migration since the table exists
        call_command('migrate', 'vendors', '--fake')
        print("  Faked vendors migration.")
        
        # Then migrate everything else
        call_command('migrate', '--fake-initial')
        print("\n🚀 ALL MIGRATIONS APPLIED SUCCESSFULLY.")
    except Exception as e:
        print(f"\n❌ Migration Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    repair()
