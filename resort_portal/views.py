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
    rooms = Room.objects.filter(vendor=vendor)
    total_rooms = rooms.count()
    occupied_rooms = rooms.filter(status='occupied').count()
    dirty_rooms = rooms.filter(status='vacant_dirty').count()
    
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
    active_folios = Folio.objects.filter(vendor=vendor, status='open').select_related('guest', 'room').order_by('room__room_number')
    
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
        'departments': departments, # Added for dynamic POS modal
    }
    
    return render(request, 'resort_portal/dashboard.html', context)

@login_required
@resort_enterprise_required
def resort_setup(request):
    """Configuration Hub for Rooms and Departments."""
    vendor = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_dept':
            name = request.POST.get('name')
            if name:
                Department.objects.create(vendor=vendor, name=name)
        elif action == 'add_room':
            room_number = request.POST.get('room_number')
            room_type = request.POST.get('room_type', 'Standard')
            rate = request.POST.get('rate', 0)
            if room_number:
                Room.objects.get_or_create(
                    vendor=vendor, 
                    room_number=room_number,
                    defaults={'room_type': room_type, 'base_rate': rate}
                )
        elif action == 'delete_dept':
            dept_id = request.POST.get('id')
            Department.objects.filter(vendor=vendor, id=dept_id).delete()
        elif action == 'delete_room':
            room_id = request.POST.get('id')
            Room.objects.filter(vendor=vendor, id=room_id).delete()

    departments = Department.objects.filter(vendor=vendor)
    rooms = Room.objects.filter(vendor=vendor).order_by('room_number')
    
    context = {
        'departments': departments,
        'rooms': rooms,
    }
    return render(request, 'resort_portal/setup.html', context)

@login_required
@resort_enterprise_required
def log_charge(request):
    """Fast POS Log Logic from Dashboard."""
    if request.method == 'POST':
        vendor = request.user
        amount = request.POST.get('amount')
        dept_id = request.POST.get('department_id')
        folio_id = request.POST.get('folio_id')
        desc = request.POST.get('description', 'Service Charge')
        
        if amount and dept_id:
            try:
                dept = Department.objects.get(vendor=vendor, id=dept_id)
                folio = None
                if folio_id:
                    folio = Folio.objects.get(vendor=vendor, id=folio_id)
                
                FolioCharge.objects.create(
                    vendor=vendor,
                    folio=folio,
                    department=dept,
                    amount=amount,
                    description=desc,
                    is_paid=False if folio else True
                )
            except (Department.DoesNotExist, Folio.DoesNotExist):
                pass
                
    from django.shortcuts import redirect
    return redirect('resort_portal:dashboard')
