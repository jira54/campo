import os
import django
import sys

# Ensure project root is on path so `config` package is importable
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()


from vendors.forms import RegisterForm

data = {
    'email': 'testvendor+smoke@example.com',
    'business_name': 'Smoke Test Vendor',
    'business_type': 'food',
    'phone_number': '+254700000000',
    'university': 'Test University',
    'password': 'Testpass!234',
    'password2': 'Testpass!234',
}

f = RegisterForm(data)
print('is_valid:', f.is_valid())
print('errors:', f.errors)
print('non_field_errors:', f.non_field_errors())
