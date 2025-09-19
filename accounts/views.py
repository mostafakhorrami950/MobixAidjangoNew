from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.backends import ModelBackend
from .forms import RegistrationForm, OTPVerificationForm
from .models import User
from otp_service.services import OTPService
from otp_service.models import OTP
import logging

# Set up logging
logger = logging.getLogger(__name__)

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
                messages.success(request, 'ثبت نام با موفقیت انجام شد. کد تأیید به شماره تلفن شما ارسال شد.')
                # Redirect to OTP verification page
                request.session['phone_number'] = user.phone_number
                request.session['registration_user_id'] = user.id
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
        return redirect('chat')
        
    phone_number = request.session.get('phone_number')
    if not phone_number:
        messages.error(request, 'جلسه منقضی شده است. لطفاً مجدداً ثبت نام کنید.')
        return redirect('register')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            form_phone_number = form.cleaned_data['phone_number']
            otp_code = form.cleaned_data['otp_code']
            
            # Verify the phone number matches the session
            if form_phone_number != phone_number:
                messages.error(request, 'شماره تلفن وارد شده با جلسه فعلی مطابقت ندارد.')
                return render(request, 'accounts/verify_otp.html', {'form': form})
            
            try:
                user = User.objects.get(phone_number=phone_number)
                is_valid, message = OTPService.verify_otp(user, otp_code)
                
                if is_valid:
                    # Mark user as verified
                    user.is_verified = True
                    user.save()
                    
                    # Force authentication without password
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    
                    # Clear session data
                    if 'phone_number' in request.session:
                        del request.session['phone_number']
                    if 'registration_user_id' in request.session:
                        del request.session['registration_user_id']
                    
                    messages.success(request, 'شماره تلفن با موفقیت تأیید شد! خوش آمدید.')
                    logger.info(f'User {user.phone_number} successfully verified and logged in')
                    
                    return redirect('chat')  # Redirect to chat page
                else:
                    messages.error(request, 'کد تأیید نامعتبر یا منقضی شده است.')
                    logger.warning(f'Invalid OTP for user {phone_number}: {message}')
            except User.DoesNotExist:
                messages.error(request, 'کاربری با این شماره تلفن یافت نشد.')
                logger.error(f'User not found for phone number: {phone_number}')
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'otp_code':
                        messages.error(request, 'کد تأیید باید ۶ رقم باشد.')
                    elif field == 'phone_number':
                        messages.error(request, 'شماره تلفن معتبر نیست.')
                    else:
                        messages.error(request, error)
    else:
        form = OTPVerificationForm(initial={'phone_number': phone_number})
    
    return render(request, 'accounts/verify_otp.html', {'form': form})

def login_view(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('chat')
        
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, 'لطفاً شماره تلفن را وارد کنید.')
            return render(request, 'accounts/login.html')
        
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
            messages.error(request, 'هیچ حسابی با این شماره تلفن یافت نشد. لطفاً ابتدا ثبت نام کنید.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'با موفقیت از سیستم خارج شدید.')
    return redirect('login')
