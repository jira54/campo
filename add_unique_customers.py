import os
import django
import random
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor
from customers.models import Customer, Purchase, Service

# Get vendor
vendor = Vendor.objects.get(email='fanueljunior08@gmail.com')

print(f"Adding 32 more customers for {vendor.business_name}...")

# Get existing services
services = list(Service.objects.filter(vendor=vendor))

# Generate unique phone numbers to avoid conflicts
existing_phones = list(Customer.objects.filter(vendor=vendor).values_list('phone', flat=True))
base_phone = 7100000000
phone_counter = base_phone + len(existing_phones) + 1000  # Start from a high number

# More diverse customer data with unique phones
new_customer_data = []
for i in range(32):
    phone_counter += 1
    new_customer_data.append({
        "name": f"Customer {i+1:02d}",
        "phone": f"07{phone_counter:07d}",  # Generate unique phone
        "notes": f"Generated customer {i+1} with unique phone number",
        "tags": random.choice(["regular", "student", "business", "freelancer", "gamer", "professional"])
    })

print("\nCreating new customers...")
created_customers = []
for i, customer_info in enumerate(new_customer_data):
    try:
        customer = Customer.objects.create(
            vendor=vendor,
            name=customer_info["name"],
            phone=customer_info["phone"],
            notes=customer_info["notes"],
            tags=customer_info["tags"]
        )
        created_customers.append(customer)
        print(f"  ✓ Created: {customer.name} ({customer.phone})")
    except Exception as e:
        print(f"  ❌ Error creating {customer_info['name']}: {e}")

print(f"\nCreating purchase history spread across 30 days...")

# Create purchases spread across 30 days
days_list = list(range(30))
random.shuffle(days_list)

for i, customer in enumerate(created_customers):
    num_purchases = random.randint(3, 8)
    
    for j in range(num_purchases):
        day_offset = days_list[(i * num_purchases + j) % 30]
        purchase_date = datetime.now() - timedelta(days=day_offset)
        hour = random.randint(8, 20)
        minute = random.randint(0, 59)
        purchase_date = purchase_date.replace(hour=hour, minute=minute)
        
        service_choice = random.choice(services)
        amount = service_choice.price
        
        if random.random() > 0.6:
            second_service = random.choice([s for s in services if s != service_choice])
            amount += second_service.price
            service_name = f"{service_choice.name} + {second_service.name}"
        else:
            service_name = service_choice.name
        
        try:
            Purchase.objects.create(
                customer=customer,
                amount=amount,
                service=service_name,
                notes=random.choice([
                    "M-Pesa payment", "Cash payment", "Quick session",
                    "Long session", "Regular customer", "Student discount"
                ]),
                purchased_at=purchase_date
            )
        except Exception as e:
            print(f"  ❌ Error creating purchase for {customer.name}: {e}")

print("\n📊 Summary:")
total_customers = Customer.objects.filter(vendor=vendor).count()
total_purchases = Purchase.objects.filter(customer__vendor=vendor).count()
total_revenue = sum(p.amount for p in Purchase.objects.filter(customer__vendor=vendor))

print(f"✓ Total Customers: {total_customers}")
print(f"✓ Total Purchases: {total_purchases}")
print(f"✓ Total Revenue: KES {total_revenue:.2f}")

print(f"\n🎉 Analytics data enhanced!")
print("Your dashboard now shows realistic daily activity across 30 days!")
