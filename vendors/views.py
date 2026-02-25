from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy

from .forms import RegisterForm, VendorProfileForm
from .greetings import get_daily_context
from customers.models import Customer, Purchase
from promotions.models import Promotion
from credit.models import CreditRecord

def landing(request):
    if request.user.is_authenticated:
        return redirect('vendors:dashboard')
    return render(request, 'vendors/landing.html')

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('vendors:dashboard')
    return redirect('vendors:landing')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('vendors:dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('email'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('vendors:dashboard')
        error = "Invalid email or password."
    return render(request, 'vendors/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            vendor = form.save()

            from billing.models import Subscription
            Subscription.objects.create(vendor=vendor, plan='free')

            messages.success(request, "Account created successfully. Please sign in to continue.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'vendors/register.html', {'form': form})


@login_required
def dashboard(request):
    vendor   = request.user
    now      = timezone.now()
    today    = now.date()
    week_ago = now - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    customers       = Customer.objects.filter(vendor=vendor)
    total_customers = customers.count()

    repeat_customers = customers.annotate(
        pc=Count('purchases')
    ).filter(pc__gt=1).count()
    repeat_rate = round((repeat_customers / total_customers * 100) if total_customers else 0)

    week_revenue = Purchase.objects.filter(
        customer__vendor=vendor,
        purchased_at__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Today's stats
    today_purchases = Purchase.objects.filter(
        customer__vendor=vendor,
        purchased_at__date=today
    )
    yesterday_purchases = Purchase.objects.filter(
        customer__vendor=vendor,
        purchased_at__date=yesterday
    )

    today_revenue = today_purchases.aggregate(total=Sum('amount'))['total'] or 0
    yesterday_revenue = yesterday_purchases.aggregate(total=Sum('amount'))['total'] or 0
    today_customers = today_purchases.values('customer').distinct().count()

    revenue_change = today_revenue - yesterday_revenue
    revenue_up = revenue_change >= 0

    promo_responses = Promotion.objects.filter(
        vendor=vendor,
        sent_at__gte=week_ago,
        status='sent'
    ).aggregate(total=Sum('response_count'))['total'] or 0

    recent_customers = customers.order_by('-added_at')[:5]

    at_risk_ids   = customers.filter(
        purchases__purchased_at__lt=now - timedelta(days=14)
    ).values_list('id', flat=True).distinct()
    at_risk_count = len(set(at_risk_ids))

    # Get login streak
    streak = getattr(vendor, 'streak', None)
    current_streak = streak.current_streak if streak else 0

    # Credit alerts for premium users
    overdue_credits = 0
    total_credit_owed = 0
    if vendor.is_premium:
        overdue_credits = CreditRecord.objects.filter(
            vendor=vendor,
            status='overdue'
        ).count()
        total_credit_owed = CreditRecord.objects.filter(
            vendor=vendor
        ).exclude(status='paid').aggregate(
            total=Sum('amount_given') - Sum('amount_paid')
        )['total'] or 0

    context = {
        'total_customers':  total_customers,
        'repeat_rate':      repeat_rate,
        'week_revenue':     week_revenue,
        'promo_responses':  promo_responses,
        'recent_customers': recent_customers,
        'at_risk_count':    at_risk_count,
        'customer_limit':   vendor.customer_limit,
        # Today's stats
        'today_revenue':    today_revenue,
        'yesterday_revenue': yesterday_revenue,
        'today_customers':  today_customers,
        'revenue_change':   abs(revenue_change),
        'revenue_up':       revenue_up,
        'today_date':       today,
        # Engagement
        'current_streak':   current_streak,
        # Credit alerts
        'overdue_credits':  overdue_credits,
        'total_credit_owed': total_credit_owed,
        # Add daily greeting context
        **get_daily_context(vendor),
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
            return redirect('/dashboard/')
    return render(request, 'vendors/profile.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'vendors/password_reset.html'
    email_template_name = 'vendors/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'vendors/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')