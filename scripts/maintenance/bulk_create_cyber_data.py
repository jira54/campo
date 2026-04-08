import os
import django
import random
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vendors.models import Vendor
from customers.models import Customer, Purchase, Service

# Get the vendor
vendor = Vendor.objects.get(email='fanueljunior08@gmail.com')

print(f"Creating data for {vendor.business_name}...")

# Cyber Cafe Services
services_data = [
    {"name": "WiFi 1 Hour", "description": "High-speed internet access", "price": 50.00, "is_popular": True},
    {"name": "WiFi 30 Minutes", "description": "Quick internet session", "price": 30.00, "is_popular": True},
    {"name": "Computer Hour", "description": "Desktop PC with internet", "price": 80.00, "is_popular": True},
    {"name": "Printing B&W", "description": "Black & white printing per page", "price": 10.00, "is_popular": False},
    {"name": "Printing Color", "description": "Color printing per page", "price": 50.00, "is_popular": False},
]

print("Creating services...")
created_services = []
for service_data in services_data:
    service, created = Service.objects.get_or_create(
        vendor=vendor,
        name=service_data["name"],
        defaults={
            "description": service_data["description"],
            "price": service_data["price"],
            "is_popular": service_data["is_popular"],
            "sort_order": len(created_services)
        }
    )
    created_services.append(service)
    if created:
        print(f"  ✓ Created: {service.name} - KES {service.price}")
    else:
        print(f"  - Exists: {service.name}")

# Customer data for cyber cafe
customer_data = [
    {"name": "John Kamau", "phone": "0712345678", "notes": "Regular morning customer, prefers WiFi 1 hour"},
    {"name": "Mary Wanjiku", "phone": "0723456789", "notes": "Student, comes for computer work"},
    {"name": "David Mutiso", "phone": "0734567890", "notes": "Business printing, weekly visits"},
    {"name": "Grace Akinyi", "phone": "0745678901", "notes": "Online job applications, 2-3 times per week"},
    {"name": "Peter Njoroge", "phone": "0756789012", "notes": "Freelancer, works remotely"},
    {"name": "Susan Achieng", "phone": "0767890123", "notes": "Research student, long sessions"},
    {"name": "James Mwangi", "phone": "0778901234", "notes": "Gaming enthusiast, weekends"},
    {"name": "Lucy Wairimu", "phone": "0789012345", "notes": "Social media management"},
    {"name": "Samuel Ochieng", "phone": "0790123456", "notes": "Online classes, daily"},
    {"name": "Esther Nduta", "phone": "0701234567", "notes": "CV printing and job hunting"},
    {"name": "Michael Kiplagat", "phone": "0711122233", "notes": "Crypto trading, prefers WiFi"},
    {"name": "Faith Chebet", "phone": "0722233344", "notes": "Online shopping assistance"},
    {"name": "Robert Waweru", "phone": "0733344455", "notes": "Document scanning and email"},
    {"name": "Nancy Atieno", "phone": "0744455566", "notes": "Video conferencing for interviews"},
    {"name": "Daniel Kinyua", "phone": "0755566677", "notes": "Programming work, 3-4 hours per visit"},
    {"name": "Beatrice Njeri", "phone": "0766677788", "notes": "Online banking and payments"},
    {"name": "Charles Kamotho", "phone": "0777788899", "notes": "Research and data entry"},
    {"name": "Rehema Salim", "phone": "0788899900", "notes": "Social media browsing"},
    {"name": "Thomas Thuo", "phone": "0799900011", "notes": "Gaming and streaming"},
    {"name": "Ann Muthoni", "phone": "0700112233", "notes": "Assignment typing and printing"},
]

print("\nCreating customers...")
created_customers = []
for i, customer_info in enumerate(customer_data):
    customer, created = Customer.objects.get_or_create(
        vendor=vendor,
        phone=customer_info["phone"],
        defaults={
            "name": customer_info["name"],
            "notes": customer_info["notes"],
            "tags": random.choice(["regular", "student", "business", "freelancer", "gamer"])
        }
    )
    created_customers.append(customer)
    if created:
        print(f"  ✓ Created: {customer.name} ({customer.phone})")
    else:
        print(f"  - Exists: {customer.name}")

print("\nCreating realistic purchase history...")
wifi_1hr = created_services[0]
wifi_30min = created_services[1]
computer_hr = created_services[2]
printing_bw = created_services[3]
printing_color = created_services[4]

for customer in created_customers:
    # Each customer has 5-15 purchases over the last 30 days
    num_purchases = random.randint(5, 15)
    
    for i in range(num_purchases):
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        purchase_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        # Random service selection based on customer type
        if "student" in customer.tags or "assignment" in customer.notes:
            service_choice = random.choice([computer_hr, wifi_1hr, printing_bw])
        elif "business" in customer.tags or "printing" in customer.notes:
            service_choice = random.choice([printing_bw, printing_color, wifi_30min])
        elif "gamer" in customer.tags or "gaming" in customer.notes:
            service_choice = random.choice([computer_hr, wifi_1hr])
        else:
            service_choice = random.choice(created_services)
        
        # Create purchase with realistic amount
        amount = service_choice.price
        
        # Sometimes customers buy multiple items
        if random.random() > 0.7:  # 30% chance of multiple items
            second_service = random.choice([s for s in created_services if s != service_choice])
            amount += second_service.price
            service_name = f"{service_choice.name} + {second_service.name}"
        else:
            service_name = service_choice.name
        
        # Create purchase
        purchase = Purchase.objects.create(
            customer=customer,
            amount=amount,
            service=service_name,
            notes=random.choice([
                "Paid via M-Pesa",
                "Cash payment",
                "Quick session",
                "Long session",
                "Regular customer",
                ""
            ]),
            purchased_at=purchase_date
        )

print("\n📊 Summary:")
print(f"✓ Services: {len(created_services)} created")
print(f"✓ Customers: {len(created_customers)} created") 
print(f"✓ Total Purchases: {Purchase.objects.filter(customer__vendor=vendor).count()}")

# Show analytics summary
total_revenue = sum(p.amount for p in Purchase.objects.filter(customer__vendor=vendor))
print(f"✓ Total Revenue: KES {total_revenue:.2f}")

print("\n🎉 Cyber cafe data creation complete!")
print("Your analytics dashboard will now show realistic data!")
