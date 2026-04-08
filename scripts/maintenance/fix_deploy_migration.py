#!/usr/bin/env python
import os
import django
from django.db import connection
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_contenttypes_migration():
    """Fix the contenttypes.0002 migration issue by marking it as applied"""
    with connection.cursor() as cursor:
        # Check if the migration is already applied
        cursor.execute("""
            SELECT COUNT(*) FROM django_migrations 
            WHERE app = 'contenttypes' AND name = '0002_remove_content_type_name'
        """)
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Mark the migration as applied with proper timestamp
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('contenttypes', '0002_remove_content_type_name', %s)
            """, [timezone.now()])
            print("Marked contenttypes.0002_remove_content_type_name as applied")
        else:
            print("contenttypes.0002_remove_content_type_name already marked as applied")

if __name__ == '__main__':
    fix_contenttypes_migration()
