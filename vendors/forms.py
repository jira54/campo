from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import Vendor, BUSINESS_TYPES

class RegisterForm(forms.ModelForm):
    # 1. Enforce strict email validation
    email = forms.EmailField(
        required=True,
        error_messages={'invalid': 'Please enter a valid email address.'}
    )

    # 2. Strict Kenyan Phone Number Validation
    phone_regex = RegexValidator(
        regex=r'^(?:254|\+254|0)?([17]\d{8})$', 
        message="Please enter a valid Kenyan phone number (e.g., 0712345678 or +254712345678)."
    )
    phone_number = forms.CharField(
        validators=[phone_regex], 
        max_length=15,
        required=True
    )

    # 3. Added specific IDs for the JavaScript visibility toggle
    password  = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'password-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'password-confirm-input'}), label='Confirm password')

    class Meta:
        model  = Vendor
        fields = ['email', 'business_name', 'owner_name', 'business_type', 'phone_number', 'university']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        vendor = super().save(commit=False)
        vendor.email    = self.cleaned_data['email']
        vendor.set_password(self.cleaned_data['password'])
        if commit:
            vendor.save()
        return vendor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Inject the Navy/Gold Tailwind classes into every input
        custom_classes = 'w-full bg-deep border border-gold border-opacity-30 text-white placeholder-gray-600 px-4 py-2 rounded focus:outline-none focus:border-gold'
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': custom_classes})
            
        # Add placeholders so they display inside the Django-rendered inputs
        self.fields['email'].widget.attrs.update({'placeholder': 'your@email.com'})
        self.fields['business_name'].widget.attrs.update({'placeholder': "e.g., John's Kitchen"})
        self.fields['owner_name'].widget.attrs.update({'placeholder': 'e.g., John Doe'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': '+254712345678'})
        self.fields['university'].widget.attrs.update({'placeholder': 'e.g., Nairobi University'})
        self.fields['password'].widget.attrs.update({'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'placeholder': '••••••••'})


class VendorProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        validators=[RegexValidator(
            regex=r'^(?:254|\+254|0)?([17]\d{8})$', 
            message="Please enter a valid Kenyan phone number."
        )], 
        max_length=15
    )

    class Meta:
        model  = Vendor
        fields = ['business_name', 'business_type', 'phone_number', 'university', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply the exact same premium styling to the profile update form
        custom_classes = 'w-full bg-deep border border-gold border-opacity-30 text-white placeholder-gray-600 px-4 py-2 rounded focus:outline-none focus:border-gold'
        for field in self.fields.values():
            field.widget.attrs.update({'class': custom_classes})