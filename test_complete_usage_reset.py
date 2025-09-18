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

def test_complete_usage_reset():
    """
    Test the complete usage reset functionality including both UserUsage and ChatSessionUsage
    """
    logger.info("=== Testing Complete Usage Reset ===")
    
    # Get model classes
    User = apps.get_model('accounts', 'User')
    SubscriptionType = apps.get_model('subscriptions', 'SubscriptionType')
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    ChatSessionUsage = apps.get_model('chatbot', 'ChatSessionUsage')
    UserUsage = apps.get_model('subscriptions', 'UserUsage')
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
        title="Test Session for Complete Usage Reset"
    )
    
    # Create some test chat session usage records
    logger.info("Creating test chat session usage records...")
    for i in range(3):
        ChatSessionUsage.objects.create(
            session=chat_session,
            user=user,
            subscription_type=subscription_type,
            tokens_count=100 + i * 50,
            free_model_tokens_count=50 + i * 25
        )
    
    # Create some test user usage records
    logger.info("Creating test user usage records...")
    for i in range(2):
        UserUsage.objects.create(
            user=user,
            subscription_type=subscription_type,
            messages_count=5 + i * 3,
            tokens_count=200 + i * 100,
            free_model_messages_count=2 + i,
            free_model_tokens_count=100 + i * 50
        )
    
    # Count records before reset
    chat_session_before_count = ChatSessionUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    ).count()
    
    user_usage_before_count = UserUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    ).count()
    
    logger.info(f"Chat session usage records before reset: {chat_session_before_count}")
    logger.info(f"User usage records before reset: {user_usage_before_count}")
    
    # Check the actual values in user usage records before reset
    user_usage_records_before = UserUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    )
    
    for record in user_usage_records_before:
        logger.info(f"Before reset - UserUsage ID {record.id}: "
                   f"messages={record.messages_count}, tokens={record.tokens_count}, "
                   f"free_messages={record.free_model_messages_count}, free_tokens={record.free_model_tokens_count}")
    
    # Test the reset methods
    logger.info("Resetting user usage...")
    UsageService.reset_user_usage(user, subscription_type)
    
    logger.info("Resetting chat session usage...")
    UsageService.reset_chat_session_usage(user, subscription_type)
    
    # Count records after reset
    chat_session_after_count = ChatSessionUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    ).count()
    
    user_usage_after_count = UserUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    ).count()
    
    logger.info(f"Chat session usage records after reset: {chat_session_after_count}")
    logger.info(f"User usage records after reset: {user_usage_after_count}")
    
    # Check the actual values in user usage records after reset
    user_usage_records_after = UserUsage.objects.filter(
        user=user,
        subscription_type=subscription_type
    )
    
    for record in user_usage_records_after:
        logger.info(f"After reset - UserUsage ID {record.id}: "
                   f"messages={record.messages_count}, tokens={record.tokens_count}, "
                   f"free_messages={record.free_model_messages_count}, free_tokens={record.free_model_tokens_count}")
    
    # Clean up the test chat session
    chat_session.delete()
    
    # Verify results
    chat_session_reset_success = (chat_session_after_count == 0)
    user_usage_reset_success = True
    
    # Check that all user usage records have zero values
    for record in user_usage_records_after:
        if (record.messages_count != 0 or record.tokens_count != 0 or 
            record.free_model_messages_count != 0 or record.free_model_tokens_count != 0):
            user_usage_reset_success = False
            break
    
    if chat_session_reset_success and user_usage_reset_success:
        logger.info("SUCCESS: Complete usage reset works correctly")
        logger.info("- ChatSessionUsage records were deleted")
        logger.info("- UserUsage records were reset to zero values")
    else:
        logger.error("FAILURE: Complete usage reset did not work as expected")
        if not chat_session_reset_success:
            logger.error("- ChatSessionUsage records were not properly deleted")
        if not user_usage_reset_success:
            logger.error("- UserUsage records were not properly reset to zero")
    
    logger.info("=== Complete Usage Reset Test Completed ===")

if __name__ == "__main__":
    test_complete_usage_reset()