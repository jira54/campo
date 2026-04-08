from django.urls import path
from . import views

app_name = 'resort_portal'

urlpatterns = [
    path('dashboard/', views.resort_dashboard, name='dashboard'),
    path('setup/', views.resort_setup, name='setup'),
    path('log-charge/', views.log_charge, name='log_charge'),
]
