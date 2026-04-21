"""
Resort Portal Utilities - Common functions and helpers
"""
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def get_active_property(request):
    """Internal helper to ensure property context is consistent in views."""
    from vendors.models import Property
    
    prop_id = request.session.get('current_property_id')
    if prop_id:
        prop = Property.objects.filter(vendor=request.user, id=prop_id).first()
        if prop: 
            return prop
    
    prop = Property.objects.filter(vendor=request.user, is_default=True).first() or \
           Property.objects.filter(vendor=request.user).first()
    if prop:
        request.session['current_property_id'] = prop.id
    return prop


def validate_guest_registration_data(request):
    """Validate guest registration data with comprehensive error checking."""
    errors = []
    
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
    
    # Validation
    if (method in ['name', 'both'] and not name) or (method == 'email' and not email):
        errors.append("Required identification fields missing.")
    
    # Phone validation if provided
    if phone and not phone.replace('-', '').replace(' ', '').isdigit():
        errors.append("Invalid phone number format.")
    
    # Email validation if provided
    if email and '@' not in email:
        errors.append("Invalid email address format.")
    
    return {
        'method': method,
        'name': name or email.split('@')[0] if email else '',
        'phone': phone or '',
        'email': email or '',
        'passport_id': passport_id or '',
        'errors': errors
    }


def get_dashboard_metrics(vendor, property_obj, period='today'):
    """Get cached dashboard metrics with fallback to calculation."""
    # Handle custom date ranges
    if period.startswith('custom_'):
        # For custom ranges, don't cache (too many combinations)
        try:
            start_str, end_str = period.split('_')[1:3]
            start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d').date()
            return calculate_dashboard_metrics_custom(vendor, property_obj, start_date, end_date)
        except Exception as e:
            logger.error(f"Error parsing custom date range: {e}")
            return get_default_metrics()
    
    cache_key = f"dashboard_metrics_{vendor.id}_{property_obj.id}_{period}"
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Calculate metrics if not cached
    try:
        metrics = calculate_dashboard_metrics(vendor, property_obj, period)
        
        # Cache for 5 minutes
        cache.set(cache_key, metrics, 300)
        return metrics
    except Exception as e:
        logger.error(f"Error calculating dashboard metrics: {e}")
        return get_default_metrics()


def calculate_dashboard_metrics_custom(vendor, property_obj, start_date, end_date):
    """Calculate dashboard metrics for custom date range."""
    from .models import ServiceCharge, StayRecord, Room, Department
    
    # Custom period metrics
    charges_current = ServiceCharge.objects.filter(
        vendor=vendor, 
        resort_property=property_obj, 
        logged_at__date__range=[start_date, end_date]
    )
    
    aggregates = charges_current.aggregate(
        total=Sum('amount'),
        tax=Sum('tax_amount'),
        net=Sum('net_amount')
    )
    
    # Room metrics
    rooms = Room.objects.filter(vendor=vendor, resort_property=property_obj)
    total_rooms = rooms.count()
    occupied_rooms = rooms.filter(status='occupied').count()
    dirty_rooms = rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).count()
    
    # Occupancy calculation
    num_days = max(1, (end_date - start_date).days + 1)
    total_capacity = total_rooms * num_days
    
    room_nights_sold = StayRecord.objects.filter(
        vendor=vendor,
        resort_property=property_obj,
        check_in_date__lte=end_date,
        check_out_date__gte=start_date
    ).count()
    
    occupancy_rate = round((room_nights_sold / total_capacity * 100) if total_capacity > 0 else 0)
    
    # Revenue metrics
    room_rev = charges_current.filter(department__name__icontains='Room').aggregate(total=Sum('amount'))['total'] or 0
    adr = round(room_rev / room_nights_sold) if room_nights_sold > 0 else 0
    revpar = round(room_rev / total_capacity) if total_capacity > 0 else 0
    
    # Department revenue
    dept_revenue = list(
        charges_current.values('department__name')
        .annotate(revenue=Sum('amount'))
        .order_by('-revenue')
    )
    dept_revenue = [{'name': d['department__name'] or 'General', 'revenue': d['revenue']} for d in dept_revenue]
    
    # Active stays and VIP arrivals
    active_stays = StayRecord.objects.filter(
        vendor=vendor,
        resort_property=property_obj,
        status='open'
    ).select_related('guest', 'room').order_by('room__room_number')
    
    vip_arrivals = StayRecord.objects.filter(
        vendor=vendor,
        resort_property=property_obj,
        check_in_date=start_date,
        guest__vip_status=True
    ).count()
    
    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'dirty_rooms': dirty_rooms,
        'occupancy_rate': occupancy_rate,
        'total_revenue': aggregates['total'] or 0,
        'total_tax': aggregates['tax'] or 0,
        'total_net': aggregates['net'] or 0,
        'room_revenue': room_rev,
        'adr': adr,
        'revpar': revpar,
        'total_revenue_today': aggregates['total'] or 0,  # For custom ranges, use total as today
        'total_tax_today': aggregates['tax'] or 0,
        'dept_revenue': dept_revenue,
        'active_stays': active_stays,
        'vip_arrivals': vip_arrivals,
        'available_rooms': rooms.filter(status='vacant_clean'),
        'all_rooms': rooms.order_by('room_number'),
        'dirty_room_list': rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).order_by('room_number'),
    }


