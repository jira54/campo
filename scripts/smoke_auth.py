import requests
from urllib.parse import urljoin
import time

BASE = 'http://127.0.0.1:8000/'

s = requests.Session()

def get_csrf(url):
    r = s.get(url)
    r.raise_for_status()
    return s.cookies.get('csrftoken', '')

try:
    # 1) GET register page to obtain CSRF
    reg_url = urljoin(BASE, 'register/')
    csrf = get_csrf(reg_url)
    print('Got CSRF:', csrf)

    # 2) POST registration
    email = f"testvendor+{int(time.time())}@example.com"
    password = 'Testpass!234'
    data = {
        'email': email,
        'business_name': 'Smoke Test Vendor',
        'owner_name': 'Smoke Owner',
        'business_type': 'food',
        'phone_number': '+254700000000',
        'university': 'Test University',
        'password': password,
        'password2': password,
        'csrfmiddlewaretoken': csrf,
    }
    headers = {'Referer': reg_url, 'X-CSRFToken': csrf}
    r = s.post(reg_url, data=data, headers=headers, allow_redirects=True)
    print('Register POST ->', r.status_code, ' final url:', r.url)

    if r.url.endswith('/login/') or '/login' in r.url:
        print('Registration redirected to login as expected.')
    else:
        print('Registration did not redirect to login; response length:', len(r.text))
        snippet = r.text[:1000]
        print('\n--- response snippet ---\n', snippet)
        # look for common Django form error markers
        markers = ['error', 'errorlist', 'non_field_errors', 'bg-red', 'text-red', 'This field is required', 'owner_name', 'Passwords do not match']
        for m in markers:
            if m.lower() in r.text.lower():
                idx = r.text.lower().find(m.lower())
                start = max(0, idx-80)
                end = idx+120
                print(f"--- found marker '{m}' at {idx} ---")
                print(r.text[start:end].replace('\n',' '))
            # specifically look for our error class used in the template
            if 'text-red-400' in r.text:
                idx = r.text.find('text-red-400')
                start = max(0, idx-120)
                end = idx+200
                print('--- text-red-400 context ---')
                print(r.text[start:end].replace('\n',' '))
        if 'This field is required' in r.text:
            print('Found "This field is required" in response (missing field)')
        if 'Passwords do not match' in r.text or 'Passwords do not match.' in r.text:
            print('Found password mismatch message')
        if 'owner_name' in r.text or 'Owner name' in r.text:
            print('Response mentions owner_name field — Owner name likely required by model')

    # 3) GET login page to get fresh CSRF
    login_url = urljoin(BASE, 'login/')
    csrf = get_csrf(login_url)
    print('Login CSRF:', csrf)

    # 4) POST login
    data = {'email': email, 'password': password, 'csrfmiddlewaretoken': csrf}
    headers = {'Referer': login_url, 'X-CSRFToken': csrf}
    r = s.post(login_url, data=data, headers=headers, allow_redirects=True)
    print('Login POST ->', r.status_code, ' final url:', r.url)

    # 5) Check dashboard access
    dash_url = urljoin(BASE, 'dashboard/')
    r = s.get(dash_url)
    print('GET /dashboard/ ->', r.status_code)
    if r.status_code == 200 and ('Dashboard' in r.text or 'CampoPawa' in r.text):
        print('Dashboard reachable after login — smoke test PASSED')
    else:
        print('Could not reach dashboard after login; maybe login failed or redirect issue')

except Exception as e:
    print('Smoke test error:', e)

