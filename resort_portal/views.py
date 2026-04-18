from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
import datetime
from datetime import timedelta
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
from vendors.models import Vendor

from .decorators import resort_enterprise_required
from .models import (
    Room, StayRecord, ServiceCharge, Department, HousekeepingLog,
    RestaurantTable, BarSeat, EventSpace, EventBooking,
    DayPass, DayVisitor, Facility, UserActivity, ResortGuest
)

def _get_active_property(request):
    """Internal helper to ensure property context is consistent in views."""
    from vendors.models import Property
    prop_id = request.session.get('current_property_id')
    if prop_id:
        prop = Property.objects.filter(vendor=request.user, id=prop_id).first()
        if prop: return prop
    
    prop = Property.objects.filter(vendor=request.user, is_default=True).first() or \
           Property.objects.filter(vendor=request.user).first()
    if prop:
        request.session['current_property_id'] = prop.id
    return prop

@login_required
@resort_enterprise_required
def _handle_guest_registration(request, vendor, current_prop):
    """Internal helper for guest registration with flexible identification methods."""
    from .models import ResortGuest, StayRecord, Room
    from django.contrib import messages
    
    method = request.POST.get('identify_method', 'name')
    name = ''
    phone = ''
    email = ''
    passport_id = ''
    
    if method == 'name':
        name = request.POST.get('name_only') or request.POST.get('name')
        phone = request.POST.get('phone_name') or request.POST.get('phone')
    elif method == 'email':
        name = request.POST.get('name_email') or request.POST.get('name')
        email = request.POST.get('email_only') or request.POST.get('email')
    elif method == 'both':
        name = request.POST.get('name_both') or request.POST.get('name')
        email = request.POST.get('email_both') or request.POST.get('email')
        phone = request.POST.get('phone_both') or request.POST.get('phone')
        passport_id = request.POST.get('passport_both')

    gtype = request.POST.get('guest_type', 'overnight')
    vip = request.POST.get('vip_status') == 'on'
    room_id = request.POST.get('room_id')
    manual_room_number = request.POST.get('manual_room')
    
    # Validation: Name is required for 'name' and 'both', Email for 'email'
    if (method in ['name', 'both'] and not name) or (method == 'email' and not email):
        messages.error(request, "Required identification fields missing.")
        return None

    guest = ResortGuest.objects.create(
        vendor=vendor,
        resort_property=current_prop,
        name=name or email.split('@')[0], # Fallback for email-only
        phone=phone or '',
        email=email or '',
        guest_type=gtype,
        passport_id=passport_id or '',
        vip_status=vip,
        preferences=request.POST.get('preferences', '')
    )
    
    # Handle check-in (Manual text entry takes priority)
    target_room = None
    if manual_room_number:
        target_room = Room.objects.filter(vendor=vendor, resort_property=current_prop, room_number__iexact=manual_room_number.strip()).first()
        if not target_room:
            # Create the room record ON THE FLY if it doesn't exist (Operational Flexibility)
            target_room = Room.objects.create(
                vendor=vendor,
                resort_property=current_prop,
                room_number=manual_room_number.strip(),
                status='vacant_clean'
            )
    elif room_id:
        target_room = Room.objects.filter(vendor=vendor, id=room_id).first()

    if target_room:
        # Create StayRecord
        StayRecord.objects.create(
            vendor=vendor,
            resort_property=current_prop,
            guest=guest,
            room=target_room,
            status='open'
        )
        
        # Mark room as occupied
        target_room.status = 'occupied'
        target_room.save()
        messages.success(request, f"Guest {guest.name} registered and checked into Room {target_room.room_number}.")
    else:
        messages.success(request, f"Guest {guest.name} registered successfully.")
        
    return guest

