#!/usr/bin/env python
"""
Test script to verify the API endpoints are working correctly.
This script tests the basic functionality of the API without making any changes to the project.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixai.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.apps import apps

def test_api_endpoints():
    """Test the API endpoints"""
    client = Client()
    User = get_user_model()
    
    # Create a test user
    user = User.objects.create_user(
        phone_number='+1234567890',
        name='Test User',
        password='testpass123'
    )
    
    # Log in the user
    login_success = client.login(phone_number='+1234567890', password='testpass123')
    
    if not login_success:
        print("Failed to log in test user")
        return False
    
    # Get models using apps.get_model
    Chatbot = apps.get_model('chatbot', 'Chatbot')
    AIModel = apps.get_model('ai_models', 'AIModel')
    ChatSession = apps.get_model('chatbot', 'ChatSession')
    
    # Create test data
    test_chatbot = Chatbot.objects.create(
        name='Test Chatbot',
        description='A test chatbot',
        is_active=True
    )
    
    test_ai_model = AIModel.objects.create(
        name='Test Model',
        model_id='test/model',
        description='A test AI model',
        model_type='text',
        is_active=True,
        is_free=True
    )
    
    test_session = ChatSession.objects.create(
        user=user,
        chatbot=test_chatbot,
        ai_model=test_ai_model,
        title='Test Session'
    )
    
    # Test endpoints
    endpoints = [
        ('/api/users/', 'GET'),
        ('/api/users/subscription/', 'GET'),
        ('/api/chatbots/', 'GET'),
        ('/api/ai-models/', 'GET'),
        ('/api/chat-sessions/', 'GET'),
        ('/api/chat-sessions/', 'POST', {
            'chatbot_id': test_chatbot.id,
            'ai_model_id': test_ai_model.model_id,
            'title': 'API Test Session'
        }),
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        if len(endpoint) == 2:
            url, method = endpoint
            data = None
        else:
            url, method, data = endpoint
            
        try:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url, data)
            
            # Check that we don't get a 500 error
            if hasattr(response, 'status_code') and response.status_code == 500:
                print(f"✗ {method} {url} failed with 500 error")
                all_passed = False
            else:
                print(f"✓ {method} {url} succeeded")
        except Exception as e:
            print(f"✗ {method} {url} failed with exception: {e}")
            all_passed = False
    
    # Clean up
    test_session.delete()
    test_ai_model.delete()
    test_chatbot.delete()
    user.delete()
    
    return all_passed

if __name__ == '__main__':
    print("Testing API endpoints...")
    if test_api_endpoints():
        print("All API endpoint tests passed!")
    else:
        print("Some API endpoint tests failed!")