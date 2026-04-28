from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
import random, string
from datetime import timedelta
from vendors.decorators import premium_required as resort_enterprise_required
from .models import (
    Room, StayRecord, ServiceCharge, Department, HousekeepingLog,
    RestaurantTable, BarSeat, EventSpace, EventBooking,
    DayPass, DayVisitor, Facility, UserActivity, ResortGuest,
    ManagerAuth
)
from .utils import (
    get_active_property, validate_guest_registration_data, 
    get_dashboard_metrics, log_user_activity, calculate_trend,
    clear_dashboard_cache, get_or_create_department
)

# Note: _get_active_property moved to utils.py as get_active_property()

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
    current_prop = get_active_property(request)
    if not current_prop:
        from django.contrib import messages
        messages.warning(request, "Please set up a property to continue.")
        return redirect('resort_portal:setup')

    # Auto-initialize 'General Services'
    if not Department.objects.filter(vendor=vendor, resort_property=current_prop).exists():
        Department.objects.create(vendor=vendor, resort_property=current_prop, name='General Services')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register_guest':
            _handle_guest_registration(request, vendor, current_prop)
    
    period = request.GET.get('period', 'today')
    is_manager_unlocked = request.session.get('resort_manager_unlocked', False)
    
    try:
        # Get metrics using utils (with caching)
        metrics = get_dashboard_metrics(vendor, current_prop, period)
        
        # Calculate previous period for trend
        from datetime import timedelta
        today = timezone.now().date()
        if period == 'today':
            prev_start = today - timedelta(days=1)
            prev_end = prev_start
        elif period == 'week':
            prev_start = today - timedelta(days=14)
            prev_end = today - timedelta(days=8)
        else:  # month
            prev_start = today - timedelta(days=60)
            prev_end = today - timedelta(days=31)
        
        prev_metrics = get_dashboard_metrics(vendor, current_prop, f"custom_{prev_start}_{prev_end}")
        rev_trend = calculate_trend(metrics['total_revenue'], prev_metrics['total_revenue'])
        
        context = {
            'period': period,
            'is_manager_unlocked': is_manager_unlocked,
            
            # Gated Financial KPIs
            'total_revenue': metrics['total_revenue'] if is_manager_unlocked else 0,
            'total_tax': metrics['total_tax'] if is_manager_unlocked else 0,
            'total_net': metrics['total_net'] if is_manager_unlocked else 0,
            'room_revenue': metrics['room_revenue'] if is_manager_unlocked else 0,
            'adr': metrics['adr'] if is_manager_unlocked else 0,
            'revpar': metrics['revpar'] if is_manager_unlocked else 0,
            'total_revenue_today': metrics['total_revenue_today'] if is_manager_unlocked else 0,
            'total_tax_today': metrics['total_tax_today'] if is_manager_unlocked else 0,
            'dept_revenue': metrics['dept_revenue'] if is_manager_unlocked else [],
            'rev_trend': rev_trend if is_manager_unlocked else 0,
            
            # Operational KPIs (always visible)
            'total_rooms': metrics['total_rooms'],
            'occupied_rooms': metrics['occupied_rooms'],
            'dirty_rooms': metrics['dirty_rooms'],
            'occupancy_rate': metrics['occupancy_rate'],
            'active_stays': metrics['active_stays'],
            'vip_arrivals': metrics['vip_arrivals'],
            'available_rooms': metrics['available_rooms'],
            'all_rooms': metrics['all_rooms'],
            'dirty_room_list': metrics['dirty_room_list'],
            'departments': Department.objects.filter(vendor=vendor, resort_property=current_prop),
            'all_guests': ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop).order_by('name'),
        }
        
    except Exception as e:
        import logging
        logging.error(f"Critical error in resort_dashboard: {e}")
        context = {
            'critical_error': str(e),
            'period': period,
            'is_manager_unlocked': False,
            'total_rooms': 0, 'occupancy_rate': 0, 'total_revenue': 0, 'dept_revenue': [],
            'active_stays': StayRecord.objects.none(),
            'available_rooms': Room.objects.none(),
            'all_rooms': Room.objects.none(),
            'dirty_room_list': Room.objects.none(),
            'departments': Department.objects.none(),
            'all_guests': ResortGuest.objects.none(),
        }
    
    template_name = 'resort_portal/dashboard-simple.html' if request.GET.get('simple') == 'true' else 'resort_portal/dashboard.html'
    return render(request, template_name, context)

