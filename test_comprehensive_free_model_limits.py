import os
import django
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from subscriptions.services import UsageService

def test_comprehensive_free_model_limits():
    """
    Comprehensive test for free model limits implementation
    """
    print("Testing comprehensive free model limits implementation...")
    
    # Get model classes
    User = apps.get_model('accounts', 'User')
    AIModel = apps.get_model('ai_models', 'AIModel')
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    UserUsage = apps.get_model('subscriptions', 'UserUsage')
    
    # Get the first user
    user = User.objects.first()
    if not user:
        print("No user found in database")
        return
        
    # Get a free AI model
    ai_model = AIModel.objects.filter(is_free=True).first()
    if not ai_model:
        print("No free AI model found in database")
        return
        
    # Get a subscription type
    subscription_type = SubscriptionType.objects.first()
    if not subscription_type:
        print("No subscription type found in database")
        return
        
    print(f"Testing with user: {user.name}")
    print(f"Testing with free AI model: {ai_model.name}")
    print(f"Testing with subscription: {subscription_type.name}")
    print(f"Max free tokens: {subscription_type.max_tokens_free}")
    print(f"Monthly free model messages: {subscription_type.monthly_free_model_messages}")
    print(f"Monthly free model tokens: {subscription_type.monthly_free_model_tokens}")
    
    # Test 1: Basic comprehensive check
    print("\n=== Test 1: Basic comprehensive check ===")
    within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
    print(f"Comprehensive check result: {within_limit}")
    print(f"Message: {message}")
    
    # Test 2: Test max_tokens_free limit
    if subscription_type.max_tokens_free > 0:
        print("\n=== Test 2: Max tokens free limit ===")
        # Temporarily set max_tokens_free to a low value for testing
        original_max_tokens_free = subscription_type.max_tokens_free
        subscription_type.max_tokens_free = 1  # Very low limit
        subscription_type.save()
        
        print(f"Testing with artificially low max_tokens_free limit: {subscription_type.max_tokens_free}")
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"Comprehensive check result with low limit: {within_limit}")
        print(f"Message: {message}")
        
        # Restore original value
        subscription_type.max_tokens_free = original_max_tokens_free
        subscription_type.save()
    
    # Test 3: Test time-based limits (using hourly as example)
    if subscription_type.hourly_max_tokens > 0:
        print("\n=== Test 3: Hourly time-based limit ===")
        # Temporarily set hourly_max_tokens to a low value for testing
        original_hourly_max_tokens = subscription_type.hourly_max_tokens
        subscription_type.hourly_max_tokens = 1  # Very low limit
        subscription_type.save()
        
        # Create a usage record to trigger the limit
        UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2,  # Exceed the limit
            free_model_messages_count=1
        )
        
        print(f"Testing with artificially low hourly_max_tokens limit: {subscription_type.hourly_max_tokens}")
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"Comprehensive check result with low hourly limit: {within_limit}")
        print(f"Message: {message}")
        
        # Clean up test usage record
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2
        ).delete()
        
        # Restore original value
        subscription_type.hourly_max_tokens = original_hourly_max_tokens
        subscription_type.save()
    
    # Test 4: Test monthly free model message limit
    if subscription_type.monthly_free_model_messages > 0:
        print("\n=== Test 4: Monthly free model message limit ===")
        # Temporarily set monthly_free_model_messages to a low value for testing
        original_monthly_free_model_messages = subscription_type.monthly_free_model_messages
        subscription_type.monthly_free_model_messages = 1  # Very low limit
        subscription_type.save()
        
        # Create a usage record to trigger the limit
        now = timezone.now()
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            monthly_end = monthly_start.replace(year=monthly_start.year + 1, month=1)
        else:
            monthly_end = monthly_start.replace(month=monthly_start.month + 1)
        
        UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            free_model_messages_count=2,  # Exceed the limit
            free_model_tokens_count=0,
            created_at=now
        )
        
        print(f"Testing with artificially low monthly_free_model_messages limit: {subscription_type.monthly_free_model_messages}")
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"Comprehensive check result with low monthly message limit: {within_limit}")
        print(f"Message: {message}")
        
        # Clean up test usage record
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            free_model_messages_count=2,
            created_at=now
        ).delete()
        
        # Restore original value
        subscription_type.monthly_free_model_messages = original_monthly_free_model_messages
        subscription_type.save()
    
    print("\nComprehensive test completed successfully!")

if __name__ == "__main__":
    test_comprehensive_free_model_limits()