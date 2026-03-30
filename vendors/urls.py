from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('',         views.dashboard,    name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('quick-sale/', views.quick_sale, name='quick_sale'),
]