@login_required
@resort_enterprise_required
def overview(request):
    """Deep Content Overview Hub."""
    from vendors.greetings import get_daily_context
    vendor = request.user
    current_prop = get_active_property(request)
    if not current_prop:
        from django.contrib import messages
        messages.warning(request, "Please set up a property to continue.")
        return redirect('resort_portal:setup')

    is_manager_unlocked = request.session.get('resort_manager_unlocked', False)
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # --- Deep Intelligence (Greetings) ---
    daily_context = get_daily_context(vendor)
    
    # --- Financial Intelligence (Gated) ---
    total_revenue_today = 0
    week_revenue = 0
    if is_manager_unlocked:
        total_revenue_today = ServiceCharge.objects.filter(
            vendor=vendor, resort_property=current_prop, is_paid=True, settled_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        week_revenue = ServiceCharge.objects.filter(
            vendor=vendor, resort_property=current_prop, is_paid=True, settled_at__date__gte=seven_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0

    # --- Guest Velocity & Loyalty ---
    all_guests = ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop)
    total_guests_count = all_guests.count()
    guests_today = all_guests.filter(created_at__date=today).count()
    
    # Loyalty Rate: Percentage of guests with > 1 folio
    repeat_guests = all_guests.filter(total_stays__gt=1).count()
    loyalty_rate = (repeat_guests / total_guests_count * 100) if total_guests_count > 0 else 0
    
    # --- Operational intelligence ---
    occupied_count = Room.objects.filter(vendor=vendor, resort_property=current_prop, status='occupied').count()
    dirty_count = Room.objects.filter(vendor=vendor, resort_property=current_prop, status__in=['vacant_dirty', 'cleaning']).count()
    
    # --- Front Desk Feed (Recent Guests matching Retail layout) ---
    # Fetching most recent stays for the "Recent Guests" list
    recent_stays = StayRecord.objects.filter(
        vendor=vendor, resort_property=current_prop
    ).select_related('guest', 'room').order_by('-id')[:5]
    
    # Arrival Alerts (for top-level stats)
    arrivals_today = StayRecord.objects.filter(vendor=vendor, resort_property=current_prop, check_in_date=today).count()
    vip_arrivals = all_guests.filter(vip_status=True, folios__check_in_date=today).count()

    context = {
        **daily_context,
        'total_revenue_today': total_revenue_today,
        'week_revenue': week_revenue,
        'guests_today': guests_today,
        'total_guests_count': total_guests_count,
        'loyalty_rate': round(loyalty_rate),
        
        'occupied_rooms': occupied_count,
        'dirty_rooms': dirty_count,
        'arrivals_today': arrivals_today,
        'vip_arrivals': vip_arrivals,
        
        'recent_stays': recent_stays,
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
    current_prop = get_active_property(request)
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
    current_prop = get_active_property(request)
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
    current_prop = get_active_property(request)
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
    current_prop = get_active_property(request)
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
    current_prop = get_active_property(request)
    spaces = EventSpace.objects.filter(vendor=vendor, resort_property=current_prop)
    bookings = EventBooking.objects.filter(vendor=vendor, resort_property=current_prop).order_by('start_date')
    
    context = {'spaces': spaces, 'bookings': bookings}
    return render(request, 'resort_portal/events_section.html', context)

@login_required
@resort_enterprise_required
def day_visitors_section(request):
    """Day-Visitor (Non-Resident) Check-in Hub."""
    vendor = request.user
    current_prop = get_active_property(request)
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
    
    vendor = request.user
    current_prop = get_active_property(request)
    if not current_prop:
        return redirect('resort_portal:setup')

    today = timezone.now().date()
    period = request.GET.get('period', '30') # Default to 30 days
    try:
        days = int(period)
    except:
        days = 30
    
    start_date = today - timedelta(days=days)
    
    # --- Data Filtering ---
    # We only count settled (paid) charges for revenue analytics
    charges = ServiceCharge.objects.filter(
        vendor=vendor,
        resort_property=current_prop,
        is_paid=True,
        settled_at__date__gte=start_date
    )

    # --- Summary Metrics ---
    summary = charges.aggregate(
        total_revenue=Sum('amount'),
        total_transactions=Count('id'),
    )
    total_rev = summary['total_revenue'] or 0
    total_trans = summary['total_transactions'] or 0
    avg_daily = total_rev / max(days, 1)

    # --- Trend Calculation (vs Previous Period) ---
    prev_start = start_date - timedelta(days=days)
    prev_summary = ServiceCharge.objects.filter(
        vendor=vendor,
        resort_property=current_prop,
        is_paid=True,
        settled_at__date__gte=prev_start,
        settled_at__date__lt=start_date
    ).aggregate(total=Sum('amount'))
    
    prev_rev = prev_summary['total'] or 0
    if prev_rev > 0:
        change_pct = ((total_rev - prev_rev) / prev_rev) * 100
    else:
        change_pct = 100 if total_rev > 0 else 0

    # --- Daily Distribution (Revenue Chart) ---
    from django.db.models.functions import TruncDate
    daily = charges.annotate(
        day=TruncDate('settled_at')
    ).values('day').annotate(
        revenue=Sum('amount')
    ).order_by('day')
    
    chart_labels = [d['day'].strftime('%d %b') for d in daily]
    chart_revenue = [float(d['revenue']) for d in daily]

    # --- Guest Segmentation (Customer Segments) ---
    # Based on all guests of this property
    guests = ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop)
    segments = {
        'loyal': 0, 'regular': 0, 'new': 0, 'at_risk': 0, 'vip': 0
    }
    for g in guests:
        s = g.status
        if s in segments:
            segments[s] += 1
    
    # --- Department Revenue Breakdown ---
    by_dept = charges.values('department__name').annotate(
        revenue=Sum('amount')
    ).order_by('-revenue')
    
    dept_names = [d['department__name'] or 'General' for d in by_dept]
    dept_revenues = [float(d['revenue']) for d in by_dept]

    # --- Top Customers & Services ---
    top_customers = ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop).annotate(
        period_spent=Sum('all_charges__amount', filter=Q(all_charges__is_paid=True, all_charges__settled_at__date__gte=start_date))
    ).exclude(period_spent=None).order_by('-period_spent')[:10]

    top_services = charges.values('description').annotate(
        revenue=Sum('amount'),
        count=Count('id')
    ).order_by('-revenue')[:10]

    # Best Day logic
    from django.db.models.functions import ExtractWeekDay
    by_weekday = charges.annotate(
        weekday=ExtractWeekDay('settled_at')
    ).values('weekday').annotate(revenue=Sum('amount')).order_by('weekday')
    
    weekday_names = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri', 7: 'Sat'}
    best_day_val = 0
    best_day_name = '—'
    for d in by_weekday:
        if d['revenue'] > best_day_val:
            best_day_val = d['revenue']
            best_day_name = weekday_names.get(d['weekday'], '—')

    import json
    context = {
        'period': period,
        'total_revenue': total_rev,
        'total_transactions': total_trans,
        'avg_daily': round(avg_daily),
        'change_pct': round(change_pct, 1),
        'best_day': best_day_name,
        
        # Chart Data (Pre-serialized)
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue': json.dumps(chart_revenue),
        'segments_json': json.dumps(segments),
        'dept_names_json': json.dumps(dept_names),
        'dept_revenues_json': json.dumps(dept_revenues),
        
        # Tables
        'top_customers': top_customers,
        'top_services': top_services,
        'by_dept': by_dept
    }
    
    return render(request, 'resort_portal/reports_section.html', context)

