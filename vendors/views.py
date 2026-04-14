from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.db.models import Sum, Count, Q, Max
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import RegisterForm, VendorProfileForm
from .greetings import get_daily_context
from customers.models import Customer, Purchase, Service
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
                
            messages.success(request, f"Welcome to CampoPawa! Your {vendor.get_business_type_display()} dashboard is ready.")
            
            # Auto-Login after registration (Instant Onboarding)
            from django.contrib.auth import login
            login(request, vendor, backend='django.contrib.auth.backends.ModelBackend')
            
            return redirect('vendors:dashboard')
    else:
        form = RegisterForm()
    
    if request.method == 'POST' and not form.is_valid():
        messages.error(request, "Please check the form for errors and try again.")

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
        last_purchase_date=Max('purchases__purchased_at')
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
        # Check if services exist for Quick Sale visibility
        'has_services': Service.objects.filter(vendor=vendor, is_active=True).exists(),
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
            
            from customers.models import Customer, Purchase

            # Get or create the generic Walk-in Customer for this vendor
            # to avoid cluttering the CRM with "Cash Customer" entries
            walkin_customer, _ = Customer.objects.get_or_create(
                vendor=request.user,
                name="Walk-in Customer",
                defaults={'phone': ''}
            )

            customer = walkin_customer
            if customer_phone:
                # Try to find existing customer if phone provided
                existing_customer = Customer.objects.filter(vendor=request.user, phone=customer_phone).first()
                if existing_customer:
                    customer = existing_customer
                else:
                    # If new phone, we keep it as Walk-in but note the phone
                    # per user request to avoid "storing as customer in customer records"
                    notes = f"{notes} | Phone: {customer_phone}" if notes else f"Phone: {customer_phone}"

            Purchase.objects.create(
                customer=customer,
                amount=amount,
                service="Quick Sale",  # Use literal string to avoid auto-creating Service objects
                notes=notes or "Quick sale from dashboard"
            )

            messages.success(request, f"Sale of KES {amount:.2f} logged.")
            return redirect('vendors:dashboard')
            
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect('vendors:dashboard')
    
    return redirect('vendors:dashboard')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'vendors/password_reset.html'
    email_template_name = 'vendors/password_reset_email.html'
    html_email_template_name = 'vendors/password_reset_email_html.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'vendors/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Send security notification email after successful password change
        user = self.user
        subject = "Security Alert: Password Successfully Updated"
        html_message = render_to_string('vendors/password_reset_success_email.html', {
            'user': user,
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                None,  # Uses DEFAULT_FROM_EMAIL
                [user.email],
                html_message=html_message,
                fail_silently=True
            )
        except Exception:
            pass
            
        return response

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)