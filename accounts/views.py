from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from .forms import RegistrationForm, OTPVerificationForm
from .models import User
from otp_service.services import OTPService
from otp_service.models import OTP

def register(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                phone_number=form.cleaned_data['phone_number'],
                name=form.cleaned_data['name'],
                username=form.cleaned_data['phone_number']  # Using phone as username
            )
            
            # Send OTP
            success, message, remaining = OTPService.create_and_send_otp(user)
            if success:
                messages.success(request, 'Registration successful. Please check your phone for the OTP code.')
                # Redirect to OTP verification page
                request.session['phone_number'] = user.phone_number
                return redirect('verify_otp')
            else:
                if remaining > 0:
                    messages.error(request, f'لطفاً {remaining} ثانیه صبر کنید تا بتوانید SMS دیگری دریافت کنید.')
                else:
                    messages.error(request, f'خطا در ارسال کد تأیید: {message}')
                user.delete()  # Delete user if OTP sending failed
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    phone_number = request.session.get('phone_number')
    if not phone_number:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            otp_code = form.cleaned_data['otp_code']
            
            try:
                user = User.objects.get(phone_number=phone_number)
                is_valid, message = OTPService.verify_otp(user, otp_code)
                
                if is_valid:
                    user.is_verified = True
                    user.save()
                    login(request, user)
                    messages.success(request, 'Phone number verified successfully!')
                    del request.session['phone_number']  # Clear session
                    return redirect('chat')  # Redirect to chat page
                else:
                    messages.error(request, message)
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = OTPVerificationForm(initial={'phone_number': phone_number})
    
    return render(request, 'accounts/verify_otp.html', {'form': form})

def login_view(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        try:
            user = User.objects.get(phone_number=phone_number)
            
            # Send OTP
            success, message, remaining = OTPService.create_and_send_otp(user)
            if success:
                messages.success(request, 'کد تأیید به شماره تلفن شما ارسال شد.')
                request.session['phone_number'] = phone_number
                request.session['last_otp_sent'] = timezone.now().timestamp()
                return redirect('verify_otp')
            else:
                if remaining > 0:
                    messages.error(request, f'لطفاً {remaining} ثانیه صبر کنید تا بتوانید کد تأیید جدیدی درخواست کنید.')
                else:
                    messages.error(request, f'خطا در ارسال کد تأیید: {message}')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this phone number.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')