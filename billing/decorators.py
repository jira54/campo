from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def premium_required(view_func):
    """
    Decorator that blocks free-tier vendors from accessing premium views.
    Redirects to upgrade page with a clear message.

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
        if not request.user.is_premium:
            messages.warning(
                request,
                "This feature requires a Premium plan. "
                "Upgrade to Premium for KES 400/month to unlock all features."
            )
            return redirect('billing:upgrade')
        return view_func(request, *args, **kwargs)
    return wrapper
