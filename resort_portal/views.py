from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
import datetime

from .decorators import resort_enterprise_required
from .models import Room, Folio, FolioCharge, Department, HousekeepingLog

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
    """Internal helper for guest registration with simplified types."""
    from .models import ResortGuest
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email', '')
    gtype = request.POST.get('guest_type', 'overnight')
    pid = request.POST.get('passport_id')
    vip = request.POST.get('vip_status') == 'on'
    
    if name:
        guest = ResortGuest.objects.create(
            vendor=vendor,
            resort_property=current_prop,
            name=name,
            phone=phone,
            email=email,
            guest_type=gtype,
            passport_id=pid,
            vip_status=vip,
            preferences=request.POST.get('preferences', '')
        )
        from django.contrib import messages
        messages.success(request, f"Guest {guest.name} registered successfully.")
        return guest
    return None

@login_required
@resort_enterprise_required
def resort_dashboard(request):
    vendor = request.user
    current_prop = _get_active_property(request)
    if not current_prop:
        from django.contrib import messages
        messages.warning(request, "Please set up a property to continue.")
        return redirect('resort_portal:setup')

    from .models import ResortGuest, Department
    
    # Auto-initialize 'General Services' if no revenue centers exist for THIS property
    if not Department.objects.filter(vendor=vendor, resort_property=current_prop).exists():
        Department.objects.create(vendor=vendor, resort_property=current_prop, name='General Services')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register_guest':
            _handle_guest_registration(request, vendor, current_prop)
    
    try:
        today = timezone.now().date()
        
        # Insights Engine: Room Status (Property-Specific)
        rooms = Room.objects.filter(vendor=vendor, resort_property=current_prop)
        total_rooms = rooms.count()
        occupied_rooms = rooms.filter(status='occupied').count()
        dirty_rooms = rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).count()
        
        occupancy_rate = round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0)
        
        # Insights Engine: Revenue Today (Property-Specific)
        charges_today = FolioCharge.objects.filter(vendor=vendor, resort_property=current_prop, logged_at__date=today)
        total_revenue_today = charges_today.aggregate(total=Sum('amount'))['total'] or 0
        
        dept_revenue = (
            charges_today.values('department__name')
            .annotate(revenue=Sum('amount'))
            .order_by('-revenue')
        )
        dept_revenue = [{'name': d['department__name'] or 'General', 'revenue': d['revenue']} for d in dept_revenue]
            
        # Active Folios (Property-Specific)
        active_folios = Folio.objects.filter(
            vendor=vendor, 
            resort_property=current_prop, 
            status='open'
        ).select_related('guest', 'room').order_by('room__room_number')
        
        # Day Visitors Today (Property-Specific)
        day_visitors = ResortGuest.objects.filter(
            vendor=vendor,
            resort_property=current_prop,
            guest_type='day_visitor',
            created_at__date=today
        ).count()

        # VIP Check-Ins Today (Property-Specific)
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
            'day_visitors': day_visitors,
            'departments': Department.objects.filter(vendor=vendor, resort_property=current_prop),
            'all_guests': ResortGuest.objects.filter(vendor=vendor, resort_property=current_prop).order_by('name'),
            'dirty_room_list': rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).order_by('room_number'),
        }
    except Exception as e:
        context = {
            'total_rooms': 0, 'occupied_rooms': 0, 'dirty_rooms': 0,
            'occupancy_rate': 0, 'total_revenue_today': 0, 'dept_revenue': [],
            'active_folios': [], 'vip_arrivals': 0, 'day_visitors': 0,
            'departments': [], 'all_guests': [], 'dirty_room_list': [],
            'critical_error': str(e)
        }
    
    # Add available rooms for check-in
    available_rooms = rooms.filter(status='clean')
    context['available_rooms'] = available_rooms
    context['all_rooms'] = rooms.order_by('room_number')
    
    # Use simplified template if requested
    template_name = 'resort_portal/dashboard-simple.html' if request.GET.get('simple') == 'true' else 'resort_portal/dashboard.html'
    return render(request, template_name, context)

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
    """Simplified Service Billing: Directly to Bill or Walk-in Profile."""
    from .models import Folio, FolioCharge, Department, ResortGuest
    vendor = request.user
    
    if request.method == 'POST':
        folio_id = request.POST.get('folio_id')
        guest_name = request.POST.get('guest_name')
        dept_id = request.POST.get('department_id')
        amount = request.POST.get('amount')
        desc = request.POST.get('description')
        
        if amount:
            try:
                folio = None
                guest = None
                
                if folio_id:
                    if folio_id.startswith('guest_'):
                        # Direct charge to a Guest Profile (no active room stay)
                        g_id = folio_id.split('_')[1]
                        guest = ResortGuest.objects.get(vendor=vendor, id=g_id)
                    else:
                        # Charge to an active Room Folio (Stay)
                        folio = Folio.objects.get(vendor=vendor, id=folio_id, status='open')
                        guest = folio.guest
                elif guest_name:
                    # Quick Walk-in Creation
                    active_prop = _get_active_property(request)
                    guest, _ = ResortGuest.objects.get_or_create(
                        vendor=vendor,
                        resort_property=active_prop,
                        name=guest_name,
                        defaults={'guest_type': 'day_visitor'}
                    )
                
                if dept_id == 'default':
                    dept = Department.objects.filter(vendor=vendor, resort_property=folio.resort_property if folio else _get_active_property(request)).first()
                else:
                    dept = Department.objects.get(vendor=vendor, id=dept_id)

                FolioCharge.objects.create(
                    vendor=vendor,
                    resort_property=folio.resort_property if folio else _get_active_property(request),
                    folio=folio,
                    guest=guest,
                    department=dept,
                    amount=amount,
                    description=desc,
                    is_paid=False if folio else True # Direct guest charges are assumed paid at POS
                )
            except (Department.DoesNotExist, Folio.DoesNotExist, ResortGuest.DoesNotExist):
                pass
                
    return redirect('resort_portal:dashboard')

