#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor
from billing.models import Subscription
from django.utils import timezone
from datetime import timedelta

# Create new user with simple password
email = 'admin@campopawa.com'
password = 'admin123'

print(f"Creating user: {email}")

# Create user
vendor = Vendor.objects.create_user(
    email=email,
    business_name='CampoPawa Admin',
    owner_name='Admin User',
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

print(f"✅ User created successfully!")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   ID: {vendor.id}")
