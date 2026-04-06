from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy

from .forms import RegisterForm, VendorProfileForm
from .greetings import get_daily_context
from customers.models import Customer, Purchase
from promotions.models import Promotion
from credit.models import CreditRecord

def landing(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('vendors:dashboard')
    return render(request, 'vendors/landing.html')

def root_redirect(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('vendors:dashboard')
    return render(request, 'vendors/landing.html')

def login_view(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('vendors:dashboard')
    
    # Check if coming from registration with stored email
    stored_email = request.session.get('registration_email')
    stored_error = None
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user:
            # Clear stored registration email on successful login
            if 'registration_email' in request.session:
                del request.session['registration_email']
            login(request, user)
            return redirect('vendors:dashboard')
        else:
            # Generic message — do not reveal whether email exists
            if not email or not password:
                error = "Please enter your email and password."
            else:
                error = "Invalid email or password. Please try again."
    else:
        error = stored_error  # Use stored error if coming from registration
        
    # Pre-fill form with registration email if available
    initial_email = stored_email if stored_email else ''
    
    return render(request, 'vendors/login.html', {
        'error': error,
        'initial_email': initial_email
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            email = form.cleaned_data['email']  # Get registered email

            from billing.models import Subscription
            Subscription.objects.create(vendor=vendor, plan='free')

            # Add 10-day free trial
            vendor.trial_end_date = timezone.now() + timedelta(days=10)
            vendor.save()

            # Logout current user to prevent session conflicts
            if request.user.is_authenticated:
                logout(request)
                
            # Store email in session for login form pre-fill
            request.session['registration_email'] = email
                
            messages.success(request, "Account created successfully. Please sign in to continue.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'vendors/register.html', {'form': form})

@login_required
def dashboard(request):
    vendor   = request.user
    
    # --- Enterprise Dashboard Router ---
    if vendor.business_type == 'ngo':
        return redirect('ngo_portal:dashboard')
    elif vendor.business_type == 'resort':
        return redirect('resort_portal:dashboard')

    now      = timezone.now()
    
    # Check if trial has expired and downgrade if needed
    if vendor.trial_end_date and vendor.trial_end_date < now:
        vendor.trial_end_date = None
        vendor.save()
    
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

    at_risk_count = customers.annotate(
        last_purchase_date=models.Max('purchases__purchased_at')
    ).filter(
        last_purchase_date__lt=now - timedelta(days=14),
        last_purchase_date__isnull=False,
    ).count()

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
        _credit_agg = CreditRecord.objects.filter(
            vendor=vendor
        ).exclude(status='paid').aggregate(
            given=Sum('amount_given'),
            paid=Sum('amount_paid')
        )
        total_credit_owed = (_credit_agg['given'] or 0) - (_credit_agg['paid'] or 0)

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


@login_required
def quick_sale(request):
    if request.method == 'POST':
        customer_phone = request.POST.get('customer_phone', '').strip()
        amount = request.POST.get('amount')
        notes = request.POST.get('notes', '')
        
        try:
            amount = float(amount)
            
            from customers.models import Customer, Purchase, Service
            
            # Auto-CRM for Cash Sales
            if customer_phone:
                customer = Customer.objects.filter(vendor=request.user, phone=customer_phone).first()
                if not customer:
                    customer = Customer.objects.create(
                        vendor=request.user,
                        phone=customer_phone,
                        name="Cash Customer"
                    )
            else:
                # Anonymous walk-in
                customer, _ = Customer.objects.get_or_create(
                    vendor=request.user,
                    name="Walk-in Customer",
                    defaults={'phone': ''}
                )
            
            # Get a default service for quick sales
            default_service = Service.objects.filter(vendor=request.user).first()
            if not default_service:
                default_service = Service.objects.create(
                    vendor=request.user,
                    name="Quick Sale",
                    description="Quick sale from dashboard",
                    price=amount
                )
            
            Purchase.objects.create(
                customer=customer,
                amount=amount,
                service=default_service.name,
                notes=notes or "Quick sale from dashboard"
            )
            
            messages.success(request, f"Sale of KES {amount:.2f} logged for {customer.name}")
            return redirect('vendors:dashboard')
            
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect('vendors:dashboard')
    
    return redirect('vendors:dashboard')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'vendors/password_reset.html'
    email_template_name = 'vendors/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'vendors/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')