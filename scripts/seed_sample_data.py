import os
import sys
import pathlib
import django

# ensure project root is on PYTHONPATH
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from vendors.models import Customer, Sale, LoyaltyReward
from decimal import Decimal
import datetime

User = get_user_model()

def create_superuser():
    email = 'admin@campopawa.test'
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email=email, business_name='Campus Admin', owner_name='Admin', phone_number='000', password='adminpass')
        print('Created superuser:', email)
    else:
        print('Superuser exists:', email)


def create_vendor_and_seed():
    vendor_email = 'vendor@campopawa.test'
    if not User.objects.filter(email=vendor_email).exists():
        vendor = User.objects.create_user(email=vendor_email, business_name='Mama Njeri', owner_name='Njeri', phone_number='0722000000', password='vendorpass')
        print('Created vendor:', vendor_email)
    else:
        vendor = User.objects.get(email=vendor_email)
        print('Vendor exists:', vendor_email)

    # Customers
    customers_data = [
        ('John Mwangi', '0711000001', 5),
        ('Aisha Ahmed', '0711000002', 2),
        ('Sam Otieno', '0711000003', 1),
    ]
    for name, phone, visits in customers_data:
        c, created = Customer.objects.get_or_create(vendor=vendor, phone_number=phone, defaults={'name': name, 'visit_count': visits})
        if not created and c.visit_count < visits:
            c.visit_count = visits
            c.save()
        print('Customer:', c.name, c.phone_number, 'visits=', c.visit_count)

    # Loyalty reward
    reward, _ = LoyaltyReward.objects.get_or_create(vendor=vendor, reward_name='Free Tea', required_visits=5)
    print('Reward:', reward.reward_name)

    # Sales
    Sale.objects.create(vendor=vendor, customer=Customer.objects.filter(vendor=vendor).first(), amount=Decimal('200.00'), date=datetime.date.today(), notes='Lunch')
    Sale.objects.create(vendor=vendor, customer=None, amount=Decimal('150.00'), date=datetime.date.today()-datetime.timedelta(days=1), notes='Snacks')
    print('Created sample sales')


if __name__ == '__main__':
    create_superuser()
    create_vendor_and_seed()
    print('Seeding complete. Superuser: admin@campopawa.test / adminpass; Vendor: vendor@campopawa.test / vendorpass')
