from django.urls import path
from . import views

app_name = 'ngo_portal'

urlpatterns = [
    path('dashboard/', views.ngo_dashboard, name='dashboard'),
    path('beneficiaries/', views.beneficiary_list, name='beneficiaries'),
    path('beneficiaries/add/', views.add_beneficiary, name='add_beneficiary'),
    path('programs/add/', views.add_program, name='add_program'),
    path('activity/log/', views.log_activity, name='log_activity'),
    path('export/audit/', views.export_donor_audit, name='export_audit'),
]
