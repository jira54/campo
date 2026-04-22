from django.db import models
from django.utils import timezone
from vendors.models import Vendor, Property

class ResortGuest(models.Model):
    GUEST_TYPES = [
        ('overnight', 'Overnight Guest'),
        ('day_visitor', 'Day Visitor (Picnic/Event/Dining)'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_guests')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, default='')
    
    # Compliance & CRM
    passport_id = models.CharField(max_length=100, blank=True, help_text="ID or Passport Number")
    nationality = models.CharField(max_length=100, blank=True, default='Kenyan')
    guest_type = models.CharField(max_length=20, choices=GUEST_TYPES, default='overnight')
    
    vip_status = models.BooleanField(default=False)
    preferences = models.TextField(blank=True, help_text="Flexible staff notes on guest preferences")
    total_stays = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_guest_type_display()})"

    @property
    def last_stay(self):
        """Returns the most recent completed folio checkout date."""
        last_folio = self.folios.filter(status='closed').order_by('-check_out_date').first()
        return last_folio.check_out_date if last_folio else None

    @property
    def is_active(self):
        """True if the guest currently has an open folio (is checked in)."""
        return self.folios.filter(status='open').exists()

    @property
    def status(self):
        """Strategic segmentation for boutique CRM."""
        if self.is_active:
            return 'active'
        if self.vip_status:
            return 'vip'
        
        last = self.last_stay
        if last:
            days_since = (timezone.now().date() - last).days
            if days_since >= 180:
                return 'at_risk'
        
        if self.total_stays >= 5:
            return 'loyal'
        if self.total_stays >= 2:
            return 'regular'
            
        return 'new'

    @property
    def status_label(self):
        labels = {
            'active': 'Active Stay',
            'vip': 'VIP Elite',
            'loyal': 'Loyal Resident',
            'regular': 'Regular',
            'at_risk': 'At Risk',
            'new': 'New Guest'
        }
        return labels.get(self.status, 'New Guest')

class Room(models.Model):
    STATUS_CHOICES = [
        ('vacant_clean',   'Vacant (Clean)'),
        ('vacant_dirty',   'Vacant (Dirty)'),
        ('cleaning',       'Cleaning In Progress'),
        ('inspected',      'Ready for Inspection'),
        ('occupied',        'Occupied'),
        ('maintenance',     'Maintenance / OOO')
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_rooms')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=100, default='Standard')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vacant_clean')
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('resort_property', 'room_number')

    def __str__(self):
        return f"Room {self.room_number} ({self.get_status_display()})"

class Department(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_departments')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100) # e.g. "Main Restaurant", "Spa", "Pool Bar"
    
    def __str__(self):
        return self.name

class StayRecord(models.Model):
    STATUS_CHOICES = [
        ('open', 'Active'),
        ('closed', 'Completed'),
        ('canceled', 'Canceled')
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_stays')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='stays')
    guest = models.ForeignKey(ResortGuest, on_delete=models.CASCADE, related_name='folios')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='stays')
    
    check_in_date = models.DateField(default=timezone.now)
    check_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    def __str__(self):
        return f"Stay #{self.id} - {self.guest.name} ({self.get_status_display()})"

class ServiceCharge(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_charges')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='charges', null=True, blank=True)
    
    # Linked to a stay or direct to guest
    stay = models.ForeignKey(StayRecord, on_delete=models.CASCADE, null=True, blank=True, related_name='charges')
    guest = models.ForeignKey(ResortGuest, on_delete=models.SET_NULL, null=True, blank=True, related_name='all_charges')
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='charges')
    
    # POS Tracking (for non-room guests)
    table = models.ForeignKey('RestaurantTable', on_delete=models.SET_NULL, null=True, blank=True, related_name='charges')
    seat = models.ForeignKey('BarSeat', on_delete=models.SET_NULL, null=True, blank=True, related_name='charges')
    
    description = models.CharField(max_length=255) # e.g., "2x Mojitos" or "Room Rate Night 1"
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount charged (VAT inclusive)")
    
    # KRA Compliance / VAT Engine fields
    tax_rate    = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)
    tax_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    is_paid = models.BooleanField(default=False)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-link guest and property if Stay is present
        if self.stay:
            if not self.guest:
                self.guest = self.stay.guest
            if not self.resort_property:
                self.resort_property = self.stay.resort_property
        elif self.guest and not self.resort_property:
            self.resort_property = self.guest.resort_property
            
        # VAT Engine Logic (KRA compliant inclusive calculation)
        if self.amount and self.tax_rate:
            from decimal import Decimal, ROUND_HALF_UP
            # Formula: Net = Gross / (1 + Rate/100)
            divisor = Decimal('1.0') + (self.tax_rate / Decimal('100.0'))
            self.net_amount = (self.amount / divisor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.tax_amount = (self.amount - self.net_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} - {self.description} ({self.department.name if self.department else 'General'})"

class HousekeepingLog(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='housekeeping_logs')
    staff_name = models.CharField(max_length=100, blank=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room.room_number}: {self.old_status} -> {self.new_status}"

class RestaurantTable(models.Model):
    STATUS_CHOICES = [('available', 'Available'), ('occupied', 'Occupied'), ('reserved', 'Reserved'), ('cleaning', 'Cleaning')]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='restaurant_tables')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='restaurant_tables')
    table_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=4)
    table_type = models.CharField(max_length=50, default='Standard') # Standard, Booth, VIP, Deck
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table {self.table_number} ({self.resort_property.name})"

