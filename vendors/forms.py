from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Vendor, BUSINESS_TYPES

class RegisterForm(forms.ModelForm):
    password  = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    class Meta:
        model  = Vendor
        fields = ['email', 'business_name', 'business_type', 'phone_number', 'university']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        vendor = super().save(commit=False)
        vendor.username = self.cleaned_data['email']
        vendor.email    = self.cleaned_data['email']
        vendor.set_password(self.cleaned_data['password'])
        if commit:
            vendor.save()
        return vendor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-ctrl'})


class VendorProfileForm(forms.ModelForm):
    class Meta:
        model  = Vendor
        fields = ['business_name', 'business_type', 'phone_number', 'university', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-ctrl'})
