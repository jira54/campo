from django.urls import path
from . import views

app_name = 'resort_portal'

urlpatterns = [
    path('dashboard/', views.resort_dashboard, name='dashboard'),
    path('setup/', views.resort_setup, name='setup'),
    path('log-charge/', views.log_charge, name='log_charge'),
    
    # Guest CRM Hub
    path('guests/', views.guest_index, name='guest_index'),
    path('guests/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    
    # Operations
    path('folio/check-out/<int:folio_id>/', views.check_out_folio, name='check_out_folio'),
    path('room/mark-clean/<int:room_id>/', views.mark_room_clean, name='mark_room_clean'),
    path('room/start-cleaning/<int:room_id>/', views.start_cleaning, name='start_cleaning'),
    path('room/finish-cleaning/<int:room_id>/', views.finish_cleaning, name='finish_cleaning'),
    path('room/inspect/<int:room_id>/', views.inspect_room, name='inspect_room'),
]
