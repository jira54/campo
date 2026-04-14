from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
import os
from vendors import views as vendor_views

def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    with open(sw_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')

def offline(request):
    return render(request, 'offline.html')

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            vendor_views.root_redirect, name='root_redirect'),
    path('landing/',    vendor_views.landing,      name='landing'),
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
    path('ngo/',        include('ngo_portal.urls')),
    path('resort/',     include('resort_portal.urls')),
    path('saas-admin/', include('admin_dashboard.urls')),
    path('sw.js', service_worker, name='service_worker'),
    path('offline/', offline, name='offline'),
]

handler404 = 'vendors.views.custom_404'
handler500 = 'vendors.views.custom_500'