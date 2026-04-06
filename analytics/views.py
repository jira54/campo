from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate, ExtractWeekDay
from datetime import timedelta
import json
from customers.models import Customer, Purchase
from billing.decorators import premium_required


@login_required
def analytics_dashboard(request):
    vendor = request.user
    
    # Redirect non-premium users with message
    if not vendor.is_premium:
        messages.warning(
            request,
            "Analytics requires a Premium plan. "
            "Upgrade to Premium for KES 300/month for detailed insights."
        )
        return redirect('billing:upgrade')
    
    today = timezone.now().date()

    context = {
        'page': 'analytics',
        'is_premium': vendor.is_premium,
        'total_customers': Customer.objects.filter(vendor=vendor).count(),
    }

    # --- Date range ---
    period = request.GET.get('period', '7')  # 7, 30, 90
    days = int(period)
    start_date = today - timedelta(days=days)

    purchases = Purchase.objects.filter(
        customer__vendor=vendor,
        purchased_at__date__gte=start_date
    )

    # --- Summary stats ---
    summary = purchases.aggregate(
        total_revenue=Sum('amount'),
        total_transactions=Count('id'),
    )

    # --- Daily breakdown ---
    daily = purchases.annotate(
        day=TruncDate('purchased_at')
    ).values('day').annotate(
        revenue=Sum('amount'),
        count=Count('id'),
    ).order_by('day')

    # --- Top customers by spend ---
    top_customers = Customer.objects.filter(vendor=vendor).annotate(
        period_spent=Sum('purchases__amount', filter=Q(purchases__purchased_at__date__gte=start_date))
    ).exclude(period_spent=None).order_by('-period_spent')[:10]

    # --- Revenue by day of week ---
    by_weekday = purchases.annotate(
        weekday=ExtractWeekDay('purchased_at')
    ).values('weekday').annotate(
        revenue=Sum('amount'),
    ).order_by('weekday')

    weekday_names = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}
    weekday_data = [{'day': weekday_names.get(d['weekday'], '?'), 'revenue': float(d['revenue'] or 0)} for d in by_weekday]
    best_day = max(weekday_data, key=lambda x: x['revenue'])['day'] if weekday_data else '—'

    # --- Average daily revenue ---
    total_rev = summary['total_revenue'] or 0
    avg_daily = total_rev / max(days, 1)

    # --- Week-over-week change ---
    prev_start = start_date - timedelta(days=days)
    prev_revenue = Purchase.objects.filter(
        customer__vendor=vendor,
        purchased_at__date__gte=prev_start,
        purchased_at__date__lt=start_date,
    ).aggregate(total=Sum('amount'))['total'] or 0

    if prev_revenue > 0:
        change_pct = ((total_rev - prev_revenue) / prev_revenue) * 100
    else:
        change_pct = 100 if total_rev > 0 else 0

    # Chart-ready: revenue by day (labels + values)
    daily_list = list(daily)
    chart_labels = [d['day'].strftime('%a %d') if d.get('day') else '' for d in daily_list]
    chart_revenue = [float(d.get('revenue') or 0) for d in daily_list]

    # Service breakdown for this period
    service_sales = []
    service_names = []
    service_revenues = []
    
    # Get all services for this vendor
    from customers.models import Service
    vendor_services = Service.objects.filter(vendor=vendor)
    
    # Calculate revenue per service
    for service in vendor_services:
        service_revenue = purchases.filter(
            service__contains=service.name
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        if service_revenue > 0:
            service_sales.append({
                'name': service.name,
                'revenue': float(service_revenue),
                'count': purchases.filter(service__contains=service.name).count()
            })
            service_names.append(service.name)
            service_revenues.append(float(service_revenue))
    
    # Sort by revenue
    service_sales.sort(key=lambda x: x['revenue'], reverse=True)

    # Segment breakdown for doughnut (all customers, not just period)
    all_customers = list(Customer.objects.filter(vendor=vendor).prefetch_related('purchases'))
    segments = {
        'loyal': sum(1 for c in all_customers if c.status == 'loyal'),
        'regular': sum(1 for c in all_customers if c.status == 'regular'),
        'new': sum(1 for c in all_customers if c.status == 'new'),
        'atrisk': sum(1 for c in all_customers if c.status == 'atrisk'),
    }

    context.update({
        'period': period,
        'start_date': start_date,
        'total_revenue': total_rev,
        'total_transactions': summary['total_transactions'] or 0,
        'avg_daily': round(avg_daily),
        'change_pct': round(change_pct, 1),
        'daily_data': list(daily),
        'top_customers': top_customers,
        'weekday_data': weekday_data,
        'best_day': best_day,
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue': json.dumps(chart_revenue),
        'segments': json.dumps(segments),
        'service_sales': service_sales[:10],  # Top 10 services
        'service_names': json.dumps(service_names),
        'service_revenues': json.dumps(service_revenues),
    })

    return render(request, 'analytics/dashboard.html', context)
