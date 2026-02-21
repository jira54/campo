"""
M-Pesa Daraja API integration.
Uses sandbox by default. Switch MPESA_ENV=production for live.
"""
import base64
import json
import requests
from datetime import datetime
from django.conf import settings


def _base_url():
    if settings.MPESA_ENV == 'production':
        return 'https://api.safaricom.co.ke'
    return 'https://sandbox.safaricom.co.ke'


def get_access_token():
    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    r   = requests.get(
        url,
        auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=10
    )
    r.raise_for_status()
    return r.json()['access_token']


def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw       = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password  = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def stk_push(phone, amount, vendor_id, plan):
    """
    Trigger M-Pesa STK Push to vendor's phone.
    phone: format 254XXXXXXXXX
    Returns Safaricom response dict.
    """
    token            = get_access_token()
    password, ts     = generate_password()
    # Normalize phone
    phone = phone.strip().replace(' ', '').replace('+', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password":          password,
        "Timestamp":         ts,
        "TransactionType":   "CustomerPayBillOnline",
        "Amount":            int(amount),
        "PartyA":            phone,
        "PartyB":            settings.MPESA_SHORTCODE,
        "PhoneNumber":       phone,
        "CallBackURL":       settings.MPESA_CALLBACK_URL,
        "AccountReference":  f"CampoPawa-{vendor_id}",
        "TransactionDesc":   f"CampoPawa {plan.title()} Subscription",
    }

    r = requests.post(
        f"{_base_url()}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15
    )
    return r.json()


def parse_callback(data):
    """
    Parse Safaricom callback POST body.
    Returns: (success: bool, mpesa_ref: str|None, amount: float|None, phone: str|None)
    """
    try:
        cb = data['Body']['stkCallback']
        if cb['ResultCode'] != 0:
            return False, None, None, None

        items = {
            item['Name']: item.get('Value')
            for item in cb['CallbackMetadata']['Item']
        }
        return (
            True,
            items.get('MpesaReceiptNumber'),
            items.get('Amount'),
            str(items.get('PhoneNumber', '')),
        )
    except (KeyError, TypeError):
        return False, None, None, None
