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
from django.contrib.auth import authenticate

# Test credentials
email = 'fanueljunior08@gmail.com'
password = 'Admin123!'

print(f"Testing login for: {email}")

# Check if user exists
try:
    user = Vendor.objects.get(email=email)
    print(f"✅ User found: {user.email}")
    print(f"   Active: {user.is_active}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Password check: {user.check_password(password)}")
except Vendor.DoesNotExist:
    print("❌ User not found")
    sys.exit(1)

# Test authentication
auth_user = authenticate(username=email, password=password)
if auth_user:
    print(f"✅ Authentication successful! User ID: {auth_user.id}")
else:
    print("❌ Authentication failed")
    sys.exit(1)
