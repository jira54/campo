from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from billing.decorators import premium_required
from customers.models import Customer
from .models import Promotion
from .forms import PromotionForm


@login_required
@premium_required
def promotion_list(request):
    promos = Promotion.objects.filter(vendor=request.user)
    return render(request, 'promotions/list.html', {'promos': promos})


@login_required
@premium_required
def promotion_compose(request):
    vendor    = request.user
    form      = PromotionForm()
    customers = Customer.objects.filter(vendor=vendor)
    segment_counts = {
        'all':     customers.count(),
        'loyal':   sum(1 for c in customers if c.status == 'loyal'),
        'regular': sum(1 for c in customers if c.status == 'regular'),
        'new':     sum(1 for c in customers if c.status == 'new'),
        'atrisk':  sum(1 for c in customers if c.status == 'atrisk'),
    }

    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promo            = form.save(commit=False)
            promo.vendor     = vendor
            seg_count        = segment_counts.get(promo.segment, 0)
            promo.recipients = seg_count
            if promo.scheduled_at:
                promo.status = 'scheduled'
            else:
                promo.status  = 'sent'
                promo.sent_at = timezone.now()
                _send_sms(promo, vendor)
            promo.save()
            messages.success(request, f"Promotion '{promo.title}' sent to {seg_count} customers!")
            return redirect('promotions:promotion_list')   # ← fixed

    return render(request, 'promotions/compose.html', {
        'form':           form,
        'segment_counts': segment_counts,
    })


def _send_sms(promo, vendor):
    import os
    if not os.getenv('AT_API_KEY'):
        return
    try:
        import africastalking
        africastalking.initialize(
            username=os.getenv('AT_USERNAME', 'sandbox'),
            api_key=os.getenv('AT_API_KEY', '')
        )
        sms       = africastalking.SMS
        customers = Customer.objects.filter(vendor=vendor)
        if promo.segment != 'all':
            customers = [c for c in customers if c.status == promo.segment]
        phones  = [c.phone for c in customers if c.phone]
        message = promo.message.replace('{name}', 'there')
        if phones:
            sms.send(message, phones, sender_id=os.getenv('AT_SENDER_ID', 'CampoPawa'))
    except Exception as e:
        print(f"SMS send failed: {e}")