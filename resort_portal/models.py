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

class Folio(models.Model):
    STATUS_CHOICES = [
        ('open', 'Checked-In (Open)'),
        ('closed', 'Checked-Out (Closed)'),
        ('canceled', 'Canceled')
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_folios')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='folios')
    guest = models.ForeignKey(ResortGuest, on_delete=models.CASCADE, related_name='folios')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='folios')
    
    check_in_date = models.DateField(default=timezone.now)
    check_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    def __str__(self):
        return f"Folio #{self.id} - {self.guest.name} ({self.get_status_display()})"

class FolioCharge(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_charges')
    resort_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='charges', null=True, blank=True)
    
    # If folio is null, it might be a Day Visitor or direct POS charge
    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, null=True, blank=True, related_name='charges')
    guest = models.ForeignKey(ResortGuest, on_delete=models.SET_NULL, null=True, blank=True, related_name='all_charges')
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='charges')
    
    description = models.CharField(max_length=255) # e.g., "2x Mojitos" or "Room Rate Night 1"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False) # True if paid instantly (walk-in), False if charged to Room
    
    logged_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-link guest and property if Folio is present
        if self.folio:
            if not self.guest:
                self.guest = self.folio.guest
            if not self.resort_property:
                self.resort_property = self.folio.resort_property
        elif self.guest and not self.resort_property:
            self.resort_property = self.guest.resort_property
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} ({self.department.name if self.department else 'General'})"

class HousekeepingLog(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='housekeeping_logs')
    staff_name = models.CharField(max_length=100, blank=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room.room_number}: {self.old_status} -> {self.new_status}"
