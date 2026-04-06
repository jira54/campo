from django.urls import path
from . import views

app_name = 'ngo_portal'

urlpatterns = [
    path('dashboard/', views.ngo_dashboard, name='dashboard'),
    path('beneficiaries/', views.beneficiary_list, name='beneficiaries'),
    path('export/audit/', views.export_donor_audit, name='export_audit'),
]
