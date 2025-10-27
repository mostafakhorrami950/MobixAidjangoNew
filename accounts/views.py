from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.apps import apps
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
        return redirect("chat")

    # Get active AI models with articles that should be shown on login/register pages
    AIModel = apps.get_model("ai_models", "AIModel")
    ai_models = (
        AIModel.objects.filter(is_active=True)
        .select_related("article")
        .filter(article__is_published=True, article__show_login_register=True)[:6]
    )  # Limit to 6 models

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                phone_number=form.cleaned_data["phone_number"],
                name=form.cleaned_data["name"],
                username=form.cleaned_data["phone_number"],  # Using phone as username
            )

            # Assign default subscription to the new user (redundancy check)
            try:
                # Get the free subscription type (Free)
                SubscriptionType = apps.get_model("subscriptions", "SubscriptionType")
                UserSubscription = apps.get_model("subscriptions", "UserSubscription")
                default_subscription = SubscriptionType.objects.get(name="Free")

                # Check if user already has a subscription (shouldn't happen but just in case)
                if not hasattr(user, "subscription"):
                    # Create user subscription
                    UserSubscription.objects.create(
                        user=user,
                        subscription_type=default_subscription,
                        is_active=True,
                        start_date=timezone.now(),
                    )
            except apps.get_model("subscriptions", "SubscriptionType").DoesNotExist:
                # If Free subscription doesn't exist, try Basic as fallback
                try:
                    SubscriptionType = apps.get_model(
                        "subscriptions", "SubscriptionType"
                    )
                    UserSubscription = apps.get_model(
                        "subscriptions", "UserSubscription"
                    )
                    default_subscription = SubscriptionType.objects.get(name="Basic")

                    # Check if user already has a subscription (shouldn't happen but just in case)
                    if not hasattr(user, "subscription"):
                        # Create user subscription
                        UserSubscription.objects.create(
                            user=user,
                            subscription_type=default_subscription,
                            is_active=True,
                            start_date=timezone.now(),
                        )
                except apps.get_model("subscriptions", "SubscriptionType").DoesNotExist:
                    # If neither Free nor Basic subscription exists, log this error
                    logger.error(
                        "Neither Free nor Basic subscription type found in database"
                    )
                    pass

            # Send OTP
            success, message, remaining = OTPService.create_and_send_otp(user)
            if success:
                messages.success(
                    request,
                    "ثبت نام با موفقیت انجام شد. کد تأیید به شماره تلفن شما ارسال شد.",
                )
                # Redirect to OTP verification page
                request.session["phone_number"] = user.phone_number
                request.session["registration_user_id"] = user.id
                return redirect("verify_otp")
            else:
                if remaining > 0:
                    messages.error(
                        request,
                        f"لطفاً {remaining} ثانیه صبر کنید تا بتوانید SMS دیگری دریافت کنید.",
                    )
                else:
                    messages.error(request, f"خطا در ارسال کد تأیید: {message}")
                user.delete()  # Delete user if OTP sending failed
    else:
        form = RegistrationForm()

    return render(
        request, "accounts/register.html", {"form": form, "ai_models": ai_models}
    )


