from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Business Info', {'fields': ('business_name', 'business_type', 'phone', 'university')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'business_name', 'business_type', 'phone', 'password1', 'password2'),
        }),
    )
    list_display = ('business_name', 'email', 'business_type', 'phone', 'is_active')
    search_fields = ('business_name', 'email', 'phone')
    list_filter = ('business_type', 'is_active', 'created_at')
    ordering = ('business_name',)
