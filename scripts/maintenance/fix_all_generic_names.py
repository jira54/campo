import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from customers.models import Customer

print("Checking for remaining generic customer names...")

# More realistic Kenyan names
kenyan_names = [
    "Hannah Kamau", "Joseph Muriuki", "Patricia Wanjiru", "Samuel Kinyua", "Esther Muthoni",
    "Nelson Ochieng", "Grace Atieno", "Michael Njoroge", "Faith Wairimu", "David Kamotho",
    "Lucy Akinyi", "Peter Mutiso", "Susan Nduta", "James Chebet", "Beatrice Thuo",
    "Robert Kiplagat", "Nancy Mwangi", "Charles Waweru", "Rehema Achieng", "Thomas Njeri",
    "Ann Otieno", "Alex Kamau", "Brenda Mutiso", "Chris Kinyua", "Diana Njoroge",
    "Eric Wairimu", "Faith Kamotho", "George Muthoni", "Hellen Thuo", "Ian Kiplagat",
    "Joyce Chebet", "Kevin Mutiso", "Lucy Akinyi", "Michael Ochieng", "Nancy Wanjiru",
    "Peter Kinyua", "Samuel Muriuki", "Susan Wanjiru", "Thomas Mwangi", "Beatrice Njoroge",
    "Robert Kamau", "Nancy Mutiso", "Charles Kinyua", "Rehema Wairimu", "James Kamotho",
    "Ann Muthoni", "Alex Otieno", "Brenda Atieno", "Chris Mwangi", "Diana Njoroge",
    "Eric Wairimu", "Faith Kamotho", "George Muthoni", "Hellen Thuo", "Ian Kiplagat"
]

# Realistic Kenyan phone number prefixes
phone_prefixes = ["0711", "0722", "0733", "0744", "0755", "0766", "0777", "0788", "0799", "0700"]

# Get all customers with generic names (Customer 01, Customer 02, etc.)
generic_customers = Customer.objects.filter(name__regex=r'^Customer \d+$')
print(f"Found {generic_customers.count()} customers with generic names")

# Show current generic names
print("\nCurrent generic customers:")
for customer in generic_customers:
    print(f"  • {customer.name} - {customer.phone}")

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

# Verify no more generic names
remaining_generic = Customer.objects.filter(name__regex=r'^Customer \d+$').count()
print(f"✅ Remaining generic customers: {remaining_generic}")

if remaining_generic == 0:
    print("🎉 All customers now have realistic names!")
else:
    print("⚠️  Some customers still have generic names")

# Show some examples
print("\n📋 Sample updated customers:")
for customer in Customer.objects.filter(vendor=customer.vendor)[:15]:
    print(f"  • {customer.name} - {customer.phone}")