@login_required
@resort_enterprise_required
def security_settings(request):
    """Dedicated Security Settings Hub."""
    vendor = request.user
    
    # Check if manager authentication is set up
    if not hasattr(vendor, 'manager_auth'):
        # Redirect to setup if no manager auth exists
        from django.contrib import messages
        messages.info(request, "Please set up your manager account first.")
        return redirect('resort_portal:manager_setup')
    
    manager_auth = vendor.manager_auth
    
    # If account is not verified, redirect to verification
    if not manager_auth.is_verified:
        from django.contrib import messages
        messages.warning(request, "Please verify your manager account to access security settings.")
        return redirect('resort_portal:manager_verify')
    
    # Check if manager is authenticated in this session
    if not request.session.get('manager_authenticated'):
        from django.contrib import messages
        messages.warning(request, "Please log in to access security settings.")
        return redirect('resort_portal:manager_login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'set_pin':
            pin = request.POST.get('pin')
            pin_confirm = request.POST.get('pin_confirm')
            
            # Enhanced validation
            if not pin or not pin_confirm:
                from django.contrib import messages
                messages.error(request, "Both PIN fields are required.")
            elif pin != pin_confirm:
                from django.contrib import messages
                messages.error(request, "PINs do not match. Please try again.")
            elif len(pin) != 4 or not pin.isdigit():
                from django.contrib import messages
                messages.error(request, "PIN must be exactly 4 digits.")
            else:
                # Check for weak PINs
                weak_pins = ['1234', '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999', '0123', '4321']
                sequential_patterns = ['0123', '1234', '2345', '3456', '4567', '5678', '6789', '9876', '8765', '7654', '6543', '5432', '4321', '3210']
                
                if pin in weak_pins or pin in sequential_patterns:
                    from django.contrib import messages
                    messages.error(request, "This PIN is too common and insecure. Please choose a more secure PIN that isn't sequential or repeating.")
                    return render(request, 'resort_portal/security.html')
                
                vendor.set_manager_pin(pin)
                log_user_activity(vendor, None, request.user, "Manager PIN Updated", f"Manager PIN was {'set' if not request.user.resort_manager_pin else 'updated'}", 'security', 'shield')
                
                from django.contrib import messages
                messages.success(request, "Manager PIN updated successfully.")
    
    return render(request, 'resort_portal/security.html')

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
    current_prop = get_active_property(request)
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
                active_prop = get_active_property(request)

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
            active_prop = get_active_property(request)
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
    current_prop = get_active_property(request)
    
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

# Manager Authentication Views
def generate_verification_code():
    """Generate 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code, vendor_name):
    """Send verification code via email."""
    subject = f"Manager Account Verification - {vendor_name}"
    message = f"""
Your verification code for {vendor_name} is: {code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.
"""
    try:
        send_mail(
            subject,
            message,
            'noreply@campopawa.com',
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        import logging
        logging.error(f"Failed to send verification email: {e}")
        return False

def manager_auth_setup(request):
    """Initial manager authentication setup."""
    vendor = request.user
    
    # Check if already set up
    if hasattr(vendor, 'manager_auth') and vendor.manager_auth.is_verified:
        return redirect('resort_portal:manager_login')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        else:
            # Create or update manager auth
            manager_auth, created = ManagerAuth.objects.get_or_create(
                vendor=vendor,
                defaults={
                    'email': email,
                    'phone': phone,
                    'password_hash': make_password(password),
                    'verification_code': generate_verification_code(),
                    'verification_expires': timezone.now() + timedelta(minutes=15),
                }
            )
            
            if not created:
                manager_auth.email = email
                manager_auth.phone = phone
                manager_auth.password_hash = make_password(password)
                manager_auth.verification_code = generate_verification_code()
                manager_auth.verification_expires = timezone.now() + timedelta(minutes=15)
                manager_auth.is_verified = False
                manager_auth.save()
            
            # Send verification email
            if send_verification_email(email, manager_auth.verification_code, vendor.business_name):
                messages.success(request, "Verification code sent to your email.")
                return redirect('resort_portal:manager_verify')
            else:
                messages.error(request, "Failed to send verification email. Please try again.")
    
    return render(request, 'resort_portal/auth/setup.html')

def manager_verify(request):
    """Verify manager account with email code."""
    vendor = request.user
    
    if not hasattr(vendor, 'manager_auth'):
        return redirect('resort_portal:manager_setup')
    
    manager_auth = vendor.manager_auth
    
    # Check if verification expired
    if timezone.now() > manager_auth.verification_expires:
        messages.error(request, "Verification code expired. Please request a new one.")
        return redirect('resort_portal:manager_setup')
    
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        
        if code == manager_auth.verification_code:
            manager_auth.is_verified = True
            manager_auth.verification_code = ''
            manager_auth.verification_expires = None
            manager_auth.save()
            
            messages.success(request, "Account verified successfully! You can now log in.")
            return redirect('resort_portal:manager_login')
        else:
            messages.error(request, "Invalid verification code.")
    
    return render(request, 'resort_portal/auth/verify.html')

def manager_login(request):
    """Manager login with email and password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            vendor = Vendor.objects.get(manager_auth__email=email)
            manager_auth = vendor.manager_auth
            
            # Check if account is locked
            if manager_auth.is_locked():
                messages.error(request, "Account locked due to too many failed attempts. Try again later.")
                return render(request, 'resort_portal/auth/login.html')
            
            # Check if account is verified
            if not manager_auth.is_verified:
                messages.error(request, "Account not verified. Please check your email.")
                return render(request, 'resort_portal/auth/login.html')
            
            # Verify password
            if check_password(password, manager_auth.password_hash):
                # Successful login
                manager_auth.reset_failed_attempts()
                request.session['manager_authenticated'] = True
                request.session['manager_vendor_id'] = vendor.id
                request.session['manager_login_time'] = timezone.now().isoformat()
                
                log_user_activity(vendor, None, request.user, "Manager Login", "Manager successfully logged in", 'security', 'shield')
                
                messages.success(request, f"Welcome back, {vendor.business_name}!")
                return redirect('resort_portal:overview')
            else:
                # Failed login
                manager_auth.increment_failed_attempts()
                remaining_attempts = 5 - manager_auth.failed_attempts
                messages.error(request, f"Invalid password. {remaining_attempts} attempts remaining.")
                
        except Vendor.DoesNotExist:
            messages.error(request, "No account found with this email.")
    
    return render(request, 'resort_portal/auth/login.html')

def manager_logout(request):
    """Manager logout."""
    if request.session.get('manager_authenticated'):
        vendor_id = request.session.get('manager_vendor_id')
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            log_user_activity(vendor, None, request.user, "Manager Logout", "Manager logged out", 'security', 'shield')
        except Vendor.DoesNotExist:
            pass
    
    # Clear manager session
    request.session.pop('manager_authenticated', None)
    request.session.pop('manager_vendor_id', None)
    request.session.pop('manager_login_time', None)
    request.session.pop('resort_manager_unlocked', None)  # Clear old PIN session
    
    messages.info(request, "Logged out successfully.")
    return redirect('resort_portal:manager_login')

def manager_forgot_password(request):
    """Forgot password - send verification code."""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            vendor = Vendor.objects.get(manager_auth__email=email)
            manager_auth = vendor.manager_auth
            
            # Generate new verification code
            manager_auth.verification_code = generate_verification_code()
            manager_auth.verification_expires = timezone.now() + timedelta(minutes=15)
            manager_auth.save()
            
            if send_verification_email(email, manager_auth.verification_code, vendor.business_name):
                messages.success(request, "Password reset code sent to your email.")
                request.session['reset_email'] = email
                return redirect('resort_portal:manager_reset_password')
            else:
                messages.error(request, "Failed to send reset email. Please try again.")
                
        except Vendor.DoesNotExist:
            messages.error(request, "No account found with this email.")
    
    return render(request, 'resort_portal/auth/forgot.html')

def manager_reset_password(request):
    """Reset password with verification code."""
    email = request.session.get('reset_email')
    
    if not email:
        return redirect('resort_portal:manager_forgot_password')
    
    try:
        vendor = Vendor.objects.get(manager_auth__email=email)
        manager_auth = vendor.manager_auth
        
        # Check if verification expired
        if timezone.now() > manager_auth.verification_expires:
            messages.error(request, "Reset code expired. Please request a new one.")
            return redirect('resort_portal:manager_forgot_password')
        
        if request.method == 'POST':
            code = request.POST.get('verification_code')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if code != manager_auth.verification_code:
                messages.error(request, "Invalid verification code.")
            elif password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif len(password) < 8:
                messages.error(request, "Password must be at least 8 characters.")
            else:
                # Reset password
                manager_auth.password_hash = make_password(password)
                manager_auth.verification_code = ''
                manager_auth.verification_expires = None
                manager_auth.save()
                
                # Clear session
                request.session.pop('reset_email', None)
                
                messages.success(request, "Password reset successfully! You can now log in.")
                return redirect('resort_portal:manager_login')
        
        return render(request, 'resort_portal/auth/reset.html', {'email': email})
        
    except Vendor.DoesNotExist:
        messages.error(request, "Invalid session. Please try again.")
        return redirect('resort_portal:manager_forgot_password')
