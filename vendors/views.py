from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, VendorProfileForm
from customers.models import Customer, Purchase
from promotions.models import Promotion
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'vendors/landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('email'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        error = "Invalid email or password."
    return render(request, 'vendors/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            # Create free subscription automatically
            from billing.models import Subscription
            Subscription.objects.create(vendor=vendor, plan='free')
            login(request, vendor)
            messages.success(request, f"Welcome to CampoPawa, {vendor.business_name}!")
            return redirect('dashboard')
    return render(request, 'vendors/register.html', {'form': form})


@login_required
def dashboard(request):
    vendor   = request.user
    now      = timezone.now()
    week_ago = now - timedelta(days=7)

    customers = Customer.objects.filter(vendor=vendor)
    total_customers = customers.count()

    # Repeat rate: customers with more than 1 purchase
    repeat_customers = customers.annotate(
        pc=Count('purchases')
    ).filter(pc__gt=1).count()
    repeat_rate = round((repeat_customers / total_customers * 100) if total_customers else 0)

    # Revenue this week
    week_revenue = Purchase.objects.filter(
        customer__vendor=vendor,
        purchased_at__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Promo responses this week
    promo_responses = Promotion.objects.filter(
        vendor=vendor,
        sent_at__gte=week_ago,
        status='sent'
    ).aggregate(total=Sum('response_count'))['total'] or 0

    # Recent 5 customers
    recent_customers = customers.order_by('-added_at')[:5]

    # At-risk: no purchase in 14+ days
    at_risk_ids = customers.filter(
        purchases__purchased_at__lt=now - timedelta(days=14)
    ).values_list('id', flat=True).distinct()
    at_risk_count = len(set(at_risk_ids))

    context = {
        'total_customers':  total_customers,
        'repeat_rate':      repeat_rate,
        'week_revenue':     week_revenue,
        'promo_responses':  promo_responses,
        'recent_customers': recent_customers,
        'at_risk_count':    at_risk_count,
        'customer_limit':   vendor.customer_limit,
    }
    return render(request, 'dashboard/overview.html', context)


@login_required
def profile_view(request):
    form = VendorProfileForm(instance=request.user)
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    return render(request, 'vendors/profile.html', {'form': form})
