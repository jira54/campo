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

# Test both users
users_to_test = [
    {'email': 'admin@campopawa.com', 'password': 'admin123'},
    {'email': 'fanueljunior08@gmail.com', 'password': 'Admin123!'}
]

print("Testing login credentials...")
print("=" * 50)

for user_data in users_to_test:
    email = user_data['email']
    password = user_data['password']
    
    print(f"\nTesting: {email}")
    print(f"Password: {password}")
    
    # Check if user exists
    try:
        user = Vendor.objects.get(email=email)
        print(f"✅ User found: {user.email}")
        print(f"   Active: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Password check: {user.check_password(password)}")
        
        # Test authentication
        auth_user = authenticate(username=email, password=password)
        if auth_user:
            print(f"✅ Authentication successful! User ID: {auth_user.id}")
        else:
            print("❌ Authentication failed")
            
    except Vendor.DoesNotExist:
        print("❌ User not found")

print("\n" + "=" * 50)
print("TEST COMPLETE")
