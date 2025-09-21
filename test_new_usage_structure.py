import os
import django
from django.apps import apps
from django.utils import timezone
from datetime import timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from subscriptions.services import UsageService

def test_new_usage_structure():
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
        
        # Create a few usage records
        print("Creating usage records...")
        UsageService.increment_usage(user, subscription_type, messages_count=1, tokens_count=50, is_free_model=False)
        UsageService.increment_usage(user, subscription_type, messages_count=1, tokens_count=75, is_free_model=False)
        UsageService.increment_usage(user, subscription_type, messages_count=1, tokens_count=25, is_free_model=True)
        
        # Test get_user_usage_for_period
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        
        messages, tokens = UsageService.get_user_usage_for_period(
            user, subscription_type, one_hour_ago, now
        )
        
        print(f"Usage in last hour: {messages} messages, {tokens} tokens")
        
        # Test get_user_free_model_usage_for_period
        free_messages, free_tokens = UsageService.get_user_free_model_usage_for_period(
            user, subscription_type, one_hour_ago, now
        )
        
        print(f"Free model usage in last hour: {free_messages} messages, {free_tokens} tokens")
        
        # Clean up test records (optional)
        UserUsage = apps.get_model('subscriptions', 'UserUsage')
        test_records = UserUsage.objects.filter(
            user=user, 
            subscription_type=subscription_type,
            created_at__gte=one_hour_ago
        )
        print(f"Created {test_records.count()} test records")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_usage_structure()