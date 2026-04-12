from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta


BUSINESS_TYPES = [
    ('food',     'Food Vendor'),
    ('printing', 'Printing / Cyber'),
    ('thrift',   'Thrift / Clothing'),
    ('rental',   'Rental Services'),
    ('cakes',    'Cakes & Confectionery'),
    ('ngo',      'NGO / Non-Profit (Pro)'),
    ('resort',   'Resort / Hospitality (Pro)'),
    ('other',    'Other')
]

PERSONA_TYPES = [
    ('msme', 'Enterprise Builder (MSME)'),
    ('ngo', 'Impact Maker (NGO)'),
    ('resort', 'Luxury Concierge (Resort)'),
]


class VendorManager(BaseUserManager):
    def create_user(self, email, business_name, owner_name, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('Vendors must have an email address')
        email = self.normalize_email(email)
        vendor = self.model(
            email=email,
            business_name=business_name,
            owner_name=owner_name,
            phone_number=phone_number,
            **extra_fields
        )
        vendor.set_password(password)
        vendor.save(using=self._db)
        return vendor

    def create_superuser(self, email, business_name, owner_name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, business_name, owner_name, phone_number, password, **extra_fields)


class Vendor(AbstractBaseUser, PermissionsMixin):
    business_name     = models.CharField(max_length=255)
    business_type    = models.CharField(max_length=30, choices=BUSINESS_TYPES, default='general')
    owner_name        = models.CharField(max_length=255)
    phone_number      = models.CharField(max_length=50)
    phone             = models.CharField(max_length=20, default='')
    business_type_custom = models.CharField(max_length=120, blank=True, default='')
    
    # --- Branding & Persona ---
    logo_url          = models.URLField(max_length=500, blank=True, default='', help_text="Direct link to your business logo")
    brand_accent_color = models.CharField(max_length=7, default='#F59E0B', help_text="Hex color for your dashboard accents")
    persona_type      = models.CharField(max_length=20, choices=PERSONA_TYPES, default='msme')
    physical_address  = models.TextField(blank=True, default='', help_text="Business physical location for tax/invoice compliance")
    
    mpesa_till_number = models.CharField(max_length=20, blank=True, default='', help_text="Used for C2B live payment tracking")
    email             = models.EmailField(unique=True)
    is_active         = models.BooleanField(default=True)
    is_staff          = models.BooleanField(default=False)
    trial_end_date    = models.DateTimeField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    objects = VendorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['business_name', 'owner_name', 'phone_number']

    def __str__(self):
        return self.business_name

    # --- Plan helpers (reads from related Subscription) ---
    @property
    def plan(self):
        sub = getattr(self, 'subscription', None)
        if sub and sub.is_active():
            return sub.plan
        return 'free'

    @property
    def is_premium(self):
        # Check if user has active trial
        if self.trial_end_date and self.trial_end_date > timezone.now():
            return True
        return self.plan in ('premium', 'bundle')

    @property
    def customer_limit(self):
        """Free tier: max 20 customers. Premium: unlimited."""
        return None if self.is_premium else 20

    def get_business_type_display(self):
        """Get the display name for business type"""
        return dict(BUSINESS_TYPES).get(self.business_type, 'General')


class Customer(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50)
    visit_count = models.IntegerField(default=1)
    last_visit = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Sale(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vendor}: {self.amount} on {self.date}"


class LoyaltyReward(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reward_name = models.CharField(max_length=255)
    required_visits = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reward_name} ({self.required_visits})"


class LoginStreak(models.Model):
    vendor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak'
    )
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    def update(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        if self.last_login_date == today:
            return  # Already updated today

        if self.last_login_date == yesterday:
            self.current_streak += 1
        else:
            self.current_streak = 1  # Reset streak

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_login_date = today
        self.save()

    def __str__(self):
        return f"{self.vendor.business_name} — {self.current_streak} day streak"
