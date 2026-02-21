from django.urls import path
from . import views

urlpatterns = [
    path('',        views.promotion_list,    name='promotion_list'),
    path('compose/', views.promotion_compose, name='promotion_compose'),
]