class BarSeat(models.Model):
    STATUS_CHOICES = [('available', 'Available'), ('occupied', 'Occupied'), ('reserved', 'Reserved')]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='bar_seats')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bar_seats')
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=50, default='Bar Stool') # Stool, Booth, Lounge
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Seat {self.seat_number} - {self.resort_property.name}"

class EventSpace(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='event_spaces')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='event_spaces')
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    space_type = models.CharField(max_length=50) # Conference, Garden, Ballroom
    rate_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.resort_property.name})"

class EventBooking(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('active', 'Active'), ('completed', 'Completed'), ('canceled', 'Canceled')]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='event_bookings')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='event_bookings')
    space = models.ForeignKey(EventSpace, on_delete=models.CASCADE, related_name='bookings')
    title = models.CharField(max_length=200)
    organizer_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.title} - {self.organizer_name}"

class DayPass(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='day_passes')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='day_passes')
    name = models.CharField(max_length=100) # e.g. "Pool Pass", "Lunch & Swim"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    includes_services = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price}"

class DayVisitor(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('completed', 'Completed'), ('canceled', 'Canceled')]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='day_visitors')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='day_visitors')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    pass_type = models.ForeignKey(DayPass, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class Facility(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_facilities')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=100) # Gym, Spa, Pool, Sauna
    status = models.CharField(max_length=50, default='Open') # Open, Closed, Maintenance
    
    def __str__(self):
        return self.name

from django.conf import settings

class ResortSettings(models.Model):
    """Centralized configuration for resort operations."""
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='resort_settings')
    resort_property = models.ForeignKey('vendors.Property', on_delete=models.CASCADE, related_name='settings', null=True, blank=True)
    
    # Financial Settings
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00, help_text="Default VAT rate for calculations")
    currency_code = models.CharField(max_length=3, default='KES', help_text="Currency code for display")
    currency_symbol = models.CharField(max_length=5, default='KSh', help_text="Currency symbol for display")
    
    # Department Configuration
    default_department_names = models.JSONField(
        default=dict, 
        help_text="Default department names for auto-creation"
    )
    
    # Operational Settings
    auto_checkout_time = models.TimeField(default='10:00', help_text="Default check-out time")
    auto_checkin_time = models.TimeField(default='14:00', help_text="Default check-in time")
    housekeeping_alert_threshold = models.PositiveIntegerField(default=5, help_text="Alert when dirty rooms exceed this number")
    
    # Display Settings
    dashboard_refresh_interval = models.PositiveIntegerField(default=300, help_text="Dashboard auto-refresh interval in seconds")
    enable_vip_alerts = models.BooleanField(default=True, help_text="Show VIP arrival alerts")
    enable_revenue_alerts = models.BooleanField(default=True, help_text="Show revenue milestone alerts")
    
    # Security Settings
    pin_expiry_days = models.PositiveIntegerField(default=90, help_text="Days after which PIN should be changed")
    max_login_attempts = models.PositiveIntegerField(default=3, help_text="Maximum failed login attempts before lockout")
    
    # Email Settings
    enable_email_receipts = models.BooleanField(default=True, help_text="Send email receipts on check-out")
    receipt_email_template = models.TextField(blank=True, help_text="Custom email template for receipts")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Resort Settings"
        verbose_name_plural = "Resort Settings"
    
    def __str__(self):
        return f"Settings for {self.vendor.business_name}"
    
    @classmethod
    def get_settings(cls, vendor, property_obj=None):
        """Get or create settings for vendor/property."""
        settings, created = cls.objects.get_or_create(
            vendor=vendor,
            resort_property=property_obj,
            defaults={
                'default_department_names': {
                    'accommodation': 'Room Revenue',
                    'restaurant': 'Main Restaurant', 
                    'bar': 'Pool Bar',
                    'spa': 'Spa & Wellness',
                    'events': 'Events & Functions'
                }
            }
        )
        return settings

