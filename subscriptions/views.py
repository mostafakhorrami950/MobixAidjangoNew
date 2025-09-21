from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.apps import apps
from decimal import Decimal
from .services import UsageService
from .usage_stats import UserUsageStatsService
from accounts.models import User
from zarinpal import ZarinPal
import json
import logging

logger = logging.getLogger(__name__)

# Custom ZarinPal class with sandbox support
class CustomZarinPal(ZarinPal):
    def __init__(self, merchant_id: str, sandbox: bool = False) -> None:
        super().__init__(merchant_id)
        self.sandbox = sandbox
        if sandbox:
            self.base_url = "https://sandbox.zarinpal.com/pg/v4/payment"
        else:
            self.base_url = "https://api.zarinpal.com/pg/v4/payment"

    def request(self, data):
        import requests
        from pydantic import validate_call
        from zarinpal.errors import ERROR_DICT
        from zarinpal.models import RequestResponse
        
        result = requests.post(
            f"{self.base_url}/request.json",
            json={"merchant_id": self.merchant_id, **data.model_dump(exclude_none=True)}
        ).json()
        if result["data"] and int(result["data"]["code"]) == 100:
            return RequestResponse(**result)
        else:
            raise ERROR_DICT.get(
                int(result["errors"]["code"]),
                Exception(f'Code: {result["errors"]["code"]}, Message: {result["errors"]["message"]}')
            )

    def verify(self, data):
        import requests
        from pydantic import validate_call
        from zarinpal.errors import ERROR_DICT
        from zarinpal.models import VerifyResponse
        
        result = requests.post(
            f"{self.base_url}/verify.json",
            json={"merchant_id": self.merchant_id, **data.model_dump(exclude_none=True)}
        ).json()
        if result["data"] and int(result["data"]["code"]) == 100:
            return VerifyResponse(**result)
        else:
            raise ERROR_DICT.get(
                int(result["errors"]["code"]),
                Exception(f'Code: {result["errors"]["code"]}, Message: {result["errors"]["message"]}')
            )

    @staticmethod
    def get_payment_link(authority: str, sandbox: bool = False) -> str:
        if sandbox:
            return f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
        else:
            return f"https://www.zarinpal.com/pg/StartPay/{authority}"

@login_required
def purchase_subscription(request):
    """Display available subscriptions for purchase"""
    # Exclude free subscriptions from the purchase page
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    subscriptions = SubscriptionType.objects.filter(is_active=True).exclude(price=0)
    
    # Get comprehensive usage statistics for the user
    usage_stats = UserUsageStatsService.get_user_usage_statistics(request.user)
    usage_summary = UserUsageStatsService.get_usage_summary_for_dashboard(request.user)
    usage_cards = UserUsageStatsService.get_usage_cards_data(request.user)
    
    context = {
        'subscriptions': subscriptions,
        'usage_stats': usage_stats,
        'usage_summary': usage_summary,
        'usage_cards': usage_cards,
    }
    return render(request, 'subscriptions/purchase.html', context)

