"""
Data migration to migrate existing PINs from Vendor model to ManagerAuth model.
"""

from django.db import migrations
from django.contrib.auth.hashers import make_password


def migrate_pins_forward(apps, schema_editor):
    """Migrate PINs from Vendor to ManagerAuth."""
    Vendor = apps.get_model('vendors', 'Vendor')
    ManagerAuth = apps.get_model('resort_portal', 'ManagerAuth')
    
    migrated = 0
    skipped = 0
    
    for vendor in Vendor.objects.filter(resort_manager_pin__isnull=False).exclude(resort_manager_pin=''):
        try:
            manager_auth = ManagerAuth.objects.get(vendor=vendor)
            
            # Copy PIN if target is empty
            if not manager_auth.manager_pin:
                manager_auth.manager_pin = vendor.resort_manager_pin
                manager_auth.save()
                migrated += 1
            else:
                skipped += 1
        except ManagerAuth.DoesNotExist:
            # Manager not set up - skip
            skipped += 1
    
    print(f"\nPIN Migration: Migrated {migrated}, Skipped {skipped}")


def migrate_pins_backward(apps, schema_editor):
    """Reverse migration (clear ManagerAuth PINs)."""
    ManagerAuth = apps.get_model('resort_portal', 'ManagerAuth')
    ManagerAuth.objects.all().update(manager_pin=None, pin_set_at=None)


class Migration(migrations.Migration):
    dependencies = [
        ('resort_portal', '0014_remove_managerauth_failed_attempts_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_pins_forward, migrate_pins_backward),
    ]
