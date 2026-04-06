from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from billing.decorators import premium_required
from customers.models import Customer
from .models import Promotion
from .forms import PromotionForm
import urllib.parse

@login_required
@premium_required
def promotion_list(request):
    promos = Promotion.objects.filter(vendor=request.user)
    # Get pending WhatsApp promotions (both WhatsApp-only and SMS & WhatsApp)
    pending_whatsapp = promos.filter(status='draft').filter(channel__in=['whatsapp', 'both'])
    # Calculate total recipients for pending promotions
    total_pending_recipients = sum(promo.recipients for promo in pending_whatsapp)
    
    return render(request, 'promotions/list.html', {
        'promos': promos,
        'pending_whatsapp': pending_whatsapp,
        'total_pending_recipients': total_pending_recipients
    })


@login_required
@premium_required
def promotion_compose(request):
    vendor    = request.user
    form      = PromotionForm(vendor=vendor)
    customers = Customer.objects.filter(vendor=vendor).prefetch_related('purchases')
    segment_counts = {
        'all':     customers.count(),
        'loyal':   sum(1 for c in customers if c.status == 'loyal'),
        'regular': sum(1 for c in customers if c.status == 'regular'),
        'new':     sum(1 for c in customers if c.status == 'new'),
        'atrisk':  sum(1 for c in customers if c.status == 'atrisk'),
    }

    if request.method == 'POST':
        form = PromotionForm(request.POST, vendor=vendor)
        if form.is_valid():
            promo            = form.save(commit=False)
            promo.vendor     = vendor
            
            # Calculate recipients based on segment
            if promo.segment == 'individual':
                seg_count = 1 if promo.individual_customer else 0
            else:
                seg_count = segment_counts.get(promo.segment, 0)
            
            promo.recipients = seg_count
            if promo.scheduled_at:
                promo.status = 'scheduled'
            elif promo.channel == 'whatsapp':
                # WhatsApp promotions should remain as 'draft' until manually sent
                promo.status = 'draft'
                messages.success(request, f"Promotion '{promo.title}' created! Send messages via WhatsApp to complete.")
            elif promo.channel == 'both':
                # SMS & WhatsApp - handle both channels
                # Try to send SMS first
                sms_sent = _send_sms(promo, vendor)
                if sms_sent:
                    # SMS sent successfully, WhatsApp remains as draft
                    promo.status = 'draft'  # Still needs WhatsApp sending
                    promo.sent_at = None    # Not fully sent yet
                    messages.success(request, f"Promotion '{promo.title}' SMS sent to {seg_count} customers! Send WhatsApp messages to complete.")
                else:
                    # SMS service unavailable, WhatsApp remains as draft
                    promo.status = 'draft'
                    promo.sent_at = None
                    messages.warning(request, f"SMS service currently unavailable. Promotion '{promo.title}' saved for WhatsApp only. SMS feature coming soon!")
            else:
                # SMS only
                sms_sent = _send_sms(promo, vendor)
                if sms_sent:
                    # SMS sent successfully
                    promo.status = 'sent'
                    promo.sent_at = timezone.now()
                    messages.success(request, f"Promotion '{promo.title}' sent to {seg_count} customers!")
                else:
                    # SMS service unavailable
                    promo.status = 'draft'
                    promo.sent_at = None
                    messages.warning(request, f"SMS service currently unavailable. Promotion '{promo.title}' saved as draft. SMS feature coming soon!")
            promo.save()
            
            # WhatsApp messages handled on line 59
            # SMS messages handled above
            return redirect('promotions:promotion_list')   # ← fixed

    return render(request, 'promotions/compose.html', {
        'form':           form,
        'segment_counts': segment_counts,
    })


def _send_sms(promo, vendor):
    import os
    if not os.getenv('AT_API_KEY'):
        # SMS service not configured - return False to indicate unavailable
        return False
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
        return True
    except Exception as e:
        # Silently handle SMS errors
        return False


@login_required
@premium_required
def promotion_detail(request, promo_id):
    promo = get_object_or_404(Promotion, id=promo_id, vendor=request.user)
    
    if promo.segment == 'individual':
        customers = [promo.individual_customer] if promo.individual_customer else []
    else:
        customers = Customer.objects.filter(vendor=request.user)
        if promo.segment != 'all':
            customers = [c for c in customers if c.status == promo.segment]
    
    # Add WhatsApp URLs to each customer for WhatsApp or both channels
    if promo.channel == 'whatsapp' or promo.channel == 'both':
        for customer in customers:
            if customer and customer.phone:
                customer.whatsapp_url = _get_whatsapp_url(promo, customer)
    
    return render(request, 'promotions/detail.html', {
        'promo': promo,
        'customers': customers,
    })


def _get_whatsapp_url(promo, customer):
    """Generate WhatsApp URL for individual customer"""
    # Check if customer has phone
    if not customer.phone:
        return None
    
    # Create a natural, human-sounding message with local language
    customer_name = customer.name or 'there'
    
    # Build a natural message that sounds like a local person texting
    message = "Hey " + str(customer_name) + "! 👋 Hope uko fiti kiongos🫡. We've missed you! Cam leo ujionee bidhaa, " + str(promo.message) + ", usiwachwe nyuma. 😊"
    
    # Clean phone number - remove all non-digits
    phone_clean = ''.join(filter(str.isdigit, str(customer.phone)))
    
    # Ensure phone has country code (add 254 for Kenya if missing and starts with 0)
    if phone_clean.startswith('0') and len(phone_clean) == 10:
        phone_clean = '254' + phone_clean[1:]
    elif len(phone_clean) == 9 and not phone_clean.startswith('254'):
        phone_clean = '254' + phone_clean
    
    # URL encode the message properly
    encoded_message = urllib.parse.quote(message)
    
    # Create WhatsApp URL
    whatsapp_url = f"https://wa.me/{phone_clean}?text={encoded_message}"
    
    return whatsapp_url


@login_required
@premium_required
def mark_whatsapp_sent(request, promo_id):
    """Mark WhatsApp promotion as sent after user sends messages"""
    promo = get_object_or_404(Promotion, id=promo_id, vendor=request.user)
    
    if request.method == 'POST' and (promo.channel == 'whatsapp' or promo.channel == 'both') and promo.status == 'draft':
        promo.status = 'sent'
        promo.sent_at = timezone.now()
        promo.save()
        
        if promo.channel == 'both':
            messages.success(request, f"SMS & WhatsApp promotion '{promo.title}' marked as sent!")
        else:
            messages.success(request, f"WhatsApp promotion '{promo.title}' marked as sent!")
    
    return redirect('promotions:promotion_detail', promo_id=promo_id)


@login_required
@premium_required
def delete_promotion(request, promo_id):
    """Delete a promotion"""
    promo = get_object_or_404(Promotion, id=promo_id, vendor=request.user)
    
    if request.method == 'POST':
        promo_title = promo.title
        promo.delete()
        messages.success(request, f"Promotion '{promo_title}' deleted successfully!")
        return redirect('promotions:promotion_list')
    
    return render(request, 'promotions/delete_confirm.html', {'promo': promo})