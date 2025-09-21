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
from django.utils import timezone

def test_reset_chat_session_usage():
    """
    Test the reset_chat_session_usage method
    """
    logger.info("=== Testing reset_chat_session_usage Method ===")
    
    # Get model classes
    User = apps.get_model('accounts', 'User')
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    ChatSessionUsage = apps.get_model('chatbot', 'ChatSessionUsage')
    AIModel = apps.get_model('ai_models', 'AIModel')
    
    # Get the first user
    user = User.objects.first()
    if not user:
        logger.error("No user found in database")
        return
        
    # Get a subscription type
    subscription_type = SubscriptionType.objects.first()
    if not subscription_type:
        logger.error("No subscription type found in database")
        return
    
    # Get an AI model for the chat session
    ai_model = AIModel.objects.first()
    if not ai_model:
        logger.error("No AI model found in database")
        return
    
    # Create a chat session
    chat_session = ChatSession.objects.create(
        user=user,
        ai_model=ai_model,
        title="Test Session for Usage Reset"
    )
    
    # Create some test chat session usage records
    logger.info("Creating test chat session usage records...")
    
    # Create a few chat session usage records
    for i in range(3):
        ChatSessionUsage.objects.create(
            session=chat_session,
            user=user,
            subscription_type=subscription_type,
            tokens_count=100 + i * 50,
            free_model_tokens_count=50 + i * 25
        )
    
    # Count records before reset
    before_count = ChatSessionUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    ).count()
    
    logger.info(f"Chat session usage records before reset: {before_count}")
    
    # Test the reset method
    deleted_count = UsageService.reset_chat_session_usage(user, subscription_type)
    
    # Count records after reset
    after_count = ChatSessionUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    ).count()
    
    logger.info(f"Chat session usage records after reset: {after_count}")
    logger.info(f"Deleted records count: {deleted_count}")
    
    # Clean up the test chat session
    chat_session.delete()
    
    if deleted_count == before_count and after_count == 0:
        logger.info("SUCCESS: reset_chat_session_usage method works correctly")
    else:
        logger.error("FAILURE: reset_chat_session_usage method did not work as expected")
    
    logger.info("=== Test Completed ===")

if __name__ == "__main__":
    test_reset_chat_session_usage()