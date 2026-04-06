from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Q

from vendors.models import Vendor
from billing.models import Subscription, PLAN_PRICES

@login_required
@user_passes_test(lambda u: u.is_superuser)
def saas_overview(request):
    now = timezone.now()
    two_weeks_ago = now - relativedelta(days=14)
    three_days_from_now = now + relativedelta(days=3)

    # 1. Total MRR Calculation
    active_subscriptions = Subscription.objects.filter(
        expires_at__gte=now
    ).exclude(plan='free')
    
    total_mrr = sum([PLAN_PRICES.get(sub.plan, 0) for sub in active_subscriptions])

    # 2. Vertical Distribution
    all_vendors = Vendor.objects.filter(is_superuser=False)
    total_vendors = all_vendors.count()
    
    retail_count = all_vendors.filter(business_type__in=['general', 'food', 'thrift', 'barber']).count()
    ngo_count = all_vendors.filter(business_type='ngo').count()
    resort_count = all_vendors.filter(business_type='resort').count()

    # 3. Churn Radar
    # A vendor is at risk if their subscription expires within 3 days OR they haven't logged in for 14 days
    churn_risks = all_vendors.filter(
        Q(last_login__isnull=True) | Q(last_login__lt=two_weeks_ago) |
        Q(subscription__expires_at__lte=three_days_from_now)
    ).distinct().select_related('subscription').order_by('last_login')

    context = {
        'total_mrr': total_mrr,
        'total_vendors': total_vendors,
        'retail_count': retail_count,
        'ngo_count': ngo_count,
        'resort_count': resort_count,
        'churn_risks': churn_risks,
        'active_subscriptions_count': active_subscriptions.count(),
    }
    
    return render(request, 'admin_dashboard/saas_overview.html', context)
