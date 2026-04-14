from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('',         views.dashboard,    name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('quick-sale/', views.quick_sale, name='quick_sale'),
    path('password-reset/complete/', views.CustomPasswordResetConfirmView.as_view(template_name='vendors/password_reset_complete.html'), name='password_reset_complete'),
    path('switch-portal/<str:portal_type>/', views.switch_portal, name='switch_portal'),
]