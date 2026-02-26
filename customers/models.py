from django.db import models
from django.utils import timezone
from datetime import timedelta

CUSTOMER_STATUS = [
    ('new',     'New'),
    ('regular', 'Regular'),
    ('loyal',   'Loyal'),
    ('atrisk',  'At-Risk'),
]

class Customer(models.Model):
    vendor   = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='customers')
    name     = models.CharField(max_length=120)
    phone    = models.CharField(max_length=20)
    notes    = models.TextField(blank=True)
    tags     = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'phone')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.name} — {self.vendor.business_name}"

    @property
    def total_visits(self):
        return self.purchases.count()

    @property
    def total_spent(self):
        return self.purchases.aggregate(
            t=models.Sum('amount')
        )['t'] or 0

    @property
    def last_purchase(self):
        return self.purchases.order_by('-purchased_at').first()

    @property
    def status(self):
        visits = self.total_visits
        last   = self.last_purchase
        if not last:
            return 'new'
        days_since = (timezone.now() - last.purchased_at).days
        if days_since >= 14:
            return 'atrisk'
        if visits >= 8:
            return 'loyal'
        if visits >= 3:
            return 'regular'
        return 'new'

    @property
    def status_label(self):
        return dict(CUSTOMER_STATUS).get(self.status, 'New')

    @property
    def initials(self):
        parts = self.name.strip().split()
        return ''.join(p[0].upper() for p in parts[:2])

    @property
    def tag_list(self):
        """Return tags as a list."""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Purchase(models.Model):
    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    service      = models.CharField(max_length=120, blank=True)
    amount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes        = models.TextField(blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.customer.name} — KES {self.amount}"


class LoyaltyProgram(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='loyalty_programs')
    name = models.CharField(max_length=100)  # e.g. "Buy 5 Get 1 Free"
    visits_required = models.PositiveIntegerField(default=5)
    reward_description = models.CharField(max_length=200)  # e.g. "Free chai"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.vendor.business_name})"


class LoyaltyCard(models.Model):
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='cards')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_cards')
    stamps = models.PositiveIntegerField(default=0)
    rewards_earned = models.PositiveIntegerField(default=0)
    last_stamped = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['program', 'customer']

    @property
    def is_reward_ready(self):
        return self.stamps >= self.program.visits_required

    @property
    def stamps_remaining(self):
        return max(0, self.program.visits_required - self.stamps)

    @property
    def progress_percent(self):
        return min(100, int((self.stamps / self.program.visits_required) * 100))

    def __str__(self):
        return f"{self.customer.name} — {self.program.name} ({self.stamps}/{self.program.visits_required})"


class Reminder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('dismissed', 'Dismissed'),
    ]

    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='reminders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reminders')
    message = models.CharField(max_length=300)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reminder: {self.customer.name} — {self.status}"


class Receipt(models.Model):
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=20, unique=True)
    sent_via_sms = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number}"

    @staticmethod
    def generate_number():
        import random
        return f"CP-{timezone.now().strftime('%y%m%d')}-{random.randint(1000, 9999)}"
