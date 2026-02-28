from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('',                    views.promotion_list,    name='promotion_list'),
    path('compose/',           views.promotion_compose, name='promotion_compose'),
    path('<int:promo_id>/',    views.promotion_detail,  name='promotion_detail'),
    path('<int:promo_id>/mark-sent/', views.mark_whatsapp_sent, name='mark_whatsapp_sent'),
    path('<int:promo_id>/delete/', views.delete_promotion, name='delete_promotion'),
]
