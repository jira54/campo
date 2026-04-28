from django.shortcuts import redirect
from django.contrib import messages


class AdminAccessMiddleware:
    """
    Middleware to restrict admin dashboard access to superusers only.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for admin routes
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to access the admin dashboard.')
                return redirect('/vendors/login/?next=' + request.path)
            
            if not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access the admin dashboard.')
                return redirect('/')
        
        response = self.get_response(request)
        return response
