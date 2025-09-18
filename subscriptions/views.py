from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from .models import SubscriptionType, UserSubscription, UserUsage, DiscountCode, DiscountUse
from .services import UsageService
from accounts.models import User
from zarinpal import ZarinPal, Config
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def purchase_subscription(request):
    """Display available subscriptions for purchase"""
    # Exclude free subscriptions from the purchase page
    subscriptions = SubscriptionType.objects.filter(is_active=True).exclude(price=0)
    return render(request, 'subscriptions/purchase.html', {'subscriptions': subscriptions})

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
        discount_code = get_object_or_404(DiscountCode, code=code)
        
        # Get the subscription
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
        
        # First calculate the remaining value from current subscription using the new method
        user = request.user
        user_subscription = user.get_subscription_type()
        amount_after_remaining_value = original_price
        
        if user_subscription:
            # Calculate total tokens used using the new ChatSessionUsage method
            total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
            
            # Use the subscription's max_tokens field
            total_token_limit = user_subscription.max_tokens
            
            # If no token limit is set, use a default calculation
            if total_token_limit == 0:
                total_token_limit = 1000000  # Default 1 million tokens
            
            # Calculate remaining tokens
            remaining_tokens = max(0, total_token_limit - total_tokens_used)
            
            # Calculate remaining days
            try:
                user_subscription_record = UserSubscription.objects.get(user=user, subscription_type=user_subscription)
                if user_subscription_record.end_date:
                    remaining_days = (user_subscription_record.end_date - timezone.now()).days
                    if remaining_days < 0:
                        remaining_days = 0
                else:
                    remaining_days = user_subscription.duration_days  # Assume full duration if no end date
            except UserSubscription.DoesNotExist:
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
        
    except DiscountCode.DoesNotExist:
        return JsonResponse({'error': 'Invalid discount code'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def initiate_payment(request, subscription_id):
    """Initiate payment for a subscription"""
    if request.method != 'POST':
        return redirect('purchase_subscription')
    
    subscription = get_object_or_404(SubscriptionType, id=subscription_id, is_active=True)
    
    # Check for intelligent upgrade
    intelligent_upgrade_data = request.session.get('intelligent_upgrade')
    if intelligent_upgrade_data and intelligent_upgrade_data.get('new_subscription_id') == subscription.id:
        # Use the calculated amount from intelligent upgrade
        original_price = Decimal(str(subscription.price))
        final_price = Decimal(str(intelligent_upgrade_data.get('amount_to_pay_tomans', subscription.price)))
        
        # Clean up session data
        if 'intelligent_upgrade' in request.session:
            del request.session['intelligent_upgrade']
    else:
        # Regular payment flow
        # Check for discount code
        discount_code = None
        discount_code_input = request.POST.get('discount_code')
        if discount_code_input:
            try:
                discount_code = DiscountCode.objects.get(code=discount_code_input)
                # Validate discount code
                if discount_code.subscription_types.exists() and not discount_code.subscription_types.filter(id=subscription_id).exists():
                    messages.error(request, 'This discount code is not valid for the selected subscription')
                    return redirect('purchase_subscription')
                
                if not discount_code.is_valid_for_user(request.user):
                    if not discount_code.is_active:
                        messages.error(request, 'This discount code is not active')
                    elif discount_code.is_expired:
                        messages.error(request, 'This discount code has expired')
                    elif discount_code.max_uses and discount_code.uses_count >= discount_code.max_uses:
                        messages.error(request, 'This discount code has reached its maximum usage limit')
                    else:
                        messages.error(request, 'You have reached the maximum usage limit for this discount code')
                    return redirect('purchase_subscription')
            except DiscountCode.DoesNotExist:
                messages.error(request, 'Invalid discount code')
                return redirect('purchase_subscription')
        
        # Calculate the final price
        original_price = Decimal(str(subscription.price))
        final_price = original_price
        
        # First calculate the remaining value from current subscription using the new method
        user = request.user
        user_subscription = user.get_subscription_type()
        amount_after_remaining_value = original_price
        
        if user_subscription:
            # Calculate total tokens used using the new ChatSessionUsage method
            total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
            
            # Use the subscription's max_tokens field
            total_token_limit = user_subscription.max_tokens
            
            # If no token limit is set, use a default calculation
            if total_token_limit == 0:
                total_token_limit = 1000000  # Default 1 million tokens
            
            # Calculate remaining tokens
            remaining_tokens = max(0, total_token_limit - total_tokens_used)
            
            # Calculate remaining days
            try:
                user_subscription_record = UserSubscription.objects.get(user=user, subscription_type=user_subscription)
                if user_subscription_record.end_date:
                    remaining_days = (user_subscription_record.end_date - timezone.now()).days
                    if remaining_days < 0:
                        remaining_days = 0
                else:
                    remaining_days = user_subscription.duration_days  # Assume full duration if no end date
            except UserSubscription.DoesNotExist:
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
            
            # Calculate the amount after deducting remaining value
            amount_after_remaining_value = max(Decimal('0'), original_price - total_remaining_value_tomans)
        
        # Apply discount if provided
        if discount_code:
            # Apply discount to the amount after remaining value calculation
            discount_amount = discount_code.calculate_discount(amount_after_remaining_value)
            final_price = amount_after_remaining_value - discount_amount
            
            # Check if discount is 100% and final price is 0
            if final_price <= 0:
                # Handle 100% discount - directly activate subscription without payment
                start_date = timezone.now()
                end_date = start_date + timezone.timedelta(days=subscription.duration_days)
                
                # Create or update user subscription
                user_subscription_obj, created = UserSubscription.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'subscription_type': subscription,
                        'is_active': True,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
                
                # Reset usage counters for the user when subscription is activated
                # Using the new method that doesn't delete data
                UsageService.reset_user_usage(request.user, subscription)
                
                # Record discount use
                DiscountUse.objects.create(
                    discount_code=discount_code,
                    user=request.user,
                    subscription_type=subscription,
                    original_price=original_price,
                    discount_amount=original_price,  # Full discount
                    final_price=Decimal('0')
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
        else:
            # No discount code, just apply remaining value deduction
            final_price = amount_after_remaining_value
    
    # Check if payment is needed (only prevent payment if final price is negative and no discount was used)
    user = request.user
    user_subscription = user.get_subscription_type()
    total_remaining_value_tomans = Decimal('0')
    discount_was_used = discount_code is not None
    
    if user_subscription:
        # Calculate total tokens used using the new ChatSessionUsage method
        total_tokens_used, free_model_tokens_used = UsageService.get_user_total_tokens_from_chat_sessions(user, user_subscription)
        
        # Use the subscription's max_tokens field
        total_token_limit = user_subscription.max_tokens
        
        # If no token limit is set, use a default calculation
        if total_token_limit == 0:
            total_token_limit = 1000000  # Default 1 million tokens
        
        # Calculate remaining tokens
        remaining_tokens = max(0, total_token_limit - total_tokens_used)
        
        # Calculate remaining days
        try:
            user_subscription_record = UserSubscription.objects.get(user=user, subscription_type=user_subscription)
            if user_subscription_record.end_date:
                remaining_days = (user_subscription_record.end_date - timezone.now()).days
                if remaining_days < 0:
                    remaining_days = 0
            else:
                remaining_days = user_subscription.duration_days  # Assume full duration if no end date
        except UserSubscription.DoesNotExist:
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
        
        # Only prevent payment if no discount was used and final price is negative
        # Changed from <= to < 0 to only show error when final price is actually negative
        if not discount_was_used and final_price < 0:
            messages.error(request, 'مبلغ قابل پرداخت از اعتبار باقیمانده شما کمتر است. نیازی به پرداخت نیست.')
            return redirect('purchase_subscription')
    
    # Initialize ZarinPal SDK
    try:
        config = Config(
            merchant_id=settings.ZARINPAL_MERCHANT_ID,
            sandbox=settings.ZARINPAL_SANDBOX
        )
        zarinpal_client = ZarinPal(config)
    except Exception as e:
        logger.error(f"Error initializing ZarinPal: {str(e)}")
        messages.error(request, 'خطا در اتصال به درگاه پرداخت. لطفاً مجدداً تلاش کنید.')
        return redirect('purchase_subscription')
    
    # Create payment request
    try:
        # Convert price to Rials (assuming price is in Tomans) for payment processing
        amount_in_rials = int(final_price * 10)
        
        payment_data = {
            "amount": amount_in_rials,
            "description": f"خرید اشتراک {subscription.name}",
            "callback_url": request.build_absolute_uri(reverse('payment_callback')),
            "mobile": getattr(request.user, 'phone_number', ''),  # Assuming User model has phone_number field
        }
        
        # Use the correct method to create payment
        payment_response = zarinpal_client.payments.create(payment_data)
        
        if payment_response and payment_response.get('data') and payment_response['data'].get('authority'):
            authority = payment_response['data']['authority']
            
            # Save payment info in session for verification (store Tomans amount for display)
            request.session['payment_authority'] = authority
            request.session['subscription_id'] = subscription.id
            request.session['payment_amount'] = amount_in_rials  # Store in Rials for payment verification
            request.session['original_price'] = float(original_price)
            request.session['final_price'] = float(final_price)  # Store in Tomans for display
            if 'discount_code' in locals() and discount_code:
                request.session['discount_code_id'] = discount_code.id
            
            # Redirect to ZarinPal payment page
            payment_url = zarinpal_client.payments.generate_payment_url(authority)
            return redirect(payment_url)
        else:
            error_message = payment_response.get('errors', 'خطا نامشخص در ایجاد پرداخت') if payment_response else 'پاسخ نامعتبر از سرور پرداخت'
            messages.error(request, f'خطا در ایجاد پرداخت: {error_message}')
            return redirect('purchase_subscription')
            
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        messages.error(request, f'خطا در ایجاد پرداخت: {str(e)}')
        return redirect('purchase_subscription')

def payment_callback(request):
    """Handle payment callback from ZarinPal"""
    # Initialize ZarinPal SDK
    try:
        config = Config(
            merchant_id=settings.ZARINPAL_MERCHANT_ID,
            sandbox=settings.ZARINPAL_SANDBOX
        )
        zarinpal_client = ZarinPal(config)
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
                # Verify payment with ZarinPal (amount should be in Rials)
                verification_data = {
                    "authority": authority,
                    "amount": payment_amount  # This is already in Rials
                }
                
                # Use the correct method to verify payment
                verification_response = zarinpal_client.verifications.verify(verification_data)
                
                if verification_response and verification_response.get('data') and verification_response['data'].get('code') == 100:
                    # Payment successful, activate subscription
                    subscription = get_object_or_404(SubscriptionType, id=subscription_id)
                    
                    # Calculate end date based on subscription duration from TODAY
                    start_date = timezone.now()
                    end_date = start_date + timezone.timedelta(days=subscription.duration_days)
                    
                    # Create or update user subscription using update_or_create to prevent IntegrityError
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
                    
                    # Record discount use if applicable
                    discount_code_id = request.session.get('discount_code_id')
                    if discount_code_id:
                        try:
                            discount_code = DiscountCode.objects.get(id=discount_code_id)
                            original_price = request.session.get('original_price', 0)  # This is in Tomans
                            final_price = request.session.get('final_price', 0)  # This is in Tomans
                            discount_amount = original_price - final_price
                            
                            # Record the discount use
                            DiscountUse.objects.create(
                                discount_code=discount_code,
                                user=request.user,
                                subscription_type=subscription,
                                original_price=original_price,
                                discount_amount=discount_amount,
                                final_price=final_price
                            )
                        except DiscountCode.DoesNotExist:
                            pass  # Ignore if discount code was deleted
                    
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
                    error_message = verification_response.get('errors', 'خطا در تأیید پرداخت') if verification_response else 'پاسخ نامعتبر از سرور تأیید'
                    return render(request, 'subscriptions/payment_callback.html', {
                        'payment_success': False,
                        'error_message': error_message
                    })
            else:
                return render(request, 'subscriptions/payment_callback.html', {
                    'payment_success': False,
                    'error_message': 'اطلاعات پرداخت نامعتبر است'
                })
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return render(request, 'subscriptions/payment_callback.html', {
                'payment_success': False,
                'error_message': f'خطا در تأیید پرداخت: {str(e)}'
            })
    else:
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
        
        # Use the subscription's max_tokens field for total limit
        total_token_limit = user_subscription.max_tokens
        
        # If no token limit is set, use a default calculation
        if total_token_limit == 0:
            total_token_limit = 1000000  # Default 1 million tokens
        
        # Calculate remaining tokens (total)
        remaining_tokens = max(0, total_token_limit - total_tokens_used)
        
        # Calculate remaining days
        user_subscription_record = UserSubscription.objects.get(user=user, subscription_type=user_subscription)
        if user_subscription_record.end_date:
            remaining_days = (user_subscription_record.end_date - timezone.now()).days
            if remaining_days < 0:
                remaining_days = 0
        else:
            remaining_days = user_subscription.duration_days  # Assume full duration if no end date
        
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
        return JsonResponse({
            'subscription_name': user_subscription.name,
            'subscription_price_tomans': float(subscription_price_tomans),
            'total_tokens_used': total_tokens_used,
            'free_model_tokens_used': free_model_tokens_used,  # Added separate free model token count
            'total_token_limit': total_token_limit,
            'remaining_tokens': remaining_tokens,
            'remaining_days': remaining_days,
            'total_remaining_value_tomans': float(total_remaining_value_tomans),
            'amount_to_pay_tomans': float(amount_to_pay),
            'user_has_remaining_value': total_remaining_value_tomans > 0
        })
        
    except UserSubscription.DoesNotExist:
        return JsonResponse({'error': 'No active subscription found'}, status=400)
    except Exception as e:
        logger.error(f"Error calculating remaining subscription value: {str(e)}")
        return JsonResponse({'error': 'Error calculating remaining subscription value'}, status=500)


@login_required
def intelligent_subscription_upgrade(request, new_subscription_id):
    """
    Handle intelligent subscription upgrade with remaining value calculation
    """
    user = request.user
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
        
        # Use the subscription's max_tokens field
        total_token_limit = current_subscription.max_tokens
        
        # If no token limit is set, use a default calculation
        if total_token_limit == 0:
            total_token_limit = 1000000  # Default 1 million tokens
        
        # Calculate remaining tokens
        remaining_tokens = max(0, total_token_limit - total_tokens_used)
        
        # Calculate remaining days
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
        
    except UserSubscription.DoesNotExist:
        messages.error(request, 'اشتراک فعلی شما یافت نشد.')
        return redirect('purchase_subscription')
    except Exception as e:
        logger.error(f"Error calculating intelligent upgrade: {str(e)}")
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
