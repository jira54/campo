"""
Custom management command to fix InconsistentMigrationHistory on Fly.io.

The production Postgres DB has admin.0001_initial recorded but vendors.0001_initial
is missing (vendors is as AUTH_USER_MODEL dependency). We fix this by:
1. Faking vendors.0001_initial so Django thinks it's already run.
2. Removing admin migrations from history so Django can re-apply them in the right order.
3. Running full migrate which will apply everything cleanly.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix InconsistentMigrationHistory by resetting conflicting migration records'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Checking django_migrations table for conflicts...')

        with connection.cursor() as cursor:
            # Check if vendors.0001_initial exists
            cursor.execute(
                "SELECT COUNT(*) FROM django_migrations WHERE app = %s AND name = %s",
                ['vendors', '0001_initial']
            )
            vendors_exists = cursor.fetchone()[0]

            # Check if admin.0001_initial exists
            cursor.execute(
                "SELECT COUNT(*) FROM django_migrations WHERE app = %s AND name = %s",
                ['admin', '0001_initial']
            )
            admin_exists = cursor.fetchone()[0]

            # Check if contenttypes.0002_remove_content_type_name exists
            cursor.execute(
                "SELECT COUNT(*) FROM django_migrations WHERE app = %s AND name = %s",
                ['contenttypes', '0002_remove_content_type_name']
            )
            contenttypes_exists = cursor.fetchone()[0]

            self.stdout.write(
                f'   vendors.0001_initial in DB: {bool(vendors_exists)}, '
                f'admin.0001_initial in DB: {bool(admin_exists)}, '
                f'contenttypes.0002 in DB: {bool(contenttypes_exists)}'
            )

            # Remove ALL admin, auth, and contenttypes migrations so they re-run in correct order
            if admin_exists or contenttypes_exists:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  Conflict detected: admin/contenttypes recorded before vendors. Fixing...'
                    )
                )
                cursor.execute(
                    "DELETE FROM django_migrations WHERE app IN ('admin', 'auth', 'contenttypes')"
                )
                deleted_count = cursor.rowcount
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Removed {deleted_count} conflicting migration records. '
                        f'Run `migrate` now to reapply cleanly.'
                    )
                )
                
                # Also fake vendors.0001_initial if it doesn't exist
                if not vendors_exists:
                    cursor.execute(
                        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                        ['vendors', '0001_initial']
                    )
                    self.stdout.write(
                        self.style.SUCCESS('✅ Faked vendors.0001_initial migration.')
                    )
            else:
                self.stdout.write(self.style.SUCCESS('✅ No conflicts detected.'))
