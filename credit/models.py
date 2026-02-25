from django.db import models
from django.conf import settings
from django.utils import timezone


class CreditRecord(models.Model):
    """A person who owes money — linked to customer or standalone."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
    ]

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_records'
    )

    # Either link to existing customer OR store name/phone manually
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credits'
    )
    debtor_name = models.CharField(max_length=200)  # Always filled (auto from customer if linked)
    debtor_phone = models.CharField(max_length=20, blank=True, default='')

    # Credit details
    amount_given = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True, default='', help_text='e.g. Lunch x3, Printing services')
    due_date = models.DateField(null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def amount_remaining(self):
        return self.amount_given - self.amount_paid

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'paid':
            return timezone.now().date() > self.due_date
        return False

    def update_status(self):
        if self.amount_paid >= self.amount_given:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'active'
        self.save()

    def __str__(self):
        return f"{self.debtor_name} owes KES {self.amount_remaining}"


class CreditPayment(models.Model):
    """Individual payment made toward a credit record."""

    credit = models.ForeignKey(
        CreditRecord,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True, default='')
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KES {self.amount} paid toward {self.credit.debtor_name}"
