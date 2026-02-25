from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView
from django.http import HttpResponse
import traceback
from vendors import views as vendor_views

def test_db(request):
    try:
        from vendors.models import Vendor
        count = Vendor.objects.count()
        return HttpResponse(f"DB works. Vendor count: {count}")
    except Exception as e:
        import traceback
        return HttpResponse(f"<pre>ERROR:\n{traceback.format_exc()}</pre>")

def debug_login(request):
    try:
        from vendors.views import login_view
        return login_view(request)
    except Exception as e:
        return HttpResponse(f"<pre>{traceback.format_exc()}</pre>", status=200)

def debug_register(request):
    try:
        from vendors.views import register_view
        return register_view(request)
    except Exception as e:
        return HttpResponse(f"<pre>{traceback.format_exc()}</pre>", status=200)

def version_check(request):
    return HttpResponse(f"Deployed version: aaad9dd - Login redirect should be 'vendors:dashboard' - UPDATED: 2f995d7 - LATEST: 2334757")

urlpatterns = [
    path('version/', version_check),
    path('test/', test_db),
    path('admin/',      admin.site.urls),
    path('',            vendor_views.root_redirect, name='root_redirect'),
    path('landing/',    vendor_views.landing,      name='landing'),
    path('debug-login/', debug_login),
    path('login/',      vendor_views.login_view,    name='login'),
    path('logout/',     vendor_views.logout_view,   name='logout'),
    path('register/',   vendor_views.register_view, name='register'),
    path('debug-register/', debug_register),
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