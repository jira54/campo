from django.db import models
from django.utils import timezone
import secrets

class Program(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='ngo_programs')
    name = models.CharField(max_length=255)
    donor = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    target_beneficiaries_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"


class Beneficiary(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Prefer not to say')
    ]
    
    VULNERABILITY_CHOICES = [
        ('none', 'None specified'),
        ('pwd', 'Person with Disability'),
        ('idp', 'Internally Displaced Person'),
        ('orphan', 'Orphaned/Vulnerable Child'),
        ('fhh', 'Female-Headed Household')
    ]

    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='ngo_beneficiaries')
    
    # Global Standard: Anonymized ID to prevent double counting
    unique_system_id = models.CharField(max_length=20, unique=True, blank=True, db_index=True)
    
    # Secure Personal Data
    name = models.CharField(max_length=255, help_text="Restricted to field workers. Excluded from aggregated donor exports.")
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True, help_text="For newsletters and program updates")
    
    # Demographics
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    date_of_birth = models.DateField(null=True, blank=True, help_text="Used to auto-calculate <18 vs 18+ brackets.")
    
    # Geography
    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    
    vulnerability_marker = models.CharField(max_length=20, choices=VULNERABILITY_CHOICES, default='none')
    
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Beneficiaries'

    def save(self, *args, **kwargs):
        if not self.unique_system_id:
            # Generate a short, unique hex ID (e.g., BEN-a1b2c3d4)
            self.unique_system_id = f"BEN-{secrets.token_hex(4)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.unique_system_id})"


class Intervention(models.Model):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='interventions')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='interventions')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='ngo_interventions')
    
    activity_type = models.CharField(max_length=255, help_text="e.g. Health Screening, Business Training")
    date_executed = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_type} - {self.beneficiary.unique_system_id}"


class Outcome(models.Model):
    INTERVENTION_STATUS_CHOICES = [
        ('significant_improvement', 'Significant Improvement'),
        ('stable', 'Stable / Progressing'),
        ('at_risk', 'At Risk / No Change'),
        ('declined', 'Declined / Regression'),
    ]

    intervention = models.OneToOneField(Intervention, on_delete=models.CASCADE, related_name='outcome')
    beneficiary  = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='outcomes')
    vendor       = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='ngo_outcomes')
    
    status       = models.CharField(max_length=50, choices=INTERVENTION_STATUS_CHOICES, default='stable')
    is_goal_met  = models.BooleanField(default=False, help_text="Did this intervention achieve the intended program outcome?")
    narrative    = models.TextField(blank=True, help_text="Detailed explanation of the change observed in the beneficiary.")
    
    verified_at  = models.DateField(default=timezone.now)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Outcome: {self.intervention.activity_type} ({self.get_status_display()})"
