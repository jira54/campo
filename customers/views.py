from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import csv
import html
from decimal import Decimal

from vendors.decorators import premium_required

from django.conf import settings
from .models import Customer, Purchase, LoyaltyProgram, LoyaltyCard, Reminder, Receipt, Service
from .forms import CustomerForm, PurchaseForm


@login_required
def customer_list(request):
    vendor  = request.user
    segment = request.GET.get('segment', 'all')
    query   = request.GET.get('q', '')

    customers = Customer.objects.filter(vendor=vendor, is_active=True).prefetch_related('purchases')

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

    form = CustomerForm()
    purchase_form = PurchaseForm()
    services = Service.objects.filter(vendor=vendor, is_active=True).order_by('sort_order', 'name')
    popular_services = services.filter(is_popular=True)
    regular_services = services.filter(is_popular=False)

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        purchase_form = PurchaseForm(request.POST)
        
        if form.is_valid():
            customer = form.save(commit=False)
            customer.vendor = vendor
            # Strip premium fields for free users
            if not vendor.is_premium:
                customer.notes = ''
                customer.tags = ''
            try:
                customer.save()
                
                # Get amount paid
                amount_paid = request.POST.get('amount_paid')
                total_amount = Decimal('0')
                service_names = []
                
                # Start with amount paid if provided
                if amount_paid:
                    try:
                        total_amount += Decimal(amount_paid)
                    except (ValueError, TypeError):
                        pass
                
                # Process predefined services
                service_ids = request.POST.getlist('services')
                if service_ids:
                    # Filter out 'other' to handle separately
                    predefined_service_ids = [sid for sid in service_ids if sid != 'other']
                    if predefined_service_ids:
                        selected_services = Service.objects.filter(id__in=predefined_service_ids, vendor=vendor)
                        total_amount += sum(service.price for service in selected_services)
                        service_names.extend([service.name for service in selected_services])
                
                # Process custom service
                custom_service_name = request.POST.get('custom_service_name', '').strip()
                custom_service_price = request.POST.get('custom_service_price', '').strip()
                custom_service_desc = request.POST.get('custom_service_description', '').strip()
                
                if 'other' in service_ids and custom_service_name and custom_service_price:
                    try:
                        price = Decimal(custom_service_price)
                        total_amount += price
                        # Build custom service description
                        custom_desc = custom_service_name
                        if custom_service_desc:
                            custom_desc += f" - {custom_service_desc}"
                        service_names.append(custom_desc)
                    except (ValueError, TypeError):
                        pass
                
                # Add custom amount if provided
                custom_amount = request.POST.get('amount')
                if custom_amount:
                    try:
                        total_amount += Decimal(custom_amount)
                    except (ValueError, TypeError):
                        pass
                
                # Create purchase if there's an amount or services
                if total_amount > 0 or service_names:
                    purchase = Purchase.objects.create(
                        customer=customer,
                        amount=total_amount,
                        service=', '.join(service_names) if service_names else '',
                        notes=request.POST.get('notes', '')
                    )
                
                messages.success(request, f"{customer.name} added successfully. Karibu tena!")
                return redirect('customers:customer_list')
            except IntegrityError:
                # Find existing customer and redirect to their detail page
                existing_customer = Customer.objects.filter(vendor=vendor, phone=customer.phone).first()
                if existing_customer:
                    messages.info(request, f"Customer with phone {customer.phone} already exists. Redirected to their profile.")
                    return redirect('customers:customer_detail', pk=existing_customer.pk)
                else:
                    messages.error(request, "A customer with this phone number already exists.")
                    return redirect('customers:customer_list')

    return render(request, 'customers/add.html', {
        'form': form,
        'purchase_form': purchase_form,
        'services': services,
        'popular_services': popular_services,
        'regular_services': regular_services,
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
def customer_toggle_active(request, pk):
    customer = get_object_or_404(Customer, pk=pk, vendor=request.user)
    if request.method == 'POST':
        customer.is_active = not customer.is_active
        customer.save()
        status = "activated" if customer.is_active else "deactivated"
        messages.success(request, f"{customer.name} {status}.")
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
        first_added_str = first_added.astimezone().strftime('%Y-%m-%d') if first_added else ''
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

    html_str = f"""
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
        safe_name = html.escape(c.name)
        safe_phone = html.escape(c.phone)
        html_str += f"""
            <tr>
                <td>{safe_name}</td>
                <td>{safe_phone}</td>
                <td>{c.total_visits}</td>
                <td>{c.total_spent}</td>
                <td><span class="status {c.status}">{c.status.title()}</span></td>
            </tr>
        """
    html_str += "</table></body></html>"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"campopawa_customers_{vendor.business_name}.pdf\"'

    pisa.CreatePDF(BytesIO(html_str.encode('utf-8')), dest=response)
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
                messages.info(request, f"Reminder prepared for {customer.name}. You can send it manually! ")
        else:
            messages.info(request, f"Please add a phone number for {customer.name} to send reminders! ")

    return redirect('customers:smart_reminders')

# ... (rest of the code remains the same)
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
def view_receipt(request, purchase_id):
    """View receipt in-app and download PDF"""
    vendor = request.user
    purchase = get_object_or_404(Purchase, pk=purchase_id, customer__vendor=vendor)
    customer = purchase.customer
    
    # Get or create receipt
    receipt, created = Receipt.objects.get_or_create(
        purchase=purchase,
        defaults={'receipt_number': Receipt.generate_number()}
    )
    
    context = {
        'purchase': purchase,
        'customer': customer,
        'vendor': vendor,
        'receipt': receipt,
    }
    
    return render(request, 'customers/receipt.html', context)


@login_required
@premium_required
def download_receipt_pdf(request, purchase_id):
    """Download receipt as PDF"""
    from xhtml2pdf import pisa
    from io import BytesIO
    
    vendor = request.user
    purchase = get_object_or_404(Purchase, pk=purchase_id, customer__vendor=vendor)
    customer = purchase.customer
    
    # Get or create receipt
    receipt, created = Receipt.objects.get_or_create(
        purchase=purchase,
        defaults={'receipt_number': Receipt.generate_number()}
    )
    
    # Generate receipt HTML
    html = f"""
    <html>
    <head>
        <style>
            @page {{
                size: 58mm 100mm;
                margin: 1.5mm;
            }}
            body {{ 
                font-family: 'Arial', sans-serif; 
                font-size: 7px; 
                margin: 0;
                padding: 0;
                background: #ffffff;
                color: #333333;
                line-height: 1.0;
                width: 56mm;
            }}
            .receipt-container {{
                width: 100%;
                margin: 0;
                background: white;
                padding: 1mm;
            }}
            .center {{
                text-align: center;
                font-weight: bold;
                margin: 0.5mm 0;
            }}
            .business-name {{
                font-size: 9px;
                color: #0D8C7F;
                margin-bottom: 0.3mm;
            }}
            .receipt-number {{
                font-size: 8px;
                color: #E8871E;
                margin-bottom: 0.3mm;
            }}
            .phone {{
                font-size: 7px;
                margin-bottom: 1mm;
            }}
            .line {{
                margin: 0.5mm 0;
                font-size: 6px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .line-label {{
                color: #666;
                flex: 0 0 25%;
            }}
            .line-value {{
                color: #333;
                flex: 0 0 75%;
                text-align: right;
            }}
            .separator {{
                border-top: 1px dashed #ccc;
                margin: 1mm 0;
            }}
            .item-line {{
                margin: 0.8mm 0;
                font-size: 6px;
                display: flex;
                justify-content: space-between;
            }}
            .item-name {{
                flex: 0 0 60%;
                color: #333;
            }}
            .item-price {{
                flex: 0 0 40%;
                text-align: right;
                color: #333;
            }}
            .total-line {{
                font-weight: bold;
                font-size: 7px;
                margin: 1mm 0;
                display: flex;
                justify-content: space-between;
                color: #E8871E;
                border-top: 1px solid #E8871E;
                padding-top: 0.8mm;
            }}
            .total-label {{
                flex: 0 0 25%;
            }}
            .total-price {{
                flex: 0 0 75%;
                text-align: right;
            }}
            .authenticity {{
                text-align: center;
                margin: 1.5mm 0;
                padding: 0.8mm;
                background: #f8f8f8;
                border: 1px solid #ddd;
                font-size: 5px;
            }}
            .auth-title {{
                font-weight: bold;
                margin-bottom: 0.3mm;
                color: #0D8C7F;
            }}
            .auth-code {{
                font-family: 'Courier New', monospace;
                font-weight: bold;
                color: #0D8C7F;
                font-size: 6px;
            }}
            .footer {{
                text-align: center;
                margin-top: 1.5mm;
                font-size: 5px;
                color: #666;
            }}
            .footer strong {{
                color: #0D8C7F;
                font-size: 6px;
            }}
        </style>
    </head>
    <body>
        <div class="receipt-container">
            <div class="center business-name">{vendor.business_name}</div>
            <div class="center receipt-number">RECEIPT #{receipt.receipt_number}</div>
            <div class="center phone">{vendor.phone if vendor.phone else 'N/A'}</div>
            
            <div class="separator"></div>
            
            <div class="line">
                <span class="line-label">Customer:</span>
                <span class="line-value">{html.escape(customer.name)}</span>
            </div>
            <div class="line">
                <span class="line-label">Phone:</span>
                <span class="line-value">{html.escape(customer.phone) if customer.phone else 'N/A'}</span>
            </div>
            <div class="line">
                <span class="line-label">Date:</span>
                <span class="line-value">{purchase.purchased_at.astimezone().strftime('%d %b %Y %H:%M')}</span>
            </div>
            
            <div class="separator"></div>
            
            <div class="item-line">
                <span class="item-name">{purchase.service or 'General Purchase'}</span>
                <span class="item-price">KES {purchase.amount}</span>
            </div>
            
            <div class="separator"></div>
            
            <div class="total-line">
                <span class="total-label">TOTAL</span>
                <span class="total-price">KES {purchase.amount}</span>
            </div>
            
            <div class="separator"></div>
            
            <div class="authenticity">
                <div class="auth-title">Authenticity Code</div>
                <div class="auth-code">CP-{vendor.id:06d}-{receipt.receipt_number.split('-')[2]}</div>
                <div style="font-size: 4px; color: #999; margin-top: 0.3mm;">Digitally Verified</div>
            </div>
            
            <div class="footer">
                <div><strong>Karibu, tena!</strong></div>
                <div>{timezone.now().astimezone().strftime('%d %b %Y %H:%M')}</div>
                <div style="font-size: 4px; color: #999;">Powered by CampoPawa</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
    
    pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    
    return response


@login_required
@premium_required
def send_receipt(request, purchase_id):
    """Send receipt via SMS (Africa's Talking) - fallback to in-app"""
    if request.method == 'POST':
        vendor = request.user
        purchase = get_object_or_404(Purchase, pk=purchase_id, customer__vendor=vendor)
        customer = purchase.customer

        receipt, created = Receipt.objects.get_or_create(
            purchase=purchase,
            defaults={'receipt_number': Receipt.generate_number()}
        )

        # Try SMS, but if it fails, show in-app receipt option
        if customer.phone:
            message = (
                f"RECEIPT #{receipt.receipt_number}\n"
                f"{vendor.business_name}\n"
                f"Amount: KES {purchase.amount}\n"
                f"Date: {purchase.purchased_at.astimezone().strftime('%d %b %Y %H:%M')}\n"
                f"Customer: {customer.name}\n"
                f"Karibu, tena!"
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
                # Fallback: show in-app receipt option with friendly message
                messages.info(request, f"Receipt ready! You can view/download it below for {customer.name}. 📄")
                return redirect('customers:view_receipt', purchase_id=purchase_id)
        else:
            messages.info(request, f"No phone number for {customer.name}. You can download the receipt instead! 📱")

    return redirect('customers:customer_detail', pk=purchase.customer.pk)


# --- Services Management ---
@login_required
def services_list(request):
    """List and manage vendor's services"""
    vendor = request.user
    services = Service.objects.filter(vendor=vendor).order_by('sort_order', 'name')
    popular_services = services.filter(is_popular=True)
    regular_services = services.filter(is_popular=False)
    
    return render(request, 'customers/services.html', {
        'services': services,
        'popular_services': popular_services,
        'regular_services': regular_services,
        'page': 'services'
    })


@login_required
def service_add(request):
    """Add a new service"""
    vendor = request.user
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '0')
        is_popular = request.POST.get('is_popular') == 'on'
        
        if name and price:
            try:
                price = float(price)
                Service.objects.create(
                    vendor=vendor,
                    name=name,
                    description=description,
                    price=price,
                    is_popular=is_popular
                )
                messages.success(request, f"Service '{name}' added successfully!")
                return redirect('customers:services_list')
            except ValueError:
                messages.error(request, "Please enter a valid price.")
        else:
            messages.error(request, "Service name and price are required.")
    
    return render(request, 'customers/service_form.html', {
        'action': 'Add'
    })


@login_required
def service_edit(request, service_id):
    """Edit an existing service"""
    vendor = request.user
    service = get_object_or_404(Service, id=service_id, vendor=vendor)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '0')
        is_popular = request.POST.get('is_popular') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        if name and price:
            try:
                price = float(price)
                service.name = name
                service.description = description
                service.price = price
                service.is_popular = is_popular
                service.is_active = is_active
                service.save()
                messages.success(request, f"Service '{name}' updated successfully!")
                return redirect('customers:services_list')
            except ValueError:
                messages.error(request, "Please enter a valid price.")
        else:
            messages.error(request, "Service name and price are required.")
    
    return render(request, 'customers/service_form.html', {
        'service': service,
        'action': 'Edit'
    })


@login_required
def service_delete(request, service_id):
    """Delete a service"""
    vendor = request.user
    service = get_object_or_404(Service, id=service_id, vendor=vendor)
    
    if request.method == 'POST':
        name = service.name
        service.delete()
        messages.success(request, f"Service '{name}' deleted successfully!")
    
    return redirect('customers:services_list')


@login_required
def service_toggle_popular(request, service_id):
    """Toggle popular status of a service"""
    vendor = request.user
    service = get_object_or_404(Service, id=service_id, vendor=vendor)
    
    if request.method == 'POST':
        service.is_popular = not service.is_popular
        service.save()
        status = "added to" if service.is_popular else "removed from"
        messages.success(request, f"'{service.name}' {status} quick add!")
    
    return redirect('customers:services_list')


@login_required
def services_reorder(request):
    """Reorder services (for drag and drop)"""
    vendor = request.user
    
    if request.method == 'POST':
        service_ids = request.POST.getlist('service_ids[]')
        try:
            services_to_update = []
            for index, service_id in enumerate(service_ids):
                # Retrieve from db and update sort_order
                service = Service.objects.get(id=service_id, vendor=vendor)
                service.sort_order = index
                services_to_update.append(service)
            # Use bulk_update to perform a single query
            Service.objects.bulk_update(services_to_update, ['sort_order'])
            return HttpResponse('OK')
        except Exception as e:
            return HttpResponse('Error', status=400)
    
    return HttpResponse('Method not allowed', status=405)