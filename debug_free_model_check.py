import os
import django
import logging

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_free_model_check.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from django.apps import apps
from subscriptions.services import UsageService

def debug_free_model_check():
    """
    Debug the free model check with detailed logging
    """
    logger.info("=== Starting Debug Free Model Check ===")
    
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
        
    logger.info(f"User: {user.name} (ID: {user.id})")
    logger.info(f"AI Model: {ai_model.name} (ID: {ai_model.id}, Free: {ai_model.is_free})")
    logger.info(f"Subscription: {subscription_type.name} (ID: {subscription_type.id})")
    
    logger.info("Subscription limits:")
    logger.info(f"  max_tokens_free: {subscription_type.max_tokens_free}")
    logger.info(f"  hourly_max_tokens: {subscription_type.hourly_max_tokens}")
    logger.info(f"  three_hours_max_tokens: {subscription_type.three_hours_max_tokens}")
    logger.info(f"  twelve_hours_max_tokens: {subscription_type.twelve_hours_max_tokens}")
    logger.info(f"  daily_max_tokens: {subscription_type.daily_max_tokens}")
    logger.info(f"  weekly_max_tokens: {subscription_type.weekly_max_tokens}")
    logger.info(f"  monthly_max_tokens: {subscription_type.monthly_max_tokens}")
    logger.info(f"  monthly_free_model_messages: {subscription_type.monthly_free_model_messages}")
    logger.info(f"  monthly_free_model_tokens: {subscription_type.monthly_free_model_tokens}")
    
    # Test comprehensive check
    logger.info("=== Running Comprehensive Check ===")
    within_limit, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
    
    logger.info(f"Result: Within limit = {within_limit}")
    logger.info(f"Message: {message}")
    
    logger.info("=== Debug Free Model Check Completed ===")

if __name__ == "__main__":
    debug_free_model_check()