from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView
from django.http import HttpResponse
from vendors import views as vendor_views

def debug_test(request):
    try:
        from django.conf import settings
        from django.db import connection
        tables = connection.introspection.table_names()
        return HttpResponse(
            f"DEBUG={settings.DEBUG}\n"
            f"TABLES={sorted(tables)}\n"
            f"HOSTS={settings.ALLOWED_HOSTS}",
            content_type='text/plain'
        )
    except Exception as e:
        return HttpResponse(f"ERROR: {e}", content_type='text/plain')

def test_dashboard_error(request):
    try:
        from django.conf import settings
        from django.db import connection
        # Force an error to test the wrapper
        raise Exception("Test error for debugging")
        return HttpResponse("Should not reach here")
    except Exception as e:
        import traceback
        return HttpResponse(f"<pre>TEST DASHBOARD ERROR:\n{traceback.format_exc()}</pre>", status=500)

def test_dashboard_no_auth(request):
    try:
        from vendors.views import dashboard
        return dashboard(request)
    except Exception as e:
        import traceback
        return HttpResponse(f"<pre>DASHBOARD NO AUTH ERROR:\n{traceback.format_exc()}</pre>", status=500)

urlpatterns = [
    path('debug-check/', debug_test),
    path('test-dashboard-error/', test_dashboard_error),
    path('test-dashboard-no-auth/', test_dashboard_no_auth),
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
]