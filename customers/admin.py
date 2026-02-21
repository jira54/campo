from django.contrib import admin
from .models import Customer, Purchase

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vendor', 'total_visits', 'added_at')
    list_filter = ('vendor', 'added_at')
    search_fields = ('name', 'phone')
    readonly_fields = ('added_at',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'service', 'purchased_at')
    list_filter = ('purchased_at', 'service')
    search_fields = ('customer__name', 'service')
    readonly_fields = ('purchased_at',)
