from django.contrib import admin
from django.urls import path, include
from vendors import views as vendor_views

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            vendor_views.landing,      name='landing'),
    path('login/',      vendor_views.login_view,    name='login'),
    path('logout/',     vendor_views.logout_view,   name='logout'),
    path('register/',   vendor_views.register_view, name='register'),
    path('dashboard/',  include('vendors.urls')),
    path('customers/',  include('customers.urls')),
    path('promotions/', include('promotions.urls')),
    path('analytics/',  include('analytics.urls')),
    path('billing/',    include('billing.urls')),
]