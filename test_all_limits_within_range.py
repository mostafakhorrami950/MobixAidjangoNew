import os
import django
import logging

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.apps import apps
from subscriptions.services import UsageService

def test_all_limits_within_range():
    """
    Test that when all limits are within range, access is granted
    """
    logger.info("=== Testing All Limits Within Range ===")
    
    # Get model classes
    User = apps.get_model('accounts', 'User')
    AIModel = apps.get_model('ai_models', 'AIModel')
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    
    # Get the first user
    user = User.objects.first()
    if not user:
        logger.error("No user found in database")
        return
        
    # Get a free AI model
    ai_model = AIModel.objects.filter(is_free=True).first()
    if not ai_model:
        logger.error("No free AI model found in database")
        return
        
    # Get a subscription type
    subscription_type = SubscriptionType.objects.first()
    if not subscription_type:
        logger.error("No subscription type found in database")
        return
    
    # Store original values
    original_max_tokens_free = subscription_type.max_tokens_free
    
    try:
        # Temporarily set max_tokens_free to a very high value to ensure it's not exceeded
        subscription_type.max_tokens_free = 10000  # High enough to not be exceeded
        subscription_type.save()
        
        # Run comprehensive check
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        logger.info(f"All limits within range test - Within limit: {within_limit}, Message: {message}")
        
        if within_limit:
            logger.info("SUCCESS: All limits are within range and access is granted")
        else:
            logger.error("FAILURE: Access was denied despite all limits being within range")
        
    finally:
        # Restore original value
        subscription_type.max_tokens_free = original_max_tokens_free
        subscription_type.save()
        
        logger.info("=== All Limits Within Range Test Completed ===")

if __name__ == "__main__":
    test_all_limits_within_range()