@login_required
@resort_enterprise_required
def resort_dashboard(request):
    vendor = request.user
    current_prop = _get_active_property(request)
    if not current_prop:
        from django.contrib import messages
        messages.warning(request, "Please set up a property to continue.")
        return redirect('resort_portal:setup')

    from .models import ResortGuest, Department, ServiceCharge, Room, StayRecord
    from django.db.models.functions import TruncDate
    
    # Auto-initialize 'General Services'
    if not Department.objects.filter(vendor=vendor, resort_property=current_prop).exists():
        Department.objects.create(vendor=vendor, resort_property=current_prop, name='General Services')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register_guest':
            _handle_guest_registration(request, vendor, current_prop)
    
    # Date Range Logic
    period = request.GET.get('period', 'today')
    today = timezone.now().date()
    
    if period == 'today':
        start_date = today
        end_date = today
        prev_start = start_date - datetime.timedelta(days=1)
        prev_end = prev_start
    elif period == 'week':
        start_date = today - datetime.timedelta(days=7)
        end_date = today
        prev_start = start_date - datetime.timedelta(days=7)
        prev_end = start_date - datetime.timedelta(days=1)
    elif period == 'month':
        start_date = today - datetime.timedelta(days=30)
        end_date = today
        prev_start = start_date - datetime.timedelta(days=30)
        prev_end = start_date - datetime.timedelta(days=1)
    else: # Default to today
        start_date = today
        end_date = today
        prev_start = start_date - datetime.timedelta(days=1)
        prev_end = prev_start

    try:
        # --- Current Period Metrics ---
        charges_current = ServiceCharge.objects.filter(vendor=vendor, resort_property=current_prop, logged_at__date__range=[start_date, end_date])
        aggregates = charges_current.aggregate(
            total=Sum('amount'),
            tax=Sum('tax_amount'),
            net=Sum('net_amount')
        )
        total_rev = aggregates['total'] or 0
        total_tax = aggregates['tax'] or 0
        total_net = aggregates['net'] or 0
        
        rooms = Room.objects.filter(vendor=vendor, resort_property=current_prop)
        total_rooms_count = rooms.count()
        num_days = (end_date - start_date).days + 1
        total_capacity = total_rooms_count * num_days
        
        # Stays in period
        room_nights_sold = StayRecord.objects.filter(
            vendor=vendor, 
            resort_property=current_prop,
            check_in_date__lte=end_date,
            check_out_date__gte=start_date
        ).count() if num_days > 0 else 0
        
        occ_rate = round((room_nights_sold / total_capacity * 100) if total_capacity > 0 else 0)
        
        # Room Revenue only
        room_rev = charges_current.filter(department__name__icontains='Room').aggregate(total=Sum('amount'))['total'] or 0
        adr = round(room_rev / room_nights_sold) if room_nights_sold > 0 else 0
        revpar = round(room_rev / total_capacity) if total_capacity > 0 else 0
        
        # --- Previous Period Metrics (for Trends) ---
        charges_prev = ServiceCharge.objects.filter(vendor=vendor, resort_property=current_prop, logged_at__date__range=[prev_start, prev_end])
        prev_rev = charges_prev.aggregate(total=Sum('amount'))['total'] or 0
        
        def calc_trend(curr, prev):
            if prev == 0: return 100 if curr > 0 else 0
            return round(((curr - prev) / prev) * 100)

        # Insights Engine: Revenue Today (Real-time simplified for summary)
        charges_today = ServiceCharge.objects.filter(vendor=vendor, resort_property=current_prop, logged_at__date=today)
        aggregates_today = charges_today.aggregate(total=Sum('amount'), tax=Sum('tax_amount'))
        total_revenue_today = aggregates_today['total'] or 0
        total_tax_today = aggregates_today['tax'] or 0
        
        dept_revenue = (
            charges_current.values('department__name')
            .annotate(revenue=Sum('amount'))
            .order_by('-revenue')
        )
        dept_revenue = [{'name': d['department__name'] or 'General', 'revenue': d['revenue']} for d in dept_revenue]
            
        # Active Stays
        active_folios = StayRecord.objects.filter(
            vendor=vendor, 
            resort_property=current_prop, 
            status='open'
        ).select_related('guest', 'room').order_by('room__room_number')
        
        # VIPs Arriving Today
        vip_arrivals = StayRecord.objects.filter(
            vendor=vendor,
            resort_property=current_prop,
            check_in_date=today,
            guest__vip_status=True
        ).count()

        is_manager_unlocked = request.session.get('resort_manager_unlocked', False)

        context = {
            'period': period,
            'total_rooms': total_rooms_count,
            'occupied_rooms': rooms.filter(status='occupied').count(),
            'dirty_rooms': rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).count(),
            'occupancy_rate': occ_rate,
            
            # Gated Financial KPIs
            'total_revenue': total_rev if is_manager_unlocked else 0,
            'total_tax': total_tax if is_manager_unlocked else 0,
            'total_net': total_net if is_manager_unlocked else 0,
            'room_revenue': room_rev if is_manager_unlocked else 0,
            'adr': adr if is_manager_unlocked else 0,
            'revpar': revpar if is_manager_unlocked else 0,
            'total_revenue_today': total_revenue_today if is_manager_unlocked else 0,
            'total_tax_today': total_tax_today if is_manager_unlocked else 0,
            'dept_revenue': dept_revenue if is_manager_unlocked else [],
            'rev_trend': calc_trend(total_rev, prev_rev) if is_manager_unlocked else 0,
            
            'active_stays': active_folios,
            'vip_arrivals': vip_arrivals,
            'available_rooms': rooms.filter(status='vacant_clean'),
            'all_rooms': rooms.order_by('room_number'),
            'dirty_room_list': rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).order_by('room_number'),
            'departments': Department.objects.filter(vendor=vendor, resort_property=current_prop),
            'all_guests': ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop).order_by('name'),
            'is_manager_unlocked': is_manager_unlocked
        }
    except Exception as e:
        context = {
            'critical_error': str(e),
            'total_rooms': 0, 'occupancy_rate': 0, 'total_revenue': 0, 'dept_revenue': []
        }
    
    template_name = 'resort_portal/dashboard-simple.html' if request.GET.get('simple') == 'true' else 'resort_portal/dashboard.html'
    return render(request, template_name, context)

