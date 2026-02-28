from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from vendors.decorators import premium_required
from .models import CreditRecord, CreditPayment
from customers.models import Customer


@login_required
@premium_required
def credit_list(request):
    vendor = request.user
    records = CreditRecord.objects.filter(vendor=vendor)

    # Update overdue statuses
    for record in records:
        if record.is_overdue and record.status not in ['paid']:
            record.status = 'overdue'
            record.save()

    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        records = records.filter(status=status_filter)

    # Search
    search = request.GET.get('q', '')
    if search:
        records = records.filter(
            Q(debtor_name__icontains=search) |
            Q(debtor_phone__icontains=search)
        )

    # Summary stats
    active = CreditRecord.objects.filter(vendor=vendor).exclude(status='paid')
    total_owed = active.aggregate(
        total=Sum('amount_given') - Sum('amount_paid')
    )['total'] or 0
    overdue_count = active.filter(status='overdue').count()
    total_records = active.count()

    return render(request, 'credit/credit_list.html', {
        'records': records,
        'total_owed': total_owed,
        'overdue_count': overdue_count,
        'total_records': total_records,
        'status_filter': status_filter,
        'search': search,
        'page': 'credit',
    })


@login_required
@premium_required
def credit_add(request):
    vendor = request.user
    customers = Customer.objects.filter(vendor=vendor).order_by('name')

    if request.method == 'POST':
        # Check if linking to existing customer
        customer_id = request.POST.get('customer_id')
        debtor_name = request.POST.get('debtor_name', '').strip()
        debtor_phone = request.POST.get('debtor_phone', '').strip()
        amount_given = request.POST.get('amount_given')
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date') or None
        credit_limit = request.POST.get('credit_limit') or None

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id, vendor=vendor)
                debtor_name = customer.name
                debtor_phone = customer.phone
            except Customer.DoesNotExist:
                pass

        if debtor_name and amount_given:
            record = CreditRecord.objects.create(
                vendor=vendor,
                customer=customer,
                debtor_name=debtor_name,
                debtor_phone=debtor_phone,
                amount_given=amount_given,
                description=description,
                due_date=due_date,
                credit_limit=credit_limit,
            )
            messages.success(request, f"Credit of KES {amount_given} recorded for {debtor_name}.")
            return redirect('credit:credit_list')
        else:
            messages.error(request, "Name and amount are required.")

    return render(request, 'credit/credit_add.html', {
        'customers': customers,
        'page': 'credit',
    })


@login_required
@premium_required
def credit_detail(request, pk):
    vendor = request.user
    record = get_object_or_404(CreditRecord, pk=pk, vendor=vendor)
    payments = record.payments.all().order_by('-paid_at')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note', '').strip()

        if amount:
            payment_amount = float(amount)
            if payment_amount > float(record.amount_remaining):
                messages.error(request, "Payment exceeds amount owed.")
            else:
                CreditPayment.objects.create(
                    credit=record,
                    amount=payment_amount,
                    note=note,
                )
                record.amount_paid += float(amount)
                record.update_status()
                messages.success(request, f"Payment of KES {amount} recorded! ✅")
                return redirect('credit:credit_detail', pk=pk)

    return render(request, 'credit/credit_detail.html', {
        'record': record,
        'payments': payments,
        'page': 'credit',
        'payment_percent': int((record.amount_paid / record.amount_given) * 100) if record.amount_given > 0 else 0,
    })


@login_required
@premium_required
def credit_send_reminder(request, pk):
    """Send SMS reminder to debtor."""
    if request.method == 'POST':
        vendor = request.user
        record = get_object_or_404(CreditRecord, pk=pk, vendor=vendor)

        if not record.debtor_phone:
            messages.error(request, "No phone number for this debtor.")
            return redirect('credit:credit_detail', pk=pk)

        message = (
            f"Hi {record.debtor_name}, this is a reminder from {vendor.business_name}. "
            f"You have an outstanding balance of KES {record.amount_remaining}."
        )
        if record.due_date:
            message += f" Due date: {record.due_date.strftime('%d %b %Y')}."
        message += " Please settle at your earliest convenience. Thank you!"

        try:
            import africastalking
            from django.conf import settings
            africastalking.initialize(
                username=settings.AT_USERNAME,
                api_key=settings.AT_API_KEY
            )
            sms = africastalking.SMS
            sms.send(message, [record.debtor_phone], sender_id=settings.AT_SENDER_ID)
            messages.success(request, f"Reminder sent to {record.debtor_name}! 📲")
        except Exception as e:
            # Silently handle SMS errors - show friendly message
            messages.info(request, f"Reminder prepared for {record.debtor_name}. You can send it manually! 📝")

    return redirect('credit:credit_detail', pk=pk)


@login_required
@premium_required
def credit_delete(request, pk):
    record = get_object_or_404(CreditRecord, pk=pk, vendor=request.user)
    if request.method == 'POST':
        name = record.debtor_name
        record.delete()
        messages.success(request, f"Credit record for {name} deleted.")
    return redirect('credit:credit_list')