class ManagerAuth(models.Model):
    """
    Unified manager authentication model.
    Replaces both Vendor.resort_manager_pin and old ManagerAuth.
    """
    
    # Core relationship
    vendor = models.OneToOneField(
        'vendors.Vendor',
        on_delete=models.CASCADE,
        related_name='manager_auth',
        primary_key=True
    )
    
    # Email/Phone credentials
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    # Password (primary login)
    password_hash = models.CharField(max_length=255)
    password_changed_at = models.DateTimeField(default=timezone.now)
    
    # PIN (secondary unlock)
    manager_pin = models.CharField(max_length=128, blank=True, null=True)
    pin_set_at = models.DateTimeField(null=True, blank=True)
    
    # Email verification
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    verification_sent_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Password security
    failed_password_attempts = models.PositiveIntegerField(default=0)
    password_locked_until = models.DateTimeField(null=True, blank=True)
    
    # PIN security
    failed_pin_attempts = models.PositiveIntegerField(default=0)
    pin_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_pin_unlock_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'resort_portal_manager_auth'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['vendor']),
        ]
        verbose_name = "Manager Authentication"
        verbose_name_plural = "Manager Authentication"
    
    def __str__(self):
        return f"Manager: {self.email}"
    
    # ============ PASSWORD METHODS ============
    
    def set_password(self, raw_password):
        """Hash and store password."""
        self.password_hash = make_password(raw_password)
        self.password_changed_at = timezone.now()
        self.failed_password_attempts = 0
        self.password_locked_until = None
        self.save()
    
    def check_password(self, raw_password):
        """Verify password (returns True/False)."""
        return check_password(raw_password, self.password_hash)
    
    def is_password_locked(self):
        """Check if account is locked due to failed attempts."""
        if not self.password_locked_until:
            return False
        if timezone.now() > self.password_locked_until:
            self.password_locked_until = None
            self.failed_password_attempts = 0
            self.save()
            return False
        return True
    
    def record_failed_password_attempt(self):
        """Record failed login attempt. Lock after 5 failures."""
        self.failed_password_attempts += 1
        
        if self.failed_password_attempts >= 5:
            self.password_locked_until = timezone.now() + timedelta(minutes=30)
        
        self.save()
    
    def reset_password_attempts(self):
        """Clear failed attempts on successful login."""
        self.failed_password_attempts = 0
        self.password_locked_until = None
        self.last_login_at = timezone.now()
        self.save()
    
    # ============ PIN METHODS ============
    
    def set_pin(self, raw_pin):
        """Hash and store PIN."""
        self.manager_pin = make_password(raw_pin)
        self.pin_set_at = timezone.now()
        self.failed_pin_attempts = 0
        self.pin_locked_until = None
        self.save()
    
    def check_pin(self, raw_pin):
        """Verify PIN (returns True/False)."""
        if not self.manager_pin:
            return False
        return check_password(raw_pin, self.manager_pin)
    
    def is_pin_locked(self):
        """Check if PIN entry is locked due to failed attempts."""
        if not self.pin_locked_until:
            return False
        if timezone.now() > self.pin_locked_until:
            self.pin_locked_until = None
            self.failed_pin_attempts = 0
            self.save()
            return False
        return True
    
    def record_failed_pin_attempt(self):
        """Record failed PIN attempt. Lock after 3 failures."""
        self.failed_pin_attempts += 1
        
        if self.failed_pin_attempts >= 3:
            self.pin_locked_until = timezone.now() + timedelta(minutes=15)
        
        self.save()
    
    def reset_pin_attempts(self):
        """Clear failed PIN attempts on successful unlock."""
        self.failed_pin_attempts = 0
        self.pin_locked_until = None
        self.last_pin_unlock_at = timezone.now()
        self.save()
    
    # ============ STATUS METHODS ============
    
    def has_pin(self):
        """Check if PIN is configured."""
        return bool(self.manager_pin)
    
    def get_password_attempts_remaining(self):
        """Get remaining attempts before lockout."""
        return max(0, 5 - self.failed_password_attempts)
    
    def get_pin_attempts_remaining(self):
        """Get remaining PIN attempts before lockout."""
        return max(0, 3 - self.failed_pin_attempts)
    
    # Legacy compatibility methods
    def is_locked(self):
        """Check if account is locked due to failed attempts."""
        return self.is_password_locked()
    
    def can_attempt_login(self):
        """Check if user can attempt login."""
        return not self.is_locked() and self.failed_password_attempts < 5
    
    def increment_failed_attempts(self):
        """Increment failed login attempts and lock if needed."""
        self.record_failed_password_attempt()
    
    def reset_failed_attempts(self):
        """Reset failed attempts after successful login."""
        self.reset_password_attempts()

class UserActivity(models.Model):
    CATEGORIES = [('guest', 'Guest Ops'), ('financial', 'Financial'), ('housekeeping', 'Housekeeping'), ('pos', 'Service/POS')]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_activities')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='activities', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    action = models.CharField(max_length=255) # e.g. "Guest Checked In"
    icon = models.CharField(max_length=10, default='✨')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='guest')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.created_at}"
