from django.contrib import admin
from .models import (
    ResortGuest, Room, StayRecord, ServiceCharge, Department,
    RestaurantTable, BarSeat, EventSpace, EventBooking,
    DayPass, DayVisitor, Facility, UserActivity, HousekeepingLog, ResortSettings
)

@admin.register(ResortGuest)
class ResortGuestAdmin(admin.ModelAdmin):
    list_display = ['name', 'guest_type', 'vip_status', 'total_stays', 'phone', 'created_at']
    search_fields = ['name', 'phone', 'email', 'passport_id']
    list_filter = ['guest_type', 'vip_status', 'created_at', 'nationality']
    readonly_fields = ['total_stays', 'created_at']
    ordering = ['-created_at']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'status', 'base_rate', 'resort_property']
    search_fields = ['room_number', 'room_type']
    list_filter = ['status', 'room_type', 'resort_property']
    ordering = ['room_number']

@admin.register(StayRecord)
class StayRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest', 'room', 'check_in_date', 'check_out_date', 'status']
    search_fields = ['guest__name', 'room__room_number']
    list_filter = ['status', 'check_in_date', 'check_out_date']
    ordering = ['-check_in_date']

@admin.register(ServiceCharge)
class ServiceChargeAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'department', 'guest', 'is_paid', 'logged_at']
    search_fields = ['description', 'guest__name', 'department__name']
    list_filter = ['is_paid', 'payment_method', 'department', 'logged_at']
    readonly_fields = ['tax_amount', 'net_amount', 'logged_at']
    ordering = ['-logged_at']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'resort_property', 'vendor']
    search_fields = ['name']
    list_filter = ['resort_property']
    ordering = ['name']

@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'capacity', 'table_type', 'status', 'resort_property']
    search_fields = ['table_number', 'table_type']
    list_filter = ['status', 'table_type']
    ordering = ['table_number']

@admin.register(BarSeat)
class BarSeatAdmin(admin.ModelAdmin):
    list_display = ['seat_number', 'seat_type', 'status', 'resort_property']
    search_fields = ['seat_number', 'seat_type']
    list_filter = ['status', 'seat_type']
    ordering = ['seat_number']

@admin.register(EventSpace)
class EventSpaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'space_type', 'rate_per_day', 'resort_property']
    search_fields = ['name', 'space_type']
    list_filter = ['space_type', 'resort_property']
    ordering = ['name']

@admin.register(EventBooking)
class EventBookingAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer_name', 'space', 'start_date', 'end_date', 'status', 'total_cost']
    search_fields = ['title', 'organizer_name']
    list_filter = ['status', 'start_date', 'space']
    ordering = ['-start_date']

@admin.register(DayPass)
class DayPassAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'resort_property']
    search_fields = ['name']
    list_filter = ['is_active', 'resort_property']
    ordering = ['name']

@admin.register(DayVisitor)
class DayVisitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'pass_type', 'number_of_guests', 'status', 'check_in_time']
    search_fields = ['name', 'phone']
    list_filter = ['status', 'pass_type', 'check_in_time']
    readonly_fields = ['check_in_time']
    ordering = ['-check_in_time']

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'resort_property']
    search_fields = ['name']
    list_filter = ['status', 'resort_property']
    ordering = ['name']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'user', 'vendor', 'created_at']
    search_fields = ['title', 'description', 'user__name']
    list_filter = ['category', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(HousekeepingLog)
class HousekeepingLogAdmin(admin.ModelAdmin):
    list_display = ['room', 'old_status', 'new_status', 'staff_name', 'timestamp']
    search_fields = ['room__room_number', 'staff_name']
    list_filter = ['old_status', 'new_status', 'timestamp']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(ResortSettings)
class ResortSettingsAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'resort_property', 'currency_code', 'default_tax_rate', 'enable_vip_alerts']
    search_fields = ['vendor__business_name', 'resort_property__name']
    list_filter = ['currency_code', 'enable_vip_alerts', 'enable_email_receipts']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Financial Settings', {
            'fields': ('default_tax_rate', 'currency_code', 'currency_symbol')
        }),
        ('Department Configuration', {
            'fields': ('default_department_names',)
        }),
        ('Operational Settings', {
            'fields': ('auto_checkout_time', 'auto_checkin_time', 'housekeeping_alert_threshold')
        }),
        ('Display Settings', {
            'fields': ('dashboard_refresh_interval', 'enable_vip_alerts', 'enable_revenue_alerts')
        }),
        ('Security Settings', {
            'fields': ('pin_expiry_days', 'max_login_attempts')
        }),
        ('Email Settings', {
            'fields': ('enable_email_receipts', 'receipt_email_template')
        }),
    )
