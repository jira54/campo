from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('upgrade/',          views.upgrade,          name='upgrade'),
    path('pay/',              views.initiate_payment,  name='pay'),
    path('mpesa/callback/',   views.mpesa_callback,    name='mpesa_callback'),
    path('success/',          views.billing_success,   name='success'),
    path('history/',          views.payment_history,   name='history'),
    
    # C2B Till Integration
    path('mpesa/c2b/validation/', views.c2b_validation, name='c2b_validation'),
    path('mpesa/c2b/confirmation/', views.c2b_confirmation, name='c2b_confirmation'),
    path('api/poll-latest-payments/', views.poll_latest_payments, name='poll_latest_payments'),
]
