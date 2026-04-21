import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'billing_tillpayment';")
    columns = cursor.fetchall()
    print("Columns in billing_tillpayment:")
    for col in columns:
        print(f"- {col[0]}")
