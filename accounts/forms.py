from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    terms_accepted = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = User
        fields = ['name', 'phone_number']
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone_number

class OTPVerificationForm(forms.Form):
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    otp_code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    def clean_otp_code(self):
        otp_code = self.cleaned_data['otp_code']
        if not otp_code.isdigit() or len(otp_code) != 6:
            raise forms.ValidationError("OTP code must be a 6-digit number.")
        return otp_code