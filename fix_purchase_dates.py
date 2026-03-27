import os
import django
import random
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from customers.models import Purchase

print("Fixing purchase dates to spread across 30 days...")

# Get all purchases
purchases = list(Purchase.objects.all())
print(f"Found {len(purchases)} purchases to update")

# Generate dates spread across last 30 days
today = datetime.now()
dates_needed = len(purchases)
days_span = 30

# Create a list of dates
date_list = []
for i in range(days_span):
    # Create multiple purchases per day (4-8 per day as requested)
    num_per_day = random.randint(4, 8)
    day_date = today - timedelta(days=i)
    
    for j in range(min(num_per_day, len(purchases) - len(date_list))):
        # Random time during business hours (8 AM - 8 PM)
        hour = random.randint(8, 20)
        minute = random.randint(0, 59)
        purchase_time = day_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        date_list.append(purchase_time)

# Shuffle the dates to make them more random
random.shuffle(date_list)

# Update purchases with new dates
updated_count = 0
for i, purchase in enumerate(purchases):
    if i < len(date_list):
        purchase.purchased_at = date_list[i]
        purchase.save()
        updated_count += 1
        if (i + 1) % 50 == 0:
            print(f"Updated {i + 1}/{len(purchases)} purchases...")

print(f"\n✅ Updated {updated_count} purchases with random dates")

# Verify the spread
from django.db.models.functions import TruncDate
from django.db.models import Count

daily_counts = Purchase.objects.annotate(
    day=TruncDate('purchased_at')
).values('day').annotate(
    count=Count('id')
).order_by('day')

print(f"\n📅 Daily distribution (showing first 10 days):")
for d in daily_counts[:10]:
    print(f'  {d["day"].strftime("%Y-%m-%d")}: {d["count"]} purchases')

print(f"\n🎉 Purchase dates are now spread across {days_span} days!")
print("Your analytics chart will show proper daily activity.")
