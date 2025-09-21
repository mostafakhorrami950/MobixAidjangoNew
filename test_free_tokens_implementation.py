import os
import django
from django.apps import apps

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from subscriptions.services import UsageService

def test_free_tokens_check():
    """
    Test the implementation of free model token limits and time-based restrictions
    """
    print("Testing free model token limits implementation...")
    
    # Get a test user, AI model, and subscription type
    try:
        # Get model classes
        User = apps.get_model('accounts', 'User')
        AIModel = apps.get_model('ai_models', 'AIModel')
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        
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
        
        # Test comprehensive check for free model
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"Comprehensive check result: {within_limit}")
        print(f"Message: {message}")
        
        # Test with a very low max_tokens_free to trigger the limit
        if subscription_type.max_tokens_free > 0:
            # Temporarily set max_tokens_free to a low value for testing
            original_max_tokens_free = subscription_type.max_tokens_free
            subscription_type.max_tokens_free = 1  # Very low limit
            subscription_type.save()
            
            print(f"\nTesting with artificially low max_tokens_free limit: {subscription_type.max_tokens_free}")
            within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
            print(f"Comprehensive check result with low limit: {within_limit}")
            print(f"Message: {message}")
            
            # Restore original value
            subscription_type.max_tokens_free = original_max_tokens_free
            subscription_type.save()
            
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_free_tokens_check()