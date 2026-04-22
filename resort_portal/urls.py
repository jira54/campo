from django.urls import path
from . import views
from . import auth_views

app_name = 'resort_portal'

urlpatterns = [
    # Main Modular Dashboard
    path('', views.overview, name='overview'),
    path('dashboard/', views.legacy_overview_redirect, name='dashboard'), # Legacy redirect
    
    path('setup/', views.resort_setup, name='setup'),
    path('log-charge/', views.log_charge, name='log_charge'),
    
    # Modular Sections
    path('guests/', views.guests_section, name='guests'),
    path('rooms/', views.rooms_section, name='rooms'),
    path('restaurant/', views.restaurant_section, name='restaurant'),
    path('bar/', views.bar_section, name='bar'),
    path('events/', views.events_section, name='events'),
    path('day-visitors/', views.day_visitors_section, name='day_visitors'),
    path('reports/', views.reports_section, name='reports'),
    path('settings/', views.settings_section, name='settings'),
    
    # Security
    path('security/', views.security_settings, name='security'),
    
    # NEW: Manager Authentication System
    path('manager-setup/', auth_views.manager_setup, name='resort_manager_setup'),
    path('manager-verify-email/', auth_views.manager_verify_email, name='resort_manager_verify'),
    path('manager-login/', auth_views.manager_login, name='resort_manager_login'),
    path('manager-logout/', auth_views.manager_logout, name='resort_manager_logout'),
    path('manager-set-pin/', auth_views.manager_set_pin, name='resort_manager_set_pin'),
    path('manager-verify-pin/', auth_views.manager_verify_pin, name='resort_verify_pin'),
    path('resort-dashboard/', auth_views.resort_dashboard, name='resort_dashboard'),
    
    # Legacy Manager Authentication (keep for compatibility)
    path('auth/setup/', views.manager_auth_setup, name='manager_setup'),
    path('auth/login/', views.manager_login, name='manager_login'),
    path('auth/logout/', views.manager_logout, name='manager_logout'),
    path('auth/verify/', views.manager_verify, name='manager_verify'),
    path('auth/forgot/', views.manager_forgot_password, name='manager_forgot'),
    path('auth/reset/', views.manager_reset_password, name='manager_reset'),
    
    path('settle-bill/', views.settle_bill, name='settle_bill'),

    # Existing detail/op views
    path('guests/index/', views.guest_index, name='guest_index'), # Internal link
    path('guests/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('stay/check-out/<int:stay_id>/', views.check_out_folio, name='check_out_folio'),
    path('room/mark-clean/<int:room_id>/', views.mark_room_clean, name='mark_room_clean'),
    path('room/start-cleaning/<int:room_id>/', views.start_cleaning, name='start_cleaning'),
    path('room/finish-cleaning/<int:room_id>/', views.finish_cleaning, name='finish_cleaning'),
    path('room/inspect/<int:room_id>/', views.inspect_room, name='inspect_room'),
    
    # Security
    path('verify-pin/', views.verify_manager_pin, name='verify_manager_pin'),
    path('request-reset-otp/', views.request_pin_reset_otp, name='request_reset_otp'),
    path('verify-reset-otp/', views.verify_pin_reset_otp, name='verify_reset_otp'),
    path('lock/', views.lock_manager_dashboard, name='lock_manager'),
]
