"""
WSGI config for config project.
"""
import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

# Auto-migrate on startup for Render free tier
try:
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    if plan:
        from django.core import management
        management.call_command('migrate', '--noinput', verbosity=0)
        print("✓ Migrations applied successfully")
except Exception as e:
    print(f"✗ Migration error: {e}")

application = get_wsgi_application()