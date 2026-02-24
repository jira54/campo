from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer, Purchase


@login_required
def analytics_dashboard(request):
    vendor = request.user
    now    = timezone.now()

    customers = Customer.objects.filter(vendor=vendor)
    total     = customers.count()

    # Basic stats (free tier gets these too)
    context = {
        'total_customers': total,
        'is_premium':      vendor.is_premium,
    }

    if vendor.is_premium:
        # Full analytics — premium only
        month_ago  = now - timedelta(days=30)
        week_ago   = now - timedelta(days=7)

        # Retention rate
        repeat = customers.annotate(pc=Count('purchases')).filter(pc__gt=1).count()
        context['retention_rate'] = round(repeat / total * 100) if total else 0

        # Revenue
        month_rev = Purchase.objects.filter(
            customer__vendor=vendor, purchased_at__gte=month_ago
        ).aggregate(t=Sum('amount'))['t'] or 0
        context['month_revenue'] = month_rev

        # Avg spend per visit
        avg_spend = Purchase.objects.filter(
            customer__vendor=vendor
        ).aggregate(a=Avg('amount'))['a'] or 0
        context['avg_spend'] = round(avg_spend)

        # Top customers
        # Use spent_total to avoid conflict with @property total_spent
        context['top_customers'] = customers.annotate(
            spent_total=Sum('purchases__amount'),
            visit_count=Count('purchases')
        ).order_by('-spent_total')[:5]

        # Weekly revenue (last 7 days, grouped by day)
        context['weekly_data'] = _weekly_revenue(vendor, now)

        # Segment breakdown
        all_c = list(customers)
        context['segments'] = {
            'loyal':   sum(1 for c in all_c if c.status == 'loyal'),
            'regular': sum(1 for c in all_c if c.status == 'regular'),
            'new':     sum(1 for c in all_c if c.status == 'new'),
            'atrisk':  sum(1 for c in all_c if c.status == 'atrisk'),
        }
    else:
        # Free tier sees a locked upgrade prompt instead of charts
        context['locked_features'] = [
            'Retention rate tracking',
            'Revenue analytics',
            'Top customer ranking',
            'Weekly revenue chart',
            'Customer segment breakdown',
        ]

    return render(request, 'analytics/dashboard.html', context)


def _weekly_revenue(vendor, now):
    """Returns list of {day, revenue} for the last 7 days."""
    result = []
    for i in range(6, -1, -1):
        day   = now - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = day.replace(hour=23, minute=59, second=59)
        rev   = Purchase.objects.filter(
            customer__vendor=vendor,
            purchased_at__range=(start, end)
        ).aggregate(t=Sum('amount'))['t'] or 0
        result.append({'day': day.strftime('%a'), 'revenue': float(rev)})
    return result
