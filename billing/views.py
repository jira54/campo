import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
import logging

from .models import Subscription, Payment, PLAN_PRICES, TillPayment
from .mpesa import stk_push, parse_callback
from customers.models import Customer
from vendors.models import Vendor


@login_required
def upgrade(request):
    vendor = request.user
    sub    = getattr(vendor, 'subscription', None)
    return render(request, 'billing/upgrade.html', {
        'current_plan':  vendor.plan,
        'days_remaining': sub.days_remaining() if sub else 0,
        'plan_prices':   PLAN_PRICES,
    })


@login_required
@require_POST
def initiate_payment(request):
    """
    Called via AJAX from the upgrade page.
    Triggers M-Pesa STK push to vendor's phone.
    """
    vendor = request.user
    plan   = request.POST.get('plan')

    if plan not in PLAN_PRICES:
        return JsonResponse({'ok': False, 'error': 'Invalid plan.'})

    amount = PLAN_PRICES[plan]
    phone  = request.POST.get('phone', vendor.phone)

    try:
        result = stk_push(phone, amount, vendor.id, plan)
        if result.get('ResponseCode') == '0':
            # Save pending payment with CheckoutRequestID for secure callback matching
            Payment.objects.create(
                vendor=vendor,
                amount=amount,
                plan_paid_for=plan,
                phone_used=phone,
                status='pending',
                checkout_request_id=result.get('CheckoutRequestID', ''),
            )
            return JsonResponse({
                'ok':      True,
                'message': 'Check your phone for the M-Pesa prompt.',
            })
        return JsonResponse({
            'ok':    False,
            'error': result.get('errorMessage', 'Payment initiation failed.'),
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@csrf_exempt   # Safaricom posts here — no CSRF token
def mpesa_callback(request):
    """
    Safaricom calls this URL after payment completes.
    Activates the vendor's subscription on success.
    """
    if request.method != 'POST':
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Method not allowed'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Bad JSON'})

    success, mpesa_ref, amount, phone, checkout_id = parse_callback(data)

    if success and mpesa_ref and amount:
        # Match payment by CheckoutRequestID (secure 1-to-1 match).
        # Fall back to phone+amount if CheckoutRequestID is missing (older payments).
        payment = None
        if checkout_id:
            payment = Payment.objects.filter(
                checkout_request_id=checkout_id,
                status='pending',
            ).first()
        if not payment:
            # Fallback: match by last 9 digits of phone + amount + plan price
            payment = Payment.objects.filter(
                phone_used__contains=phone[-9:] if phone else '',
                amount=amount,
                status='pending',
            ).order_by('-created_at').first()

        if payment:
            payment.status       = 'confirmed'
            payment.mpesa_ref    = mpesa_ref
            payment.confirmed_at = timezone.now()
            payment.save()

            # Activate or extend subscription
            sub, _ = Subscription.objects.get_or_create(vendor=payment.vendor)
            sub.plan = payment.plan_paid_for
            sub.extend_by_one_month()

    # Always return success to Safaricom (they retry on failure)
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@login_required
def payment_history(request):
    payments = Payment.objects.filter(vendor=request.user)
    return render(request, 'billing/history.html', {'payments': payments})


@login_required
def billing_success(request):
    return render(request, 'billing/success.html', {
        'plan': getattr(request.user, 'plan', 'free'),
    })


# --- M-Pesa C2B Endpoints (Live Till Integration) ---

@csrf_exempt
def c2b_validation(request):
    """Safaricom C2B Validation Webhook. Always accepts the payment."""
    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })

@csrf_exempt
def c2b_confirmation(request):
    """Safaricom C2B Confirmation Webhook. Logs the live payment and runs Auto-CRM."""
    try:
        data = json.loads(request.body)
        
        transaction_id = data.get('TransID', '')
        amount         = data.get('TransAmount', '0')
        till_number    = data.get('BusinessShortCode', '')
        phone_number   = data.get('MSISDN', '')
        customer_name  = f"{data.get('FirstName', '')} {data.get('LastName', '')}".strip()

        if transaction_id and till_number:
            # Find the vendor that owns this Till Number
            vendor = Vendor.objects.filter(mpesa_till_number=str(till_number)).first()
            if vendor:
                # 1. Save the Till Payment
                till_payment, created = TillPayment.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults={
                        'vendor': vendor,
                        'amount': float(amount),
                        'customer_name': customer_name,
                        'phone_number': phone_number,
                    }
                )

                # 2. **Auto-CRM Logic**
                if created and phone_number:
                    # Check if customer exists
                    customer, cust_created = Customer.objects.get_or_create(
                        vendor=vendor,
                        phone_number=phone_number,
                        defaults={
                            'name': customer_name if customer_name else 'M-Pesa Customer',
                            'visit_count': 1
                        }
                    )
                    
                    if not cust_created:
                        customer.visit_count += 1
                        customer.save(update_fields=['visit_count', 'last_visit'])

        return JsonResponse({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })
    except Exception as e:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})


@login_required
def poll_latest_payments(request):
    """Dashboard JS pings this to check for new C2B payments."""
    unviewed = TillPayment.objects.filter(vendor=request.user, is_viewed=False)
    
    payments_data = []
    for p in unviewed:
        payments_data.append({
            'id': p.id,
            'amount': str(p.amount),
            'customer_name': p.customer_name,
            'phone_number': p.phone_number[-4:] if p.phone_number else '',
            'time': p.created_at.strftime('%H:%M'),
        })
        p.is_viewed = True
        p.save(update_fields=['is_viewed'])

    return JsonResponse({'new_payments': payments_data})
