#!/usr/bin/env python3

"""
Test script to verify the server error fixes:
1. UnboundLocalError for time-based variables in comprehensive_check
2. AttributeError for 'chatbot.ai_model' in templates

This script will test key endpoints and functionality that were throwing errors.
"""

import os
import sys
import django
from django.test.client import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobixaidjangonew.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import SubscriptionType, UserSubscription
from subscriptions.services import UsageService
from ai_models.models import AIModel, ModelSubscription
from chatbot.models import Chatbot, ChatSession
import json

def test_comprehensive_check():
    """Test that comprehensive_check doesn't throw UnboundLocalError anymore"""
    print("Testing comprehensive_check method...")
    
    try:
        # Get the first user
        User = get_user_model()
        user = User.objects.first()
        if not user:
            print("❌ No user found for testing")
            return False
        
        # Get user's subscription
        subscription_type = user.get_subscription_type()
        if not subscription_type:
            print("❌ No subscription found for user")
            return False
        
        # Get a free AI model
        ai_model = AIModel.objects.filter(is_free=True).first()
        if not ai_model:
            print("❌ No free AI model found for testing")
            return False
        
        # Test comprehensive check
        result, message = UsageService.comprehensive_check(user, ai_model, subscription_type)
        print(f"✅ Comprehensive check completed successfully: {result}, {message}")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive check failed with error: {str(e)}")
        return False

def test_chat_endpoints():
    """Test chat endpoints for server errors"""
    print("Testing chat endpoints...")
    
    client = Client()
    
    try:
        # Test main chat page (this uses the templates with chatbot.ai_model)
        response = client.get('/chat/')
        if response.status_code == 200:
            print("✅ Chat page loads successfully")
        else:
            print(f"❌ Chat page returned status {response.status_code}")
            return False
        
        # Test chatbot models endpoint
        chatbot = Chatbot.objects.filter(is_active=True).first()
        if chatbot:
            response = client.get(f'/chat/chatbot/{chatbot.id}/models/')
            if response.status_code == 200 or response.status_code == 302:  # 302 for login redirect
                print("✅ Chatbot models endpoint works")
            else:
                print(f"❌ Chatbot models endpoint returned status {response.status_code}")
                return False
        
        # Test models endpoint
        response = client.get('/chat/models/')
        if response.status_code == 200 or response.status_code == 302:  # 302 for login redirect
            print("✅ Models endpoint works")
        else:
            print(f"❌ Models endpoint returned status {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chat endpoints test failed with error: {str(e)}")
        return False

def test_template_rendering():
    """Test template rendering without chatbot.ai_model errors"""
    print("Testing template rendering...")
    
    from django.template.loader import get_template
    from django.template import Context
    
    try:
        # Test the main chat template
        template = get_template('chatbot/chat.html')
        
        # Create mock data
        available_chatbots = [
            {'id': 1, 'name': 'Test Bot', 'user_has_access': True}
        ]
        available_models = [
            {'model_id': 'test-model', 'name': 'Test Model', 'is_free': True, 'user_has_access': True}
        ]
        chat_sessions = []
        
        context = {
            'available_chatbots': available_chatbots,
            'available_models': available_models,
            'chat_sessions': chat_sessions,
        }
        
        # Try to render the template
        rendered = template.render(context)
        print("✅ Chat template renders successfully")
        return True
        
    except Exception as e:
        print(f"❌ Template rendering failed with error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Server Error Fixes\n" + "="*50)
    
    tests = [
        ("Comprehensive Check", test_comprehensive_check),
        ("Chat Endpoints", test_chat_endpoints),
        ("Template Rendering", test_template_rendering),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n📊 Test Results:")
    print("="*50)
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The server error fixes are working correctly.")
        print("The following issues have been resolved:")
        print("1. ✅ UnboundLocalError for time-based variables in comprehensive_check")
        print("2. ✅ AttributeError for 'chatbot.ai_model' in templates")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)