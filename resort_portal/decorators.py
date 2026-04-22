from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def resort_enterprise_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
            
        if not request.user.is_superuser and request.user.business_type != 'resort':
            raise PermissionDenied("This portal is restricted to Enterprise Resort accounts.")
            
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_auth_required(view_func):
    """
    Verify manager is authenticated.
    Redirects to login if not authenticated or not verified.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in first")
            return redirect('resort_manager_login')
        
        # Check if vendor has manager_auth
        if not hasattr(request.user, 'vendor'):
            messages.error(request, "User is not associated with a vendor")
            return redirect('resort_manager_login')
        
        try:
            manager_auth = request.user.vendor.manager_auth
        except:
            messages.warning(request, "Please complete manager setup")
            return redirect('resort_manager_setup')
        
        # Check if verified
        if not manager_auth.is_verified:
            messages.warning(request, "Please verify your email first")
            return redirect('resort_manager_verify')
        
        # Attach to request for easy access
        request.manager_auth = manager_auth
        return view_func(request, *args, **kwargs)
    
    return wrapper


def pin_required(view_func):
    """
    Verify PIN is unlocked for this session.
    Redirects to PIN entry if not unlocked.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Must be authenticated first
        if not hasattr(request, 'manager_auth'):
            return redirect('resort_manager_login')
        
        # Check if PIN is required
        if not request.manager_auth.has_pin():
            # PIN not set, allow access
            return view_func(request, *args, **kwargs)
        
        # Check if PIN is unlocked in session
        if not request.session.get('pin_unlocked', False):
            messages.info(request, "Please verify your PIN")
            return redirect('resort_verify_pin')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
