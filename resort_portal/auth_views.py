"""
Views for manager authentication.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from vendors.models import Vendor
from .models import ManagerAuth
from .services import ManagerAuthService
from .decorators import manager_auth_required, pin_required


# ============ SETUP FLOW ============

@require_http_methods(["GET", "POST"])
@csrf_protect
def manager_setup(request):
    """
    Manager setup: Enter email, phone, password.
    Initiates email verification.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        confirm = request.POST.get('password_confirm', '').strip()
        
        # Basic validation
        if not all([email, phone, password, confirm]):
            messages.error(request, "All fields are required")
            return render(request, 'resort_portal/auth/setup.html')
        
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return render(request, 'resort_portal/auth/setup.html')
        
        # Get vendor from logged-in user
        if not request.user.is_authenticated or not hasattr(request.user, 'vendor'):
            messages.error(request, "Must be logged in as vendor")
            return redirect('resort_manager_login')
        
        vendor = request.user.vendor
        
        # Call service
        success, manager_auth, error = ManagerAuthService.setup_manager(
            vendor, email, phone, password
        )
        
        if not success:
            messages.error(request, error)
            return render(request, 'resort_portal/auth/setup.html')
        
        messages.success(request, f"Verification code sent to {email}")
        return redirect('resort_manager_verify')
    
    return render(request, 'resort_portal/auth/setup.html')


@require_http_methods(["GET", "POST"])
@csrf_protect
def manager_verify_email(request):
    """
    Email verification: Enter 6-digit code.
    """
    # Get manager from request or redirect
    if not request.user.is_authenticated:
        return redirect('resort_manager_login')
    
    try:
        manager_auth = request.user.vendor.manager_auth
    except:
        return redirect('resort_manager_setup')
    
    if manager_auth.is_verified:
        messages.info(request, "Email already verified")
        return redirect('resort_manager_login')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, "Verification code required")
            return render(request, 'resort_portal/auth/verify.html')
        
        success, message = ManagerAuthService.verify_email(manager_auth, code)
        
        if success:
            messages.success(request, message)
            return redirect('resort_manager_login')
        else:
            messages.error(request, message)
            return render(request, 'resort_portal/auth/verify.html')
    
    context = {
        'email': manager_auth.email
    }
    return render(request, 'resort_portal/auth/verify.html', context)


# ============ LOGIN FLOW ============

@require_http_methods(["GET", "POST"])
@csrf_protect
def manager_login(request):
    """
    Manager login: Email + password.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not all([email, password]):
            messages.error(request, "Email and password required")
            return render(request, 'resort_portal/auth/login.html')
        
        # Get manager
        try:
            manager_auth = ManagerAuth.objects.get(email=email)
        except ManagerAuth.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, 'resort_portal/auth/login.html')
        
        # Check verification
        if not manager_auth.is_verified:
            messages.warning(request, "Email not verified. Please verify first")
            return redirect('resort_manager_verify')
        
        # Authenticate password
        success, message = ManagerAuthService.authenticate_password(manager_auth, password)
        
        if not success:
            messages.error(request, message)
            return render(request, 'resort_portal/auth/login.html')
        
        # Log in the user
        login(request, manager_auth.vendor.user)
        request.session['manager_authenticated'] = True
        request.session['pin_unlocked'] = False  # Reset PIN unlock
        
        messages.success(request, "Logged in successfully")
        
        # Redirect to PIN unlock if required
        if manager_auth.has_pin():
            return redirect('resort_verify_pin')
        else:
            return redirect('resort_dashboard')
    
    return render(request, 'resort_portal/auth/login.html')


@require_http_methods(["POST"])
def manager_logout(request):
    """
    Manager logout: Clear session and cookies.
    """
    logout(request)
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('resort_manager_login')


# ============ PIN MANAGEMENT ============

@require_http_methods(["GET", "POST"])
@csrf_protect
@manager_auth_required
def manager_set_pin(request):
    """
    Set or update manager PIN.
    Requires password authentication.
    """
    manager_auth = request.manager_auth
    
    if request.method == 'POST':
        new_pin = request.POST.get('new_pin', '').strip()
        confirm_pin = request.POST.get('confirm_pin', '').strip()
        
        if not all([new_pin, confirm_pin]):
            messages.error(request, "Both PIN fields required")
            return render(request, 'resort_portal/auth/set_pin.html')
        
        # Call service
        success, message = ManagerAuthService.set_pin(manager_auth, new_pin, confirm_pin)
        
        if success:
            messages.success(request, message)
            return redirect('resort_dashboard')
        else:
            messages.error(request, message)
            return render(request, 'resort_portal/auth/set_pin.html')
    
    context = {
        'has_pin': manager_auth.has_pin()
    }
    return render(request, 'resort_portal/auth/set_pin.html', context)


@require_http_methods(["GET", "POST"])
@csrf_protect
@manager_auth_required
def manager_verify_pin(request):
    """
    Verify PIN to unlock dashboard access.
    """
    manager_auth = request.manager_auth
    
    # If no PIN is set, skip
    if not manager_auth.has_pin():
        request.session['pin_unlocked'] = True
        return redirect('resort_dashboard')
    
    if request.method == 'POST':
        pin = request.POST.get('pin', '').strip()
        
        if not pin:
            messages.error(request, "PIN required")
            return render(request, 'resort_portal/auth/verify_pin.html')
        
        # Call service
        success, message = ManagerAuthService.authenticate_pin(manager_auth, pin)
        
        if success:
            request.session['pin_unlocked'] = True
            messages.success(request, "Access granted")
            return redirect('resort_dashboard')
        else:
            messages.error(request, message)
            return render(request, 'resort_portal/auth/verify_pin.html')
    
    context = {
        'attempts_remaining': manager_auth.get_pin_attempts_remaining()
    }
    return render(request, 'resort_portal/auth/verify_pin.html', context)


# ============ DASHBOARD ============

@manager_auth_required
@pin_required
def resort_dashboard(request):
    """
    Protected dashboard: Requires authentication + PIN unlock.
    """
    manager_auth = request.manager_auth
    
    context = {
        'manager_email': manager_auth.email,
        'manager_phone': manager_auth.phone,
        'has_pin': manager_auth.has_pin(),
        'last_login': manager_auth.last_login_at,
    }
    
    return render(request, 'resort_portal/dashboard.html', context)
