from django import forms
from .models import Promotion, PROMO_CHANNEL, PROMO_SEGMENT

class PromotionForm(forms.ModelForm):
    class Meta:
        model  = Promotion
        fields = ['title', 'message', 'channel', 'segment', 'individual_customer', 'scheduled_at']
        widgets = {
            'message':      forms.Textarea(attrs={'rows': 4}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        vendor = kwargs.pop('vendor', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-ctrl'})
        self.fields['scheduled_at'].required = False
        
        # Add customer choices for individual selection
        if vendor:
            self.fields['individual_customer'] = forms.ModelChoiceField(
                queryset=vendor.customers.all(),
                empty_label="Select a customer...",
                required=False,
                widget=forms.Select(attrs={'class': 'form-ctrl'})
            )
        
        # Hide individual_customer field unless segment is 'individual'
        if self.data.get('segment') != 'individual':
            self.fields['individual_customer'].widget = forms.HiddenInput()
