from .models import Property

def property_context(request):
    """Provides the current active property and all properties for the vendor."""
    if not request.user.is_authenticated:
        return {}
    
    # We only care about properties for resort owners (or anyone who has them)
    # But usually this is for the Resort Portal
    all_props = Property.objects.filter(vendor=request.user)
    
    current_prop_id = request.session.get('current_property_id')
    current_prop = None
    
    if current_prop_id:
        current_prop = all_props.filter(id=current_prop_id).first()
    
    if not current_prop:
        current_prop = all_props.filter(is_default=True).first() or all_props.first()
        if current_prop:
            request.session['current_property_id'] = current_prop.id
            
    return {
        'current_property': current_prop,
        'vendor_properties': all_props
    }
