from django.db import models
from django.contrib.auth import get_user_model

Vendor = get_user_model()


class AdminActivityLog(models.Model):
    """Track admin actions for audit purposes"""
    ACTION_TYPES = [
        ('plan_change', 'Plan Changed'),
        ('trial_extend', 'Trial Extended'),
        ('payment_confirm', 'Payment Confirmed'),
        ('payment_reject', 'Payment Rejected'),
        ('payment_manual', 'Manual Payment Added'),
        ('user_login', 'Admin Login'),
        ('user_logout', 'Admin Logout'),
        ('user_export', 'User Data Exported'),
        ('payment_export', 'Payment Data Exported'),
    ]
    
    admin = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_user = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_target')
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Activity Log'
        verbose_name_plural = 'Admin Activity Logs'
    
    def __str__(self):
        return f"{self.admin.email} - {self.get_action_type_display()} - {self.created_at}"