@login_required
@resort_enterprise_required
def overview(request):
    """New Modular Overview Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    if not current_prop:
        from django.contrib import messages
        messages.warning(request, "Please set up a property to continue.")
        return redirect('resort_portal:setup')

    is_manager_unlocked = request.session.get('resort_manager_unlocked', False)
    today = timezone.now().date()
    
    # Financials (Gated)
    total_revenue_today = 0
    if is_manager_unlocked:
        total_revenue_today = ServiceCharge.objects.filter(
            vendor=vendor, resort_property=current_prop, logged_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0

    # Operational KPI
    occupied_count = Room.objects.filter(vendor=vendor, resort_property=current_prop, status='occupied').count()
    dirty_count = Room.objects.filter(vendor=vendor, resort_property=current_prop, status__in=['vacant_dirty', 'cleaning']).count()
    
    # Activity Feed
    activities = UserActivity.objects.filter(vendor=vendor, resort_property=current_prop).order_by('-created_at')[:8]
    
    # Arrival Alerts
    arrivals_today = StayRecord.objects.filter(vendor=vendor, resort_property=current_prop, check_in_date=today).count()
    vip_arrivals = ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop, vip_status=True, stays__check_in_date=today).count()

    context = {
        'total_revenue_today': total_revenue_today,
        'occupied_rooms': occupied_count,
        'dirty_rooms': dirty_count,
        'arrivals_today': arrivals_today,
        'vip_arrivals': vip_arrivals,
        'activities': activities,
        'is_manager_unlocked': is_manager_unlocked,
        'active_property': current_prop
    }
    return render(request, 'resort_portal/overview.html', context)

@login_required
def legacy_overview_redirect(request):
    return redirect('resort_portal:overview')

@login_required
@resort_enterprise_required
def guests_section(request):
    """Modular Guest CRM & Registration Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    tab = request.GET.get('tab', 'list')
    
    if request.method == 'POST' and request.POST.get('action') == 'register_guest':
        _handle_guest_registration(request, vendor, current_prop)

    guests = ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop).order_by('-created_at')
    active_folios = StayRecord.objects.filter(vendor=vendor, resort_property=current_prop, status='open')
    
    context = {
        'current_tab': tab,
        'guests': guests,
        'active_folios': active_folios,
        'available_rooms': Room.objects.filter(vendor=vendor, resort_property=current_prop, status='vacant_clean'),
    }
    return render(request, 'resort_portal/guests_section.html', context)