def calculate_dashboard_metrics(vendor, property_obj, period='today'):
    """Calculate dashboard metrics for given period."""
    from .models import ServiceCharge, StayRecord, Room, Department
    
    today = timezone.now().date()
    
    # Date range logic
    if period == 'today':
        start_date = today
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today
        end_date = today
    
    # Current period metrics
    charges_current = ServiceCharge.objects.filter(
        vendor=vendor, 
        resort_property=property_obj, 
        logged_at__date__range=[start_date, end_date]
    )
    
    aggregates = charges_current.aggregate(
        total=Sum('amount'),
        tax=Sum('tax_amount'),
        net=Sum('net_amount')
    )
    
    # Room metrics
    rooms = Room.objects.filter(vendor=vendor, resort_property=property_obj)
    total_rooms = rooms.count()
    occupied_rooms = rooms.filter(status='occupied').count()
    dirty_rooms = rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).count()
    
    # Occupancy calculation
    num_days = max(1, (end_date - start_date).days + 1)
    total_capacity = total_rooms * num_days
    
    room_nights_sold = StayRecord.objects.filter(
        vendor=vendor,
        resort_property=property_obj,
        check_in_date__lte=end_date,
        check_out_date__gte=start_date
    ).count()
    
    occupancy_rate = round((room_nights_sold / total_capacity * 100) if total_capacity > 0 else 0)
    
    # Revenue metrics
    room_rev = charges_current.filter(department__name__icontains='Room').aggregate(total=Sum('amount'))['total'] or 0
    adr = round(room_rev / room_nights_sold) if room_nights_sold > 0 else 0
    revpar = round(room_rev / total_capacity) if total_capacity > 0 else 0
    
    # Today's metrics
    charges_today = ServiceCharge.objects.filter(
        vendor=vendor, 
        resort_property=property_obj, 
        logged_at__date=today
    )
    
    today_aggregates = charges_today.aggregate(total=Sum('amount'), tax=Sum('tax_amount'))
    
    # Department revenue
    dept_revenue = list(
        charges_current.values('department__name')
        .annotate(revenue=Sum('amount'))
        .order_by('-revenue')
    )
    dept_revenue = [{'name': d['department__name'] or 'General', 'revenue': d['revenue']} for d in dept_revenue]
    
    # Active stays and VIP arrivals
    active_stays = StayRecord.objects.filter(
        vendor=vendor,
        resort_property=property_obj,
        status='open'
    ).select_related('guest', 'room').order_by('room__room_number')
    
    vip_arrivals = StayRecord.objects.filter(
        vendor=vendor,
        resort_property=property_obj,
        check_in_date=today,
        guest__vip_status=True
    ).count()
    
    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'dirty_rooms': dirty_rooms,
        'occupancy_rate': occupancy_rate,
        'total_revenue': aggregates['total'] or 0,
        'total_tax': aggregates['tax'] or 0,
        'total_net': aggregates['net'] or 0,
        'room_revenue': room_rev,
        'adr': adr,
        'revpar': revpar,
        'total_revenue_today': today_aggregates['total'] or 0,
        'total_tax_today': today_aggregates['tax'] or 0,
        'dept_revenue': dept_revenue,
        'active_stays': active_stays,
        'vip_arrivals': vip_arrivals,
        'available_rooms': rooms.filter(status='vacant_clean'),
        'all_rooms': rooms.order_by('room_number'),
        'dirty_room_list': rooms.filter(status__in=['vacant_dirty', 'cleaning', 'inspected']).order_by('room_number'),
    }


def get_default_metrics():
    """Return safe default metrics when calculations fail."""
    from .models import StayRecord, Room, Department, ResortGuest
    
    return {
        'total_rooms': 0,
        'occupied_rooms': 0,
        'dirty_rooms': 0,
        'occupancy_rate': 0,
        'total_revenue': 0,
        'total_tax': 0,
        'total_net': 0,
        'room_revenue': 0,
        'adr': 0,
        'revpar': 0,
        'total_revenue_today': 0,
        'total_tax_today': 0,
        'dept_revenue': [],
        'active_stays': StayRecord.objects.none(),
        'vip_arrivals': 0,
        'available_rooms': Room.objects.none(),
        'all_rooms': Room.objects.none(),
        'dirty_room_list': Room.objects.none(),
    }


def log_user_activity(vendor, property_obj, user, title, description, category='general', icon='info'):
    """Log user activity for audit trail."""
    from .models import UserActivity
    
    try:
        UserActivity.objects.create(
            vendor=vendor,
            resort_property=property_obj,
            user=user,
            title=title,
            description=description,
            category=category,
            icon=icon
        )
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")


def calculate_trend(current, previous):
    """Calculate percentage trend with error handling."""
    try:
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)
    except Exception:
        return 0


def clear_dashboard_cache(vendor_id, property_id):
    """Clear dashboard cache for specific vendor/property."""
    periods = ['today', 'week', 'month']
    for period in periods:
        cache_key = f"dashboard_metrics_{vendor_id}_{property_id}_{period}"
        cache.delete(cache_key)


def get_or_create_department(vendor, property_obj, name):
    """Get or create department with error handling."""
    from .models import Department
    
    try:
        dept, created = Department.objects.get_or_create(
            vendor=vendor,
            resort_property=property_obj,
            name=name,
            defaults={'name': name}
        )
        return dept
    except Exception as e:
        logger.error(f"Error getting/creating department {name}: {e}")
        return None
