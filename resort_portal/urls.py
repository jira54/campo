from django.urls import path
from . import views

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
