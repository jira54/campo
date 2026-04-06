from django.db import models
from django.utils import timezone
from vendors.models import Vendor

class ResortGuest(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_guests')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    vip_status = models.BooleanField(default=False)
    preferences = models.TextField(blank=True, help_text="e.g. Allergic to peanuts, prefers ground floor")
    total_stays = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}{' (VIP)' if self.vip_status else ''}"

class Room(models.Model):
    STATUS_CHOICES = [
        ('vacant_clean', 'Vacant (Clean)'),
        ('vacant_dirty', 'Vacant (Needs Cleaning)'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Out of Order')
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=100, default='Standard')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vacant_clean')
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('vendor', 'room_number')

    def __str__(self):
        return f"Room {self.room_number} ({self.get_status_display()})"

class Department(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_departments')
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
    guest = models.ForeignKey(ResortGuest, on_delete=models.CASCADE, related_name='folios')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='folios')
    
    check_in_date = models.DateField(default=timezone.now)
    check_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    def __str__(self):
        return f"Folio #{self.id} - {self.guest.name} ({self.get_status_display()})"

class FolioCharge(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='resort_charges')
    
    # If folio is null, it means it's a Walk-In customer paying directly at the POS
    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, null=True, blank=True, related_name='charges')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='charges')
    
    description = models.CharField(max_length=255) # e.g., "2x Mojitos" or "Room Rate Night 1"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False) # True if paid instantly (walk-in), False if charged to Room
    
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} ({self.department.name if self.department else 'General'})"
