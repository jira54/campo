from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Customer, Purchase
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
    purchases = customer.purchases.all()
    pform     = PurchaseForm()

    if request.method == 'POST':
        pform = PurchaseForm(request.POST)
        if pform.is_valid():
            p          = pform.save(commit=False)
            p.customer = customer
            p.save()
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