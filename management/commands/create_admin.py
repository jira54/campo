from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from billing.models import Subscription
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create admin user with specified email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address for the admin user')
        parser.add_argument('--password', type=str, default='Admin123!', help='Password for the admin user')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        
        # Check if user already exists
        if Vendor.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists'))
            return
        
        # Create admin user
        vendor = Vendor.objects.create_user(
            email=email,
            business_name='CampoPawa Admin',
            owner_name='System Admin',
            phone_number='+254712345678',
            password=password
        )
        
        # Make staff and superuser
        vendor.is_staff = True
        vendor.is_superuser = True
        vendor.save()
        
        # Create subscription
        Subscription.objects.create(vendor=vendor, plan='premium')
        
        # Add trial period
        vendor.trial_end_date = timezone.now() + timedelta(days=365)
        vendor.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        self.stdout.write(self.style.SUCCESS('You can now login with these credentials'))
