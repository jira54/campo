import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor
from billing.models import Subscription
from django.utils import timezone
from datetime import timedelta

# Target Email
target_email = 'fanueljunior08@gmail.com'

try:
    vendor = Vendor.objects.get(email=target_email)
    
    # Create or update subscription
    sub, created = Subscription.objects.get_or_create(vendor=vendor)
    sub.plan = 'premium_retail'
    # Give 1 year of access
    sub.expires_at = timezone.now() + timedelta(days=365)
    sub.save()
    
    print(f"✅ SUCCESS: {vendor.email} is now Premium (Superuser Bypass + Active Subscription)")
    print(f"   - Plan: {sub.plan}")
    print(f"   - Expires: {sub.expires_at}")
    print(f"   - Is Superuser: {vendor.is_superuser}")
    print(f"   - Final is_premium result: {vendor.is_premium}")

except Vendor.DoesNotExist:
    print(f"❌ ERROR: User with email {target_email} not found.")
except Exception as e:
    print(f"❌ ERROR: {e}")
