from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('',         views.dashboard,    name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('quick-sale/', views.quick_sale, name='quick_sale'),
    path('password-reset/complete/', views.CustomPasswordResetConfirmView.as_view(template_name='vendors/password_reset_complete.html'), name='password_reset_complete'),
    path('switch-portal/<str:portal_type>/', views.switch_portal, name='switch_portal'),
    path('switch-property/<int:property_id>/', views.switch_property, name='switch_property'),
    path('onboarding/dismiss/', views.dismiss_onboarding, name='dismiss_onboarding'),
    path('security/2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('security/2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('security/2fa/challenge/', views.two_factor_challenge, name='two_factor_challenge'),
    path('security/2fa/disable/', views.disable_2fa, name='disable_2fa'),
    path('business-note/save/', views.save_business_note, name='save_business_note'),
    path('quick-note/save/', views.save_quick_note, name='save_quick_note'),
    path('contact/', views.contact_form, name='contact_form'),
]