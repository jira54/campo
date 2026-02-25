from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView
from vendors import views as vendor_views

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            vendor_views.landing,      name='landing'),
    path('login/',      vendor_views.login_view,    name='login'),
    path('logout/',     vendor_views.logout_view,   name='logout'),
    path('register/',   vendor_views.register_view, name='register'),
    path('password-reset/', vendor_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='vendors/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', vendor_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(template_name='vendors/password_reset_complete.html'), name='password_reset_complete'),
    path('dashboard/',  include('vendors.urls')),
    path('customers/',  include('customers.urls')),
    path('promotions/', include('promotions.urls')),
    path('analytics/',  include('analytics.urls')),
    path('billing/',    include('billing.urls')),
    path('notes/',      include('notes.urls')),
    path('credit/',     include('credit.urls')),
]