@login_required
@resort_enterprise_required
def guest_index(request):
    """Strategic Guest CRM Hub."""
    from .models import ResortGuest, Folio
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
    from .models import ResortGuest, FolioCharge
    vendor = request.user
    guest = get_object_or_404(ResortGuest, vendor=vendor, id=guest_id)
    
    # Stay Records
    folios = guest.folios.all().order_by('-check_in_date')
    
    # Financial Intelligence
    all_charges = FolioCharge.objects.filter(guest=guest, vendor=vendor).order_by('-logged_at')
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
        'folios': folios,
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
    return redirect('resort_portal:dashboard')

@login_required
@resort_enterprise_required
def check_out_folio(request, folio_id):
    """The Grand Finale: Finalize billing and housekeeping."""
    from django.shortcuts import get_object_or_404, redirect
    from .models import Folio, Room
    
    vendor = request.user
    folio = get_object_or_404(Folio, vendor=vendor, id=folio_id, status='open')
    
    # 1. Archive the stay
    folio.status = 'closed'
    folio.check_out_date = timezone.now().date()
    folio.save()
    
    # Update Guest Lifetime Stays
    folio.guest.total_stays += 1
    folio.guest.save()
    
    # 2. Flag Room for Housekeeping
    if folio.room:
        folio.room.status = 'vacant_dirty'
        folio.room.save()
        
    # 3. Calculate Final Toll
    charges = folio.charges.all()
    total = charges.aggregate(total=Sum('amount'))['total'] or 0
    
    # 4. Dispatch Receipt (Only if Guest has Email)
    if folio.guest.email:
        try:
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.core.mail import send_mail
            
            subject = f"Receipt: Your Stay at {vendor.business_name}"
            html_message = render_to_string('resort_portal/folio_receipt_email.html', {
                'folio': folio,
                'charges': charges,
                'total': total,
                'vendor': vendor,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                None, # Uses DEFAULT_FROM_EMAIL
                [folio.guest.email],
                html_message=html_message,
                fail_silently=True
            )
            messages.success(request, f"Digital receipt sent to {folio.guest.email}")
        except Exception:
            messages.warning(request, "Check-out successful, but receipt email failed to send.")
    
    messages.success(request, f"Guest {folio.guest.name} checked out. Room {folio.room.room_number if folio.room else 'N/A'} is now flagged for cleaning.")
    
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
