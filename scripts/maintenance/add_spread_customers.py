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
if not services:
    print("No services found! Creating basic services first...")
    services_data = [
        {"name": "WiFi 1 Hour", "description": "High-speed internet access", "price": 50.00, "is_popular": True},
        {"name": "WiFi 30 Minutes", "description": "Quick internet session", "price": 30.00, "is_popular": True},
        {"name": "Computer Hour", "description": "Desktop PC with internet", "price": 80.00, "is_popular": True},
        {"name": "Printing B&W", "description": "Black & white printing per page", "price": 10.00, "is_popular": False},
        {"name": "Printing Color", "description": "Color printing per page", "price": 50.00, "is_popular": False},
    ]
    
    for service_data in services_data:
        service = Service.objects.create(
            vendor=vendor,
            name=service_data["name"],
            description=service_data["description"],
            price=service_data["price"],
            is_popular=service_data["is_popular"]
        )
        services.append(service)
    
    print(f"Created {len(services)} services")

# More diverse customer data
new_customer_data = [
    {"name": "Alex Mwangi", "phone": "0711222334", "notes": "Morning regular, coffee and WiFi"},
    {"name": "Brenda Achieng", "phone": "0722333445", "notes": "Student, research projects"},
    {"name": "Chris Kamau", "phone": "0733444556", "notes": "Remote worker, 4-5 hour sessions"},
    {"name": "Diana Wairimu", "phone": "0744555667", "notes": "Online shopping assistance"},
    {"name": "Eric Otieno", "phone": "0755667788", "notes": "Gaming tournaments, weekends"},
    {"name": "Faith Njeri", "phone": "0766778899", "notes": "Job applications, daily"},
    {"name": "George Thuo", "phone": "0777889900", "notes": "Business emails and printing"},
    {"name": "Hellen Mutiso", "phone": "0788990011", "notes": "Social media management"},
    {"name": "Ian Kinyua", "phone": "0799001122", "notes": "Programming and coding"},
    {"name": "Joyce Akinyi", "phone": "0700112233", "notes": "Video calls, family abroad"},
    {"name": "Kevin Njoroge", "phone": "0711223344", "notes": "Freelance writing"},
    {"name": "Lucy Wanjiku", "phone": "0722334455", "notes": "Online classes, evening"},
    {"name": "Michael Ochieng", "phone": "0733445566", "notes": "Stock trading, WiFi only"},
    {"name": "Nancy Chebet", "phone": "0744556677", "notes": "Assignment typing"},
    {"name": "Robert Nduta", "phone": "0755667788", "notes": "Document scanning"},
    {"name": "Susan Atieno", "phone": "0766778899", "notes": "Online banking"},
    {"name": "Thomas Waweru", "phone": "0777889900", "notes": "Research student"},
    {"name": "Ann Muthoni", "phone": "0788990011", "notes": "CV creation service"},
    {"name": "Benard Kamotho", "phone": "0799001122", "notes": "Email correspondence"},
    {"name": "Catherine Salim", "phone": "0700112233", "notes": "Social media browsing"},
    {"name": "Daniel Kiplagat", "phone": "0711223344", "notes": "Gaming and streaming"},
    {"name": "Elizabeth Njeri", "phone": "0722334455", "notes": "Online courses"},
    {"name": "Francis Mwangi", "phone": "0733445566", "notes": "Business printing"},
    {"name": "Grace Achieng", "phone": "0744556677", "notes": "Video conferencing"},
    {"name": "Henry Kamau", "phone": "0755667788", "notes": "Crypto trading"},
    {"name": "Irene Wairimu", "phone": "0766778899", "notes": "Content creation"},
    {"name": "James Otieno", "phone": "0777889900", "notes": "Remote meetings"},
    {"name": "Karen Mutiso", "phone": "0788990011", "notes": "Assignment help"},
    {"name": "Lawrence Njoroge", "phone": "0799001122", "notes": "Web development"},
    {"name": "Maryanne Akinyi", "phone": "0700112233", "notes": "Online tutoring"},
    {"name": "Nicholas Chebet", "phone": "0711223344", "notes": "Digital marketing"},
    {"name": "Olivia Nduta", "phone": "0722334455", "notes": "Photography editing"},
    {"name": "Peter Waweru", "phone": "0733445566", "notes": "Music production"},
    {"name": "Quinter Muthoni", "phone": "0744556677", "notes": "Online gaming"},
    {"name": "Richard Kamotho", "phone": "0755667788", "notes": "Data analysis"},
]

print("\nCreating new customers...")
created_customers = []
for i, customer_info in enumerate(new_customer_data):
    customer = Customer.objects.create(
        vendor=vendor,
        name=customer_info["name"],
        phone=customer_info["phone"],
        notes=customer_info["notes"],
        tags=random.choice(["regular", "student", "business", "freelancer", "gamer", "professional"])
    )
    created_customers.append(customer)
    print(f"  ✓ Created: {customer.name} ({customer.phone})")

print(f"\nCreating purchase history spread across 30 days...")

# Create purchases spread across 30 days, 4 customers per day
days_list = list(range(30))  # 0-29 days ago
random.shuffle(days_list)  # Randomize the order

for i, customer in enumerate(created_customers):
    # Each customer gets 3-8 purchases
    num_purchases = random.randint(3, 8)
    
    for j in range(num_purchases):
        # Spread purchases across different days
        day_offset = days_list[(i * num_purchases + j) % 30]
        purchase_date = datetime.now() - timedelta(days=day_offset)
        
        # Random time during the day
        hour = random.randint(8, 20)  # 8 AM to 8 PM
        minute = random.randint(0, 59)
        purchase_date = purchase_date.replace(hour=hour, minute=minute)
        
        # Random service selection
        service_choice = random.choice(services)
        amount = service_choice.price
        
        # Sometimes multiple services
        if random.random() > 0.6:  # 40% chance of multiple items
            second_service = random.choice([s for s in services if s != service_choice])
            amount += second_service.price
            service_name = f"{service_choice.name} + {second_service.name}"
        else:
            service_name = service_choice.name
        
        # Create purchase
        Purchase.objects.create(
            customer=customer,
            amount=amount,
            service=service_name,
            notes=random.choice([
                "M-Pesa payment",
                "Cash payment", 
                "Quick session",
                "Long session",
                "Regular customer",
                "Student discount",
                "Bulk printing",
                "Weekend special",
                ""
            ]),
            purchased_at=purchase_date
        )

print("\n📊 Summary:")
total_customers = Customer.objects.filter(vendor=vendor).count()
total_purchases = Purchase.objects.filter(customer__vendor=vendor).count()
total_revenue = sum(p.amount for p in Purchase.objects.filter(customer__vendor=vendor))

print(f"✓ Total Customers: {total_customers}")
print(f"✓ Total Purchases: {total_purchases}")
print(f"✓ Total Revenue: KES {total_revenue:.2f}")

# Show daily distribution
print("\n📅 Daily Customer Distribution (last 30 days):")
from django.db.models import Count
from django.db.models.functions import TruncDate

daily_counts = Purchase.objects.filter(
    customer__vendor=vendor,
    purchased_at__date__gte=datetime.now().date() - timedelta(days=30)
).annotate(
    day=TruncDate('purchased_at')
).values('day').annotate(
    count=Count('id')
).order_by('day')

for day_data in daily_counts[:10]:  # Show first 10 days
    day_str = day_data['day'].strftime('%Y-%m-%d')
    print(f"  {day_str}: {day_data['count']} purchases")

print(f"\n🎉 Analytics data enhanced!")
print("Your dashboard now shows realistic daily activity across 30 days!")
