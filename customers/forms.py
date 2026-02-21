from django import forms
from .models import Customer, Purchase

class CustomerForm(forms.ModelForm):
    class Meta:
        model  = Customer
        fields = ['name', 'phone', 'notes']

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
