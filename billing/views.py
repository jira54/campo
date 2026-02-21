import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import Subscription, Payment, PLAN_PRICES
from .mpesa import stk_push, parse_callback


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

    if plan not in ('premium', 'bundle'):
        return JsonResponse({'ok': False, 'error': 'Invalid plan.'})

    amount = PLAN_PRICES[plan]
    phone  = request.POST.get('phone', vendor.phone)

    try:
        result = stk_push(phone, amount, vendor.id, plan)
        if result.get('ResponseCode') == '0':
            # Save pending payment
            Payment.objects.create(
                vendor=vendor,
                amount=amount,
                plan_paid_for=plan,
                phone_used=phone,
                status='pending',
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

    success, mpesa_ref, amount, phone = parse_callback(data)

    if success and mpesa_ref and amount:
        # Find the most recent pending payment matching phone + amount
        payment = Payment.objects.filter(
            phone_used__contains=phone[-9:],  # last 9 digits
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
        'plan': request.user.plan,
    })
