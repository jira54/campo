#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import login, logout
from vendors.views import login_view
from vendors.models import Vendor

print("=== Testing Login View Directly ===")

# Create a test client
client = Client()

# Test 1: Direct login view test
print("\n1. Testing login view with POST request:")
factory = RequestFactory()
request = factory.post('/login/', {
    'email': 'fanueljunior08@gmail.com',
    'password': 'admin123'
})

# Add session and messages middleware
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

messages = MessageMiddleware(lambda x: None)
messages.process_request(request)

# Call the login view
try:
    response = login_view(request)
    print(f"Response status: {response.status_code}")
    if hasattr(response, 'url'):
        print(f"Redirect URL: {response.url}")
    elif hasattr(response, 'context_data'):
        error = response.context_data.get('error', 'No error')
        print(f"Error in context: {error}")
except Exception as e:
    print(f"Error in login view: {e}")

# Test 2: Test with Django test client
print("\n2. Testing with Django test client:")
try:
    response = client.post('/login/', {
        'email': 'fanueljunior08@gmail.com',
        'password': 'admin123'
    }, follow=False)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirect location: {response.get('Location', 'No location')}")
    elif response.status_code == 200:
        # Check if there's an error message in the response
        content = response.content.decode('utf-8')
        if 'error' in content.lower():
            print("Error found in response content")
            # Extract error message if possible
            if 'Invalid credentials' in content:
                print("Error: Invalid credentials")
        else:
            print("No obvious error in content")
except Exception as e:
    print(f"Error with test client: {e}")

# Test 3: Check if user can login directly
print("\n3. Testing direct login:")
try:
    from django.contrib.auth import authenticate
    user = authenticate(username='fanueljunior08@gmail.com', password='admin123')
    if user:
        print("✓ Authentication successful")
        # Test direct login
        request = factory.get('/')
        middleware.process_request(request)
        request.session.save()
        login(request, user)
        print(f"✓ Login successful, user: {request.user}")
    else:
        print("✗ Authentication failed")
except Exception as e:
    print(f"Error in direct login: {e}")
