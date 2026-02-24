from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('',        views.promotion_list,    name='promotion_list'),
    path('compose/', views.promotion_compose, name='promotion_compose'),
]
