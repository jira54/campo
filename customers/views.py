from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import csv

from vendors.decorators import premium_required

from django.conf import settings
from .models import Customer, Purchase, LoyaltyProgram, LoyaltyCard, Reminder, Receipt
from .forms import CustomerForm, PurchaseForm


@login_required
def customer_list(request):
    vendor  = request.user
    segment = request.GET.get('segment', 'all')
    query   = request.GET.get('q', '')

    customers = Customer.objects.filter(vendor=vendor)

    if query:
        customers = customers.filter(name__icontains=query) | \
                    customers.filter(phone__icontains=query)

    limit = vendor.customer_limit
    total = customers.count()

    all_customers = list(customers)
    if segment != 'all':
        all_customers = [c for c in all_customers if c.status == segment]

    segment_counts = {}
    for status, label in [('all','All'),('loyal','Loyal'),('regular','Regular'),('new','New'),('atrisk','At-Risk')]:
        if status == 'all':
            segment_counts[status] = total
        else:
            segment_counts[status] = sum(1 for c in all_customers if c.status == status)

    context = {
        'customers':  all_customers,
        'total':      total,
        'segment':    segment,
        'query':      query,
        'limit':      limit,
        'near_limit': limit and total >= limit - 2,
        'at_limit':   limit and total >= limit,
        'segment_tabs': [
            ('all',     'All',     total),
            ('loyal',   'Loyal',   segment_counts.get('loyal',   0)),
            ('regular', 'Regular', segment_counts.get('regular', 0)),
            ('new',     'New',     segment_counts.get('new',     0)),
            ('atrisk',  'At-Risk', segment_counts.get('atrisk',  0)),
        ]
    }
    return render(request, 'customers/list.html', context)


@login_required
def customer_add(request):
    vendor = request.user

    if vendor.customer_limit:
        current = Customer.objects.filter(vendor=vendor).count()
        if current >= vendor.customer_limit:
            messages.error(
                request,
                f"Free plan limit reached ({vendor.customer_limit} customers). "
                "Upgrade to Premium for unlimited customers."
            )
            return redirect('billing:upgrade')

    form          = CustomerForm()
    purchase_form = PurchaseForm()

    if request.method == 'POST':
        form          = CustomerForm(request.POST)
        purchase_form = PurchaseForm(request.POST)
        if form.is_valid():
            customer        = form.save(commit=False)
            customer.vendor = vendor
            # Strip premium fields for free users
            if not vendor.is_premium:
                customer.notes = ''
                customer.tags  = ''
            try:
                customer.save()
                if purchase_form.is_valid() and request.POST.get('amount'):
                    purchase          = purchase_form.save(commit=False)
                    purchase.customer = customer
                    purchase.save()
                messages.success(request, f"{customer.name} added successfully.")
                return redirect('customers:customer_list')
            except IntegrityError:
                messages.error(request, "A customer with this phone number already exists.")

    return render(request, 'customers/add.html', {
        'form':          form,
        'purchase_form': purchase_form,
    })


@login_required
def customer_detail(request, pk):
    customer  = get_object_or_404(Customer, pk=pk, vendor=request.user)
    vendor    = request.user
    purchases = customer.purchases.all()
    pform     = PurchaseForm()

    if request.method == 'POST':
        pform = PurchaseForm(request.POST)
        if pform.is_valid():
            p          = pform.save(commit=False)
            p.customer = customer
            p.save()

            # Auto-generate receipt for premium vendors
            if vendor.is_premium:
                Receipt.objects.create(
                    purchase=p,
                    receipt_number=Receipt.generate_number(),
                )

            # Loyalty stamps for premium vendors
            if vendor.is_premium:
                programs = LoyaltyProgram.objects.filter(vendor=vendor, is_active=True)
                for prog in programs:
                    card, created = LoyaltyCard.objects.get_or_create(
                        program=prog, customer=customer
                    )
                    card.stamps += 1
                    card.last_stamped = timezone.now()
                    if card.is_reward_ready:
                        card.rewards_earned += 1
                        card.stamps = 0
                        messages.info(request, f"🎉 {customer.name} earned: {prog.reward_description}!")
                    card.save()

            messages.success(request, "Purchase logged.")
            return redirect('customers:customer_detail', pk=pk)

    return render(request, 'customers/detail.html', {
        'customer':  customer,
        'purchases': purchases,
        'pform':     pform,
    })


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, vendor=request.user)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f"{name} removed.")
    return redirect('customers:customer_list')


