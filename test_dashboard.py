#!/usr/bin/env python
import os
import sys
import django
import time
import urllib.request

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'D:\\campo')
django.setup()

time.sleep(1)

try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/dashboard/', timeout=5)
    print('SUCCESS: Dashboard loaded with HTTP', response.status)
except urllib.error.HTTPError as e:
    if e.code == 302:
        print('SUCCESS: Dashboard redirect (login required) - No TypeError!')
    else:
        print(f'ERROR: HTTP {e.code}')
except Exception as e:
    print(f'Connection error: {type(e).__name__}: {e}')
