from django.urls import path
from . import views

app_name = 'resort_portal'

urlpatterns = [
    path('dashboard/', views.resort_dashboard, name='dashboard'),
]
