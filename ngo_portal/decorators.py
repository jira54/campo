from django.core.exceptions import PermissionDenied
from functools import wraps

def ngo_enterprise_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Must be authenticated, must be 'ngo', and must be a premium tier (or in this prototype we can just block strictly on industry).
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs) # letting @login_required handle redirection
            
        if not request.user.is_superuser and request.user.business_type != 'ngo':
            raise PermissionDenied("This portal is restricted to Enterprise NGO accounts.")
            
        return view_func(request, *args, **kwargs)
    return wrapper