@login_required
@resort_enterprise_required
def rooms_section(request):
    """Housekeeping & Room Readiness Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    rooms = Room.objects.filter(vendor=vendor, resort_property=current_prop).order_by('room_number')
    
    context = {
        'rooms': rooms,
        'housekeeping_queue': rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']),
    }
    return render(request, 'resort_portal/rooms_section.html', context)

@login_required
@resort_enterprise_required
def restaurant_section(request):
    """POS & Table Management Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    tables = RestaurantTable.objects.filter(vendor=vendor, resort_property=current_prop).order_by('table_number')
    
    # Logic for Active Bills list (for the POS Hub)
    active_bills = []
    occupied_tables = tables.filter(status='occupied')
    for table in occupied_tables:
        total = ServiceCharge.objects.filter(vendor=vendor, table=table, is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
        active_bills.append({'ref_id': table.id, 'name': f"Table {table.table_number}", 'total': total})

    context = {'tables': tables, 'active_bills': active_bills}
    return render(request, 'resort_portal/restaurant_section.html', context)

@login_required
@resort_enterprise_required
def bar_section(request):
    """Bar Tabs & Seating Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    seats = BarSeat.objects.filter(vendor=vendor, resort_property=current_prop).order_by('seat_number')
    
    # Logic for Active Bills list
    active_bills = []
    occupied_seats = seats.filter(status='occupied')
    for seat in occupied_seats:
        total = ServiceCharge.objects.filter(vendor=vendor, seat=seat, is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
        active_bills.append({'ref_id': seat.id, 'name': f"Seat {seat.seat_number}", 'total': total})

    context = {'seats': seats, 'active_bills': active_bills}
    return render(request, 'resort_portal/bar_section.html', context)

@login_required
@resort_enterprise_required
def events_section(request):
    """Event Bookings & Space Readiness Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    spaces = EventSpace.objects.filter(vendor=vendor, resort_property=current_prop)
    bookings = EventBooking.objects.filter(vendor=vendor, resort_property=current_prop).order_by('start_date')
    
    context = {'spaces': spaces, 'bookings': bookings}
    return render(request, 'resort_portal/events_section.html', context)

@login_required
@resort_enterprise_required
def day_visitors_section(request):
    """Day-Visitor (Non-Resident) Check-in Hub."""
    vendor = request.user
    current_prop = _get_active_property(request)
    visitors = DayVisitor.objects.filter(vendor=vendor, resort_property=current_prop, status='active')
    passes = DayPass.objects.filter(vendor=vendor, resort_property=current_prop, is_active=True)
    
    context = {'visitors': visitors, 'passes': passes}
    return render(request, 'resort_portal/day_visitors_section.html', context)

@login_required
@resort_enterprise_required
def reports_section(request):
    """Management Financial & Analytics Hub (Manager Only PIN Gated)."""
    if not request.session.get('resort_manager_unlocked'):
        return redirect('resort_portal:overview')
    
    # Financial context aggregation logic here...
    return render(request, 'resort_portal/reports_section.html', {})

@login_required
@resort_enterprise_required
def settings_section(request):
    """Property & Security Control Hub."""
    return render(request, 'resort_portal/settings_section.html', {})

@login_required
@resort_enterprise_required
def resort_setup(request):
    """Configuration Hub for Rooms and Departments."""
    vendor = request.user
    current_prop = _get_active_property(request)
    if not current_prop:
        # If no property, we must create one
        from vendors.models import Property
        current_prop = Property.objects.create(vendor=vendor, name=vendor.business_name, is_default=True)
        request.session['current_property_id'] = current_prop.id

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_dept':
            name = request.POST.get('name')
            if name:
                Department.objects.create(vendor=vendor, resort_property=current_prop, name=name)
        elif action == 'add_room':
            room_number = request.POST.get('room_number')
            room_type = request.POST.get('room_type', 'Standard')
            rate = request.POST.get('rate', 0)
            if room_number:
                Room.objects.get_or_create(
                    vendor=vendor, 
                    resort_property=current_prop,
                    room_number=room_number,
                    defaults={'room_type': room_type, 'base_rate': rate}
                )
        elif action == 'delete_dept':
            dept_id = request.POST.get('id')
            Department.objects.filter(vendor=vendor, resort_property=current_prop, id=dept_id).delete()
        elif action == 'delete_room':
            room_id = request.POST.get('id')
            Room.objects.filter(vendor=vendor, resort_property=current_prop, id=room_id).delete()
        elif action == 'set_pin':
            pin = request.POST.get('pin')
            if pin and len(pin) == 4 and pin.isdigit():
                vendor.set_manager_pin(pin)
                from django.contrib import messages
                messages.success(request, "Manager PIN updated successfully.")
            else:
                from django.contrib import messages
                messages.error(request, "Invalid PIN. Must be 4 digits.")

    departments = Department.objects.filter(vendor=vendor, resort_property=current_prop)
    rooms = Room.objects.filter(vendor=vendor, resort_property=current_prop).order_by('room_number')
    
    context = {
        'departments': departments,
        'rooms': rooms,
        'active_property': current_prop
    }
    return render(request, 'resort_portal/setup.html', context)

@login_required
@resort_enterprise_required
def log_charge(request):
    """Refined Operational Service Billing Supporting Table/Seat/Guest Modal."""
    from .models import StayRecord, ServiceCharge, Department, ResortGuest, RestaurantTable, BarSeat, UserActivity
    from django.contrib import messages
    vendor = request.user
    
    if request.method == 'POST':
        ref_type = request.POST.get('ref_type') # 'guest', 'table', 'seat'
        ref_id = request.POST.get('ref_id')
        amount = request.POST.get('amount')
        desc = request.POST.get('description')
        
        if amount and ref_id:
            try:
                guest = None
                stay = None
                table = None
                seat = None
                dept_name = 'General Services'
                active_prop = _get_active_property(request)

                if ref_type == 'guest':
                    guest = ResortGuest.objects.get(vendor=vendor, id=ref_id)
                    stay = guest.folios.filter(status='open').first()
                elif ref_type == 'table':
                    table = RestaurantTable.objects.get(vendor=vendor, id=ref_id)
                    table.status = 'occupied'
                    table.save()
                    dept_name = 'Main Restaurant'
                elif ref_type == 'seat':
                    seat = BarSeat.objects.get(vendor=vendor, id=ref_id)
                    seat.status = 'occupied'
                    seat.save()
                    dept_name = 'Pool Bar'

                # Get or Create Department
                dept, _ = Department.objects.get_or_create(
                    vendor=vendor, resort_property=active_prop, name=dept_name
                )

                ServiceCharge.objects.create(
                    vendor=vendor,
                    resort_property=active_prop,
                    stay=stay,
                    guest=guest,
                    table=table,
                    seat=seat,
                    department=dept,
                    amount=amount,
                    description=desc,
                    is_paid=False if stay else True # Charged to room if guest is in-house
                )
                
                # Log Activity
                UserActivity.objects.create(
                    vendor=vendor,
                    resort_property=active_prop,
                    user=request.user,
                    title="Service Order Logged",
                    description=f"Charged KSh {amount} for {desc} (Ref: {ref_type} {ref_id})",
                    category='pos',
                    icon='💳'
                )
                
                messages.success(request, f"KSh {amount} charged for {desc}")
            except Exception as e:
                messages.error(request, f"Error logging charge: {str(e)}")
                
    return redirect(request.META.get('HTTP_REFERER', 'resort_portal:overview'))

@login_required
@resort_enterprise_required
def settle_bill(request):
    """Process payment and clear the table/seat."""
    from .models import ServiceCharge, RestaurantTable, BarSeat, UserActivity
    from django.contrib import messages
    vendor = request.user
    
    if request.method == 'POST':
        ref_type = request.POST.get('ref_type')
        ref_id = request.POST.get('ref_id')
        pay_method = request.POST.get('payment_method')
        
        try:
            active_prop = _get_active_property(request)
            charges = []
            location_name = ""

            if ref_type == 'table':
                table = RestaurantTable.objects.get(vendor=vendor, id=ref_id)
                charges = ServiceCharge.objects.filter(vendor=vendor, table=table, is_paid=False)
                table.status = 'available'
                table.save()
                location_name = f"Table {table.table_number}"
            elif ref_type == 'seat':
                seat = BarSeat.objects.get(vendor=vendor, id=ref_id)
                charges = ServiceCharge.objects.filter(vendor=vendor, seat=seat, is_paid=False)
                seat.status = 'available'
                seat.save()
                location_name = f"Seat {seat.seat_number}"

            total_paid = 0
            for charge in charges:
                total_paid += charge.amount
                charge.is_paid = True
                charge.payment_method = pay_method
                charge.settled_at = timezone.now()
                charge.save()

            UserActivity.objects.create(
                vendor=vendor,
                resort_property=active_prop,
                user=request.user,
                title="Bill Settled",
                description=f"Collected KSh {total_paid} via {pay_method.upper()} for {location_name}",
                category='finance',
                icon='💰'
            )
            messages.success(request, f"Payment of KSh {total_paid} recorded for {location_name}. Table is now available.")
        except Exception as e:
            messages.error(request, f"Settle failed: {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', 'resort_portal:overview'))

@login_required
@resort_enterprise_required
def guest_index(request):
    """Strategic Guest CRM Hub."""
    from .models import ResortGuest, StayRecord
    vendor = request.user
    current_prop = _get_active_property(request)
    
    if request.method == 'POST' and request.POST.get('action') == 'register_guest':
        _handle_guest_registration(request, vendor, current_prop)
    
    guests = ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop).order_by('-created_at')
    
    # Segment Counts
    segment_counts = {
        'all': guests.count(),
        'active': guests.filter(folios__status='open').distinct().count(),
        'vip': guests.filter(vip_status=True).count(),
        'loyal': guests.filter(total_stays__gte=5).count(),
        'at_risk': 0, 
    }
    
    # Filtering & Search
    q = request.GET.get('q')
    gtype = request.GET.get('type')
    segment = request.GET.get('segment')
    
    if q:
        guests = guests.filter(
            Q(name__icontains=q) | 
            Q(phone__icontains=q) | 
            Q(passport_id__icontains=q)
        )
    if gtype:
        guests = guests.filter(guest_type=gtype)

    if segment:
        if segment == 'active':
            guests = guests.filter(folios__status='open').distinct()
        elif segment == 'vip':
            guests = guests.filter(vip_status=True)
        elif segment == 'loyal':
            guests = guests.filter(total_stays__gte=5)
        elif segment == 'at_risk':
            six_months_ago = timezone.now().date() - datetime.timedelta(days=180)
            guests = guests.filter(
                folios__status='closed',
                folios__check_out_date__lt=six_months_ago
            ).distinct()

    return render(request, 'resort_portal/guest_list.html', {
        'guests': guests,
        'search_query': q or '',
        'current_type': gtype or '',
        'current_segment': segment or '',
        'segments': segment_counts,
    })

@login_required
@resort_enterprise_required
def guest_detail(request, guest_id):
    """360-degree View of a Guest Personal Journey."""
    from django.shortcuts import get_object_or_404
    from .models import ResortGuest, ServiceCharge
    vendor = request.user
    guest = get_object_or_404(ResortGuest, vendor=vendor, id=guest_id)
    
    # Stay Records
    stays = guest.folios.all().order_by('-check_in_date')
    
    # Financial Intelligence
    all_charges = ServiceCharge.objects.filter(guest=guest, vendor=vendor).order_by('-logged_at')
    total_lifetime_spend = all_charges.aggregate(total=Sum('amount'))['total'] or 0
    
    if request.method == 'POST':
        # Update preferences (Boutique Notes)
        notes = request.POST.get('preferences')
        if notes is not None:
            guest.preferences = notes
            guest.save(update_fields=['preferences'])
            from django.contrib import messages
            messages.success(request, f"Updated boutique notes for {guest.name}")

    context = {
        'guest': guest,
        'stays': stays,
        'all_charges': all_charges,
        'total_lifetime_spend': total_lifetime_spend,
    }
    return render(request, 'resort_portal/guest_detail.html', context)

@login_required
@resort_enterprise_required
def mark_room_clean(request, room_id):
    """Housekeeping Reset: Mark a dirty room as clean."""
    from .models import Room
    vendor = request.user
    room = get_object_or_404(Room, vendor=vendor, id=room_id)
    
    room.status = 'vacant_clean'
    room.save()
    
    from django.contrib import messages
    messages.success(request, f"Room {room.room_number} is now marked as Vacant (Clean).")
    
    from django.shortcuts import redirect
    return redirect('resort_portal:overview')

@login_required
@resort_enterprise_required
def check_out_folio(request, stay_id):
    """Finalize billing for a resident guest stay."""
    from django.shortcuts import get_object_or_404, redirect
    from .models import StayRecord, Room
    
    vendor = request.user
    stay = get_object_or_404(StayRecord, vendor=vendor, id=stay_id, status='open')
    
    # 1. Archive the stay
    stay.status = 'closed'
    stay.check_out_date = timezone.now().date()
    stay.save()
    
    # Update Guest Lifetime Stays
    stay.guest.total_stays += 1
    stay.guest.save()
    
    # 2. Flag Room for Housekeeping
    if stay.room:
        stay.room.status = 'vacant_dirty'
        stay.room.save()
        
    # 3. Calculate Final Toll
    charges = stay.charges.all()
    total = charges.aggregate(total=Sum('amount'))['total'] or 0
    
    # 4. Dispatch Receipt (Only if Guest has Email)
    if stay.guest.email:
        try:
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.core.mail import send_mail
            
            subject = f"Receipt: Your Stay at {vendor.business_name}"
            html_message = render_to_string('resort_portal/bill_receipt_email.html', {
                'stay': stay,
                'charges': charges,
                'total': total,
                'vendor': vendor,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                None, # Uses DEFAULT_FROM_EMAIL
                [stay.guest.email],
                html_message=html_message,
                fail_silently=True
            )
            messages.success(request, f"Digital receipt sent to {stay.guest.email}")
        except Exception:
            messages.warning(request, "Check-out successful, but receipt email failed to send.")
    
    messages.success(request, f"Guest {stay.guest.name} checked out. Room {stay.room.room_number if stay.room else 'N/A'} is now flagged for cleaning.")
    
    return redirect('resort_portal:dashboard')
@login_required
@resort_enterprise_required
def start_cleaning(request, room_id):
    vendor = request.user
    room = get_object_or_404(Room, vendor=vendor, id=room_id)
    old_status = room.status
    room.status = 'cleaning'
    room.save()
    HousekeepingLog.objects.create(room=room, old_status=old_status, new_status='cleaning', staff_name=request.user.name)
    from django.contrib import messages
    messages.info(request, f"Room {room.room_number} cleaning started.")
    return redirect('resort_portal:dashboard')

@login_required
@resort_enterprise_required
def finish_cleaning(request, room_id):
    vendor = request.user
    room = get_object_or_404(Room, vendor=vendor, id=room_id)
    old_status = room.status
    room.status = 'inspected'
    room.save()
    HousekeepingLog.objects.create(room=room, old_status=old_status, new_status='inspected', staff_name=request.user.name)
    from django.contrib import messages
    messages.success(request, f"Room {room.room_number} cleaning finished. Ready for inspection.")
    return redirect('resort_portal:dashboard')

@login_required
@resort_enterprise_required
def inspect_room(request, room_id):
    vendor = request.user
    room = get_object_or_404(Room, vendor=vendor, id=room_id)
    old_status = room.status
    room.status = 'vacant_clean'
    room.save()
    HousekeepingLog.objects.create(room=room, old_status=old_status, new_status='vacant_clean', staff_name=request.user.name, notes="Inspected and Approved")
    from django.contrib import messages
    messages.success(request, f"Room {room.room_number} inspected and marked Clean.")
    return redirect('resort_portal:dashboard')

@login_required
@resort_enterprise_required
@require_POST
def verify_manager_pin(request):
    pin = request.POST.get('pin')
    vendor = request.user
    
    if vendor.resort_manager_pin and check_password(pin, vendor.resort_manager_pin):
        # Mark session as unlocked for this login
        request.session['resort_manager_unlocked'] = True
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid PIN'})


@login_required
@resort_enterprise_required
@require_POST
def request_pin_reset_otp(request):
    identification = request.POST.get('identification', '').strip()
    ident_type = request.POST.get('type', 'phone') # 'phone' or 'email'
    vendor = request.user
    
    # Check if identification matches current vendor
    match = False
    if ident_type == 'phone' and vendor.phone_number == identification:
        match = True
    elif ident_type == 'email' and vendor.email == identification:
        match = True
        
    if not match:
        return JsonResponse({'success': False, 'message': f'Identification does not match our records for this {ident_type}.'})
    
    # Generate 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    vendor.resort_otp = otp
    vendor.resort_otp_expiry = timezone.now() + timedelta(minutes=10)
    vendor.save()
    
    # Send OTP
    success = False
    if ident_type == 'phone':
        try:
            import africastalking
            africastalking.initialize(
                username=getattr(settings, 'AT_USERNAME', 'sandbox'),
                api_key=getattr(settings, 'AT_API_KEY', '')
            )
            sms = africastalking.SMS
            message = f"Your CampoPawa Resort Manager Reset Code is: {otp}. Valid for 10 minutes."
            sms.send(message, [vendor.phone_number], sender_id=getattr(settings, 'AT_SENDER_ID', 'CampoPawa'))
            success = True
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Failed to send SMS: {str(e)}'})
    else:
        try:
            send_mail(
                'Resort Manager Reset Code',
                f'Your CampoPawa Resort Manager Reset Code is: {otp}. Valid for 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [vendor.email],
                fail_silently=False,
            )
            success = True
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Failed to send Email: {str(e)}'})
            
    return JsonResponse({'success': success})


@login_required
@resort_enterprise_required
@require_POST
def verify_pin_reset_otp(request):
    otp = request.POST.get('otp', '').strip()
    new_pin = request.POST.get('new_pin', '').strip()
    vendor = request.user
    
    if not vendor.resort_otp or vendor.resort_otp != otp:
        return JsonResponse({'success': False, 'message': 'Invalid reset code.'})
        
    if vendor.resort_otp_expiry < timezone.now():
        return JsonResponse({'success': False, 'message': 'Code has expired.'})
        
    if len(new_pin) != 4 or not new_pin.isdigit():
        return JsonResponse({'success': False, 'message': 'New PIN must be 4 digits.'})
        
    # Success: Save new hashed PIN and clear OTP
    vendor.resort_manager_pin = make_password(new_pin)
    vendor.resort_otp = None
    vendor.resort_otp_expiry = None
    vendor.save()
    
    request.session['resort_manager_unlocked'] = True
    return JsonResponse({'success': True})

@login_required
@resort_enterprise_required
def lock_manager_dashboard(request):
    """Explicitly clear the manager authorization session state."""
    if 'resort_manager_unlocked' in request.session:
        del request.session['resort_manager_unlocked']
    from django.contrib import messages
    messages.info(request, "Manager view has been locked.")
    return redirect('resort_portal:dashboard')
