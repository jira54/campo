import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor

# Make the user premium
try:
    vendor = Vendor.objects.get(email='fanueljunior08@gmail.com')
    vendor.is_premium = True
    vendor.save()
    print(f"✓ Made {vendor.email} premium")
    print(f"  - Is Premium: {vendor.is_premium}")
except Exception as e:
    print(f"Error: {e}")
