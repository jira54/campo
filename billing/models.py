from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta

PLAN_CHOICES = [
    ('free',             'Free Tier'),
    ('premium_retail',   'Retail Pro — KES 700/mo'),
    ('enterprise_ngo',   'Enterprise NGO — KES 3,500/mo'),
    ('enterprise_resort','Enterprise Resort — KES 3,500/mo'),
]

PLAN_PRICES = {
    'free':              0,
    'premium_retail':    700,
    'enterprise_ngo':    3500,
    'enterprise_resort': 3500,
}

class Subscription(models.Model):
    vendor     = models.OneToOneField(
        'vendors.Vendor', on_delete=models.CASCADE, related_name='subscription'
    )
    plan       = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.vendor.business_name} — {self.plan}"

    def is_active(self):
        if self.plan == 'free':
            return True
        return bool(self.expires_at and self.expires_at > timezone.now())

    def days_remaining(self):
        if not self.expires_at:
            return 0
        return max(0, (self.expires_at - timezone.now()).days)

    def extend_by_one_month(self):
        base = max(self.expires_at or timezone.now(), timezone.now())
        self.expires_at = base + relativedelta(months=1)
        self.save()


class Payment(models.Model):
    STATUS = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed',    'Failed'),
    ]
    vendor        = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='payments')
    amount        = models.DecimalField(max_digits=10, decimal_places=2)
    plan_paid_for = models.CharField(max_length=20, choices=PLAN_CHOICES)
    mpesa_ref            = models.CharField(max_length=60, blank=True)
    phone_used           = models.CharField(max_length=20, blank=True)
    checkout_request_id  = models.CharField(max_length=100, blank=True, default='',
                               help_text='Safaricom CheckoutRequestID — used to match callbacks')
    status               = models.CharField(max_length=15, choices=STATUS, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)
    confirmed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vendor.business_name} — KES {self.amount} [{self.status}]"


class TillPayment(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='till_payments')
    transaction_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=50, blank=True, default='')
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} - {self.customer_name}"
