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
