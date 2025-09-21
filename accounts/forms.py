from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09123456789'}),
        label='شماره تلفن همراه',
        error_messages={
            'required': 'شماره تلفن ضروری است.',
            'max_length': 'شماره تلفن نباید بیش از ۱۵ کاراکتر باشد.'
        }
    )
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام و نام خانوادگی'}),
        label='نام کامل',
        error_messages={
            'required': 'نام ضروری است.',
            'max_length': 'نام نباید بیش از ۱۰۰ کاراکتر باشد.'
        }
    )
    terms_accepted = forms.BooleanField(
        required=True, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='قوانین و مقررات را میپذیرم',
        error_messages={
            'required': 'پذیرفتن قوانین و مقررات ضروری است.'
        }
    )
    
    class Meta:
        model = User
        fields = ['name', 'phone_number']
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        
        # Remove any whitespace
        phone_number = phone_number.strip()
        
        # Basic phone number validation
        if not phone_number:
            raise forms.ValidationError('شماره تلفن وارد نشده است.')
            
        if not phone_number.isdigit():
            raise forms.ValidationError('شماره تلفن تنها باید شامل عدد باشد.')
            
        if len(phone_number) != 11:
            raise forms.ValidationError('شماره تلفن باید دقیقاً ۱۱ رقم باشد.')
            
        if not phone_number.startswith('09'):
            raise forms.ValidationError('شماره تلفن باید با ۰۹ شروع شود.')
        
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('این شماره تلفن قبلاً ثبت شده است. لطفاً وارد شوید.')
        return phone_number

class OTPVerificationForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label='شماره تلفن همراه',
        error_messages={
            'required': 'شماره تلفن ضروری است.'
        }
    )
    otp_code = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'کد ۶ رقمی',
            'maxlength': '6',
            'pattern': '[0-9]{6}'
        }),
        label='کد تأیید (۶ رقمی)',
        error_messages={
            'required': 'کد تأیید ضروری است.',
            'max_length': 'کد تأیید باید ۶ رقم باشد.'
        }
    )
    
    def clean_otp_code(self):
        otp_code = self.cleaned_data['otp_code']
        
        # Remove any whitespace
        otp_code = otp_code.strip()
        
        if not otp_code:
            raise forms.ValidationError('کد تأیید وارد نشده است.')
            
        if not otp_code.isdigit():
            raise forms.ValidationError('کد تأیید تنها باید شامل عدد باشد.')
            
        if len(otp_code) != 6:
            raise forms.ValidationError('کد تأیید باید دقیقاً ۶ رقم باشد.')
            
        return otp_code
