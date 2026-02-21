from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('upgrade/',          views.upgrade,          name='upgrade'),
    path('pay/',              views.initiate_payment,  name='pay'),
    path('mpesa/callback/',   views.mpesa_callback,    name='mpesa_callback'),
    path('success/',          views.billing_success,   name='success'),
    path('history/',          views.payment_history,   name='history'),
]