@login_required
def apply_discount_code(request):
    """Apply a discount code to a subscription"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = request.POST
        code = data.get('code')
        subscription_id = data.get('subscription_id')
        
        # Validate inputs
        if not code or not subscription_id:
            return JsonResponse({'error': 'Code and subscription ID are required'}, status=400)
        
        # Get the discount code
        DiscountCode = apps.get_model('subscriptions', 'DiscountCode')
        discount_code = get_object_or_404(DiscountCode, code=code)
        
        # Get the subscription
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        subscription = get_object_or_404(SubscriptionType, id=subscription_id, is_active=True)
        
        # Check if discount code is valid for this subscription
        if discount_code.subscription_types.exists() and not discount_code.subscription_types.filter(id=subscription_id).exists():
            return JsonResponse({'error': 'This discount code is not valid for the selected subscription'}, status=400)
        
        # Check if discount code is valid for the user
        if not discount_code.is_valid_for_user(request.user):
            if not discount_code.is_active:
                return JsonResponse({'error': 'This discount code is not active'}, status=400)
            elif discount_code.is_expired:
                return JsonResponse({'error': 'This discount code has expired'}, status=400)
            elif discount_code.max_uses and discount_code.uses_count >= discount_code.max_uses:
                return JsonResponse({'error': 'This discount code has reached its maximum usage limit'}, status=400)
            else:
                return JsonResponse({'error': 'You have reached the maximum usage limit for this discount code'}, status=400)
        
        # Calculate discount - ensure we're working with the same types
        original_price = Decimal(str(subscription.price))
        
        # First calculate the remaining value from current subscription, ensuring consistency with display logic
        user = request.user
        user_subscription = user.get_subscription_type()
        amount_after_remaining_value = original_price

        if user_subscription:
            # Combine tokens from both ChatSessionUsage and UserUsage
            total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
            
            UserUsage = apps.get_model('subscriptions', 'UserUsage')
            user_usage_records = UserUsage.objects.filter(user=user, subscription_type=user_subscription)
            
            total_user_usage_tokens = 0
            for record in user_usage_records:
                total_user_usage_tokens += record.tokens_count
                
            combined_total_tokens_used = total_tokens_used + total_user_usage_tokens

            # Use the subscription's max_tokens field
            total_token_limit = user_subscription.max_tokens
            
            # If no token limit is set, use a default calculation
            if total_token_limit == 0:
                total_token_limit = 1000000  # Default 1 million tokens
            
            # Calculate remaining tokens
            remaining_tokens = max(0, total_token_limit - combined_total_tokens_used)
            
            # Calculate remaining days
            try:
                UserSubscription = apps.get_model('subscriptions', 'UserSubscription')
                user_subscription_record = UserSubscription.objects.get(user=user, subscription_type=user_subscription)
                if user_subscription_record.end_date:
                    remaining_days = (user_subscription_record.end_date - timezone.now()).days
                    if remaining_days < 0:
                        remaining_days = 0
                else:
                    remaining_days = user_subscription.duration_days
            except apps.get_model('subscriptions', 'UserSubscription').DoesNotExist:
                remaining_days = user_subscription.duration_days
            
            # New calculation formula
            total_days = user_subscription.duration_days
            total_tokens = total_token_limit
            
            if total_days > 0 and total_tokens > 0:
                value_per_unit = user_subscription.price / (Decimal(total_days) * Decimal(total_tokens))
                total_remaining_value_tomans = Decimal(remaining_days) * Decimal(remaining_tokens) * value_per_unit
            else:
                total_remaining_value_tomans = Decimal('0')
            
            # Calculate the amount after deducting remaining value
            amount_after_remaining_value = max(Decimal('0'), original_price - total_remaining_value_tomans)
        
        # Now apply discount to the amount after remaining value calculation
        discount_amount = discount_code.calculate_discount(amount_after_remaining_value)
        final_price = amount_after_remaining_value - discount_amount
        
        return JsonResponse({
            'success': True,
            'original_price': float(original_price),
            'discount_amount': float(discount_amount),
            'final_price': float(final_price),
            'discount_code': discount_code.code
        })
        
    except apps.get_model('subscriptions', 'DiscountCode').DoesNotExist:
        return JsonResponse({'error': 'Invalid discount code'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def initiate_payment(request, subscription_id):
    """Initiate payment for a subscription"""
    if request.method != 'POST':
        return redirect('purchase_subscription')
    
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    subscription = get_object_or_404(SubscriptionType, id=subscription_id, is_active=True)
    
    discount_code = None
    original_price = Decimal(str(subscription.price))
    final_price = original_price

    # Check for intelligent upgrade first
    intelligent_upgrade_data = request.session.get('intelligent_upgrade')
    if intelligent_upgrade_data and intelligent_upgrade_data.get('new_subscription_id') == subscription.id:
        final_price = Decimal(str(intelligent_upgrade_data.get('amount_to_pay_tomans', subscription.price)))
        if 'intelligent_upgrade' in request.session:
            del request.session['intelligent_upgrade']
    else:
        # Regular payment flow with remaining value and discount calculation
        amount_after_remaining_value = original_price
        user = request.user
        user_subscription = user.get_subscription_type()

        if user_subscription:
            # Consistent remaining value calculation
            total_tokens_used, _ = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
            
            UserUsage = apps.get_model('subscriptions', 'UserUsage')
            user_usage_records = UserUsage.objects.filter(user=user, subscription_type=user_subscription)
            
            total_user_usage_tokens = sum(record.tokens_count for record in user_usage_records)
            combined_total_tokens_used = total_tokens_used + total_user_usage_tokens

            total_token_limit = user_subscription.max_tokens or 1000000
            remaining_tokens = max(0, total_token_limit - combined_total_tokens_used)
            
            try:
                user_subscription_record = apps.get_model('subscriptions', 'UserSubscription').objects.get(user=user, subscription_type=user_subscription)
                remaining_days = max(0, (user_subscription_record.end_date - timezone.now()).days) if user_subscription_record.end_date else user_subscription.duration_days
            except apps.get_model('subscriptions', 'UserSubscription').DoesNotExist:
                remaining_days = user_subscription.duration_days

            total_days = user_subscription.duration_days
            if total_days > 0 and total_token_limit > 0:
                value_per_unit = user_subscription.price / (Decimal(total_days) * Decimal(total_token_limit))
                total_remaining_value_tomans = Decimal(remaining_days) * Decimal(remaining_tokens) * value_per_unit
            else:
                total_remaining_value_tomans = Decimal('0')
            
            amount_after_remaining_value = max(Decimal('0'), original_price - total_remaining_value_tomans)

        # Apply discount code if it exists
        discount_code_input = request.POST.get('discount_code')
        if discount_code_input:
            try:
                DiscountCode = apps.get_model('subscriptions', 'DiscountCode')
                discount_code = DiscountCode.objects.get(code=discount_code_input)
                if not discount_code.is_valid_for_user(request.user):
                    messages.error(request, 'کد تخفیف معتبر نیست.')
                    return redirect('purchase_subscription')
                
                discount_amount = discount_code.calculate_discount(amount_after_remaining_value)
                final_price = amount_after_remaining_value - discount_amount
            except apps.get_model('subscriptions', 'DiscountCode').DoesNotExist:
                messages.error(request, 'کد تخفیف نامعتبر است.')
                return redirect('purchase_subscription')
        else:
            final_price = amount_after_remaining_value

    # Handle 100% discount or zero payment case
    if final_price <= 0:
        # Handle 100% discount - directly activate subscription without payment
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=subscription.duration_days)
        
        # Create or update user subscription
        UserSubscription = apps.get_model('subscriptions', 'UserSubscription')
        user_subscription_obj, created = UserSubscription.objects.update_or_create(
            user=request.user,
            defaults={
                'subscription_type': subscription,
                'is_active': True,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        # Reset usage counters for the user when subscription is activated using the new method
        # This method doesn't delete data, just resets counters as requested
        UsageService.reset_user_usage(request.user, subscription)
        
        # ALSO reset chat session usage to ensure tokens are properly reset after payment
        UsageService.reset_chat_session_usage(request.user, subscription)
        
        # Record discount use only if there's actually a discount code
        if discount_code:
            DiscountUse = apps.get_model('subscriptions', 'DiscountUse')
            DiscountUse.objects.create(
                discount_code=discount_code,
                user=request.user,
                subscription_type=subscription,
                original_price=original_price,
                discount_amount=original_price,  # Full discount
                final_price=Decimal('0')
            )
        
        # Record financial transaction for 100% discount
        FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
        FinancialTransaction.objects.create(
            user=request.user,
            subscription_type=subscription,
            transaction_type='subscription_purchase',
            status='completed',
            amount=Decimal('0'),
            original_amount=original_price,
            discount_amount=discount_code.discount_value if discount_code else Decimal('0'),
            discount_code=discount_code,
            authority='DISCOUNT-' + discount_code.code if discount_code else 'FREE_ACTIVATION',  # Unique authority for discount transactions
            reference_id='DISCOUNT-' + discount_code.code if discount_code else 'FREE_ACTIVATION'
        )
        
        # Clear any existing payment session data
        keys_to_delete = ['payment_authority', 'subscription_id', 'payment_amount', 
                        'original_price', 'final_price', 'discount_code_id']
        for key in keys_to_delete:
            if key in request.session:
                del request.session[key]
        
        # Redirect to success page
        messages.success(request, 'اشتراک شما با موفقیت فعال شد!')
        return redirect('purchase_subscription')


    # Proceed to payment gateway
    try:
        zarinpal_client = CustomZarinPal(
            merchant_id=settings.ZARINPAL_MERCHANT_ID,
            sandbox=getattr(settings, 'ZARINPAL_SANDBOX', False)
        )
        
        amount_in_rials = int(final_price * 10)
        
        # Validate amount is within acceptable limits (1000 Rials minimum, 500,000,000 Rials maximum)
        if amount_in_rials < 1000:
            messages.error(request, 'مبلغ پرداختی کمتر از حد مجاز است. حداقل مبلغ 100 تومان می‌باشد.')
            return redirect('purchase_subscription')
        
        if amount_in_rials > 500000000:
            messages.error(request, 'مبلغ پرداختی بیشتر از حد مجاز است. حداکثر مبلغ 50,000,000 تومان می‌باشد.')
            return redirect('purchase_subscription')

        from zarinpal import RequestInput
        
        # Create dynamic callback URL based on current request
        callback_url = request.build_absolute_uri(reverse('payment_callback'))
        payment_data = RequestInput(
            amount=amount_in_rials,
            description=f"خرید اشتراک {subscription.name}",
            callback_url=callback_url
        )
        
        payment_response = zarinpal_client.request(payment_data)
        
        if payment_response and hasattr(payment_response, 'data') and hasattr(payment_response.data, 'authority'):
            authority = payment_response.data.authority
            
            # Save payment info in session
            request.session['payment_authority'] = authority
            request.session['subscription_id'] = subscription.id
            request.session['payment_amount'] = amount_in_rials
            request.session['original_price'] = float(original_price)
            request.session['final_price'] = float(final_price)
            if discount_code:
                request.session['discount_code_id'] = discount_code.id

            # Record pending financial transaction
            FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
            discount_amount = original_price - final_price
            FinancialTransaction.objects.create(
                user=request.user,
                subscription_type=subscription,
                transaction_type='subscription_purchase',
                status='pending',
                amount=final_price,
                original_amount=original_price,
                discount_amount=discount_amount,
                discount_code=discount_code,
                authority=authority
            )

            payment_url = zarinpal_client.get_payment_link(authority, sandbox=getattr(settings, 'ZARINPAL_SANDBOX', False))
            return redirect(payment_url)
        else:
            error_message = str(payment_response) if payment_response else 'پاسخ نامعتبر از سرویس پرداخت'
            messages.error(request, f'خطا در ایجاد پرداخت: {error_message}')
            return redirect('purchase_subscription')
            
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        # Provide more detailed error message based on common ZarinPal issues
        error_message = str(e)
        if "merchant_id" in error_message.lower():
            messages.error(request, 'خطا در ایجاد پرداخت: مرچنت کد داخل تنظیمات وارد نشده است.')
        elif "callbackurl" in error_message.lower():
            messages.error(request, 'خطا در ایجاد پرداخت: آدرس بازگشت (callbackurl) وارد نشده است.')
        elif "description" in error_message.lower():
            messages.error(request, 'خطا در ایجاد پرداخت: توضیحات (description) وارد نشده است.')
        elif "500" in error_message:
            messages.error(request, 'خطا در ایجاد پرداخت: توضیحات از حد مجاز 500 کاراکتر بیشتر است.')
        elif "amount" in error_message.lower():
            messages.error(request, 'خطا در ایجاد پرداخت: مبلغ پرداختی کمتر یا بیشتر از حد مجاز است.')
        else:
            messages.error(request, f'خطا در ایجاد پرداخت: {error_message}')
        return redirect('purchase_subscription')

def payment_callback(request):
    """Handle payment callback from ZarinPal"""
    # Initialize ZarinPal SDK with sandbox support
    try:
        zarinpal_client = CustomZarinPal(
            merchant_id=settings.ZARINPAL_MERCHANT_ID,
            sandbox=getattr(settings, 'ZARINPAL_SANDBOX', False)
        )
    except Exception as e:
        logger.error(f"Error initializing ZarinPal in callback: {str(e)}")
        return render(request, 'subscriptions/payment_callback.html', {
            'payment_success': False,
            'error_message': 'خطا در اتصال به درگاه پرداخت'
        })
    
    # Get payment info from session
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    
    # Verify payment if successful
    if status == 'OK' and authority:
        try:
            # Get payment details from session
            session_authority = request.session.get('payment_authority')
            subscription_id = request.session.get('subscription_id')
            payment_amount = request.session.get('payment_amount')  # This is in Rials
            
            if authority == session_authority and subscription_id and payment_amount:
                from zarinpal import VerifyInput
                
                # Verify payment with ZarinPal (amount should be in Rials)
                verification_data = VerifyInput(
                    authority=authority,
                    amount=payment_amount  # This is already in Rials
                )
                
                # Use the correct method to verify payment
                verification_response = zarinpal_client.verify(verification_data)
                
                if verification_response and verification_response.data and verification_response.data.code == 100:
                    # Payment successful, activate subscription
                    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
                    subscription = get_object_or_404(SubscriptionType, id=subscription_id)
                    
                    # Calculate end date based on subscription duration from TODAY
                    start_date = timezone.now()
                    end_date = start_date + timezone.timedelta(days=subscription.duration_days)
                    
                    # Create or update user subscription using update_or_create to prevent IntegrityError
                    UserSubscription = apps.get_model('subscriptions', 'UserSubscription')
                    user_subscription, created = UserSubscription.objects.update_or_create(
                        user=request.user,
                        defaults={
                            'subscription_type': subscription,
                            'is_active': True,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                    )
                    
                    # Reset usage counters for the user when subscription is activated using the new method
                    # This method doesn't delete data, just resets counters as requested
                    UsageService.reset_user_usage(request.user, subscription)
                    
                    # ALSO reset chat session usage to ensure tokens are properly reset after payment
                    UsageService.reset_chat_session_usage(request.user, subscription)

                    # Record discount use if applicable
                    discount_code_id = request.session.get('discount_code_id')
                    discount_code_obj = None
                    if discount_code_id:
                        try:
                            DiscountCode = apps.get_model('subscriptions', 'DiscountCode')
                            discount_code_obj = DiscountCode.objects.get(id=discount_code_id)
                            original_price = request.session.get('original_price', 0)  # This is in Tomans
                            final_price = request.session.get('final_price', 0)  # This is in Tomans
                            discount_amount = original_price - final_price
                            
                            # Record the discount use
                            DiscountUse = apps.get_model('subscriptions', 'DiscountUse')
                            DiscountUse.objects.create(
                                discount_code=discount_code_obj,
                                user=request.user,
                                subscription_type=subscription,
                                original_price=original_price,
                                discount_amount=discount_amount,
                                final_price=final_price
                            )
                        except apps.get_model('subscriptions', 'DiscountCode').DoesNotExist:
                            pass  # Ignore if discount code was deleted
                    
                    # Update financial transaction status to completed
                    FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
                    try:
                        financial_transaction = FinancialTransaction.objects.get(authority=authority)
                        financial_transaction.status = 'completed'
                        financial_transaction.reference_id = authority  # Using authority as reference ID
                        financial_transaction.save()
                    except FinancialTransaction.DoesNotExist:
                        # Create transaction if it doesn't exist (fallback)
                        original_price = request.session.get('original_price', 0)
                        final_price = request.session.get('final_price', 0)
                        discount_amount = original_price - final_price if original_price and final_price else 0
                        
                        FinancialTransaction.objects.create(
                            user=request.user,
                            subscription_type=subscription,
                            transaction_type='subscription_purchase',
                            status='completed',
                            amount=Decimal(str(final_price)) if final_price else 0,
                            original_amount=Decimal(str(original_price)) if original_price else 0,
                            discount_amount=Decimal(str(discount_amount)) if discount_amount else 0,
                            discount_code=discount_code_obj,
                            authority=authority,
                            reference_id=authority
                        )
                    
                    # Clear payment session data
                    keys_to_delete = ['payment_authority', 'subscription_id', 'payment_amount', 
                                    'original_price', 'final_price', 'discount_code_id']
                    for key in keys_to_delete:
                        if key in request.session:
                            del request.session[key]
                    
                    return render(request, 'subscriptions/payment_callback.html', {
                        'payment_success': True,
                        'authority': authority
                    })
                else:
                    if verification_response and verification_response.errors:
                        error_message = ', '.join(verification_response.errors)
                    elif verification_response and verification_response.data:
                        error_message = f'کد خطا: {verification_response.data.code} - {verification_response.data.message}'
                    else:
                        error_message = 'پاسخ نامعتبر از سرور تأیید'
                    
                    # Update financial transaction status to failed
                    FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
                    try:
                        financial_transaction = FinancialTransaction.objects.get(authority=authority)
                        financial_transaction.status = 'failed'
                        financial_transaction.save()
                    except FinancialTransaction.DoesNotExist:
                        pass  # Ignore if transaction doesn't exist
                    
                    return render(request, 'subscriptions/payment_callback.html', {
                        'payment_success': False,
                        'error_message': error_message
                    })
            else:
                # Update financial transaction status to failed
                FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
                try:
                    financial_transaction = FinancialTransaction.objects.get(authority=authority)
                    financial_transaction.status = 'failed'
                    financial_transaction.save()
                except FinancialTransaction.DoesNotExist:
                    pass  # Ignore if transaction doesn't exist
                
                return render(request, 'subscriptions/payment_callback.html', {
                    'payment_success': False,
                    'error_message': 'اطلاعات پرداخت نامعتبر است'
                })
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            
            # Update financial transaction status to failed
            FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
            try:
                financial_transaction = FinancialTransaction.objects.get(authority=authority)
                financial_transaction.status = 'failed'
                financial_transaction.save()
            except FinancialTransaction.DoesNotExist:
                pass  # Ignore if transaction doesn't exist
            
            return render(request, 'subscriptions/payment_callback.html', {
                'payment_success': False,
                'error_message': f'خطا در تأیید پرداخت: {str(e)}'
            })
    else:
        # Update financial transaction status to failed (payment cancelled)
        FinancialTransaction = apps.get_model('subscriptions', 'FinancialTransaction')
        try:
            financial_transaction = FinancialTransaction.objects.get(authority=authority)
            financial_transaction.status = 'failed'
            financial_transaction.save()
        except FinancialTransaction.DoesNotExist:
            pass  # Ignore if transaction doesn't exist
        
        return render(request, 'subscriptions/payment_callback.html', {
            'payment_success': False,
            'error_message': 'پرداخت توسط کاربر لغو شد'
        })

        
@login_required
def calculate_remaining_subscription_value(request):
    """
    Calculate the remaining value of a user's subscription based on token usage
    and redirect to payment page with the remaining amount
    Implements professional subscription logic with proper monthly reset
    """
    try:
        user = request.user
        user_subscription = user.get_subscription_type()
        
        if not user_subscription:
            return JsonResponse({'error': 'No active subscription found'}, status=400)
        
        # Calculate total tokens used using the new ChatSessionUsage method
        total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
        
        # Also get tokens from UserUsage for backward compatibility
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        user_usage_records = UserUsage.objects.filter(user=user, subscription_type=user_subscription)
        
        total_user_usage_tokens = 0
        total_user_usage_free_tokens = 0
        for record in user_usage_records:
            total_user_usage_tokens += record.tokens_count
            total_user_usage_free_tokens += record.free_model_tokens_count
        
        # Combine tokens from both sources
        combined_total_tokens_used = total_tokens_used + total_user_usage_tokens
        combined_free_model_tokens_used = free_model_tokens_used + total_user_usage_free_tokens
        
        # Use the subscription's max_tokens field for total limit
        total_token_limit = user_subscription.max_tokens
        
        # If no token limit is set, use a default calculation
        if total_token_limit == 0:
            total_token_limit = 1000000  # Default 1 million tokens
        
        # Calculate remaining tokens (total)
        remaining_tokens = max(0, total_token_limit - combined_total_tokens_used)
        
        # Calculate remaining days
        UserSubscriptionModel = apps.get_model('subscriptions', 'UserSubscription')
        try:
            user_subscription_record = UserSubscriptionModel.objects.get(user=user, subscription_type=user_subscription)
            if user_subscription_record.end_date:
                remaining_days = (user_subscription_record.end_date - timezone.now()).days
                if remaining_days < 0:
                    remaining_days = 0
            else:
                remaining_days = user_subscription.duration_days  # Assume full duration if no end date
        except apps.get_model('subscriptions', 'UserSubscription').DoesNotExist:
            # If no subscription record exists, use the subscription's default duration
            remaining_days = user_subscription.duration_days
        
        # New calculation formula:
        # Value per unit = Total Price / (Days * Tokens)
        # Remaining Value = Remaining Days * Remaining Tokens * Value per unit
        
        # Calculate value per unit (in Tomans)
        total_days = user_subscription.duration_days
        total_tokens = total_token_limit
        
        if total_days > 0 and total_tokens > 0:
            value_per_unit = user_subscription.price / (Decimal(total_days) * Decimal(total_tokens))
            total_remaining_value_tomans = Decimal(remaining_days) * Decimal(remaining_tokens) * value_per_unit
        else:
            total_remaining_value_tomans = Decimal('0')
        
        # Get the subscription price in Tomans
        subscription_price_tomans = user_subscription.price
        
        # Calculate the amount to pay (subscription price minus remaining value)
        amount_to_pay = max(Decimal('0'), subscription_price_tomans - total_remaining_value_tomans)
        
        # Return the calculation details (all values in Tomans)
        response_data = {
            'subscription_name': user_subscription.name,
            'subscription_price_tomans': float(subscription_price_tomans),
            'total_tokens_used': combined_total_tokens_used,
            'free_model_tokens_used': combined_free_model_tokens_used,  # Added separate free model token count
            'total_token_limit': total_token_limit,
            'remaining_tokens': remaining_tokens,
            'remaining_days': remaining_days,
            'total_remaining_value_tomans': float(total_remaining_value_tomans),
            'amount_to_pay_tomans': float(amount_to_pay),
            'user_has_remaining_value': total_remaining_value_tomans > 0
        }
        
        return JsonResponse(response_data)
        
    except apps.get_model('subscriptions', 'UserSubscription').DoesNotExist:
        return JsonResponse({'error': 'No active subscription found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error calculating remaining subscription value: {str(e)}'}, status=500)


@login_required
def intelligent_subscription_upgrade(request, new_subscription_id):
    """
    Handle intelligent subscription upgrade with remaining value calculation
    """
    user = request.user
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    new_subscription = get_object_or_404(SubscriptionType, id=new_subscription_id, is_active=True)
    
    # Get current subscription
    current_subscription = user.get_subscription_type()
    
    if not current_subscription:
        messages.error(request, 'شما اشتراک فعالی ندارید.')
        return redirect('purchase_subscription')
    
    # Calculate remaining value from current subscription using the new method
    try:
        # Calculate total tokens used using the new ChatSessionUsage method
        total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, current_subscription)
        
        # Also get tokens from UserUsage for backward compatibility
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        user_usage_records = UserUsage.objects.filter(user=user, subscription_type=current_subscription)
        
        total_user_usage_tokens = 0
        total_user_usage_free_tokens = 0
        for record in user_usage_records:
            total_user_usage_tokens += record.tokens_count
            total_user_usage_free_tokens += record.free_model_tokens_count
        
        # Combine tokens from both sources
        combined_total_tokens_used = total_tokens_used + total_user_usage_tokens
        combined_free_model_tokens_used = free_model_tokens_used + total_user_usage_free_tokens
        
        # Use the subscription's max_tokens field
        total_token_limit = current_subscription.max_tokens
        
        # If no token limit is set, use a default calculation
        if total_token_limit == 0:
            total_token_limit = 1000000  # Default 1 million tokens
        
        # Calculate remaining tokens
        remaining_tokens = max(0, total_token_limit - combined_total_tokens_used)
        
        # Calculate remaining days
        UserSubscription = apps.get_model('subscriptions', 'UserSubscription')
        user_subscription_record = UserSubscription.objects.get(user=user, subscription_type=current_subscription)
        if user_subscription_record.end_date:
            remaining_days = (user_subscription_record.end_date - timezone.now()).days
            if remaining_days < 0:
                remaining_days = 0
        else:
            remaining_days = current_subscription.duration_days  # Assume full duration if no end date
        
        # Calculate value per unit (in Tomans)
        total_days = current_subscription.duration_days
        total_tokens = total_token_limit
        
        if total_days > 0 and total_tokens > 0:
            value_per_unit = current_subscription.price / (Decimal(total_days) * Decimal(total_tokens))
            total_remaining_value_tomans = Decimal(remaining_days) * Decimal(remaining_tokens) * value_per_unit
        else:
            total_remaining_value_tomans = Decimal('0')
        
        # Calculate the amount to pay for new subscription
        new_subscription_price = new_subscription.price
        amount_to_pay = max(Decimal('0'), new_subscription_price - total_remaining_value_tomans)
        
        # Store upgrade information in session
        request.session['intelligent_upgrade'] = {
            'new_subscription_id': new_subscription.id,
            'new_subscription_name': new_subscription.name,
            'new_subscription_price': float(new_subscription_price),
            'remaining_value': float(total_remaining_value_tomans),
            'amount_to_pay_tomans': float(amount_to_pay),
            'current_subscription_id': current_subscription.id
        }
        
        # Redirect to purchase page with upgrade information
        return redirect('purchase_subscription')
        
    except apps.get_model('subscriptions', 'UserSubscription').DoesNotExist:
        messages.error(request, 'اشتراک فعلی شما یافت نشد.')
        return redirect('purchase_subscription')
    except Exception as e:
        messages.error(request, 'خطا در محاسبه ارتقاء هوشمند اشتراک.')
        return redirect('purchase_subscription')


@login_required
def complete_intelligent_upgrade(request):
    """
    Complete the intelligent subscription upgrade after payment
    """
    # This would be called after successful payment
    # Reset usage counters for the user using the new method that doesn't delete data
    user = request.user
    current_subscription = user.get_subscription_type()
    
    if current_subscription:
        # Reset all usage records for the current subscription using the new method
        UsageService.reset_user_usage(user, current_subscription)
    
    # Clear the intelligent upgrade session data
    if 'intelligent_upgrade' in request.session:
        del request.session['intelligent_upgrade']
    
    messages.success(request, 'اشتراک شما با موفقیت ارتقاء یافت و محدودیت‌های استفاده بازنشانی شد.')
    return redirect('purchase_subscription')

@login_required
def test_subscription_calculation(request):
    """
    Test view to diagnose subscription calculation issues
    """
    try:
        user = request.user
        
        # Test 1: Check if user has a subscription
        try:
            user_subscription = user.get_subscription_type()
        except Exception as e:
            return JsonResponse({'error': f'Error getting user subscription: {e}'})
        
        if not user_subscription:
            return JsonResponse({'error': 'No active subscription found'})
        
        # Test 2: Check if we can access the UserSubscription record
        try:
            UserSubscriptionModel = apps.get_model('subscriptions', 'UserSubscription')
            user_subscription_record = UserSubscriptionModel.objects.get(user=user, subscription_type=user_subscription)
        except apps.get_model('subscriptions', 'UserSubscription').DoesNotExist:
            return JsonResponse({'error': 'UserSubscription record not found'})
        except Exception as e:
            return JsonResponse({'error': f'Error accessing UserSubscription record: {e}'})
        
        # Test 3: Check token usage calculation
        try:
            total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
        except Exception as e:
            return JsonResponse({'error': f'Error calculating token usage: {e}'})
        
        # If all tests pass, return success
        return JsonResponse({
            'success': True,
            'message': 'All tests passed',
            'user_id': user.id,
            'subscription': user_subscription.name if user_subscription else None
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {e}'})
