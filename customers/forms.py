from django import forms
from .models import Customer, Purchase

class CustomerForm(forms.ModelForm):
    class Meta:
        model  = Customer
        fields = ['name', 'phone', 'notes', 'tags']
        widgets = {
            'name':  forms.TextInput(attrs={
                'class': 'w-full bg-navy border border-gold border-opacity-20 text-white rounded px-4 py-3',
                'placeholder': 'Customer name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-navy border border-gold border-opacity-20 text-white rounded px-4 py-3',
                'placeholder': '0712345678'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full bg-navy border border-gold border-opacity-20 text-white rounded px-4 py-3',
                'placeholder': 'e.g. Prefers chapati, comes mornings...',
                'rows': 3
            }),
            'tags':  forms.TextInput(attrs={
                'class': 'w-full bg-navy border border-gold border-opacity-20 text-white rounded px-4 py-3',
                'placeholder': 'e.g. regular breakfast, bulk printer'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-ctrl'})


class PurchaseForm(forms.ModelForm):
    class Meta:
        model  = Purchase
        fields = ['service', 'amount', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-ctrl'})
