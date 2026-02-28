from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('',                 views.customer_list,       name='customer_list'),
    path('add/',             views.customer_add,        name='customer_add'),
    path('<int:pk>/',        views.customer_detail,     name='customer_detail'),
    path('<int:pk>/delete/', views.customer_delete,     name='customer_delete'),
    path('<int:pk>/toggle-active/', views.customer_toggle_active, name='customer_toggle_active'),

    # Export (Premium)
    path('export/csv/',      views.customer_export_csv, name='customer_export_csv'),
    path('export/pdf/',      views.customer_export_pdf, name='customer_export_pdf'),

    # Loyalty (Premium)
    path('loyalty/',         views.loyalty_dashboard,   name='loyalty_dashboard'),
    path('loyalty/create/',  views.loyalty_create,     name='loyalty_create'),
    path('loyalty/stamp/<int:card_id>/', views.loyalty_stamp, name='loyalty_stamp'),

    # Smart Reminders (Premium)
    path('reminders/',       views.smart_reminders,     name='smart_reminders'),
    path('reminders/send/<int:customer_id>/',    views.send_reminder,    name='send_reminder'),
    path('reminders/dismiss/<int:customer_id>/', views.dismiss_reminder, name='dismiss_reminder'),

    # Receipts (Premium)
    path('receipt/send/<int:purchase_id>/', views.send_receipt, name='send_receipt'),
    path('receipt/view/<int:purchase_id>/', views.view_receipt, name='view_receipt'),
    path('receipt/download/<int:purchase_id>/', views.download_receipt_pdf, name='download_receipt_pdf'),

    # Services Management
    path('services/',         views.services_list,        name='services_list'),
    path('services/add/',     views.service_add,          name='service_add'),
    path('services/edit/<int:service_id>/', views.service_edit, name='service_edit'),
    path('services/delete/<int:service_id>/', views.service_delete, name='service_delete'),
    path('services/toggle-popular/<int:service_id>/', views.service_toggle_popular, name='service_toggle_popular'),
    path('services/reorder/',  views.services_reorder,     name='services_reorder'),
]