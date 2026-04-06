from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('core/', views.saas_overview, name='saas_overview'),
]
