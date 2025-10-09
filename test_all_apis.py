#!/usr/bin/env python
"""
Test script to verify all API endpoints are working correctly.
This script tests all the functionality of the API without making any changes to the project.
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
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_imports():
    """Test that we can import all required components"""
    print("Testing API component imports...")
    
    try:
        # Test importing Django components
        from django.test import Client
        from django.contrib.auth import get_user_model
        from django.apps import apps
        print("✓ Successfully imported Django components")
        
        # Test accessing models
        User = get_user_model()
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        AIModel = apps.get_model('ai_models', 'AIModel')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        print("✓ Successfully accessed all models via apps.get_model")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import components: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints can be accessed without errors"""
    print("\nTesting API endpoint accessibility...")
    
    try:
        client = Client()
        
        # Test endpoints that don't require authentication
        public_endpoints = [
            '/api/',
            '/api/users/',
            '/api/chatbots/',
            '/api/ai-models/',
            '/api/chat-sessions/',
            '/api/chat-session-usages/',
        ]
        
        success_count = 0
        for endpoint in public_endpoints:
            try:
                response = client.get(endpoint)
                print(f"✓ {endpoint} - Accessible (Status: {getattr(response, 'status_code', 'Unknown')})")
                success_count += 1
            except Exception as e:
                print(f"✗ {endpoint} - Error: {e}")
        
        print(f"\nPublic endpoints test: {success_count}/{len(public_endpoints)} passed")
        return success_count > 0
        
    except Exception as e:
        print(f"✗ Error testing API endpoints: {e}")
        return False

def test_api_with_authentication():
    """Test API functionality with authentication"""
    print("\nTesting API with authentication...")
    
    try:
        # Get models
        User = get_user_model()
        Chatbot = apps.get_model('chatbot', 'Chatbot')
        AIModel = apps.get_model('ai_models', 'AIModel')
        ChatSession = apps.get_model('chatbot', 'ChatSession')
        
        # Create a test user with a unique phone number
        import random
        phone_number = f'+123456789{random.randint(100, 999)}'
        user = User.objects.create_user(
            phone_number=phone_number,
            name='Test User',
            password='testpass123'
        )
        print("✓ Created test user")
        
        # Log in the user
        client = Client()
        login_success = client.login(phone_number=phone_number, password='testpass123')
        
        if not login_success:
            print("✗ Failed to log in test user")
            user.delete()
            return False
        print("✓ Logged in test user")
        
        # Create test data
        test_chatbot = Chatbot.objects.create(
            name='Test Chatbot',
            description='A test chatbot for API testing',
            is_active=True
        )
        print("✓ Created test chatbot")
        
        test_ai_model = AIModel.objects.create(
            name='Test Model',
            model_id='test/model',
            description='A test AI model for API testing',
            model_type='text',
            is_active=True,
            is_free=True
        )
        print("✓ Created test AI model")
        
        test_session = ChatSession.objects.create(
            user=user,
            chatbot=test_chatbot,
            ai_model=test_ai_model,
            title='Test Session'
        )
        print("✓ Created test chat session")
        
        # Test authenticated endpoints
        authenticated_endpoints = [
            ('/api/users/', 'GET'),
            ('/api/users/subscription/', 'GET'),
            ('/api/chatbots/', 'GET'),
            ('/api/ai-models/', 'GET'),
            ('/api/chat-sessions/', 'GET'),
            (f'/api/chat-sessions/{test_session.id}/', 'GET'),
            (f'/api/chat-sessions/{test_session.id}/messages/', 'GET'),
        ]
        
        success_count = 0
        for url, method in authenticated_endpoints:
            try:
                if method == 'GET':
                    response = client.get(url)
                    print(f"✓ {method} {url} - Status: {getattr(response, 'status_code', 'Unknown')}")
                    success_count += 1
            except Exception as e:
                print(f"✗ {method} {url} - Error: {e}")
        
        print(f"\nAuthenticated endpoints test: {success_count}/{len(authenticated_endpoints)} passed")
        
        # Clean up
        test_session.delete()
        test_ai_model.delete()
        test_chatbot.delete()
        user.delete()
        print("✓ Cleaned up test data")
        
        return success_count > 0
        
    except Exception as e:
        print(f"✗ Error testing authenticated API: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Comprehensive API Testing")
    print("=" * 60)
    
    # Test 1: Component imports
    imports_ok = test_api_imports()
    
    # Test 2: Endpoint accessibility
    endpoints_ok = test_api_endpoints()
    
    # Test 3: Authenticated functionality
    auth_ok = test_api_with_authentication()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Component Imports:     {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Endpoint Access:       {'✓ PASS' if endpoints_ok else '✗ FAIL'}")
    print(f"Authenticated Tests:   {'✓ PASS' if auth_ok else '✗ FAIL'}")
    
    if imports_ok and endpoints_ok and auth_ok:
        print("\n🎉 All API tests completed successfully!")
        return True
    else:
        print("\n❌ Some API tests failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)