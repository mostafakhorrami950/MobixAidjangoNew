#!/usr/bin/env python
"""
Test script to verify the cost multiplier warning functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from ai_models.models import AIModel
from chatbot.models import ChatSession, Chatbot
from accounts.models import User
from django.utils import timezone
from django.apps import apps

# Import the function we want to test
from chatbot.views import _send_initial_welcome_message

def test_cost_multiplier_warning():
    print("Testing cost multiplier warning functionality...")
    
    # Create a test user if one doesn't exist
    user, created = User.objects.get_or_create(
        phone_number='09123456790',
        defaults={'name': 'Test User Warning', 'username': '09123456790'}
    )
    print(f"User: {user.name}")
    
    # Get or create a chatbot
    chatbot, created = Chatbot.objects.get_or_create(
        name='Test Chatbot',
        defaults={'description': 'A test chatbot for testing warnings'}
    )
    print(f"Chatbot: {chatbot.name}")
    
    # Get the existing AI model
    ai_model = AIModel.objects.first()
    print(f"AI Model: {ai_model.name}")
    print(f"Original cost multiplier: {ai_model.token_cost_multiplier}")
    
    # Create a chat session
    session = ChatSession.objects.create(
        user=user,
        chatbot=chatbot,
        title='Test Session for Warning'
    )
    print(f"Session created: {session.title}")
    
    # Test 1: Normal model with multiplier = 1.0 (should not show warning)
    print("\n--- Test 1: Model with multiplier = 1.0 ---")
    ai_model.token_cost_multiplier = 1.0
    ai_model.save()
    
    # Clear any existing messages
    ChatMessage = apps.get_model('chatbot', 'ChatMessage')
    ChatMessage.objects.filter(session=session).delete()
    
    # Send welcome message
    _send_initial_welcome_message(session, chatbot, ai_model)
    
    # Check the message content
    message = ChatMessage.objects.filter(session=session).first()
    has_warning = "هشدار مهم" in message.content
    print(f"Message contains warning: {has_warning}")
    print(f"Test 1: {'PASS' if not has_warning else 'FAIL'} - No warning expected for multiplier = 1.0")
    
    # Test 2: Model with multiplier = 2.0 (should show warning)
    print("\n--- Test 2: Model with multiplier = 2.0 ---")
    ai_model.token_cost_multiplier = 2.0
    ai_model.save()
    
    # Create a new session for this test
    session2 = ChatSession.objects.create(
        user=user,
        chatbot=chatbot,
        title='Test Session for Warning 2'
    )
    
    # Clear any existing messages
    ChatMessage.objects.filter(session=session2).delete()
    
    # Send welcome message
    _send_initial_welcome_message(session2, chatbot, ai_model)
    
    # Check the message content
    message = ChatMessage.objects.filter(session=session2).first()
    has_warning = "هشدار مهم" in message.content
    has_multiplier_text = "2.0" in message.content
    print(f"Message contains warning: {has_warning}")
    print(f"Message contains multiplier text: {has_multiplier_text}")
    print(f"Test 2: {'PASS' if has_warning and has_multiplier_text else 'FAIL'} - Warning expected for multiplier = 2.0")
    
    # Test 3: Model with multiplier = 1.5 (should show warning)
    print("\n--- Test 3: Model with multiplier = 1.5 ---")
    ai_model.token_cost_multiplier = 1.5
    ai_model.save()
    
    # Create a new session for this test
    session3 = ChatSession.objects.create(
        user=user,
        chatbot=chatbot,
        title='Test Session for Warning 3'
    )
    
    # Clear any existing messages
    ChatMessage.objects.filter(session=session3).delete()
    
    # Send welcome message
    _send_initial_welcome_message(session3, chatbot, ai_model)
    
    # Check the message content
    message = ChatMessage.objects.filter(session=session3).first()
    has_warning = "هشدار مهم" in message.content
    has_multiplier_text = "1.5" in message.content
    print(f"Message contains warning: {has_warning}")
    print(f"Message contains multiplier text: {has_multiplier_text}")
    print(f"Test 3: {'PASS' if has_warning and has_multiplier_text else 'FAIL'} - Warning expected for multiplier = 1.5")
    
    print("\n--- Test Summary ---")
    print("All tests completed. Check results above.")

if __name__ == '__main__':
    test_cost_multiplier_warning()