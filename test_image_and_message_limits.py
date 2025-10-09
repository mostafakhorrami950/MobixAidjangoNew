#!/usr/bin/env python
"""
Test script for image generation and message sending limitations
"""
import os
import sys
import django
import json
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_and_message_limits():
    """Test image generation and message sending limitations"""
    try:
        # Get a test user (first user in database)
        User = get_user_model()
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
        
        # Test 1: Check if we can access the validate_message endpoint
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from chatbot.api import ChatSessionViewSet
        from chatbot.models import ChatSession, Chatbot
        import json
        
        # Create a test chat session
        from django.apps import apps
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        
        chatbot = Chatbot.objects.filter(is_active=True).first()
        if not chatbot:
            logger.error("No active chatbot found")
            return False
            
        session = ChatSession.objects.create(
            user=user,
            chatbot=chatbot,
            title="Test Session for Limit Testing"
        )
        logger.info(f"Created test session: {session.id}")
        
        # Test 2: Test the validation service directly
        from chatbot.validation_service import MessageValidationService
        
        # Test basic validation (should pass)
        logger.info("Testing basic validation...")
        is_valid, error_message, error_code = MessageValidationService.validate_all_limits(
            user=user,
            session=session,
            ai_model=session.ai_model,
            uploaded_files=None,
            generate_image=False
        )
        logger.info(f"Basic validation result: valid={is_valid}, message='{error_message}', code={error_code}")
        
        # Test image generation validation
        logger.info("Testing image generation validation...")
        is_valid, error_message, error_code = MessageValidationService.validate_all_limits(
            user=user,
            session=session,
            ai_model=session.ai_model,
            uploaded_files=None,
            generate_image=True
        )
        logger.info(f"Image generation validation result: valid={is_valid}, message='{error_message}', code={error_code}")
        
        # Test 3: Test the actual send_message view logic by calling validation service directly
        # This simulates what happens in the send_message view
        logger.info("Testing send_message validation logic...")
        
        # Simulate the validation that happens in send_message view
        is_valid, error_message, error_code = MessageValidationService.validate_all_limits(
            user=user,
            session=session,
            ai_model=session.ai_model,
            uploaded_files=None,
            generate_image=True  # This simulates image generation request
        )
        logger.info(f"Send message validation result: valid={is_valid}, message='{error_message}', code={error_code}")
        
        # Clean up
        session.delete()
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_image_and_message_limits()
    sys.exit(0 if success else 1)