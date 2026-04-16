from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
import time

def rate_limit(key_prefix, limit=5, period=60):
    """
    Simple rate limiting decorator using Django cache.
    Default: 5 attempts per 60 seconds.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Use IP address as the key suffix
            ip = request.META.get('REMOTE_ADDR')
            key = f"ratelimit:{key_prefix}:{ip}"
            
            requests = cache.get(key, [])
            now = time.time()
            
            # Filter requests within the period
            requests = [req for req in requests if now - req < period]
            
            if len(requests) >= limit:
                return HttpResponseForbidden("Too many requests. Please try again later.")
            
            requests.append(now)
            cache.set(key, requests, period)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
