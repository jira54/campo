from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
import datetime

from .decorators import resort_enterprise_required
from .models import Room, Folio, FolioCharge, Department

@login_required
@resort_enterprise_required
def resort_dashboard(request):
    vendor = request.user
    today = timezone.now().date()
    
    # Insights Engine: Room Status
    total_rooms = Room.objects.filter(vendor=vendor).count()
    occupied_rooms = Room.objects.filter(vendor=vendor, status='occupied').count()
    dirty_rooms = Room.objects.filter(vendor=vendor, status='vacant_dirty').count()
    
    occupancy_rate = round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0)
    
    # Insights Engine: Revenue Today
    charges_today = FolioCharge.objects.filter(vendor=vendor, logged_at__date=today)
    total_revenue_today = charges_today.aggregate(total=Sum('amount'))['total'] or 0
    
    # Revenue by Department (e.g. Bar vs Spa vs Restaurant)
    departments = Department.objects.filter(vendor=vendor)
    dept_revenue = []
    for dept in departments:
        rev = charges_today.filter(department=dept).aggregate(total=Sum('amount'))['total'] or 0
        dept_revenue.append({'name': dept.name, 'revenue': rev})
        
    # Active Folios (Live Guests in House)
    active_folios = Folio.objects.filter(vendor=vendor, status='open').select_related('guest', 'room')
    
    # VIP Check-Ins Today
    vip_arrivals = active_folios.filter(
        check_in_date=today,
        guest__vip_status=True
    ).count()

    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'dirty_rooms': dirty_rooms,
        'occupancy_rate': occupancy_rate,
        'total_revenue_today': total_revenue_today,
        'dept_revenue': dept_revenue,
        'active_folios': active_folios,
        'vip_arrivals': vip_arrivals,
    }
    
    return render(request, 'resort_portal/dashboard.html', context)
