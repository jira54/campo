from django import template

register = template.Library()

@register.filter
def select_status(queryset, status):
    """Filters a queryset by status (e.g. rooms|select_status:'vacant_clean')"""
    if not queryset:
        return []
    try:
        return queryset.filter(status=status)
    except:
        # Fallback for lists
        return [item for item in queryset if getattr(item, 'status', None) == status]

@register.filter
def divide(value, arg):
    """Divides the value by the arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplies the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
