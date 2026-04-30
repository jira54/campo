from django.utils import timezone
from .models import AdminActivityLog


def log_admin_action(request, action_type, target_user=None, description=''):
    """
    Log admin activity for audit purposes
    """
    if request.user.is_superuser:
        AdminActivityLog.objects.create(
            admin=request.user,
            action_type=action_type,
            target_user=target_user,
            description=description,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        )


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
