#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor

# Create admin user
try:
    user = Vendor.objects.create_user(
        email='admin@campo.com',
        business_name='Admin',
        owner_name='Admin',
        phone_number='1234567890',
        password='admin123'
    )
    print(f"✓ Created user: {user.email}")
    print("Login details:")
    print("Email: admin@campo.com")
    print("Password: admin123")
except Exception as e:
    print(f"Error: {e}")
