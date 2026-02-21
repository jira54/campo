from django.db import models

PROMO_STATUS = [
    ('draft',     'Draft'),
    ('scheduled', 'Scheduled'),
    ('sent',      'Sent'),
    ('failed',    'Failed'),
]

PROMO_CHANNEL = [
    ('whatsapp', 'WhatsApp'),
    ('sms',      'SMS'),
    ('both',     'Both'),
]

PROMO_SEGMENT = [
    ('all',     'All Customers'),
    ('loyal',   'Loyal Only'),
    ('regular', 'Regular'),
    ('new',     'New Customers'),
    ('atrisk',  'At-Risk'),
]

class Promotion(models.Model):
    vendor         = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='promotions')
    title          = models.CharField(max_length=120)
    message        = models.TextField()
    channel        = models.CharField(max_length=15, choices=PROMO_CHANNEL, default='whatsapp')
    segment        = models.CharField(max_length=15, choices=PROMO_SEGMENT, default='all')
    status         = models.CharField(max_length=15, choices=PROMO_STATUS, default='draft')
    scheduled_at   = models.DateTimeField(null=True, blank=True)
    sent_at        = models.DateTimeField(null=True, blank=True)
    recipients     = models.IntegerField(default=0)
    response_count = models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.status}]"

    @property
    def response_rate(self):
        if not self.recipients:
            return 0
        return round(self.response_count / self.recipients * 100)
