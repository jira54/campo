from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def premium_required(view_func):
    """
    Decorator that blocks free-tier vendors from accessing premium views.
    Redirects to upgrade page with a clear message based on the feature being accessed.

    Usage:
        @login_required
        @premium_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        # 0. DIRECT ADMIN BYPASS (Ensures superusers are never blocked)
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
            
        if not request.user.is_premium:
            # Get user's current plan
            current_plan = getattr(request.user, 'plan', 'free')
            
            # Determine required plan based on the view/module being accessed
            view_name = view_func.__name__
            required_plan = get_required_plan_for_view(view_name)
            
            if required_plan == 'premium_retail':
                messages.warning(
                    request,
                    "This feature requires Retail Pro plan. "
                    "Upgrade to Retail Pro for KES 700/month to unlock unlimited capacity, reward programs, and smart payment mapping."
                )
            elif required_plan == 'enterprise_resort' or required_plan == 'enterprise_ngo':
                messages.warning(
                    request,
                    "This feature requires Enterprise plan. "
                    "Upgrade to Enterprise for KES 3,500/month to unlock NGO/Impact Portal, Resort/Hospitality Portal, and Multi-Tenant Sync Control."
                )
            else:
                messages.warning(
                    request,
                    "This feature requires a higher plan. "
                    "Upgrade your plan to unlock more features."
                )
            
            return redirect('billing:upgrade')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_required_plan_for_view(view_name):
    """
    Determine the required plan based on the view name or module.
    This can be extended to check URL patterns or module names.
    """
    # Check if view contains resort-related keywords
    if 'resort' in view_name.lower() or 'ngo' in view_name.lower():
        return 'enterprise_resort'
    
    # Check if view contains retail-related keywords  
    elif 'retail' in view_name.lower() or 'vendor' in view_name.lower():
        return 'premium_retail'
    
    # Default to premium_retail for unknown views
    return 'premium_retail'
