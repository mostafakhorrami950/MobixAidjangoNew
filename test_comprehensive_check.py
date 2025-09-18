import os
import django
from django.utils import timezone
from datetime import timedelta
from django.apps import apps

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from subscriptions.services import UsageService

def test_comprehensive_check():
    # Get a test user, AI model, and subscription type
    try:
        User = apps.get_model('accounts', 'User')
        AIModel = apps.get_model('ai_models', 'AIModel')
        SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
        
        user = User.objects.first()
        ai_model = AIModel.objects.first()
        subscription_type = SubscriptionType.objects.first()
        
        if not user or not ai_model or not subscription_type:
            print("No user, AI model, or subscription type found in database")
            return
            
        print(f"Testing with user: {user.name}")
        print(f"Testing with AI model: {ai_model.name}")
        print(f"Testing with subscription: {subscription_type.name}")
        
        # Test comprehensive check
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"Comprehensive check result: {within_limit}, Message: {message}")
        
        # Test with a free model
        free_model = AIModel.objects.filter(is_free=True).first()
        if free_model:
            print(f"\nTesting with free model: {free_model.name}")
            within_limit, message = UsageService.comprehensive_check(user, free_model, subscription_type)
            print(f"Free model check result: {within_limit}, Message: {message}")
        
    except Exception as e:
        print(f"Error in test: {e}")

if __name__ == "__main__":
    test_comprehensive_check()