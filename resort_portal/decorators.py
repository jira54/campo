from django.core.exceptions import PermissionDenied
from functools import wraps

def resort_enterprise_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
            
        if request.user.business_type != 'resort':
            raise PermissionDenied("This portal is restricted to Enterprise Resort accounts.")
            
        return view_func(request, *args, **kwargs)
    return wrapper
