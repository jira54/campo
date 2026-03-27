import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from customers.models import Customer

print("Updating generic customer names with realistic Kenyan names...")

# Realistic Kenyan names
kenyan_names = [
    "John Mwangi", "Mary Wanjiku", "David Mutiso", "Grace Akinyi", "Peter Njoroge",
    "Susan Achieng", "James Mwangi", "Lucy Wairimu", "Samuel Ochieng", "Esther Nduta",
    "Michael Kiplagat", "Faith Chebet", "Robert Waweru", "Nancy Atieno", "Daniel Kinyua",
    "Beatrice Njeri", "Charles Kamotho", "Rehema Salim", "Thomas Thuo", "Ann Muthoni",
    "Alex Mwangi", "Brenda Achieng", "Chris Kamau", "Diana Wairimu", "Eric Otieno",
    "Faith Njeri", "George Thuo", "Hellen Mutiso", "Ian Kinyua", "Joyce Akinyi",
    "Kevin Njoroge", "Lucy Wanjiku", "Michael Ochieng", "Nancy Chebet"
]

# Realistic Kenyan phone number prefixes
phone_prefixes = ["0711", "0722", "0733", "0744", "0755", "0766", "0777", "0788", "0799", "0700"]

# Get customers with generic names
generic_customers = Customer.objects.filter(name__regex=r'^Customer \d+$')
print(f"Found {generic_customers.count()} customers with generic names")

# Update each customer
updated_count = 0
for customer in generic_customers:
    # Pick a random name that hasn't been used
    available_names = [name for name in kenyan_names 
                      if not Customer.objects.filter(vendor=customer.vendor, name=name).exists()]
    
    if available_names:
        old_name = customer.name
        new_name = random.choice(available_names)
        
        # Also update phone to be more realistic
        prefix = random.choice(phone_prefixes)
        suffix = f"{random.randint(100000, 999999)}"
        new_phone = f"{prefix}{suffix}"
        
        # Update customer
        customer.name = new_name
        customer.phone = new_phone
        customer.save()
        
        updated_count += 1
        print(f"  ✓ Updated: {old_name} → {new_name} ({new_phone})")
        
        # Remove used name from list
        kenyan_names.remove(new_name)
    else:
        print(f"  ⚠️  No more unique names available for {customer.name}")

print(f"\n✅ Updated {updated_count} customers with realistic Kenyan names")
print(f"✅ Updated phone numbers to realistic format")

# Show some examples
print("\n📋 Sample updated customers:")
for customer in Customer.objects.filter(vendor=customer.vendor)[:10]:
    print(f"  • {customer.name} - {customer.phone}")

print("\n🎉 Customer data now looks realistic and professional!")
