import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from customers.models import Purchase
from django.db.models.functions import TruncDate
from django.db.models import Count
from datetime import datetime, timedelta

# Check purchase dates
purchases = Purchase.objects.all().order_by('purchased_at')
print(f'Total purchases: {purchases.count()}')
print('First 10 purchase dates:')
for i, p in enumerate(purchases[:10]):
    print(f'{i+1}. {p.purchased_at.strftime("%Y-%m-%d %H:%M")}')
    
# Check daily distribution
print('\nDaily purchase counts:')
daily = purchases.annotate(day=TruncDate('purchased_at')).values('day').annotate(count=Count('id')).order_by('day')
for d in daily:
    print(f'{d["day"].strftime("%Y-%m-%d")}: {d["count"]} purchases')

print('\nDate range:')
first_date = purchases.first().purchased_at
last_date = purchases.last().purchased_at
print(f'From: {first_date.strftime("%Y-%m-%d")}')
print(f'To: {last_date.strftime("%Y-%m-%d")}')
print(f'Span: {(last_date - first_date).days} days')
