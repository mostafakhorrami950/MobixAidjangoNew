#!/usr/bin/env python
"""
Simple test for image generation and message sending limitations
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_limits():
    """Test image generation and message sending limitations"""
    try:
        # Import models using apps.get_model
        from django.apps import apps
        from chatbot.validation_service import MessageValidationService
        from chatbot.limitation_service import LimitationMessageService
        from subscriptions.services import UsageService
        
        # Get a test user (first user in database)
        User = apps.get_model('accounts', 'User')
        user = User.objects.first()
        if not user:
            logger.error("No user found in database")
            return False
            
        logger.info(f"Testing with user: {user}")
        
        # Get user's subscription
        subscription_type = user.get_subscription_type()
        if not subscription_type:
            logger.error("User has no subscription")
            return False
            
        logger.info(f"User subscription: {subscription_type.name}")
        logger.info(f"Daily image limit: {subscription_type.daily_image_generation_limit}")
        logger.info(f"Hourly message limit: {subscription_type.hourly_max_messages}")
        logger.info(f"Daily token limit: {subscription_type.daily_max_tokens}")
        
        # Test the validation service with a simple check
        logger.info("Testing validation service...")
        
        # Test image generation limit check directly
        logger.info("Testing image generation limit check...")
        within_limit, message = UsageService.check_image_generation_limit(
            user, subscription_type
        )
        logger.info(f"Image generation limit check: within_limit={within_limit}, message='{message}'")
        
        # Test hourly message limit check
        logger.info("Testing hourly message limit check...")
        within_limit, message = UsageService.check_usage_limit(
            user, subscription_type, 1, False  # 1 token, not free model
        )
        logger.info(f"Usage limit check: within_limit={within_limit}, message='{message}'")
        
        logger.info("All tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_limits()
    print(f"Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)