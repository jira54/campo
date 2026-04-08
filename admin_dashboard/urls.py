from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('core/', views.saas_overview, name='saas_overview'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:vendor_id>/update/', views.update_vendor_status, name='update_vendor_status'),
    path('revenue/', views.revenue_tracking, name='revenue_tracking'),
]