def verify_otp(request):
    """
    Verify OTP code for user authentication
    Handles CSRF token validation and OTP verification
    """
    # Log the request for debugging
    logger.info(
        f"verify_otp called - Method: {request.method}, User authenticated: {request.user.is_authenticated}"
    )

    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        logger.info(
            f"User {request.user.phone_number} already authenticated, redirecting to chat"
        )
        return redirect("chat")

    # Check session data
    phone_number = request.session.get("phone_number")
    if not phone_number:
        logger.warning("verify_otp: No phone_number in session")
        messages.error(
            request,
            "جلسه شما منقضی شده است. لطفاً مجدداً از صفحه ورود یا ثبت نام اقدام کنید.",
        )
        # Redirect to login if they're trying to login or register if new user
        if "registration_user_id" in request.session:
            return redirect("register")
        return redirect("login")

    logger.info(f"verify_otp: Processing for phone number: {phone_number}")

    if request.method == "POST":
        # Log CSRF token presence
        csrf_token = request.POST.get("csrfmiddlewaretoken")
        if csrf_token:
            logger.info("CSRF token present in POST request")
        else:
            logger.error("CSRF token missing in POST request")
            messages.error(
                request,
                "خطای امنیتی: توکن CSRF یافت نشد. لطفاً صفحه را رفرش کنید و دوباره تلاش کنید.",
            )
            form = OTPVerificationForm(initial={"phone_number": phone_number})
            return render(request, "accounts/verify_otp.html", {"form": form})
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            form_phone_number = form.cleaned_data["phone_number"]
            otp_code = form.cleaned_data["otp_code"]

            # Verify the phone number matches the session
            if form_phone_number != phone_number:
                logger.warning(
                    f"Phone number mismatch - Form: {form_phone_number}, Session: {phone_number}"
                )
                messages.error(
                    request,
                    "شماره تلفن وارد شده با شماره درخواستی مطابقت ندارد. لطفاً مجدداً تلاش کنید.",
                )
                return render(request, "accounts/verify_otp.html", {"form": form})

            try:
                User = apps.get_model("accounts", "User")
                user = User.objects.get(phone_number=phone_number)
                logger.info(f"Verifying OTP for user: {phone_number}")
                is_valid, message = OTPService.verify_otp(user, otp_code)

                if is_valid:
                    # Mark user as verified
                    user.is_verified = True
                    user.save()

                    # Force authentication without password
                    user.backend = "django.contrib.auth.backends.ModelBackend"
                    login(request, user)

                    # Clear session data
                    if "phone_number" in request.session:
                        del request.session["phone_number"]
                    if "registration_user_id" in request.session:
                        del request.session["registration_user_id"]

                    messages.success(
                        request, "شماره تلفن با موفقیت تأیید شد! خوش آمدید."
                    )
                    logger.info(
                        f"User {user.phone_number} successfully verified and logged in"
                    )

                    # Check if user came from registration or login
                    if "registration_user_id" in request.session:
                        # New user - redirect to chat
                        return redirect("chat")
                    else:
                        # Existing user logging in - redirect to chat
                        return redirect("chat")
                else:
                    if "expired" in message.lower() or "منقضی" in message:
                        messages.error(
                            request,
                            "کد تأیید منقضی شده است. لطفاً کد جدید درخواست کنید.",
                        )
                    elif "not found" in message.lower() or "یافت نشد" in message:
                        messages.error(
                            request, "کد تأیید وجود ندارد. لطفاً مجدداً تلاش کنید."
                        )
                    else:
                        messages.error(
                            request, "کد تأیید اشتباه است. لطفاً دوباره بررسی کنید."
                        )
                    logger.warning(f"Invalid OTP for user {phone_number}: {message}")
            except apps.get_model("accounts", "User").DoesNotExist:
                messages.error(
                    request, "خطای سیستمی: کاربر یافت نشد. لطفاً مجدداً ثبت نام کنید."
                )
                logger.error(f"User not found for phone number: {phone_number}")
                return redirect("register")
            except Exception as e:
                logger.error(f"Unexpected error in verify_otp: {str(e)}", exc_info=True)
                messages.error(
                    request,
                    "خطای سیستمی رخ داد. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
                )
                form = OTPVerificationForm(initial={"phone_number": phone_number})
                return render(request, "accounts/verify_otp.html", {"form": form})
        else:
            # Form validation errors - display the actual error messages from forms.py
            logger.warning(f"Form validation errors: {form.errors}")
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, str(error))
    else:
        # GET request
        logger.info(f"verify_otp GET request for phone: {phone_number}")
        form = OTPVerificationForm(initial={"phone_number": phone_number})

    # Add CSRF token to context explicitly
    context = {
        "form": form,
    }
    return render(request, "accounts/verify_otp.html", context)


def login_view(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect("chat")

    # Get active AI models with articles that should be shown on login/register pages
    AIModel = apps.get_model("ai_models", "AIModel")
    ai_models = (
        AIModel.objects.filter(is_active=True)
        .select_related("article")
        .filter(article__is_published=True, article__show_login_register=True)[:6]
    )  # Limit to 6 models

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")

        # Validate phone number format
        if not phone_number:
            messages.error(request, "لطفاً شمارع تلفن را وارد کنید.")
            return render(request, "accounts/login.html", {"ai_models": ai_models})

        phone_number = phone_number.strip()

        # Basic validation
        if (
            not phone_number.isdigit()
            or len(phone_number) != 11
            or not phone_number.startswith("09")
        ):
            messages.error(request, "شماره تلفن باید ۱۱ رقم باشد و با ۰۹ شروع شود.")
            return render(request, "accounts/login.html", {"ai_models": ai_models})

        try:
            User = apps.get_model("accounts", "User")
            user = User.objects.get(phone_number=phone_number)

            # Send OTP
            success, message, remaining = OTPService.create_and_send_otp(user)
            if success:
                messages.success(request, "کد تأیید به شماره تلفن شما ارسال شد.")
                request.session["phone_number"] = phone_number
                request.session["last_otp_sent"] = timezone.now().timestamp()
                return redirect("verify_otp")
            else:
                if remaining > 0:
                    messages.error(
                        request,
                        f"لطفاً {remaining} ثانیه صبر کنید تا بتوانید کد تأیید جدیدی درخواست کنید.",
                    )
                else:
                    messages.error(request, f"خطا در ارسال کد تأیید: {message}")
        except apps.get_model("accounts", "User").DoesNotExist:
            messages.error(
                request,
                "هیچ حساب کاربری با این شماره تلفن یافت نشد. ابتدا ثبت نام کنید.",
            )

    return render(request, "accounts/login.html", {"ai_models": ai_models})


def logout_view(request):
    logout(request)
    messages.success(request, "با موفقیت از سیستم خارج شدید.")
    return redirect("login")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")
