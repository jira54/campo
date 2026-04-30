from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from vendors.models import Vendor
from billing.models import Subscription, Payment
from datetime import timedelta
from .models import AdminActivityLog
from .utils import log_admin_action


@login_required
def dashboard(request):
    """Main admin dashboard with overview statistics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    # Get statistics
    total_users = Vendor.objects.count()
    active_subscriptions = Subscription.objects.filter(plan__in=['premium_retail', 'enterprise_ngo', 'enterprise_resort']).count()
    free_users = Subscription.objects.filter(plan='free').count()
    
    # Revenue calculations
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Payment.objects.filter(
        status='confirmed',
        confirmed_at__gte=this_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_revenue = Payment.objects.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
    
    # New signups
    today = timezone.now().date()
    new_today = Vendor.objects.filter(created_at__date=today).count()
    new_week = Vendor.objects.filter(created_at__gte=today - timedelta(days=7)).count()
    new_month = Vendor.objects.filter(created_at__gte=this_month).count()
    
    # Trial users
    active_trials = Vendor.objects.filter(trial_end_date__gt=timezone.now()).count()
    expired_trials = Vendor.objects.filter(trial_end_date__lte=timezone.now(), trial_end_date__isnull=False).count()
    
    # Recent activity
    recent_users = Vendor.objects.order_by('-created_at')[:5]
    recent_payments = Payment.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'free_users': free_users,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'new_today': new_today,
        'new_week': new_week,
        'new_month': new_month,
        'active_trials': active_trials,
        'expired_trials': expired_trials,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
    }
    
    return render(request, 'platform_admin/dashboard.html', context)


@login_required
def user_list(request):
    """List all users with filtering"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    users = Vendor.objects.all().order_by('-created_at')
    
    # Filtering
    search_query = request.GET.get('search', '')
    plan_filter = request.GET.get('plan', '')
    business_type_filter = request.GET.get('business_type', '')
    
    if search_query:
        users = users.filter(
            Q(business_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if plan_filter:
        users = users.filter(subscription__plan=plan_filter)
    
    if business_type_filter:
        users = users.filter(business_type=business_type_filter)
    
    context = {
        'users': users,
        'search_query': search_query,
        'plan_filter': plan_filter,
        'business_type_filter': business_type_filter,
    }
    
    return render(request, 'platform_admin/user_list.html', context)


@login_required
def user_detail(request, user_id):
    """Detailed view of a single user"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    user = get_object_or_404(Vendor, id=user_id)
    subscription = getattr(user, 'subscription', None)
    payments = user.payments.all().order_by('-created_at')[:10]
    
    context = {
        'user': user,
        'subscription': subscription,
        'payments': payments,
    }
    
    return render(request, 'platform_admin/user_detail.html', context)


@login_required
def change_plan(request, user_id):
    """Manually change user's subscription plan"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    user = get_object_or_404(Vendor, id=user_id)
    
    if request.method == 'POST':
        new_plan = request.POST.get('plan')
        duration = request.POST.get('duration', '1')
        notes = request.POST.get('notes', '')
        
        # Get or create subscription
        subscription, created = Subscription.objects.get_or_create(vendor=user)
        
        # Update plan
        subscription.plan = new_plan
        
        # Set expiry based on duration
        if new_plan != 'free':
            if duration == '1':
                subscription.expires_at = timezone.now() + timedelta(days=30)
            elif duration == '3':
                subscription.expires_at = timezone.now() + timedelta(days=90)
            elif duration == '6':
                subscription.expires_at = timezone.now() + timedelta(days=180)
            elif duration == '12':
                subscription.expires_at = timezone.now() + timedelta(days=365)
            elif duration == 'indefinite':
                subscription.expires_at = None
        else:
            subscription.expires_at = None
        
        subscription.save()
        
        # Log admin action
        log_admin_action(
            request, 
            'plan_change', 
            target_user=user, 
            description=f'Changed plan from {old_plan} to {new_plan} for {duration} duration'
        )
        
        messages.success(request, f'Successfully changed plan for {user.business_name} to {new_plan}.')
        return redirect('platform_admin:user_detail', user_id=user_id)
    
    context = {
        'user': user,
        'subscription': getattr(user, 'subscription', None),
    }
    
    return render(request, 'platform_admin/change_plan.html', context)


@login_required
def extend_trial(request, user_id):
    """Extend user's trial period"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    user = get_object_or_404(Vendor, id=user_id)
    
    if request.method == 'POST':
        days = int(request.POST.get('days', 7))
        notes = request.POST.get('notes', '')
        
        if user.trial_end_date and user.trial_end_date > timezone.now():
            user.trial_end_date += timedelta(days=days)
        else:
            user.trial_end_date = timezone.now() + timedelta(days=days)
        
        user.save()
        
        # Log admin action
        log_admin_action(
            request, 
            'trial_extend', 
            target_user=user, 
            description=f'Extended trial by {days} days. Notes: {notes}'
        )
        
        messages.success(request, f'Successfully extended trial for {user.business_name} by {days} days.')
        return redirect('platform_admin:user_detail', user_id=user_id)
    
    context = {
        'user': user,
    }
    
    return render(request, 'platform_admin/extend_trial.html', context)


@login_required
def payment_list(request):
    """List all payments with filtering"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    payments = Payment.objects.all().order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    plan_filter = request.GET.get('plan', '')
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    if plan_filter:
        payments = payments.filter(plan_paid_for=plan_filter)
    
    context = {
        'payments': payments,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
    }
    
    return render(request, 'platform_admin/payment_list.html', context)


@login_required
def manual_payment(request):
    """Add manual payment (bank transfer, cash, etc.)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        plan_paid_for = request.POST.get('plan_paid_for')
        transaction_reference = request.POST.get('transaction_reference')
        payment_date = request.POST.get('payment_date')
        notes = request.POST.get('notes', '')
        
        vendor = get_object_or_404(Vendor, id=vendor_id)
        
        # Create payment
        payment = Payment.objects.create(
            vendor=vendor,
            amount=amount,
            payment_method=payment_method,
            plan_paid_for=plan_paid_for,
            transaction_reference=transaction_reference,
            payment_date=payment_date,
            notes=notes,
            status='confirmed',
            confirmed_at=timezone.now()
        )
        
        # Update subscription
        subscription, created = Subscription.objects.get_or_create(vendor=vendor)
        subscription.plan = plan_paid_for
        subscription.expires_at = timezone.now() + timedelta(days=30)
        subscription.save()
        
        # Log admin action
        log_admin_action(
            request, 
            'payment_manual', 
            target_user=vendor, 
            description=f'Added manual payment of KES {amount} via {payment_method} for {plan_paid_for}'
        )
        
        messages.success(request, f'Successfully added manual payment of KES {amount} for {vendor.business_name}.')
        return redirect('platform_admin:payment_list')
    
    context = {
        'vendors': Vendor.objects.all(),
    }
    
    return render(request, 'platform_admin/manual_payment.html', context)


@login_required
def confirm_payment(request, payment_id):
    """Confirm a pending payment"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'pending':
        payment.status = 'confirmed'
        payment.confirmed_at = timezone.now()
        payment.save()
        
        # Update subscription
        subscription, created = Subscription.objects.get_or_create(vendor=payment.vendor)
        subscription.plan = payment.plan_paid_for
        subscription.expires_at = timezone.now() + timedelta(days=30)
        subscription.save()
        
        # Log admin action
        log_admin_action(
            request, 
            'payment_confirm', 
            target_user=payment.vendor, 
            description=f'Confirmed payment of KES {payment.amount} for {payment.plan_paid_for}'
        )
        
        messages.success(request, f'Payment confirmed for {payment.vendor.business_name}.')
    else:
        messages.warning(request, 'Payment is not in pending status.')
    
    return redirect('platform_admin:payment_list')


@login_required
def reject_payment(request, payment_id):
    """Reject a pending payment"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('/dashboard/')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'pending':
        payment.status = 'failed'
        payment.save()
        
        # Log admin action
        log_admin_action(
            request, 
            'payment_reject', 
            target_user=payment.vendor, 
            description=f'Rejected payment of KES {payment.amount} for {payment.plan_paid_for}'
        )
        
        messages.success(request, f'Payment rejected for {payment.vendor.business_name}.')
    else:
        messages.warning(request, 'Payment is not in pending status.')
    
    return redirect('platform_admin:payment_list')
