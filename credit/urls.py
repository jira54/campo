from django.urls import path
from . import views

app_name = 'credit'

urlpatterns = [
    path('', views.credit_list, name='credit_list'),
    path('add/', views.credit_add, name='credit_add'),
    path('<int:pk>/', views.credit_detail, name='credit_detail'),
    path('<int:pk>/reminder/', views.credit_send_reminder, name='credit_send_reminder'),
    path('<int:pk>/delete/', views.credit_delete, name='credit_delete'),
]
