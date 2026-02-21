from django.contrib import admin
from .models import Subscription, Payment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'plan', 'expires_at', 'started_at')
    list_filter = ('plan', 'started_at')
    search_fields = ('vendor__business_name',)
    readonly_fields = ('started_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'amount', 'plan_paid_for', 'status', 'created_at')
    list_filter = ('status', 'plan_paid_for', 'created_at')
    search_fields = ('vendor__business_name', 'mpesa_ref')
    readonly_fields = ('created_at', 'mpesa_ref')
