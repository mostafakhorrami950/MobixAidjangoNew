import os
import django
from django.utils import timezone
from datetime import timedelta
from django.apps import apps

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from subscriptions.services import UsageService

def test_usage_limits():
    # Get a test user and subscription type
    try:
        User = apps.get_model('accounts', 'User')
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        
        user = User.objects.first()
        subscription_type = SubscriptionType.objects.first()
        
        if not user or not subscription_type:
            print("No user or subscription type found in database")
            return
            
        print(f"Testing with user: {user.name}")
        print(f"Testing with subscription: {subscription_type.name}")
        
        # Test usage limit checking
        within_limit, message = UsageService.check_usage_limit(user, subscription_type, 100, False)
        print(f"Usage limit check result: {within_limit}, Message: {message}")
        
        # Test free model usage limit checking
        within_limit, message = UsageService.check_usage_limit(user, subscription_type, 100, True)
        print(f"Free model usage limit check result: {within_limit}, Message: {message}")
        
        # Test incrementing usage
        UsageService.increment_usage(user, subscription_type, 1, 100, False)
        print("Incremented regular usage")
        
        # Test incrementing free model usage
        UsageService.increment_usage(user, subscription_type, 1, 50, True)
        print("Incremented free model usage")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_usage_limits()