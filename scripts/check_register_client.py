import os
import django
import sys

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()

from django.test import Client

c = Client()
resp = c.get('/register/', HTTP_HOST='127.0.0.1')
print('GET /register/ ->', resp.status_code)

data = {
    'email': 'testvendor+client@example.com',
    'business_name': 'Client Test Vendor',
    'owner_name': 'Client Owner',
    'business_type': 'food',
    'phone_number': '+254700000001',
    'password': 'ClientPass!1',
    'password2': 'ClientPass!1',
}

resp = c.post('/register/', data, follow=True, HTTP_HOST='127.0.0.1')
print('POST returned status (raw):', resp.status_code)
print('POST /register/ ->', resp.status_code)
print('redirect_chain:', resp.redirect_chain)

# If context is available, look for form
if resp.context:
    for ctx in resp.context:
        if hasattr(ctx, 'get') and 'form' in ctx:
            form = ctx['form']
            print('form is_valid:', form.is_valid())
            print('form errors:', form.errors)
            print('non_field_errors:', form.non_field_errors())
            break
else:
    print('No context available on response.')

print('Final url:', resp.request.get('PATH_INFO'))
