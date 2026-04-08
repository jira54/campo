import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor

# Check if user already exists
try:
    existing_user = Vendor.objects.get(email='fanueljunior08@gmail.com')
    print('User already exists: fanueljunior08@gmail.com')
except Vendor.DoesNotExist:
    try:
        user = Vendor.objects.create_user(
            email='fanueljunior08@gmail.com',
            business_name='New_Fanuels',
            owner_name='Fanuel Junior',
            phone_number='1234567890',
            password='admin123'
        )
        print('User created successfully')
        print('Email: fanueljunior08@gmail.com')
        print('Password: admin123')
    except Exception as e:
        print(f'Error creating user: {e}')
except Exception as e:
    print(f'Error checking user: {e}')
