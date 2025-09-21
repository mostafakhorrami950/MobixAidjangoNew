import os
import django
from django.apps import apps

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from subscriptions.services import UsageService

def test_free_tokens_check():
    # Get a test user, AI model, and subscription type
    try:
        User = apps.get_model('accounts', 'User')
        AIModel = apps.get_model('ai_models', 'AIModel')
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        
        user = User.objects.first()
        ai_model = AIModel.objects.filter(is_free=True).first()
        subscription_type = SubscriptionType.objects.first()
        
        if not user or not ai_model or not subscription_type:
            print("No user, AI model, or subscription type found in database")
            return
            
        print(f"Testing with user: {user.name}")
        print(f"Testing with free AI model: {ai_model.name}")
        print(f"Testing with subscription: {subscription_type.name}")
        print(f"Max free tokens: {subscription_type.max_tokens_free}")
        
        # Test comprehensive check for free model
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"Comprehensive check result: {within_limit}, Message: {message}")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_free_tokens_check()