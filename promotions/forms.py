from django import forms
from .models import Promotion, PROMO_CHANNEL, PROMO_SEGMENT

class PromotionForm(forms.ModelForm):
    class Meta:
        model  = Promotion
        fields = ['title', 'message', 'channel', 'segment', 'scheduled_at']
        widgets = {
            'message':      forms.Textarea(attrs={'rows': 4}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-ctrl'})
        self.fields['scheduled_at'].required = False
