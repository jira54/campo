from django.urls import path
from . import views

app_name = 'platform_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/change-plan/', views.change_plan, name='change_plan'),
    path('users/<int:user_id>/extend-trial/', views.extend_trial, name='extend_trial'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/manual/', views.manual_payment, name='manual_payment'),
    path('payments/<int:payment_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('payments/<int:payment_id>/reject/', views.reject_payment, name='reject_payment'),
]
