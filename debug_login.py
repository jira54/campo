#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate
from django.test import RequestFactory
from vendors.models import Vendor

print("=== Detailed Login Debug ===")

# Test the exact authentication process
email = "fanueljunior08@gmail.com"
password = "admin123"

print(f"Testing authentication for: {email}")

# 1. Check user exists
try:
    user = Vendor.objects.get(email=email)
    print(f"✓ User found: {user.business_name}")
    print(f"  - Active: {user.is_active}")
    print(f"  - Staff: {user.is_staff}")
    print(f"  - Has usable password: {user.has_usable_password()}")
    print(f"  - Password hash: {user.password[:60]}...")
except Vendor.DoesNotExist:
    print("✗ User not found")
    exit()

# 2. Test password verification
password_check = user.check_password(password)
print(f"✓ Password check result: {password_check}")

# 3. Test authenticate function (without request)
auth_result = authenticate(username=email, password=password)
print(f"✓ Authenticate (no request): {auth_result}")

# 4. Test authenticate function (with mock request)
factory = RequestFactory()
request = factory.post('/login/', {'email': email, 'password': password})
auth_result_with_request = authenticate(request=request, username=email, password=password)
print(f"✓ Authenticate (with request): {auth_result_with_request}")

# 5. Check authentication backend
from django.contrib.auth import get_backends
backends = get_backends()
print(f"✓ Available backends: {backends}")

# 6. Manual authentication test
from django.contrib.auth.backends import ModelBackend
backend = ModelBackend()
manual_auth = backend.get_user(user.id) if backend.authenticate(request, username=email, password=password) else None
print(f"✓ Manual backend auth: {manual_auth}")

# 7. Test if there are any issues with the user model
print(f"✓ User class: {user.__class__.__name__}")
print(f"✓ User module: {user.__class__.__module__}")
print(f"✓ Is authenticated: {user.is_authenticated}")
