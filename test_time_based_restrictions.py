import os
import django
import logging
from datetime import timedelta
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.apps import apps
from subscriptions.services import UsageService

def test_time_based_restrictions():
    """
    Test time-based restrictions for free models
    """
    logger.info("=== Testing Time-Based Restrictions ===")
    
    # Get model classes
    User = apps.get_model('accounts', 'User')
    AIModel = apps.get_model('ai_models', 'AIModel')
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    UserUsage = apps.get_model('subscriptions', 'UserUsage')
    
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
    original_hourly = subscription_type.hourly_max_tokens
    original_three_hours = subscription_type.three_hours_max_tokens
    original_twelve_hours = subscription_type.twelve_hours_max_tokens
    
    try:
        # Test 1: Hourly limit
        logger.info("=== Test 1: Hourly Limit ===")
        subscription_type.hourly_max_tokens = 1  # Set very low limit
        subscription_type.save()
        
        # Create usage that exceeds the limit
        now = timezone.now()
        hourly_start = now - timedelta(hours=1)
        
        # Delete any existing test records
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            created_at__gte=hourly_start
        ).delete()
        
        # Create usage records that exceed the limit
        UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2,  # Exceeds limit of 1
            created_at=now
        )
        
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        logger.info(f"Hourly limit test - Within limit: {within_limit}, Message: {message}")
        
        # Clean up
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2
        ).delete()
        
        # Test 2: 3-hour limit
        logger.info("=== Test 2: 3-Hour Limit ===")
        subscription_type.hourly_max_tokens = 0  # Reset
        subscription_type.three_hours_max_tokens = 1  # Set very low limit
        subscription_type.save()
        
        # Create usage that exceeds the limit
        three_hours_start = now - timedelta(hours=3)
        
        # Delete any existing test records
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            created_at__gte=three_hours_start
        ).delete()
        
        # Create usage records that exceed the limit
        UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2,  # Exceeds limit of 1
            created_at=now
        )
        
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        logger.info(f"3-hour limit test - Within limit: {within_limit}, Message: {message}")
        
        # Clean up
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2
        ).delete()
        
        # Test 3: 12-hour limit
        logger.info("=== Test 3: 12-Hour Limit ===")
        subscription_type.three_hours_max_tokens = 0  # Reset
        subscription_type.twelve_hours_max_tokens = 1  # Set very low limit
        subscription_type.save()
        
        # Create usage that exceeds the limit
        twelve_hours_start = now - timedelta(hours=12)
        
        # Delete any existing test records
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            created_at__gte=twelve_hours_start
        ).delete()
        
        # Create usage records that exceed the limit
        UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2,  # Exceeds limit of 1
            created_at=now
        )
        
        within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        logger.info(f"12-hour limit test - Within limit: {within_limit}, Message: {message}")
        
        # Clean up
        UserUsage.objects.filter(
            user=user,
            subscription_type=subscription_type,
            free_model_tokens_count=2
        ).delete()
        
    finally:
        # Restore original values
        subscription_type.hourly_max_tokens = original_hourly
        subscription_type.three_hours_max_tokens = original_three_hours
        subscription_type.twelve_hours_max_tokens = original_twelve_hours
        subscription_type.save()
        
        logger.info("=== Time-Based Restrictions Test Completed ===")

if __name__ == "__main__":
    test_time_based_restrictions()