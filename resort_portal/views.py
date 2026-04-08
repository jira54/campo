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
    from .models import ResortGuest
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register_guest':
            name = request.POST.get('name')
            if name:
                guest = ResortGuest.objects.create(
                    vendor=vendor,
                    name=name,
                    phone=request.POST.get('phone', ''),
                    email=request.POST.get('email', ''),
                    passport_id=request.POST.get('passport_id', ''),
                    nationality=request.POST.get('nationality', 'Kenyan'),
                    guest_type=request.POST.get('guest_type', 'overnight'),
                    vip_status=request.POST.get('vip_status') == 'on',
                    preferences=request.POST.get('preferences', '')
                )
                from django.contrib import messages
                messages.success(request, f"Guest {guest.name} registered successfully.")
    
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
        'all_guests': ResortGuest.objects.filter(vendor=vendor).order_by('name'), # Added for universal billing
        'dirty_room_list': rooms.filter(status='vacant_dirty').order_by('room_number'), # Added for Housekeeping Controller
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
        guest_id = request.POST.get('guest_id')
        desc = request.POST.get('description', 'Service Charge')
        
        if amount and dept_id:
            try:
                from .models import ResortGuest
                dept = Department.objects.get(vendor=vendor, id=dept_id)
                folio = None
                guest = None
                
                if folio_id:
                    folio = Folio.objects.get(vendor=vendor, id=folio_id)
                elif guest_id:
                    guest = ResortGuest.objects.get(vendor=vendor, id=guest_id)
                
                FolioCharge.objects.create(
                    vendor=vendor,
                    folio=folio,
                    guest=guest,
                    department=dept,
                    amount=amount,
                    description=desc,
                    is_paid=False if folio else True
                )
            except (Department.DoesNotExist, Folio.DoesNotExist):
                pass
                
    from django.shortcuts import redirect
    return redirect('resort_portal:dashboard')

@login_required
@resort_enterprise_required
def guest_index(request):
    """Boutique Guest Directory Index."""
    from .models import ResortGuest
    vendor = request.user
    guests = ResortGuest.objects.filter(vendor=vendor).order_by('-created_at')
    
    # Filtering & Search
    q = request.GET.get('q')
    gtype = request.GET.get('type')
    
    if q:
        guests = guests.filter(
            Q(name__icontains=q) | 
            Q(phone__icontains=q) | 
            Q(passport_id__icontains=q)
        )
    if gtype:
        guests = guests.filter(guest_type=gtype)

    return render(request, 'resort_portal/guest_list.html', {
        'guests': guests,
        'search_query': q or '',
        'current_type': gtype or '',
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