@login_required
def customer_export_csv(request):
    vendor = request.user
    customers = Customer.objects.filter(vendor=vendor).order_by('name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="campopawa_customers_{vendor.business_name}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Total Visits', 'Total Spent (KES)', 'Status', 'Tags', 'Notes', 'First Added'])

    for c in customers:
        first_added = getattr(c, 'added_at', None)
        first_added_str = first_added.strftime('%Y-%m-%d') if first_added else ''
        writer.writerow([
            c.name,
            c.phone,
            c.total_visits,
            c.total_spent,
            c.status,
            c.tags,
            c.notes,
            first_added_str,
        ])

    return response


@login_required
def customer_export_pdf(request):
    """Simple HTML-to-PDF using xhtml2pdf (install: pip install xhtml2pdf)"""
    from xhtml2pdf import pisa

    vendor = request.user
    customers = Customer.objects.filter(vendor=vendor).order_by('name')

    html = f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; font-size: 12px; }}
        h1 {{ color: #0D8C7F; font-size: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #0F1B2D; color: #E8871E; padding: 8px; text-align: left; font-size: 11px; }}
        td {{ padding: 6px 8px; border-bottom: 1px solid #ddd; font-size: 10px; }}
        .status {{ padding: 2px 8px; border-radius: 10px; font-size: 9px; font-weight: bold; }}
        .loyal {{ background: #0D8C7F; color: white; }}
        .regular {{ background: #3B82F6; color: white; }}
        .new {{ background: #22C55E; color: white; }}
        .atrisk {{ background: #EF4444; color: white; }}
    </style></head>
    <body>
        <h1>CampoPawa — Customer Report</h1>
        <p><strong>{vendor.business_name}</strong> | Generated: {timezone.now().strftime('%d %b %Y')}</p>
        <p>Total Customers: {customers.count()}</p>
        <table>
            <tr><th>Name</th><th>Phone</th><th>Visits</th><th>Spent (KES)</th><th>Status</th></tr>
    """
    for c in customers:
        html += f"""
            <tr>
                <td>{c.name}</td>
                <td>{c.phone}</td>
                <td>{c.total_visits}</td>
                <td>{c.total_spent}</td>
                <td><span class="status {c.status}">{c.status.title()}</span></td>
            </tr>
        """
    html += "</table></body></html>"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"campopawa_customers_{vendor.business_name}.pdf\"'

    pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    return response


# --- Loyalty (Premium) ---
@login_required
@premium_required
def loyalty_dashboard(request):
    vendor = request.user
    programs = LoyaltyProgram.objects.filter(vendor=vendor, is_active=True)

    program_data = []
    for prog in programs:
        cards = LoyaltyCard.objects.filter(program=prog).select_related('customer')
        ready = cards.filter(stamps__gte=prog.visits_required).count()
        program_data.append({
            'program': prog,
            'total_enrolled': cards.count(),
            'rewards_ready': ready,
            'cards': cards.order_by('-stamps')[:10],
        })

    return render(request, 'customers/loyalty.html', {
        'page': 'customers',
        'program_data': program_data,
    })


@login_required
@premium_required
def loyalty_create(request):
    vendor = request.user
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        visits = int(request.POST.get('visits_required', 5) or 5)
        reward = request.POST.get('reward_description', '').strip()

        if name and reward:
            LoyaltyProgram.objects.create(
                vendor=vendor,
                name=name,
                visits_required=visits,
                reward_description=reward,
            )
            messages.success(request, f"Loyalty program '{name}' created!")
        else:
            messages.error(request, "Please fill in all fields.")
    return redirect('customers:loyalty_dashboard')


@login_required
@premium_required
def loyalty_stamp(request, card_id):
    """Add a stamp to a customer's loyalty card."""
    card = get_object_or_404(LoyaltyCard, pk=card_id, program__vendor=request.user)
    if request.method == 'POST':
        card.stamps += 1
        card.last_stamped = timezone.now()

        if card.is_reward_ready:
            card.rewards_earned += 1
            card.stamps = 0
            messages.success(request, f"🎉 {card.customer.name} earned a reward: {card.program.reward_description}!")
        else:
            messages.success(request, f"Stamp added! {card.customer.name}: {card.stamps}/{card.program.visits_required}")

        card.save()
    return redirect('customers:loyalty_dashboard')


# --- Smart Reminders (Premium) ---
@login_required
@premium_required
def smart_reminders(request):
    vendor = request.user
    today = timezone.now().date()

    customers = Customer.objects.filter(vendor=vendor)

    at_risk = []
    for c in customers:
        last_purchase = c.purchases.order_by('-purchased_at').first()
        if last_purchase:
            days_since = (today - last_purchase.purchased_at.date()).days
            if days_since >= 14:
                at_risk.append({
                    'customer': c,
                    'days_since': days_since,
                    'last_purchase': last_purchase,
                    'suggested_message': f"Hi {c.name}! We haven't seen you in a while. Come back and enjoy a special offer at {vendor.business_name}! 🎉"
                })

    at_risk.sort(key=lambda x: x['days_since'], reverse=True)

    pending = Reminder.objects.filter(vendor=vendor, status='pending').select_related('customer')

    return render(request, 'customers/reminders.html', {
        'page': 'customers',
        'at_risk': at_risk,
        'pending_reminders': pending,
        'total_at_risk': len(at_risk),
    })


@login_required
@premium_required
def send_reminder(request, customer_id):
    if request.method == 'POST':
        vendor = request.user
        customer = get_object_or_404(Customer, pk=customer_id, vendor=vendor)
        message = request.POST.get('message', '').strip()

        if message and customer.phone:
            try:
                import africastalking
                africastalking.initialize(
                    username=getattr(settings, 'AT_USERNAME', 'sandbox'),
                    api_key=getattr(settings, 'AT_API_KEY', '')
                )
                sms = africastalking.SMS
                sms.send(message, [customer.phone], sender_id=getattr(settings, 'AT_SENDER_ID', 'CampoPawa'))

                Reminder.objects.create(
                    vendor=vendor,
                    customer=customer,
                    message=message,
                    status='sent',
                    sent_at=timezone.now(),
                )
                messages.success(request, f"Reminder sent to {customer.name}!")
            except Exception as e:
                messages.error(request, f"Failed to send: {e}")
        else:
            messages.error(request, "Message and phone number required.")

    return redirect('customers:smart_reminders')


@login_required
@premium_required
def dismiss_reminder(request, customer_id):
    if request.method == 'POST':
        vendor = request.user
        customer = get_object_or_404(Customer, pk=customer_id, vendor=vendor)

        Reminder.objects.create(
            vendor=vendor,
            customer=customer,
            message='[Dismissed by vendor]',
            status='dismissed',
        )
        messages.info(request, f"{customer.name} dismissed from reminders.")

    return redirect('customers:smart_reminders')


# --- Receipts (Premium) ---
@login_required
@premium_required
def send_receipt(request, purchase_id):
    if request.method == 'POST':
        vendor = request.user
        purchase = get_object_or_404(Purchase, pk=purchase_id, customer__vendor=vendor)
        customer = purchase.customer

        receipt, created = Receipt.objects.get_or_create(
            purchase=purchase,
            defaults={'receipt_number': Receipt.generate_number()}
        )

        if customer.phone:
            message = (
                f"RECEIPT #{receipt.receipt_number}\n"
                f"{vendor.business_name}\n"
                f"Amount: KES {purchase.amount}\n"
                f"Date: {purchase.purchased_at.strftime('%d %b %Y %H:%M')}\n"
                f"Customer: {customer.name}\n"
                f"Thank you for your business!"
            )

            try:
                import africastalking
                africastalking.initialize(
                    username=getattr(settings, 'AT_USERNAME', 'sandbox'),
                    api_key=getattr(settings, 'AT_API_KEY', '')
                )
                sms = africastalking.SMS
                sms.send(message, [customer.phone], sender_id=getattr(settings, 'AT_SENDER_ID', 'CampoPawa'))

                receipt.sent_via_sms = True
                receipt.sent_at = timezone.now()
                receipt.save()

                messages.success(request, f"Receipt sent to {customer.name}!")
            except Exception as e:
                messages.error(request, f"Failed to send receipt: {e}")
        else:
            messages.error(request, "Customer has no phone number.")

    return redirect('customers:customer_detail', pk=purchase.customer.pk)