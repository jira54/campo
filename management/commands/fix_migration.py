from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Fix contenttypes migration issue by checking database schema'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if the name column exists in django_content_type table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'django_content_type' AND column_name = 'name'
            """)
            result = cursor.fetchone()
            
            if result:
                self.stdout.write(
                    self.style.WARNING('name column exists in django_content_type table')
                )
                # Mark the migration as applied without running it
                cursor.execute("""
                    INSERT INTO django_migrations (app, name) 
                    VALUES ('contenttypes', '0002_remove_content_type_name')
                    ON CONFLICT (app, name) DO NOTHING
                """)
                self.stdout.write(
                    self.style.SUCCESS('Marked contenttypes.0002_remove_content_type_name as applied')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('name column does not exist - migration should be fine')
                )
        
        # Verify contenttypes table is working
        try:
            content_types = ContentType.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'ContentType table is working correctly ({content_types} entries)')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error accessing ContentType table: {e}')
            )
